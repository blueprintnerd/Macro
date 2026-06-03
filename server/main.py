import time
import subprocess
import os
import json
import sys
from setup import main as run_gui

def main():
    config_path = "config.json"
    
    # Run GUI once if config doesn't exist
    if not os.path.exists(config_path):
        print("Starting...")
        run_gui()
        # After GUI closes, check if config was created
        if not os.path.exists(config_path):
            print("Setup cancelled or failed.")
            return

    # Start background services
    print("Setup detected. Running in background mode.")
    api_path = os.path.join(os.path.dirname(__file__), "background", "api.py")
    api_proc = subprocess.Popen([sys.executable, api_path])

    scan_path = os.path.join(os.path.dirname(__file__), "background", "scan.py")
    try:
        while True:
            subprocess.run([sys.executable, scan_path])
            with open(config_path, "r") as f:
                interval = json.load(f).get("scan_interval", 3600)
            time.sleep(interval)
    except KeyboardInterrupt:
        api_proc.terminate()

if __name__ == "__main__":
    main()
