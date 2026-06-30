from flask import Flask, send_from_directory, abort, jsonify, send_file, request, Response
import os
import sqlite3
import json

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENTS_DIR = os.path.join(BASE_DIR, 'clients')


@app.route('/')
def index():
    return send_from_directory(CLIENTS_DIR, 'dashboard.html')


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
    cursor.execute(f"SELECT rowid as id, * FROM {table_name}")
    rows = cursor.fetchall()

    result = [dict(row) for row in rows]
    conn.close()
    return jsonify(result)


@app.route('/api/stream/<media_type>/<int:item_id>')
def stream_media(media_type, item_id):
    db_map = {
        "music": "music.db",
        "video": "video.db"
    }
    if media_type not in db_map:
        return abort(404)

    db_path = os.path.join(BASE_DIR, db_map[media_type])
    if not os.path.exists(db_path):
        return abort(404)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    table_name = media_type
    cursor.execute(f"SELECT path FROM {table_name} WHERE rowid = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None or not os.path.exists(row[0]):
        return abort(404)

    file_path = row[0]
    file_size = os.path.getsize(file_path)
    ext = os.path.splitext(file_path)[1].lower()

    mime_map = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.flac': 'audio/flac',
        '.m4a': 'audio/mp4',
        '.ogg': 'audio/ogg',
        '.aac': 'audio/aac',
        '.mp4': 'video/mp4',
        '.mkv': 'video/x-matroska',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.webm': 'video/webm',
        '.m4v': 'video/mp4',
    }
    mime = mime_map.get(ext, 'application/octet-stream')

    # Support byte-range requests for seeking in media players
    range_header = request.headers.get('Range')
    if range_header:
        byte_start, byte_end = 0, file_size - 1
        match = range_header.replace('bytes=', '').split('-')
        if match[0]:
            byte_start = int(match[0])
        if len(match) > 1 and match[1]:
            byte_end = int(match[1])

        chunk_size = (byte_end - byte_start) + 1
        with open(file_path, 'rb') as f:
            f.seek(byte_start)
            data = f.read(chunk_size)

        response = Response(
            data,
            206,
            mimetype=mime,
            content_type=mime,
            direct_passthrough=True
        )
        response.headers.add('Content-Range', f'bytes {byte_start}-{byte_end}/{file_size}')
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Content-Length', chunk_size)
        return response

    return send_file(file_path, mimetype=mime)


@app.route('/api/search/<media_type>')
def search_media(media_type):
    """Basic search endpoint using SQL LIKE."""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    db_map = {
        "music": ("music.db", "music", "name"),
        "video": ("video.db", "video", "title"),
    }
    if media_type not in db_map:
        return abort(404)

    db_file, table, col = db_map[media_type]
    db_path = os.path.join(BASE_DIR, db_file)
    if not os.path.exists(db_path):
        return jsonify([])

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT rowid as id, * FROM {table} WHERE {col} LIKE ? OR artist LIKE ?",
        (f"%{query}%", f"%{query}%") if media_type == "music" else (f"%{query}%", f"%{query}%")
    )
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/<client_name>/')
def client_home(client_name):
    client_path = os.path.join(CLIENTS_DIR, client_name)
    home_file = os.path.join(client_path, 'home.html')
    if os.path.exists(home_file):
        return send_from_directory(client_path, 'home.html')
    return abort(404)


@app.route('/<client_name>/<path:filename>')
def serve_client_files(client_name, filename):
    client_path = os.path.join(CLIENTS_DIR, client_name)
    full_path = os.path.join(client_path, filename)
    if os.path.exists(full_path):
        return send_from_directory(client_path, filename)
    return abort(404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
