from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)
FILES_PATH = "files.json"
CONFIG_PATH = "config.json"

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({"status": "running", "service": "macro-backend"})

@app.route('/files', methods=['GET'])
def get_files():
    if os.path.exists(FILES_PATH):
        with open(FILES_PATH, "r") as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/config', methods=['GET'])
def get_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return jsonify(json.load(f))
    return jsonify({"paths": [], "scan_interval": 3600})

@app.route('/config', methods=['POST'])
def update_config():
    data = request.json
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)
    return jsonify({"message": "Config updated"}), 200

if __name__ == "__main__":
    app.run(port=1470)
