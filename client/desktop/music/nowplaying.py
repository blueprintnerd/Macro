import requests
import sys
import PyQt6.QtWidgets as QtWidgets
import hashlib

def check_if_playing(api_url):
    up = requests.get(f"{api_url}/up")
    if up contains "e":
        print('The server is not up. Are you sure Macro Server is running?'
    else:
        return 