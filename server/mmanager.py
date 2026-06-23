from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Footer, Header, Static, Button, Input
import sys
import requests

class MacroManager(App):

    BINDINGS = [
        ("s", "enter_setup", "Set up this machine as a server")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="IP address", id="ip_input")

        yield Button("Continue to ", id="signin")
        yield Footer()

class Installer(Screen):
    def compose(self)-> ComposeResult:
        yield Header()
        yield Static("Install Prerequisities")
        yield Input(placeholder="Enter your sudo password")
        yield Button("Start installing", id="installer")
        yield Footer()

    def filepaths():
        yield Header()
        yield Input(placeholder="Enter a filepath to use with the server", id="filepath_input")
        yield button("Add directory") 

    def ip_auth(ip_address):
        fetch_machine_name = requests.get(f"http://{ip_address}/name")
        yield Static(f"Authenticating to {fetch_machine_name}")
    # -----------------------------------------------------------------------+
    def write_setup_to_variable(): 
        sudo_password = self.query_one("#sudo_password")

    def pre_req(self, sud_pwd):
        sudoverify = subprocess.run(f"sudo echo 'sudo works btw' | echo {sudo_password}")
        if "works"  in subprocess:
            try:
                update_package_lists = subprocess.run(f"sudo apt update | echo {sudo_password}")
            except:
                error_message = "Error: unable to update package lists"
                return error_message, False

        else: 
            estring = "There was an error running sudo. is the password correct?"
            return estring, False

if __name__ == "__main__":
    app = MacroManager()
    app.run()


