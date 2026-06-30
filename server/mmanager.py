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

# ── C++ binary paths ────────────────────────────────────────────────────────
# Bazel puts the binary in bazel-bin/server/macro_server (from repo root).
# We also check next to mmanager.py in case it was copied there manually.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)

SERVER_BINARY_PATHS = [
    os.path.join(REPO_ROOT, "bazel-bin", "server", "macro_server"),  # Bazel output
    os.path.join(BASE_DIR, "macro_server"),                            # manual copy
]
SCANNER_BINARY_PATHS = [
    os.path.join(REPO_ROOT, "bazel-bin", "server", "scanner"),
    os.path.join(BASE_DIR, "scanner_bin"),
]

def find_binary(paths: list[str]) -> str | None:
    """Return the first path in the list that exists as an executable."""
    for p in paths:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    return None


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
            yield Button("Connect", id="signin")
            yield Button("Set up this computer as a Macro Server", id="setup_button")
        yield Footer()

    @on(Button.Pressed, "#signin")
    def on_signin(self) -> None:
        ip = self.query_one("#ip_input").value.strip()
        if ip == "localhost":
            self.push_screen(LocalDashboard())
        elif ip:
            self.push_screen(PortScannerScreen(ip))
        else:
            self.notify("Please enter an IP address or 'localhost'")

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
        name = self.query_one("#server_name_input").value.strip()
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
                log.update("✓ Package lists updated successfully")
            else:
                log.update("✗ Error updating packages — you can continue anyway")
        else:
            log.update("✗ Sudo verification failed — check your password")

    def verify_sudo(self, password: str) -> bool:
        try:
            proc = subprocess.run(
                ["sudo", "-S", "echo", "verified"],
                input=password.encode(),
                capture_output=True,
                check=True
            )
            return b"verified" in proc.stdout
        except Exception:
            return False

    def run_apt_update(self, password: str) -> bool:
        try:
            subprocess.run(["sudo", "-S", "apt", "update"], input=password.encode(), capture_output=True)
            return True
        except Exception:
            return False

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
            yield Input(placeholder="Enter a filepath (e.g. /home/user/Music)", id="filepath_input")
            yield Button("Add Directory", id="add_dir_button")
            yield VerticalScroll(id="dir_list_container")
            yield Button("Continue", id="continue_button", variant="primary")
        yield Footer()

    @on(Button.Pressed, "#add_dir_button")
    def add_directory(self) -> None:
        path = self.query_one("#filepath_input").value.strip()
        if path:
            if not os.path.exists(path):
                self.notify(f"Warning: path does not exist: {path}")
            self.app.install_data["directories"].append(path)
            self.query_one("#dir_list_container").mount(Static(f"  📁 {path}"))
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
            "Use Grep as a backend (Fastest option)": "ripgrep will be used instead if it is found on this system",
            "Use a embedding model (Requires 4GB+ RAM)": "Understands natural language queries, but is power intensive",
            "Manually set up keywords": "Show certain files at the top when matching keywords are searched",
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
            base = os.path.dirname(os.path.abspath(__file__))

            config_path = os.path.join(base, "config.txt")
            with open(config_path, "w") as f:
                f.write(data["server_name"])

            directory_path = os.path.join(base, "directory.json")
            with open(directory_path, "w") as f:
                json.dump(
                    {"directories": data["directories"], "search_backend": data["search_backend"]},
                    f,
                    indent=2
                )

            Functions.init_database()
            log.update("✓ Setup complete! Returning to home...")
            self.notify("Macro Server set up successfully!")

            # Pop the entire wizard stack back to main screen
            def go_home():
                # Pop until we're back at the root (MacroManager has no screens left to pop)
                while len(self.app.screen_stack) > 1:
                    self.app.pop_screen()

            self.set_timer(2, go_home)

        except Exception as e:
            log.update(f"✗ Error: {e}")


