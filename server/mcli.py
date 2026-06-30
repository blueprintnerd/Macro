"""
mcli.py — Macro CLI client (remote downloader / content browser)

Usage:
    python mcli.py

Keyboard shortcuts:
    d  Download queue
    c  Configure server IP
    h  View search history
    q  Quit
"""

import sqlite3
import json
import os
import requests
import subprocess
from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, Button, Input, DataTable
from textual.screen import Screen
from textual import on


CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcli_config.json")
LOG_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcli_log.db")


def get_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"server_ip": "", "server_port": 5000}


def save_config(cfg: dict) -> None:
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


def init_log_db() -> None:
    conn = sqlite3.connect(LOG_DB)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY, search_term TEXT, returned_results INTEGER, downloaded TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.commit()
    conn.close()


def commit_to_log(search_term: str, returned_results: int, downloaded: str | None) -> None:
    init_log_db()
    conn = sqlite3.connect(LOG_DB)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (search_term, returned_results, downloaded) VALUES (?, ?, ?)",
        (search_term, returned_results, downloaded or "N/A")
    )
    conn.commit()
    conn.close()


# ── Screens ──────────────────────────────────────────────────────────────────

class MCli(App):
    BINDINGS = [
        ("d", "push_screen('downloads')", "Downloads"),
        ("c", "push_screen('config')", "Configure"),
        ("h", "push_screen('history')", "History"),
        ("q", "quit", "Quit"),
    ]
    CSS = """
    Screen { background: #0a0a0b; align: center middle; }
    #main { width: 65; border: solid #3b82f6; background: #161618; padding: 2 4; border-radius: 1; }
    #title { text-align: center; color: #3b82f6; text-style: bold; margin-bottom: 1; }
    Input { margin: 1 0; border: tall #27272a; background: #0a0a0b; }
    Input:focus { border: tall #3b82f6; }
    Button { width: 100%; margin-top: 1; background: #27272a; color: white; border: none; }
    Button:hover { background: #3b82f6; }
    Button.-primary { background: #3b82f6; }
    #status { color: #a1a1aa; margin: 1 0; padding: 0 1; }
    """

    def __init__(self):
        super().__init__()
        self.cfg = get_config()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="main"):
            yield Static("Macro CLI Client", id="title")
            ip = self.cfg.get("server_ip", "")
            port = self.cfg.get("server_port", 5000)
            yield Static(f"Server: {ip}:{port}" if ip else "No server configured — press C to set one", id="status")
            yield Input(placeholder="Search music or video by title / artist...", id="searchbar")
            yield Button("Search Music", id="search_music", variant="primary")
            yield Button("Search Video", id="search_video")
        yield Footer()

    def on_mount(self) -> None:
        self.install_screen(IPConfig(self.cfg), name="config")
        self.install_screen(DownloadHistory(), name="downloads")
        self.install_screen(SearchHistory(), name="history")

    @on(Button.Pressed, "#search_music")
    def do_search_music(self) -> None:
        query = self.query_one("#searchbar").value.strip()
        if query:
            self.push_screen(SearchResultsScreen(query, "music", self.cfg))
        else:
            self.notify("Enter a search term first")

    @on(Button.Pressed, "#search_video")
    def do_search_video(self) -> None:
        query = self.query_one("#searchbar").value.strip()
        if query:
            self.push_screen(SearchResultsScreen(query, "video", self.cfg))
        else:
            self.notify("Enter a search term first")


class IPConfig(Screen):
    CSS = """
    Screen { background: #0a0a0b; align: center middle; }
    #cfg_box { width: 65; border: solid #3b82f6; background: #161618; padding: 2 4; border-radius: 1; }
    .heading { text-style: bold; background: #3b82f6; color: white; padding: 0 1; margin-bottom: 1; }
    Input { margin: 1 0; border: tall #27272a; background: #0a0a0b; }
    Input:focus { border: tall #3b82f6; }
    Button { width: 100%; margin-top: 1; background: #27272a; color: white; border: none; }
    Button:hover { background: #3b82f6; }
    Button.-primary { background: #3b82f6; }
    #log { color: #a1a1aa; margin: 1 0; padding: 0 1; min-height: 1; }
    """

    def __init__(self, cfg: dict):
        super().__init__()
        self.cfg = cfg

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="cfg_box"):
            yield Static("Configure Server", classes="heading")
            yield Static("Enter the IP address of your Macro server")
            yield Input(value=self.cfg.get("server_ip", ""), placeholder="192.168.1.100 or localhost", id="ip_input")
            yield Input(value=str(self.cfg.get("server_port", 5000)), placeholder="Port (default 5000)", id="port_input")
            yield Button("Verify & Save", id="verify_btn", variant="primary")
            yield Button("Save without verifying", id="save_btn")
            yield Button("← Back", id="back_btn")
            yield Static("", id="log")
        yield Footer()

    @on(Button.Pressed, "#verify_btn")
    def verify_and_save(self) -> None:
        ip = self.query_one("#ip_input").value.strip()
        port_str = self.query_one("#port_input").value.strip() or "5000"
        log = self.query_one("#log")
        try:
            port = int(port_str)
        except ValueError:
            log.update("✗ Invalid port number")
            return
        log.update(f"Connecting to {ip}:{port}...")
        try:
            r = requests.get(f"http://{ip}:{port}/name", timeout=3)
            if r.status_code == 200:
                log.update(f"✓ Connected! Server name: {r.text.strip()}")
                self._save(ip, port)
            else:
                log.update(f"✗ Server returned status {r.status_code}")
        except Exception as e:
            log.update(f"✗ Could not reach server: {e}")

    @on(Button.Pressed, "#save_btn")
    def save_no_verify(self) -> None:
        ip = self.query_one("#ip_input").value.strip()
        port_str = self.query_one("#port_input").value.strip() or "5000"
        try:
            port = int(port_str)
        except ValueError:
            port = 5000
        self._save(ip, port)
        self.query_one("#log").update("✓ Saved")

    def _save(self, ip: str, port: int) -> None:
        self.cfg["server_ip"] = ip
        self.cfg["server_port"] = port
        save_config(self.cfg)
        self.app.cfg = self.cfg
        # Update status label in main screen
        try:
            self.app.query_one("#status").update(f"Server: {ip}:{port}")
        except Exception:
            pass

    @on(Button.Pressed, "#back_btn")
    def go_back(self) -> None:
        self.app.pop_screen()


