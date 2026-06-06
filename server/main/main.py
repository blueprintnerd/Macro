from qt_material_icons import MaterialIcon
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ServerManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Server Manager")
        self.resize(800, 600)
        self.setStyleSheet("background-color: #121212; color: #ffffff;")
        
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel("Server Manager")
        label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

class ServerManager:
    @staticmethod
    def main_server_ui():
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        win = ServerManagerWindow()
        win.show()
        app.exec()
