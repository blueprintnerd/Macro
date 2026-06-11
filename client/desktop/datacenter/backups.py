import hashlib
import sqlite3
import sys

def start_backup(clients, username):
    if clients == "all":
        print("Macro will now create a backup of all media formats")
    elif clients == "music":
        print("Macro will now create a backup of all of the music")