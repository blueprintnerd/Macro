from flask import Flask, send_from_directory, abort
import os

app = Flask(__name__)

# Base directory for clients
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENTS_DIR = os.path.join(BASE_DIR, 'clients')

@app.route('/')
def index():
    return "Macro Server is running. Access clients at /<client_name>/"

@app.route('/name')
def get_name():
    # This endpoint is used by the Macro Manager to identify the server
    config_path = os.path.join(BASE_DIR, 'config.txt')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return f.read().strip()
    return "Macro Server (Default)"

@app.route('/<client_name>/')
def client_home(client_name):
    """Serves the home.html for a specific client."""
    client_path = os.path.join(CLIENTS_DIR, client_name)
    if os.path.exists(os.path.join(client_path, 'home.html')):
        return send_from_directory(client_path, 'home.html')
    else:
        abort(404)

@app.route('/<client_name>/<path:filename>')
def serve_client_files(client_name, filename):
    """Serves static files (html, css, js, etc.) for a specific client."""
    client_path = os.path.join(CLIENTS_DIR, client_name)
    # Check if the file exists in the client's directory
    full_path = os.path.join(client_path, filename)
    if os.path.exists(full_path):
        return send_from_directory(client_path, filename)
    else:
        # Fallback to home.html if it's a directory or missing file (SPA style) 
        # but let's stick to simple file serving for now.
        abort(404)

if __name__ == '__main__':
    # Hosting on 0.0.0.0 makes it accessible on the local network
    app.run(host='0.0.0.0', port=5000, debug=True)
