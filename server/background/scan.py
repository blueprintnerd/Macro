from qt_material_icons import MaterialIcon
import json
import os
from pathlib import Path
from scan_music import scan_metadata_from_file

def scan():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config.json")
    files_path = os.path.join(base_dir, "files.json")
    
    if not os.path.exists(config_path):
        print("config.json not found")
        return

    with open(config_path, "r") as f:
        paths = json.load(f).get("paths", [])

    # Load existing tracked files
    existing_files = []
    if os.path.exists(files_path):
        try:
            with open(files_path, "r") as f:
                existing_files = json.load(f)
                if not isinstance(existing_files, list):
                    existing_files = []
        except Exception:
            existing_files = []

    # Get maximum ID assigned so far
    last_number = max([f["id"] for f in existing_files if "id" in f], default=0)

    # Scan directories to find current files and their metadata
    scanned_files = []
    for path_str in paths:
        path = Path(path_str)
        if not path.exists():
            continue
            
        for file_path in path.rglob('*'):
            if file_path.is_file():
                if "__MACOSX" in file_path.parts or file_path.name.startswith("._"):
                
                    continue
                meta = scan_metadata_from_file(str(file_path))
                scanned_files.append({
                    "name": file_path.name,
                    "path": str(file_path.absolute()),
                    "size": file_path.stat().st_size,
                    "metadata": meta
                })

    existing_by_path = {f["path"]: f for f in existing_files}
    
    updated_files = []
    
    # Track which existing files are claimed
    claimed_ids = set()

    unmatched_scanned = []
    for scanned in scanned_files:
        path = scanned["path"]
        if path in existing_by_path:
            existing = existing_by_path[path]
            # Keep same ID, update details
            updated_entry = {
                "id": existing["id"],
                "path": path,
                "name": scanned["name"],
                "size": scanned["size"],
                "metadata": scanned["metadata"],
                "status": "present"
            }
            updated_files.append(updated_entry)
            claimed_ids.add(existing["id"])
        else:
            unmatched_scanned.append(scanned)


    unclaimed_deleted = [f for f in existing_files if f["id"] not in claimed_ids]
    
    def metadata_matches(s, e):
        return (s["size"] == e.get("size") and
                s["name"] == e.get("name") and
                s["metadata"] == e.get("metadata", {}))

    for scanned in unmatched_scanned:
        matched_existing = None
        for existing in unclaimed_deleted:
            if metadata_matches(scanned, existing):
                matched_existing = existing
                break
        
        if matched_existing is not None:
            # We found a matching deleted/unclaimed entry! Reuse the ID.
            updated_entry = {
                "id": matched_existing["id"],
                "path": scanned["path"],
                "name": scanned["name"],
                "size": scanned["size"],
                "metadata": scanned["metadata"],
                "status": "present"
            }
            updated_files.append(updated_entry)
            claimed_ids.add(matched_existing["id"])
            unclaimed_deleted.remove(matched_existing)
        else:
            # No match found, assign a new ID
            last_number += 1
            updated_entry = {
                "id": last_number,
                "path": scanned["path"],
                "name": scanned["name"],
                "size": scanned["size"],
                "metadata": scanned["metadata"],
                "status": "present"
            }
            updated_files.append(updated_entry)
            claimed_ids.add(last_number)

    # 3. Any remaining unclaimed entries in existing_files are now marked as "deleted"
    for existing in unclaimed_deleted:
        existing["status"] = "deleted"
        updated_files.append(existing)

    # Sort files by ID for cleanliness
    updated_files.sort(key=lambda x: x["id"])

    with open(files_path, "w") as f:
        json.dump(updated_files, f, indent=2)
    
    present_count = sum(1 for f in updated_files if f["status"] == "present")
    deleted_count = len(updated_files) - present_count
    print(f"Scanned: {present_count} present, {deleted_count} deleted.")

if __name__ == "__main__":
    scan()
