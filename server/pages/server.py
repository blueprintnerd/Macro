from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
import subprocess
import os

class ServerPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("Server Control")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.scan_btn = QPushButton("Run File Scan")
        self.api_btn = QPushButton("Start API")
        
        
        layout.addWidget(self.scan_btn)
        layout.addWidget(self.api_btn)

        self.scan_btn.clicked.connect(self.run_scan)
        self.api_btn.clicked.connect(self.toggle_api)
        
        
        self.api_process = None

    def run_scan(self):
        script_path = os.path.join(os.path.dirname(__file__), "..", "background", "scan.py")
        subprocess.Popen(["python", script_path])

    def toggle_api(self):
        if self.api_process is None:
            script_path = os.path.join(os.path.dirname(__file__), "..", "background", "api.py")
            self.api_process = subprocess.Popen(["python", script_path])
            self.api_btn.setText("Stop API")
        else:
            self.api_process.terminate()
            self.api_process = None
            self.api_btn.setText("Start API")
