from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Center, Middle, Vertical
from textual.widgets import Footer, Header, Static, Button, Input
from textual.screen import Screen
from textual import on
import sys
import requests
import subprocess

class MacroManager(App):
    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="main_container"):
            yield Static("Macro Manager", id="title")
            yield Input(placeholder="IP address", id="ip_input")
            yield Button("Continue to", id="signin")
            yield Button("Set up this computer as a Macro Server", id="setup_button")
        yield Footer()

    @on(Button.Pressed, "#signin")
    def on_signin(self) -> None:
        ip = self.query_one("#ip_input").value
        if ip:
            self.push_screen(IPAuthScreen(ip))

    @on(Button.Pressed, "#setup_button")
    def on_setup(self) -> None:
        self.push_screen(Installer())

class IPAuthScreen(Screen):
    def __init__(self, ip_address: str):
        super().__init__()
        self.ip_address = ip_address

    def compose(self) -> ComposeResult:
        yield Header()
        yield Center(Middle(Vertical(
            Static(f"Authenticating to {self.ip_address}...", id="auth_status"),
            Button("Back", id="back_button")
        )))
        yield Footer()

    def on_mount(self) -> None:
        self.run_auth()

    async def run_auth(self) -> None:
        status = self.query_one("#auth_status")
        try:
            
            response = requests.get(f"http://{self.ip_address}/name", timeout=5)
            if response.status_code == 200:
                status.update(f"Connected to: {response.text}")
            else:
                status.update(f"Failed to connect: {response.status_code}")
        except Exception as e:
            status.update(f"Error: {str(e)}")

    @on(Button.Pressed, "#back_button")
    def on_back(self) -> None:
        self.app.pop_screen()

class Installer(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            yield Static("Install Prerequisites", classes="heading")
            yield Input(placeholder="Enter your sudo password", password=True, id="sudo_password")
            yield Button("Start installing", id="install_button")
            yield Static("", id="install_log")
            
            yield Static("Configuration", classes="heading")
            yield Input(placeholder="Enter a filepath to use with the server", id="filepath_input")
            yield Button("Add directory", id="add_dir_button")
            yield Static("", id="dir_list")
        yield Footer()

    @on(Button.Pressed, "#install_button")
    def start_install(self) -> None:
        sudo_pwd = self.query_one("#sudo_password").value
        log = self.query_one("#install_log")
        
        if not sudo_pwd:
            log.update("Please enter sudo password")
            return

        log.update("Verifying sudo...")
        if self.verify_sudo(sudo_pwd):
            log.update("Sudo verified. Updating package lists...")
            if self.run_apt_update(sudo_pwd):
                log.update("Package lists updated successfully!")
            else:
                log.update("Error: Unable to update package lists.")
        else:
            log.update("Error: Sudo verification failed. Check password.")

    def verify_sudo(self, password: str) -> bool:
        try:
            proc = subprocess.run(
                ["sudo", "-S", "echo", "verified"],
                input=password.encode(),
                capture_output=True,
                check=True
            )
            return b"verified" in proc.stdout
        except subprocess.CalledProcessError:
            return False

    def run_apt_update(self, password: str) -> bool:
        try:
            subprocess.run(
                ["sudo", "-S", "apt", "update"],
                input=password.encode(),
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    @on(Button.Pressed, "#add_dir_button")
    def add_directory(self) -> None:
        path = self.query_one("#filepath_input").value
        dir_list = self.query_one("#dir_list")
        if path:
            current = dir_list.renderable
            new_text = f"{current}\n{path}" if current else path
            dir_list.update(new_text)
            self.query_one("#filepath_input").value = ""

class FilePaths(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Link your media files")
        yield Input(placeholder="Enter a filepath")
        yield Button("Add another filepath")
class SemanticSearch(Screen):
    def compose(self) -> ComposeResult():
        yield Static("Select a search backend")
        with RadioSet(id="search_backend"):
            yield RadioButton("Use Grep as a backend")
            yield RadioButton("Use a embedding model (Requires at least 4GB of ram)")
            yield 

if __name__ == "__main__":
    app = MacroManager()
    app.run()


