import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QLineEdit, QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt

CONFIG_FILE = "config.json"

class LocationsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Manage File Paths"))

        self.path_list = QListWidget()
        layout.addWidget(self.path_list)

        input_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        browse_btn = QPushButton("Browse")
        add_btn = QPushButton("Add")
        
        input_layout.addWidget(self.path_input)
        input_layout.addWidget(browse_btn)
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)

        remove_btn = QPushButton("Remove Selected")
        layout.addWidget(remove_btn)

        browse_btn.clicked.connect(self.browse_path)
        add_btn.clicked.connect(self.add_path)
        remove_btn.clicked.connect(self.remove_path)

        self.load_paths()

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.path_input.setText(path)

    def add_path(self):
        path = self.path_input.text().strip()
        if path:
            self.path_list.addItem(path)
            self.path_input.clear()
            self.save_paths()

    def remove_path(self):
        for item in self.path_list.selectedItems():
            self.path_list.takeItem(self.path_list.row(item))
        self.save_paths()

    def load_paths(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                paths = json.load(f).get("paths", [])
                self.path_list.addItems(paths)

    def save_paths(self):
        paths = [self.path_list.item(i).text() for i in range(self.path_list.count())]
        with open(CONFIG_FILE, "w") as f:
            json.dump({"paths": paths}, f)
