"""
fetchplaylist.py — Pull playlists from a remote Macro server.

Reads the server IP from directory.json and fetches available playlists.
"""

import json
import os
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRECTORY_FILE = os.path.join(BASE_DIR, "directory.json")


def load_config() -> dict:
    if not os.path.exists(DIRECTORY_FILE):
        raise FileNotFoundError(f"directory.json not found at {DIRECTORY_FILE}")
    with open(DIRECTORY_FILE, "r") as f:
        return json.load(f)


def fetch_playlists(ip: str, port: int = 5000) -> list[dict]:
    """Fetch the music library (used as playlist source) from a remote Macro server."""
    url = f"http://{ip}:{port}/api/library/music"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to Macro server at {ip}:{port}")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"Server returned an error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


if __name__ == "__main__":
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(e)
        exit(1)

    # The config may have a server_ip field (set by mcli or manually)
    ip = config.get("server_ip", "127.0.0.1")
    port = config.get("server_port", 5000)

    print(f"Fetching playlists from {ip}:{port}...")
    songs = fetch_playlists(ip, port)

    if songs:
        print(f"Found {len(songs)} song(s):")
        for song in songs[:20]:  # Show first 20
            print(f"  {song.get('name', 'Unknown')} — {song.get('artist', 'Unknown Artist')}")
        if len(songs) > 20:
            print(f"  ... and {len(songs) - 20} more")
    else:
        print("No songs found.")
