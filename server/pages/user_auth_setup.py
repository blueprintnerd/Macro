import os
os.environ["QT_API"] = "pyqt6"
from qt_material_icons import MaterialIcon
import json
import hashlib
import secrets
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"pbkdf2_sha256$100000${salt}${key.hex()}"

class UserAuthSetupPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        icon = MaterialIcon("person_add")
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(24))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        title = QLabel("Create an account")
        title.setFont(QFont("Outfit", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Create an account to use with the client")
        subtitle.setFont(QFont("Inter", 11))
        subtitle.setStyleSheet("color: #888888;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        self.user_field = QLineEdit()
        self.user_field.setPlaceholderText("Username")
        self.user_field.setStyleSheet(self.line_edit_style())

        self.pass_field = QLineEdit()
        self.pass_field.setPlaceholderText("Password")
        self.pass_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_field.setStyleSheet(self.line_edit_style())

        self.confirm_field = QLineEdit()
        self.confirm_field.setPlaceholderText("Confirm Password")
        self.confirm_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_field.setStyleSheet(self.line_edit_style())

        layout.addWidget(self.user_field)
        layout.addWidget(self.pass_field)
        layout.addWidget(self.confirm_field)

        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Inter", 10))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        save_btn = QPushButton("Save User Credentials")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #B8F397;
                color: #000000;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a3e081;
            }
        """)
        save_btn.clicked.connect(self.save_user)
        layout.addWidget(save_btn)

    def line_edit_style(self):
        return """
            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                max-width: 300px;
            }
        """

    def save_user(self):
        username = self.user_field.text().strip()
        password = self.pass_field.text()
        confirm = self.confirm_field.text()

        if not username or not password:
            self.status_label.setText("Username and Password are required.")
            self.status_label.setStyleSheet("color: #ff5555;")
            return

        if password != confirm:
            self.status_label.setText("Passwords do not match.")
            self.status_label.setStyleSheet("color: #ff5555;")
            return

        # Load existing config
        config_data = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config_data = json.load(f)
            except Exception:
                pass

        if "users" not in config_data:
            config_data["users"] = {}

        hashed = hash_password(password)
        config_data["users"][username] = hashed

        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config_data, f, indent=2)
            self.status_label.setText(f"User '{username}' saved successfully!")
            self.status_label.setStyleSheet("color: #55ff55;")
            self.user_field.clear()
            self.pass_field.clear()
            self.confirm_field.clear()
        except Exception as e:
            self.status_label.setText(f"Error saving config: {e}")
            self.status_label.setStyleSheet("color: #ff5555;")
