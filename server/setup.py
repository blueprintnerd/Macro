import sys
import os
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget
)
from PyQt6.QtCore import QTimer
from pages.home import HomePage
from pages.locations import LocationsPage
from pages.music import MusicPage
from pages.internet import InternetPage
from pages.server import ServerPage
from splash import show_splash
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Setup")
        self.resize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)

        self.content_area = QStackedWidget()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.content_area)

        self.add_page("Home", HomePage())
        self.add_page("Locations", LocationsPage())
        self.add_page("Music", MusicPage())
        self.add_page("Internet", InternetPage())
        self.add_page("Server", ServerPage())

        self.sidebar.currentRowChanged.connect(self.content_area.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

    def add_page(self, title, widget):
        self.sidebar.addItem(title)
        self.content_area.addWidget(widget)

def main():
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    splash = show_splash(app)
    window = MainWindow()
    
    def show_main():
        if splash:
            splash.finish(window)
        window.show()

    QTimer.singleShot(3000, show_main)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
