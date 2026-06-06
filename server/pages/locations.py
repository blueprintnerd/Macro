from qt_material_icons import MaterialIcon
import json
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QLineEdit, QPushButton, QFileDialog
from PyQt6.QtCore import Qt

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

class LocationsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.paths = self.load_paths()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Manage File Paths")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        self.update_list()

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter or browse folder path...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
            }
        """)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse)
        browse_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #B8F397;
                        color: #000000;
                        border: none;
                        border-radius: 6px;
                        padding: 10px 15px;
                        text-align: left;
                        font-weight: bold;
                    }
                """)

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add)
        add_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #B8F397;
                        color: #000000;
                        border: none;
                        border-radius: 6px;
                        padding: 10px 15px;
                        text-align: left;
                        font-weight: bold;
                    }
                """)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(browse_btn)
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)

        clear_btn = QPushButton("Clear All Paths")
        clear_btn.clicked.connect(self.clear_paths)
        layout.addWidget(clear_btn)
        clear_btn.setStyleSheet("""
                 QPushButton {
                        background-color: #B8F397;
                        color: #000000;
                        border: none;
                        border-radius: 6px;
                        padding: 10px 15px;
                        text-align: left;
                        font-weight: bold;
                    }
        """)

    def update_list(self):
        self.list_widget.clear()
        for path in self.paths:
            self.list_widget.addItem(path)

    def browse(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            self.input_field.setText(path)

    def add(self):
        text = self.input_field.text().strip()
        if text:
            self.paths.append(text)
            self.save_paths()
            self.update_list()
            self.input_field.clear()

    def clear_paths(self):
        self.paths = []
        self.save_paths()
        self.update_list()

    def load_paths(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f).get("paths", [])
            except Exception:
                pass
        return []

    def save_paths(self):
        config_data = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config_data = json.load(f)
            except Exception:
                pass
        config_data["paths"] = self.paths
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=2)