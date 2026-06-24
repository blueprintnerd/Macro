from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Center, Middle, Vertical
from textual.widgets import Footer, Header, Static, Button, Input, RadioSet, RadioButton, ProgressBar
from textual.screen import Screen
from textual import on
import sys
import asyncio
import sqlite3
import requests
import subprocess
import httpx  # Switched to httpx for async non-blocking network calls

class MacroManager(App):
    CSS_PATH = "style.tcss"
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="main_container"):
            yield Static("Macro Manager", id="title")
            yield Input(placeholder="IP address (if the server is on this device, type localhost)", id="ip_input")
            yield Button("Continue to", id="signin")
            yield Button("Set up this computer as a Macro Server", id="setup_button")
        yield Footer()

    @on(Button.Pressed, "#signin")
    def on_signin(self) -> None:
        ip = self.query_one("#ip_input").value
        if ip == "localhost":
                self.push_screen(LocalDashboard())
        elif ip:
            self.push_screen(PortScannerScreen(ip))

    @on(Button.Pressed, "#setup_button")
    def on_setup(self) -> None:
        self.push_screen(Installer())

class LocalDashboard(Screen):
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("app not yet implemented")
        yield Footer()

class PortScannerScreen(Screen):
    def __init__(self, ip_address: str):
        super().__init__()
        self.ip_address = ip_address
        self.found_ports = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Center(Middle(Vertical(
            Static(f"Scanning {self.ip_address} for Macro servers...", id="scan_status"),
            ProgressBar(total=65535, id="scan_progress"),
            VerticalScroll(id="found_list_container"),
            Button("Back", id="back_button")
        )))
        yield Footer()

    def on_mount(self) -> None:
        self.run_scan_task = asyncio.create_task(self.run_scan())

    async def run_scan(self) -> None:
        status = self.query_one("#scan_status")
        progress = self.query_one("#scan_progress")
        found_container = self.query_one("#found_list_container")
        
        semaphore = asyncio.Semaphore(500)

        async def check_port(port):
            async with semaphore:
                try:
                    _, writer = await asyncio.wait_for(
                        asyncio.open_connection(self.ip_address, port), 
                        timeout=0.2
                    )
                    writer.close()
                    await writer.wait_closed()
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None, 
                        lambda: requests.get(f"http://{self.ip_address}:{port}/name", timeout=1)
                    )
                    if response.status_code == 200:
                        return port, response.text
                except:
                    pass
                finally:
                    progress.advance(1)
                return None

        tasks = [check_port(port) for port in range(1, 65536)]
        
        for completed_task in asyncio.as_completed(tasks):
            result = await completed_task
            if result:
                port, name = result
                self.found_ports.append((port, name))
                found_container.mount(Button(f"Connect to {name} on port {port}", id=f"port_{port}"))
                status.update(f"Scanning... Found {len(self.found_ports)} servers")

        status.update(f"Scan complete. Found {len(self.found_ports)} servers.")

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_button":
            if hasattr(self, "run_scan_task"):
                self.run_scan_task.cancel()
            self.app.pop_screen()
        elif event.button.id and event.button.id.startswith("port_"):
            port = int(event.button.id.split("_")[1])
            # For now, just show it's connected. In a real app, this would go to the dashboard.
            self.query_one("#scan_status").update(f"Connecting to port {port}...")

class Installer(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            yield Static("Server Configuration", classes="heading")
            yield Input(placeholder="Enter server name", id="server_name_input")
            
            yield Static("Install Prerequisites", classes="heading")
            yield Input(placeholder="Enter your sudo password", password=True, id="sudo_password")
            yield Button("Start installing", id="install_button")
            yield Static("", id="install_log")
            
            yield Static("File Directories", classes="heading")
            yield Input(placeholder="Enter a filepath to use with the server", id="filepath_input")
            yield Button("Add directory", id="add_dir_button")
            yield Static("", id="dir_list")
        yield Footer()

    @on(Button.Pressed, "#install_button")
    def start_install(self) -> None:
        sudo_pwd = self.query_one("#sudo_password").value
        server_name = self.query_one("#server_name_input").value
        log = self.query_one("#install_log")
        
        if not server_name:
            log.update("Please enter a server name")
            return

        if not sudo_pwd:
            log.update("Please enter sudo password")
            return

        # Save server name
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config.txt")
            with open(config_path, "w") as f:
                f.write(server_name)
        except Exception as e:
            log.update(f"Error saving config: {e}")
            return

        log.update("Verifying sudo...")
        if self.verify_sudo(sudo_pwd):
            log.update("Updating package lists...")
            if self.run_apt_update(sudo_pwd):
                log.update("Package lists updated")
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
        yield Button("-")
        yield Button("Continue")

class SemanticSearch(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Select a search backend")
        yield Static("Can be switched later in Macro Manager")
        with RadioSet(id="search_backend"):
            yield RadioButton("Use Grep as a backend (Fastest option)")
            yield RadioButton("Use a embedding model (Requires 4GB+ RAM)")
            yield RadioButton("Manually set uo keywords show results on search")
            yield RadioButton("Disable search")
        yield Static(id="backend_descripton")
        yield Button("Continue")
    @on(RadioSet.Changed)
    def update_description(self, event: RadioSet.Changed) -> None:
        description = self.query_one("#backend_description")
        backend = str(event.pressed.label)
        
        descriptions = {
            "Use Grep as a backend (Fastest option)": "ripgrep will be used instead if it is found",
            "Use a embedding model (Requires 4GB+ RAM)": "Understands natural language, though power intensive and may be slower",
            "Manually set uo keywords show results on search": "Allows you to manipulate search results for certain keywords",
            "Disable search": "Search will be disabled entirely."
        }
        
        description.update(descriptions.get(backend, ""))
        description.add_class("visible")
class Functions():
    def init_database():
        #TOOD: Find out how to restrict each connection to use half of the CPUs threads
        music_server_connection = sqlite3.connect("music.db")
        video_server_connection = sqlite3.connect("video.db")
        file_server_connection = sqlite3.connect("files.db")
        photo_server_connection = sqlite.connect("photo.db")
        communication_server_connection = sqlite3.connect("communications.db")

        music_cursor = music_server_connection.cursor()
        video_cursor = video_server_connection.cursor()
        file_cursor = file_server_connection.cursor()
        photo_cursor = photo_server_connection.cursor()
        chat_cursor = communication_server_connection.cursor()

        music_cursor.execute("CREATE TABLE music(name, artist, album, playlist, number)")
        video_cursor.execute("CREATE TABLE video(title, creator, resolution, number)")
        file_cursor.execute("CREATE TABLE files(name, size, type, number)")
        photo_cursor.execute("CREATE TABLE photos(album, name, person, number)")
        communication_cursor.execute("CREATE TABLE chat(person, datetime, tags, number)")
if __name__ == "__main__":
    app = MacroManager()
    app.run()
