from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import FileResponse, JSONResponse
import hashlib
import secrets
import uvicorn
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
import sys\
from background.sqlite import create_connection
from background.webdav import get_dav_app
from a2wsgi import WSGIMiddleware

app = FastAPI(title="Macro API")

# Mount WebDAV
app.mount("/dav", WSGIMiddleware(get_dav_app()))

security = HTTPBasic()

def verify_password(credentials: HTTPBasicCredentials):
    conn = create_connection()
    if conn is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not connect to the database",
        )
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT hashed_password FROM users WHERE username = ?", (credentials.username,))
        user_data = cursor.fetchone()

        if user_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )

        hashed = user_data[0]
        parts = hashed.split('$')
        if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid auth config",
                headers={"WWW-Authenticate": "Basic"},
            )

        iterations = int(parts[1])
        salt = parts[2]
        stored_key = parts[3]
        key = hashlib.pbkdf2_hmac('sha256', credentials.password.encode('utf-8'), salt.encode('utf-8'), iterations)

        if not secrets.compare_digest(key.hex(), stored_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials.username
    finally:
        conn.close()

async def get_current_user(
    request: Request, credentials: Optional[HTTPBasicCredentials] = Depends(security)
):
    if request.client.host in ("127.0.0.1", "localhost"):
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM users")
                users = cursor.fetchall()
                if len(users) == 1:
                    return users[0][0]
            finally:
                conn.close()

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="NoSSO failed or not applicable, Basic Auth required",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return verify_password(credentials)


@app.get("/login")
def login(username: str = Depends(get_current_user)):
    return {"status": "authenticated", "username": username}

@app.get("/status")
def get_status(username: str = Depends(get_current_user)):
    return {"status": "running", "service": "macro-backend"}

@app.get("/art")
def get_art(username: str = Depends(get_current_user)):
    return "not yet implemented"

@app.get("/files")
def get_files(username: str = Depends(get_current_user)):
    conn = create_connection()
    if conn is None:
        return []
    try:
        import sqlite3
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

@app.get("/stream/{file_id}")
def stream_file(file_id: int, username: str = Depends(get_current_user)):
    conn = create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM files WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        if row and os.path.exists(row[0]):
            return FileResponse(row[0])
        raise HTTPException(status_code=404, detail="File not found")
    finally:
        conn.close()

@app.get("/config")
def get_config(username: str = Depends(get_current_user)):
    conn = create_connection()
    if conn is None:
        return {"paths": [], "scan_interval": 3600}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM config")
        rows = cursor.fetchall()
        config = {row[0]: json.loads(row[1]) for row in rows}
        return config
    finally:
        conn.close()


@app.post("/config")
async def update_config(request: Request, username: str = Depends(get_current_user)):
    data = await request.json()
    conn = create_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection error")
    try:
        cursor = conn.cursor()
        for key, value in data.items():
            cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, json.dumps(value)))
        conn.commit()
        return {"message": "Config updated"}
    finally:
        conn.close()

@app.get("/status")
def fetch_status(username: str = Depends(get_current_user)):
    ram_usage = os.popen('free -m').readlines()[-1].split()[1]0
    return {"status": "running", "service": "macro-backend"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1470)
