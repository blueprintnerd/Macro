import PyQt6
import sys
import os
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

def show_splash(app):
    splash_path = os.path.join(os.path.dirname(__file__), "assets", "splash.png")
    if not os.path.exists(splash_path):
        print(f"Error: Splash image not found at {splash_path}")
        return None
    
    splash = QSplashScreen(QPixmap(splash_path))
    splash.show()
    app.processEvents()
    return splash
