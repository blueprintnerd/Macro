from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
import subprocess
import os

class NotificationSync(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        question = QLabel("Would you like to show this device's notification on the client?")

        button1 = QPushButton("No")
        button2 = QPushButton("Yes")        