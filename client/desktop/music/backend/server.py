from fastapi import FastAPI

app = FastAPI()

served_html = """
<!DOCTYPE html>
<html>
<head>
<title>Macro Server</title>
</head>
<body>
    <h1>Macro Music is running</h1>
    <p>Nothing is playing</p>
</body>
</html>
"""

@app.get("/")
def read_root():
    return {"message": "Macro is Running!"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/up") 
def up():
    return {"message":f"{served_html}"}

@app.get("/now_playing")
def get_now_playing():
    return {"message":"Not yet implemented"}