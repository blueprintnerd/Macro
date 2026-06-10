
import sqlite3
import os
import json
import hashlib
import secrets
import sys

# Add project root to path to allow for absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from background.sqlite import create_connection, setup_database

def hash_password(password):
    salt = secrets.token_hex(16)
    iterations = 260000
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${key.hex()}"

def run_tui_setup():
    # First, ensure the database and tables are created.
    setup_database()

    print("Macro server setup is not complete. Starting command-line setup...")
    
    conn = create_connection()
    if conn is None:
        print("Error: Could not connect to the database.")
        return

    try:
        cursor = conn.cursor()

        print("\n--- User Setup ---")
        username = input("Enter username: ")
        password = input("Enter password (characters will be visible): ")
        
        hashed_password = hash_password(password)
        
        cursor.execute("INSERT OR REPLACE INTO users (username, hashed_password) VALUES (?, ?)", (username, hashed_password))
        print(f"User '{username}' created successfully.")

        print("\n--- Music Folders ---")
        paths = []
        while True:
            path = input("Enter a full path to a music folder (or press Enter to finish): ")
            if not path:
                break
            
            if os.path.isdir(path):
                paths.append(path)
                print(f"Added: {path}")
            else:
                print("Error: The path does not exist or is not a directory. Please try again.")

        cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", ("paths", json.dumps(paths)))
        print("Music folders saved.")

        print("\n--- Scan Interval ---")
        while True:
            try:
                interval_str = input("Enter the scan interval in seconds [3600]: ")
                if not interval_str:
                    interval = 3600
                    break
                interval = int(interval_str)
                if interval > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", ("scan_interval", json.dumps(interval)))
        print("Scan interval saved.")

        conn.commit()
        print("\nConfiguration complete! The server will now start.")

    finally:
        conn.close()

if __name__ == '__main__':
    run_tui_setup()
