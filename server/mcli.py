import sqlite3
import flask
import textual
import ffmpeg
import json
import requests
import subprocess
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

class MCli(App):
    BINDINGS = [
         ("d", "download_queue", "Downloaded"),
         ("c", "config", "Configure server IP"),
         ("l", "toggle_logging", "Disable/Enable Logging"),
         ("h", "view_history", "View Search history"),
         ("q", "quit", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Macro Downloader")
        yield Input(placeholder="Search a macro server", id="searchbar")
        yield Button("Seaarch")

class MCli_to_server(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield 

class IPConfig(Screen):
    def conpose(self) -> ComposeResult:
        yield Header()
        yield Static("Enter your server IP address")
        yield Input(placeholder="192.168.-.---", id=server_ipaddr)
        yield Button("Verify & Save")
        yield Button("Save without verifying")
        yield Button("Authenticate for Admin Actions")

        def verify_server_ip():
            try:
                requests_fetch(ip_address)
                previews = requests.fetch(ip_address + "/clients/database/previews")
            except:
                err_msg = "Failed to reach IP Address"
                return err_msg

class Authenticate_for_IP(ip_address):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Sign into your server to perform admin actions")
        yield
        yield
        yield Button("Authenticate from the server")
class Authenticate_From_Server(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Enter the code you see on the server")
        yield Input(placeholder="XXXXXXXX")
        yield Button("Finish signup")

class ScraperDashboard(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("You can pull from sources you have set up in the Macro Manager")
        yield Input(placeholder="You can download content from your sources")
        yield Button("Go")

class Downloads(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        log_connection = sqlite3.connect("log.db")
        log_cursor = log_connection.cursor()
        log_cursor.execute("IF NOT EXISTS TABLE logs CREATE TABLE logs(search_term, returned_results, downloaded_content)")
        log_cursor.commit()
        #TODO: Save downloads to a log and show them here
        #TODO: Add an easy way to access logs (Maybe the server can have a dedicated API?)
def commit_to_log(search_term, returned_results, downloaded):
    connection = sqlite3.connect("log.db")
    cursor = connection.cursor()
    if downloaded == None:
        downloaded = "N/A"
        cursor.execute(
            "INSERT into logs(search_term, returned_results, downloaded) VALUES (?, ?, ?)",
            (search_term, returned_results, downloaded) 
        )
        connection.commit()
        connection.close()
    else:
        connection = sqlite3.connect("log.db")
        cursor = connection.cursor()
        cursor.execute (
            "INSERT INTO logs (search_term, returned_results, downloaded) VALUES (?, ?, ?)",
            (search_term, returned_results, downloaded)
        )