class SearchResultsScreen(Screen):
    CSS = """
    Screen { background: #0a0a0b; }
    #results_box { margin: 2 4; border: solid #27272a; background: #161618; padding: 2; border-radius: 1; }
    .heading { text-style: bold; background: #3b82f6; color: white; padding: 0 1; margin-bottom: 1; }
    Button { margin-top: 1; background: #27272a; color: white; border: none; }
    Button:hover { background: #3b82f6; }
    #log { color: #60a5fa; margin: 1 0; padding: 0 1; min-height: 1; }
    """

    def __init__(self, query: str, media_type: str, cfg: dict):
        super().__init__()
        self.query_str = query
        self.media_type = media_type
        self.cfg = cfg
        self.results = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="results_box"):
            yield Static(f"Results for: \"{self.query_str}\"", classes="heading")
            yield Static("", id="log")
            yield VerticalScroll(id="result_list")
            yield Button("← Back", id="back_btn")
        yield Footer()

    def on_mount(self) -> None:
        self.search()

    def search(self) -> None:
        log = self.query_one("#log")
        ip = self.cfg.get("server_ip", "")
        port = self.cfg.get("server_port", 5000)
        if not ip:
            log.update("✗ No server configured. Press C to set one.")
            return
        log.update(f"Searching {self.media_type}...")
        try:
            r = requests.get(
                f"http://{ip}:{port}/api/search/{self.media_type}",
                params={"q": self.query_str},
                timeout=5
            )
            self.results = r.json()
            commit_to_log(self.query_str, len(self.results), None)
            log.update(f"Found {len(self.results)} result(s)")
            container = self.query_one("#result_list")
            container.remove_children()
            if not self.results:
                container.mount(Static("No results found."))
            for item in self.results:
                label = item.get("name") or item.get("title") or "Unknown"
                sub = item.get("artist") or item.get("creator") or ""
                container.mount(Static(f"  {'🎵' if self.media_type == 'music' else '🎬'} {label}  —  {sub}"))
        except Exception as e:
            log.update(f"✗ Error: {e}")

    @on(Button.Pressed, "#back_btn")
    def go_back(self) -> None:
        self.app.pop_screen()


class SearchHistory(Screen):
    CSS = """
    Screen { background: #0a0a0b; align: center middle; }
    #hist_box { width: 80; max-height: 40; border: solid #27272a; background: #161618; padding: 2 4; border-radius: 1; }
    .heading { text-style: bold; background: #3b82f6; color: white; padding: 0 1; margin-bottom: 1; }
    Button { margin-top: 1; background: #27272a; color: white; border: none; }
    Button:hover { background: #3b82f6; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="hist_box"):
            yield Static("Search History", classes="heading")
            yield DataTable(id="hist_table")
            yield Button("← Back", id="back_btn")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Term", "Results", "Downloaded", "Time")
        try:
            init_log_db()
            conn = sqlite3.connect(LOG_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT search_term, returned_results, downloaded, timestamp FROM logs ORDER BY id DESC LIMIT 50")
            for row in cursor.fetchall():
                table.add_row(*[str(c) for c in row])
            conn.close()
        except Exception as e:
            table.add_row(f"Error: {e}", "", "", "")

    @on(Button.Pressed, "#back_btn")
    def go_back(self) -> None:
        self.app.pop_screen()


class DownloadHistory(Screen):
    CSS = """
    Screen { background: #0a0a0b; align: center middle; }
    #dl_box { width: 80; max-height: 40; border: solid #27272a; background: #161618; padding: 2 4; border-radius: 1; }
    .heading { text-style: bold; background: #3b82f6; color: white; padding: 0 1; margin-bottom: 1; }
    Button { margin-top: 1; background: #27272a; color: white; border: none; }
    Button:hover { background: #3b82f6; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="dl_box"):
            yield Static("Download Queue", classes="heading")
            yield Static("Downloads will appear here once you add content from search results.", id="dl_status")
            yield DataTable(id="dl_table")
            yield Button("← Back", id="back_btn")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("File", "Status", "Downloaded")
        try:
            init_log_db()
            conn = sqlite3.connect(LOG_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT downloaded, 'complete', timestamp FROM logs WHERE downloaded != 'N/A' ORDER BY id DESC LIMIT 50")
            rows = cursor.fetchall()
            conn.close()
            if rows:
                for row in rows:
                    table.add_row(*[str(c) for c in row])
                self.query_one("#dl_status").update("")
        except Exception as e:
            self.query_one("#dl_status").update(f"Error loading: {e}")

    @on(Button.Pressed, "#back_btn")
    def go_back(self) -> None:
        self.app.pop_screen()


if __name__ == "__main__":
    app = MCli()
    app.run()
