import requests
import json

directory_file = json.load("r", "../directory.json")

#TODO: make this so that it checks the json for an ip assress
tester = requests.get("127.0.0.1:6302")
if "View" in tester:
    playlist_list = requests.get("127.0.0.1:6302/playlists/jsonform")
    
    

