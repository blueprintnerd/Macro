from flask import Flask, send_from_directory, abort, jsonify
import os
import sqlite3
import json

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENTS_DIR = os.path.join(BASE_DIR, 'clients')

@app.route('/')
def index():
    return "Macro Server is running. Access clients at /<client_name>/"

@app.route('/name')
def get_name():
    config_path = os.path.join(BASE_DIR, 'config.txt')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return f.read().strip()
    return "Macro Server"

@app.route('/api/config')
def get_config():
    config_path = os.path.join(BASE_DIR, 'config.txt')
    directory_path = os.path.join(BASE_DIR, 'directory.json')
    config = {"name": "Macro Server", "directories": []}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config["name"] = f.read().strip()
    if os.path.exists(directory_path):
        with open(directory_path, 'r') as f:
            config.update(json.load(f))
    return jsonify(config)

@app.route('/api/library/<media_type>')
def get_library(media_type):
    db_map = {
        "music": "music.db",
        "video": "video.db",
        "files": "files.db",
        "photos": "photo.db"
    }
    if media_type not in db_map:
        return abort(404)
    
    db_path = os.path.join(BASE_DIR, db_map[media_type])
    if not os.path.exists(db_path):
        return jsonify([])

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    table_name = "photos" if media_type == "photos" else media_type
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    result = [dict(row) for row in rows]
    conn.close()
    return jsonify(result)

@app.route('/<client_name>/')
def client_home(client_name):
...
    client_path = os.path.join(CLIENTS_DIR, client_name)
    if os.path.exists(os.path.join(client_path, 'home.html')):
        return send_from_directory(client_path, 'home.html')
    else:
        abort(404)

@app.route('/<client_name>/<path:filename>')
def serve_client_files(client_name, filename):
    client_path = os.path.join(CLIENTS_DIR, client_name)
    full_path = os.path.join(client_path, filename)
    if os.path.exists(full_path):
        return send_from_directory(client_path, filename)
    else:
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
