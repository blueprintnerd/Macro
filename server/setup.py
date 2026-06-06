import os
os.environ["QT_API"] = "pyqt6"
from qt_material_icons import MaterialIcon
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QStackedWidget, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from pages.home import HomePage
from pages.locations import LocationsPage
from pages.user_auth_setup import UserAuthSetupPage
from pages.finalizer import Finalizer

class MainApp:
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.win = QMainWindow()
        self.win.setWindowTitle("Macro Setup")
        self.win.resize(900, 600)
        self.central = QWidget()
        self.win.setCentralWidget(self.central)
        self.central.setStyleSheet("background-color: #121212; color: #ffffff;")
        
        self.main_layout = QHBoxLayout(self.central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("background-color: #1a1a1a; border-right: 0px solid #2d2d2d;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(15, 30, 15, 30)
        self.sidebar_layout.setSpacing(10)

        # Logo / Title in Sidebar
        logo_label = QLabel("Macro")
        logo_label.setFont(QFont("Outfit", 22, QFont.Weight.Bold))
        logo_label.setStyleSheet("color: #007acc; margin-bottom: 20px; padding-left: 5px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # self.sidebar_layout.addWidget(logo_label)

        # Content area StackedWidget
        self.stacked_widget = QStackedWidget()
        
        # Instantiate pages
        self.pages = {
            "Home": HomePage(),
            "Locations": LocationsPage(),
            "Setup accounts": UserAuthSetupPage(),
            "Finish Setup": Finalizer()
        }

        self.buttons = {}
        self.setup_sidebar()

        for page in self.pages.values():
            self.stacked_widget.addWidget(page)

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.stacked_widget)
        
        self.show_page("Home")
        self.win.show()

    def setup_sidebar(self):
        for name in self.pages:
            btn = QPushButton(name)
            btn.setFont(QFont("Inter", 11, QFont.Weight.Medium))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #aaaaaa;
                    border: none;
                    border-radius: 2px;
                    padding: 4px 7px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #2a2a2a;
                    color: #B8F397;
                }
            """)
            btn.clicked.connect(lambda checked, n=name: self.show_page(n))
            self.sidebar_layout.addWidget(btn)
            self.buttons[name] = btn

        self.sidebar_layout.addStretch()

    def show_page(self, name):
        page_widget = self.pages[name]
        self.stacked_widget.setCurrentWidget(page_widget)

        for btn_name, btn in self.buttons.items():
            if btn_name == name:
                btn.setStyleSheet("""
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
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #aaaaaa;
                        border: none;
                        border-radius: 6px;
                        padding: 10px 15px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #2a2a2a;
                        color: #ffffff;
                    }
                """)

    def run(self):
        self.app.exec()

def main():
    app = MainApp()
    app.run()

if __name__ == "__main__":
    main()
