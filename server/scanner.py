import os
import sqlite3
import json
import subprocess
import sys

#maybe create a progrss bar to show the cureent scanning progress

def scan_media():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directory_path = os.path.join(base_dir, "directory.json")
    
    if not os.path.exists(directory_path):
        print("No directory.json found. Run the installer first.")
        return

    with open(directory_path, "r") as f:
        config = json.load(f)
        directories = config.get("directories", [])

    music_db = sqlite3.connect(os.path.join(base_dir, "music.db"))
    video_db = sqlite3.connect(os.path.join(base_dir, "video.db"))
    
    music_cursor = music_db.cursor()
    video_cursor = video_db.cursor()

    music_extensions = {'.mp3', '.wav', '.flac', '.m4a'}
    video_extensions = {'.mp4', '.mkv', '.avi', '.mov'}

    for directory in directories:
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}")
            continue

        for root, _, files in os.walk(directory):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                filepath = os.path.join(root, file)
                
                if ext in music_extensions:
                    # Basic metadata extraction (could be improved with mutagen)
                    music_cursor.execute(
                        "INSERT INTO music (name, artist, album, playlist, number, play_count) VALUES (?, ?, ?, ?, ?, ?)",
                        (file, "Unknown Artist", "Unknown Album", "Default", 0, 0)
                    )
                elif ext in video_extensions:
                    video_cursor.execute(
                        "INSERT INTO video (title, creator, resolution, number, play_count) VALUES (?, ?, ?, ?, ?)",
                        (file, "Unknown Creator", "Unknown", 0, 0)
                    )

    music_db.commit()
    video_db.commit()
    music_db.close()
    video_db.close()
    print("Scan complete.")

if __name__ == "__main__":
    scan_media()
