from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        large_label = QLabel("Welcome to Macro")
        large_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        label = QLabel("Click a sidebar button to get started")
        layout.addWidget(large_label)
        layout.addWidget(label)