class LocalDashboard(Screen):
    def __init__(self):
        super().__init__()
        self.server_process = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="dashboard_container"):
            yield Static("Local Macro Server", id="status_title")
            yield Static("Checking status...", id="server_status")
            yield Button("Start Server", id="start_stop_button", variant="success")
            yield Button("Scan Now", id="scan_button", variant="primary")
            yield Button("Open in Browser", id="open_browser_button")
            yield Button("← Back", id="back_button")
        yield Footer()

    def on_mount(self) -> None:
        self.check_server_status()

    def check_server_status(self) -> None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                running = s.connect_ex(('localhost', 5000)) == 0
                self.update_ui(running)
        except Exception:
            self.update_ui(False)

    def update_ui(self, running: bool) -> None:
        status = self.query_one("#server_status")
        button = self.query_one("#start_stop_button")
        if running:
            status.update("Running on http://localhost:5000")
            button.label = "Stop Server"
            button.variant = "error"
        else:
            status.update("○ Stopped")
            button.label = "Start Server"
            button.variant = "success"

    @on(Button.Pressed, "#scan_button")
    def run_scanner(self) -> None:
        scanner_bin = find_binary(SCANNER_BINARY_PATHS)
        if scanner_bin:
            subprocess.Popen([scanner_bin], cwd=BASE_DIR)
            self.notify("C++ scanner started in background")
        else:
            # Fall back to Python scanner
            scanner_path = os.path.join(BASE_DIR, "scanner.py")
            subprocess.Popen([sys.executable, scanner_path], cwd=BASE_DIR)
            self.notify("Python scanner started (build C++ scanner with: bazel build //server:scanner)")

    @on(Button.Pressed, "#start_stop_button")
    async def toggle_server(self) -> None:
        status = self.query_one("#server_status")
        if "Running" in str(status.renderable):
            if self.server_process:
                self.server_process.terminate()
                self.server_process = None
            else:
                # Kill any stray server processes (C++ or Python fallback)
                subprocess.run(["pkill", "-f", "macro_server"], capture_output=True)
                subprocess.run(["pkill", "-f", "app.py"], capture_output=True)
            await asyncio.sleep(1)
            self.check_server_status()
        else:
            server_bin = find_binary(SERVER_BINARY_PATHS)
            if server_bin:
                # Launch the C++ server; pass the server/ directory as base path
                self.server_process = subprocess.Popen(
                    [server_bin, "5000", BASE_DIR],
                    cwd=BASE_DIR
                )
                self.notify("Starting C++ server…")
            else:
                # Binary not built yet — tell the user how to build it
                self.notify(
                    "C++ server not built yet.\n"
                    "Run: bazel build //server:macro_server",
                    severity="warning"
                )
                return
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
        self.found_servers = []  # list of (port, name)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Center(Middle(Vertical(
            Static(f"Scanning {self.ip_address} for Macro servers...", id="scan_status"),
            ProgressBar(total=65535, id="scan_progress"),
            VerticalScroll(id="found_list_container"),
            Button("← Back", id="back_button")
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
                        return port, response.text.strip()
                except Exception:
                    pass
                finally:
                    progress.advance(1)
                return None

        tasks = [check_port(port) for port in range(1, 65536)]

        for completed_task in asyncio.as_completed(tasks):
            result = await completed_task
            if result:
                port, name = result
                self.found_servers.append((port, name))
                found_container.mount(
                    Button(f"Connect to {name}  (port {port})", id=f"port_{port}")
                )
                status.update(f"Scanning... Found {len(self.found_servers)} server(s)")

        status.update(f"Scan complete. Found {len(self.found_servers)} server(s).")

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_button":
            if hasattr(self, "run_scan_task"):
                self.run_scan_task.cancel()
            self.app.pop_screen()
        elif event.button.id and event.button.id.startswith("port_"):
            port = int(event.button.id.split("_")[1])
            # Find the server name for this port
            name = next((n for p, n in self.found_servers if p == port), "Macro Server")
            self.app.push_screen(RemoteDashboard(self.ip_address, port, name))


class RemoteDashboard(Screen):
    """Dashboard for a remote Macro server discovered via port scan."""

    def __init__(self, ip: str, port: int, name: str):
        super().__init__()
        self.ip = ip
        self.port = port
        self.name = name
        self.base_url = f"http://{ip}:{port}"

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="dashboard_container"):
            yield Static(f"{self.name}", id="status_title")
            yield Static(f"Connected to {self.base_url}", id="server_status")
            yield Button("Open Music", id="open_music_button", variant="primary")
            yield Button("Open Video", id="open_video_button", variant="primary")
            yield Button("Open Dashboard in Browser", id="open_browser_button")
            yield Button("← Back", id="back_button")
        yield Footer()

    @on(Button.Pressed, "#open_music_button")
    def open_music(self) -> None:
        webbrowser.open(f"{self.base_url}/music/")

    @on(Button.Pressed, "#open_video_button")
    def open_video(self) -> None:
        webbrowser.open(f"{self.base_url}/video/")

    @on(Button.Pressed, "#open_browser_button")
    def open_browser(self) -> None:
        webbrowser.open(self.base_url)

    @on(Button.Pressed, "#back_button")
    def back(self) -> None:
        self.app.pop_screen()


class Functions:
    @staticmethod
    def init_database():
        base_dir = os.path.dirname(os.path.abspath(__file__))

        dbs = {
            "music.db": [
                "CREATE TABLE IF NOT EXISTS music(name, path, artist, album, playlist, number, play_count, lyrics)"
            ],
            "video.db": [
                "CREATE TABLE IF NOT EXISTS video(title, path, creator, resolution, number, play_count)"
            ],
            "files.db": [
                "CREATE TABLE IF NOT EXISTS files(name, path, size, type, number, play_count)"
            ],
            "photo.db": [
                "CREATE TABLE IF NOT EXISTS photos(album, name, path, person, number, play_count)"
            ],
            "communications.db": [
                "CREATE TABLE IF NOT EXISTS chat(person, datetime, tags, number, send_count)"
            ],
        }

        for db_name, statements in dbs.items():
            conn = sqlite3.connect(os.path.join(base_dir, db_name))
            cursor = conn.cursor()
            for stmt in statements:
                cursor.execute(stmt)
            conn.commit()
            conn.close()


if __name__ == "__main__":
    app = MacroManager()
    app.run()
