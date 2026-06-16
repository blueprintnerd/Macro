import requests
import sys
import os
from requests.auth import HTTPBasicAuth

def main():
    print("=== Macro Client Stub ===")
    server_url = input("Server URL (default: http://localhost:1470): ").strip() or "http://localhost:1470"
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    print(f"\nAuthenticating with {server_url}...")
    try:
        response = requests.get(f"{server_url}/login", auth=HTTPBasicAuth(username, password), timeout=5)
        if response.status_code == 200:
            print("Successfully authenticated!")
            print(f"Welcome, {username}.")
            
            dav_url = f"{server_url}/dav/"
            print("\n--- Storage Info ---")
            print(f"WebDAV URL: {dav_url}")
            print("You can mount this URL as a network drive in your OS.")
            print(f"User: {username}")
            print("Pass: [Your Password]")
            
            if sys.platform == "linux":
                print("\nTo mount on Linux (requires davfs2):")
                print(f"sudo mount -t davfs {dav_url} /mnt/macro")
            elif sys.platform == "win32":
                print("\nTo mount on Windows:")
                print(f"net use Z: {dav_url} /user:{username}")
            elif sys.platform == "darwin":
                print("\nTo mount on macOS:")
                print(f"Open Finder -> Go -> Connect to Server -> Enter: {dav_url}")
                
        else:
            print("Authentication failed. Please check your credentials.")
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    main()
