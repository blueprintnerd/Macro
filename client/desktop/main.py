from qt_material_icons import MaterialIcon
import sys
import os
import requests
from requests.auth import HTTPBasicAuth
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QStackedWidget, QListWidget, QListWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class LoginWidget(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        title = QLabel("Macro Login")
        layout.addWidget(title)

        self.url_input = QLineEdit("http://127.0.0.1:1470")
        layout.addWidget(self.url_input)
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pass_input)

        self.error_label = QLabel("")
        layout.addWidget(self.error_label)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.attempt_login)
        layout.addWidget(login_btn)

    def attempt_login(self):
        url = self.url_input.text().strip()
        username = self.user_input.text().strip()
        password = self.pass_input.text()

        if not url or not username or not password:
            self.error_label.setText("All fields are required.")
            return

        try:
            response = requests.post(
                f"{url}/login", 
                auth=HTTPBasicAuth(username, password),
                timeout=5
            )
            if response.status_code == 200:
                self.error_label.setText("")
                self.parent_window.on_login_success(url, username, password)
            else:
                self.error_label.setText("Invalid credentials.")
        except Exception as e:
            self.error_label.setText(f"Error: {str(e)}")


class DashboardWidget(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        firefox
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Header info
        self.header_label = QLabel("Macro Files")
        layout.addWidget(self.header_label)

        # File List Widget
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.play_media)
        layout.addWidget(self.list_widget)

        # Status / Now Playing info
        self.now_playing_label = QLabel("Now Playing: None")
        layout.addWidget(self.now_playing_label)

        # Controls
        ctrl_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)

        ctrl_layout.addWidget(refresh_btn)
        ctrl_layout.addWidget(logout_btn)
        layout.addLayout(ctrl_layout)

    def refresh_data(self):
        url = self.parent_window.api_url
        auth = self.parent_window.auth

        try:
            response = requests.get(f"{url}/files", auth=auth, timeout=5)
            if response.status_code == 200:
                self.list_widget.clear()
                files = response.json()
                for f in files:
                    # Only show files that are present
                    if f.get("status", "present") == "present":
                        item = QListWidgetItem(f.get("name", "Unknown File"))
                        # Store file info inside the item
                        item.setData(Qt.ItemDataRole.UserRole, f)
                        self.list_widget.addItem(item)
            else:
                QMessageBox.warning(self, "Error", "Failed to retrieve files.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection failed: {str(e)}")

    def play_media(self, item):
        file_info = item.data(Qt.ItemDataRole.UserRole)
        if not file_info:
            return

        file_path = file_info.get("path")
        file_name = file_info.get("name")
        
        if os.path.exists(file_path):
            self.now_playing_label.setText(f"Now Playing: {file_name}")
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.player.play()
        else:
            self.now_playing_label.setText(f"File not found locally: {file_name}")
            # Try to stream from API as fallback
            url = f"{self.parent_window.api_url}/stream/{file_info.get('id')}"
            # Note: QMediaPlayer handles basic auth in URLs if formatted as http://user:pass@host
            # Split url protocol
            if url.startswith("http://"):
                username = self.parent_window.username
                password = self.parent_window.password
                auth_url = url.replace("http://", f"http://{username}:{password}@")
                self.now_playing_label.setText(f"Streaming: {file_name}")
                self.player.setSource(QUrl(auth_url))
                self.player.play()
            else:
                QMessageBox.critical(self, "Error", f"Cannot play: {file_path}")

    def logout(self):
        self.player.stop()
        self.parent_window.on_logout()


class DesktopClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro Client")
        self.resize(600, 400)

        self.api_url = ""
        self.username = ""
        self.password = ""
        self.auth = None

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.login_widget = LoginWidget(self)
        self.dashboard_widget = DashboardWidget(self)

        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.dashboard_widget)

        self.stacked_widget.setCurrentWidget(self.login_widget)

    def on_login_success(self, url, username, password):
        self.api_url = url
        self.username = username
        self.password = password
        self.auth = HTTPBasicAuth(username, password)
        self.dashboard_widget.refresh_data()
        self.stacked_widget.setCurrentWidget(self.dashboard_widget)

    def on_logout(self):
        self.api_url = ""
        self.username = ""
        self.password = ""
        self.auth = None
        self.login_widget.user_input.clear()
        self.login_widget.pass_input.clear()
        self.stacked_widget.setCurrentWidget(self.login_widget)

def main():
    app = QApplication(sys.argv)
    win = DesktopClientWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
