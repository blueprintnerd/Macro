from qt_material_icons import MaterialIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        icon = MaterialIcon("smb_share")
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(24))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Macro")
        title.setFont(QFont("Outfit", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Select a tab from the sidebar to get started")
        subtitle.setFont(QFont("Inter", 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addWidget(subtitle)
