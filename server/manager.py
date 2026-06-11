import textual
import sys
import requests
import os
import hashlib

def pull_api_stats(api_url):
    request_checker = requests.get(api_url)
    if request_checker.status_code == 200:
        return request_checker.json()
    else:
        error_msg = "The Macro manager was unable to connect to the server"
        return None