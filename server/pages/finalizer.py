import os
os.environ["QT_API"] = "pyqt6"
from qt_material_icons import MaterialIcon
import sys
import subprocess
import getpass
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QHBoxLayout, QProgressBar, QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class Finalizer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        title = QLabel("Enter your sudo password to complete setup")
        title.setFont(QFont("Outfit", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addStretch()
        
        self.sudo_slot = QLineEdit()
        self.sudo_slot.setPlaceholderText("Password here...")
        self.sudo_slot.setEchoMode(QLineEdit.EchoMode.Password)
        self.sudo_slot.setStyleSheet("""
            QLineEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                max-width: 400px;
            }
        """)

        send_button = QPushButton("Start")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #B8F397;
                color: #000000;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                max-width: 400px;
            }
            QPushButton:hover {
                background-color: #a3e081;
            }
        """)
        send_button.clicked.connect(self.start_service)

        layout.addWidget(self.sudo_slot, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(send_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Inter", 11))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def start_service(self):
        password = self.sudo_slot.text()
        if not password:
            self.status_label.setText("Please enter your password.")
            self.status_label.setStyleSheet("color: #ff5555;")
            return

        self.status_label.setText("Setting up systemd service...")
        self.status_label.setStyleSheet("color: #ffffff;")
        QApplication.processEvents()

        server_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        config_file = os.path.join(server_dir, "config.json")
        
        if not os.path.exists(config_file):
            try:
                with open(config_file, "w") as f:
                    json.dump({"paths": [], "scan_interval": 3600}, f, indent=2)
            except Exception as e:
                self.status_label.setText(f"Error creating config: {e}")
                self.status_label.setStyleSheet("color: #ff5555;")
                return

        service_name = "macro.service"
        temp_service_path = "/tmp/macro.service"
        user = getpass.getuser()

        service_content = f"""[Unit]
Description=Macro API Service
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={server_dir}
ExecStart={sys.executable} {os.path.join(server_dir, "main.py")}
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
        try:
            with open(temp_service_path, "w") as f:
                f.write(service_content)
        except Exception as e:
            self.status_label.setText(f"Error writing temp file: {e}")
            self.status_label.setStyleSheet("color: #ff5555;")
            return

        commands = [
            f"sudo -S cp {temp_service_path} /etc/systemd/system/{service_name}",
            "sudo -S systemctl daemon-reload",
            f"sudo -S systemctl enable {service_name}",
            f"sudo -S systemctl start {service_name}"
        ]

        success = True
        for cmd in commands:
            try:
                proc = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = proc.communicate(input=password + "\n")
                if proc.returncode != 0:
                    success = False
                    error_msg = stderr.strip() or stdout.strip() or f"Command failed: {cmd}"
                    self.status_label.setText(f"Error: {error_msg}")
                    self.status_label.setStyleSheet("color: #ff5555;")
                    break
            except Exception as e:
                success = False
                self.status_label.setText(f"Execution failed: {e}")
                self.status_label.setStyleSheet("color: #ff5555;")
                break

        # Cleanup temp file
        try:
            if os.path.exists(temp_service_path):
                os.remove(temp_service_path)
        except Exception:
            pass

        if success:
            self.status_label.setText("Service successfully created and started! Closing...")
            self.status_label.setStyleSheet("color: #55ff55;")
            QTimer.singleShot(2000, lambda: QApplication.instance().quit())
