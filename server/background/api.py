from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import FileResponse, JSONResponse
import json
import os
import hashlib
import secrets
import uvicorn
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

app = FastAPI(title="Macro API")
security = HTTPBasic()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES_PATH = os.path.join(BASE_DIR, "files.json")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if not os.path.exists(CONFIG_PATH):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        users = config.get("users", {})
        username = credentials.username
        password = credentials.password
        
        if username not in users:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
            
        hashed = users[username]
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
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
        
        if not secrets.compare_digest(key.hex(), stored_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return username
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Basic"},
        )

@app.get("/login")
def login(username: str = Depends(check_auth)):
    return {"status": "authenticated", "username": username}

@app.get("/status")
def get_status(username: str = Depends(check_auth)):
    return {"status": "running", "service": "macro-backend"}

@app.get("/art")
    return "not yet implemented"

@app.get("/files")
def get_files(username: str = Depends(check_auth)):
    if os.path.exists(FILES_PATH):
        with open(FILES_PATH, "r") as f:
            return json.load(f)
    return []

@app.get("/stream/{file_id}")
def stream_file(file_id: int, username: str = Depends(check_auth)):
    if os.path.exists(FILES_PATH):
        with open(FILES_PATH, "r") as f:
            files = json.load(f)
        for file_info in files:
            if file_info.get("id") == file_id:
                path = file_info.get("path")
                if os.path.exists(path):
                    return FileResponse(path)
                break
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/config")
def get_config(username: str = Depends(check_auth)):
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {"paths": [], "scan_interval": 3600}

@app.post("/config")
async def update_config(request: Request, username: str = Depends(check_auth)):
    data = await request.json()
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)
    return {"message": "Config updated"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1470)
