import json
import os
from pathlib import Path

def scan():
    config_path = "config.json"
    files_path = "files.json"
    
    if not os.path.exists(config_path):
        print("config.json not found")
        return

    with open(config_path, "r") as f:
        paths = json.load(f).get("paths", [])

    all_files = []
    for path_str in paths:
        path = Path(path_str)
        if not path.exists():
            continue
            
        for file_path in path.rglob('*'):
            if file_path.is_file():
                all_files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size
                })

    with open(files_path, "w") as f:
        json.dump(all_files, f, indent=2)
    print(f"Scanned {len(all_files)} files.")

if __name__ == "__main__":
    scan()
