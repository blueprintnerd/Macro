import os
import sqlite3
import json
import hashlib
import secrets
from wsgidav.dav_provider import DAVProvider, DAVCollection, DAVNonCollection
from wsgidav.http_authenticator import HTTPAuthenticator
from wsgidav.dc.base_dc import BaseDomainController
from wsgidav.wsgidav_app import WsgiDAVApp
from a2wsgi import WSGIMiddleware
from background.sqlite import DB_PATH

class MacroDomainController(BaseDomainController):
    def __init__(self):
        super().__init__()

    def get_domain_realm(self, input_environ):
        return "Macro WebDAV"

    def require_authentication(self, input_environ):
        return True

    def basic_auth_user(self, realm, username, password, input_environ):
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT hashed_password FROM users WHERE username = ?", (username,))
            user_data = cursor.fetchone()
            if user_data is None:
                return False
            
            hashed = user_data[0]
            parts = hashed.split('$')
            if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
                return False

            iterations = int(parts[1])
            salt = parts[2]
            stored_key = parts[3]
            key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)

            if secrets.compare_digest(key.hex(), stored_key):
                return True
            return False
        finally:
            conn.close()

def get_dav_app():
    # Load paths from database
    paths = []
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = 'paths'")
        row = cursor.fetchone()
        if row:
            paths = json.loads(row[0])
    except:
        pass
    finally:
        conn.close()

    # Configure WsgiDAV
    config = {
        "host": "0.0.0.0",
        "port": 8080,
        "mount_path": "/dav",
        "provider_mapping": {},
        "http_authenticator": {
            "domain_controller": MacroDomainController(),
            "accept_basic": True,
            "accept_digest": False,
            "default_to_digest": False,
        },
        "simple_dc": {"user_mapping": {}}, # We use custom domain controller
        "verbose": 1,
    }

    # Map paths to virtual directories
    for i, path in enumerate(paths):
        dir_name = os.path.basename(path) or f"folder_{i}"
        if os.path.exists(path):
            config["provider_mapping"][f"/{dir_name}"] = path

    return WsgiDAVApp(config)
