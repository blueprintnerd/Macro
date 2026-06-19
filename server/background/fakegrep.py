import os
import sqlite3

def grep_contents_for_drive(text):
    connection = sqlite3.connect("music.")
    #!() as a way to signify the character has been replaced
    sanitized_input = text.replace("\\", "!(/)" )