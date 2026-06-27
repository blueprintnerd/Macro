from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Center, Middle, Vertical
from textual.widgets import Footer, Header, Static, Button, Input, RadioSet, RadioButton, ProgressBar
from textual.screen import Screen
from textual import on
import json
import socket
import webbrowser
import os
import sys
import asyncio
import sqlite3
import requests
import subprocess
import httpx
class MacroManager(App):
    CSS_PATH = "style.tcss"
    def __init__(self):
        super().__init__()
        self.install_data = {
            "server_name": "",
            "directories": [],
            "search_backend": "Disable search"
        }

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
        self.push_screen(ServerNameScreen())

class ServerNameScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="wizard_container"):
            yield Static("Step 1: Server Configuration", classes="heading")
            yield Static("Choose a name for your Macro Server")
            yield Input(placeholder="Enter server name", id="server_name_input")
            yield Button("Continue", id="continue_button", variant="primary")
        yield Footer()

    @on(Button.Pressed, "#continue_button")
    def next_step(self) -> None:
        name = self.query_one("#server_name_input").value
        if name:
            self.app.install_data["server_name"] = name
            self.app.push_screen(PrerequisitesScreen())
        else:
            self.notify("Please enter a server name")

class PrerequisitesScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="wizard_container"):
            yield Static("Step 2: Install Prerequisites", classes="heading")
            yield Static("Enter your sudo password to install system packages")
            yield Input(placeholder="Sudo password", password=True, id="sudo_password")
            yield Button("Verify & Update", id="verify_button")
            yield Static("", id="install_log")
            yield Button("Continue", id="continue_button", variant="primary")
            yield Button("Skip for now", id="skip_button")
        yield Footer()

    @on(Button.Pressed, "#verify_button")
    def verify(self) -> None:
        pwd = self.query_one("#sudo_password").value
        log = self.query_one("#install_log")
        if not pwd:
            log.update("Please enter sudo password")
            return
        
        log.update("Verifying sudo...")
        if self.verify_sudo(pwd):
            log.update("Updating package lists...")
            if self.run_apt_update(pwd):
                log.update("Package lists updated")
            else:
                log.update("Error updating packages")
        else:
            log.update("Sudo verification failed")

    def verify_sudo(self, password: str) -> bool:
        try:
            proc = subprocess.run(["sudo", "-S", "echo", "verified"], input=password.encode(), capture_output=True, check=True)
            return b"verified" in proc.stdout
        except: return False

    def run_apt_update(self, password: str) -> bool:
        try:
            subprocess.run(["sudo", "-S", "apt", "update"], input=password.encode(), capture_output=True)
            return True
        except: return False

    @on(Button.Pressed, "#continue_button")
    @on(Button.Pressed, "#skip_button")
    def next_step(self) -> None:
        self.app.push_screen(FilePathsScreen())

class FilePathsScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="wizard_container"):
            yield Static("Step 3: Media Directories", classes="heading")
            yield Static("Add folders containing your music and videos")
            yield Input(placeholder="Enter a filepath", id="filepath_input")
            yield Button("Add Directory", id="add_dir_button")
            yield VerticalScroll(id="dir_list_container")
            yield Button("Continue", id="continue_button", variant="primary")
        yield Footer()

    @on(Button.Pressed, "#add_dir_button")
    def add_directory(self) -> None:
        path = self.query_one("#filepath_input").value
        if path:
            self.app.install_data["directories"].append(path)
            self.query_one("#dir_list_container").mount(Static(path))
            self.query_one("#filepath_input").value = ""

    @on(Button.Pressed, "#continue_button")
    def next_step(self) -> None:
        self.app.push_screen(SearchBackendScreen())

class SearchBackendScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="wizard_container"):
            yield Static("Step 4: Search Configuration", classes="heading")
            yield Static("Select a search backend")
            with RadioSet(id="search_backend"):
                yield RadioButton("Use Grep as a backend (Fastest option)")
                yield RadioButton("Use a embedding model (Requires 4GB+ RAM)")
                yield RadioButton("Manually set up keywords")
                yield RadioButton("Disable search", value=True)
            yield Static("", id="backend_descripton")
            yield Button("Continue", id="continue_button", variant="primary")
        yield Footer()

    @on(RadioSet.Changed)
    def update_description(self, event: RadioSet.Changed) -> None:
        description = self.query_one("#backend_descripton")
        backend = str(event.pressed.label)
        self.app.install_data["search_backend"] = backend
        
        descriptions = {
            "Use Grep as a backend (Fastest option)": "ripgrep will be used instead if it is found",
            "Use a embedding model (Requires 4GB+ RAM)": "Understands natural language, power intensive",
            "Manually set up keywords": "Allows you to show certain files at the top when certain keywords are used in search",
            "Disable search": "Search will be disabled entirely."
        }
        description.update(descriptions.get(backend, ""))

    @on(Button.Pressed, "#continue_button")
    def next_step(self) -> None:
        self.app.push_screen(FinishScreen())

class FinishScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="wizard_container"):
            yield Static("Final Step: Save & Finish", classes="heading")
            yield Static("Click Finish to save your configuration and initialize databases.")
            yield Button("Finish Installation", id="finish_button", variant="success")
            yield Static("", id="status_log")
        yield Footer()

    @on(Button.Pressed, "#finish_button")
    def finish(self) -> None:
        log = self.query_one("#status_log")
        try:
            data = self.app.install_data
            config_path = os.path.join(os.path.dirname(__file__), "config.txt")
            with open(config_path, "w") as f:
                f.write(data["server_name"])
            
            directory_path = os.path.join(os.path.dirname(__file__), "directory.json")
            with open(directory_path, "w") as f:
                json.dump({"directories": data["directories"], "search_backend": data["search_backend"]}, f)
            
            Functions.init_database()
            log.update("Setup Complete!")
            self.notify("Macro Server setup successfully!")
            # Pop back to the main menu
            self.set_timer(2, lambda: self.app.pop_screen()) # pop FinishScreen
            self.set_timer(2, lambda: self.app.pop_screen()) # pop SearchBackend
            self.set_timer(2, lambda: self.app.pop_screen()) # pop FilePaths
            self.set_timer(2, lambda: self.app.pop_screen()) # pop Prerequisites
            self.set_timer(2, lambda: self.app.pop_screen()) # pop ServerName
        except Exception as e:
            log.update(f"Error: {e}")

class LocalDashboard(Screen):
    def __init__(self):
        super().__init__()
        self.server_process = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="dashboard_container"):
            yield Static("Local Macro Server Status", id="status_title")
            yield Static("Checking status...", id="server_status")
            yield Button("Start Server", id="start_stop_button", variant="success")
            yield Button("Scan Now", id="scan_button", variant="primary")
            yield Button("Open Client", id="open_browser_button")
            yield Button("Back", id="back_button")
        yield Footer()

    def on_mount(self) -> None:
        self.check_server_status()

    def check_server_status(self) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                running = s.connect_ex(('localhost', 5000)) == 0
                self.update_ui(running)
        except:
            self.update_ui(False)

    def update_ui(self, running: bool) -> None:
        status = self.query_one("#server_status")
        button = self.query_one("#start_stop_button")
        if running:
            status.update("Running on http://localhost:5000")
            button.label = "Stop Server"
            button.variant = "error"
        else:
            status.update("Stopped")
            button.label = "Start Server"
            button.variant = "success"

    @on(Button.Pressed, "#scan_button")
    def run_scanner(self) -> None:
        scanner_path = os.path.join(os.path.dirname(__file__), "scanner.py")
        subprocess.Popen([sys.executable, scanner_path])
        self.notify("Scanner started in background")

    @on(Button.Pressed, "#start_stop_button")
    async def toggle_server(self) -> None:
        status = self.query_one("#server_status")
        if "Running" in str(status.renderable):
            if self.server_process:
                self.server_process.terminate()
                self.server_process = None
            else:
                try:
                    subprocess.run(["pkill", "-f", "app.py"])
                except:
                    pass
            await asyncio.sleep(1)
            self.check_server_status()
        else:
            server_path = os.path.join(os.path.dirname(__file__), "app.py")
            self.server_process = subprocess.Popen([sys.executable, server_path])
            await asyncio.sleep(2)
            self.check_server_status()

    @on(Button.Pressed, "#open_browser_button")
    def open_browser(self) -> None:
        webbrowser.open("http://localhost:5000")

    @on(Button.Pressed, "#back_button")
    def back(self) -> None:
        self.app.pop_screen()

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

class Functions():
    @staticmethod
    def init_database():
        #TOOD: Find out how to restrict each connection to use half of the CPUs threads
        #TODO: Setup the code to add another table to the data if semantic search is enabled
        base_dir = os.path.dirname(os.path.abspath(__file__))
        music_server_connection = sqlite3.connect(os.path.join(base_dir, "music.db"))
        video_server_connection = sqlite3.connect(os.path.join(base_dir, "video.db"))
        file_server_connection = sqlite3.connect(os.path.join(base_dir, "files.db"))
        photo_server_connection = sqlite3.connect(os.path.join(base_dir, "photo.db"))
        communication_server_connection = sqlite3.connect(os.path.join(base_dir, "communications.db"))

        music_cursor = music_server_connection.cursor()
        video_cursor = video_server_connection.cursor()
        file_cursor = file_server_connection.cursor()
        photo_cursor = photo_server_connection.cursor()
        chat_cursor = communication_server_connection.cursor()

        music_cursor.execute("CREATE TABLE IF NOT EXISTS music(name, artist, album, playlist, number, play_count, lyrics)")
        video_cursor.execute("CREATE TABLE IF NOT EXISTS video(title, creator, resolution, number, play_count)")
        file_cursor.execute("CREATE TABLE IF NOT EXISTS files(name, size, type, number, play_count)")
        photo_cursor.execute("CREATE TABLE IF NOT EXISTS photos(album, name, person, number, play_count)")
        chat_cursor.execute("CREATE TABLE IF NOT EXISTS chat(person, datetime, tags, number, send_count)")
        
        music_server_connection.commit()
        video_server_connection.commit()
        file_server_connection.commit()
        photo_server_connection.commit()
        communication_server_connection.commit()
        
        music_server_connection.close()
        video_server_connection.close()
        file_server_connection.close()
        photo_server_connection.close()
        communication_server_connection.close()
if __name__ == "__main__":
    app = MacroManager()
    app.run()
