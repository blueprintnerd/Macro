import os
import sqlite3
import json
import sys

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

    # Ensure tables exist (idempotent)
    music_cursor.execute(
        "CREATE TABLE IF NOT EXISTS music(name, path, artist, album, playlist, number, play_count, lyrics)"
    )
    video_cursor.execute(
        "CREATE TABLE IF NOT EXISTS video(title, path, creator, resolution, number, play_count)"
    )

    music_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac'}
    video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.m4v'}

    # Try to import mutagen for real metadata
    try:
        from mutagen import File as MutagenFile
        use_mutagen = True
    except ImportError:
        use_mutagen = False
        print("mutagen not installed — using filename as song name. Run: pip install mutagen")

    music_added = 0
    video_added = 0

    for directory in directories:
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}")
            continue

        for root, _, files in os.walk(directory):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                filepath = os.path.join(root, file)

                if ext in music_extensions:
                    # Check for duplicate by path
                    music_cursor.execute("SELECT rowid FROM music WHERE path = ?", (filepath,))
                    if music_cursor.fetchone():
                        continue  # Already indexed

                    name = os.path.splitext(file)[0]
                    artist = "Unknown Artist"
                    album = "Unknown Album"

                    if use_mutagen:
                        try:
                            audio = MutagenFile(filepath, easy=True)
                            if audio:
                                name = (audio.get("title") or [name])[0]
                                artist = (audio.get("artist") or ["Unknown Artist"])[0]
                                album = (audio.get("album") or ["Unknown Album"])[0]
                        except Exception:
                            pass

                    music_cursor.execute(
                        "INSERT INTO music (name, path, artist, album, playlist, number, play_count, lyrics) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (name, filepath, artist, album, "Default", 0, 0, "")
                    )
                    music_added += 1

                elif ext in video_extensions:
                    # Check for duplicate by path
                    video_cursor.execute("SELECT rowid FROM video WHERE path = ?", (filepath,))
                    if video_cursor.fetchone():
                        continue

                    title = os.path.splitext(file)[0]
                    video_cursor.execute(
                        "INSERT INTO video (title, path, creator, resolution, number, play_count) VALUES (?, ?, ?, ?, ?, ?)",
                        (title, filepath, "Unknown Creator", "Unknown", 0, 0)
                    )
                    video_added += 1

    music_db.commit()
    video_db.commit()
    music_db.close()
    video_db.close()
    print(f"Scan complete. Added {music_added} music file(s), {video_added} video file(s).")

if __name__ == "__main__":
    scan_media()
