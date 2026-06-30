"""
grabber.py — Download or read a file/URL for the Macro engine.
"""

import requests
import os


def grab_link_or_file(path: str) -> bytes | None:
    """
    Try to fetch content from `path`.

    - If it looks like a URL (http:// / https://), perform an HTTP GET.
    - Otherwise, try to read it as a local file path.

    Returns raw bytes on success, or None on failure.
    """
    path = path.strip()

    if path.startswith("http://") or path.startswith("https://"):
        try:
            response = requests.get(path, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"HTTP fetch failed for {path}: {e}")
            return None

    # Treat as local file
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return f.read()
        except OSError as e:
            print(f"Could not read file {path}: {e}")
            return None

    print(f"Path not found and not a valid URL: {path}")
    return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python grabber.py <url or filepath>")
        sys.exit(1)
    result = grab_link_or_file(sys.argv[1])
    if result:
        print(f"Fetched {len(result)} bytes.")
    else:
        print("Failed to fetch content.")