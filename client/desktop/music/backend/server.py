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
def up():z