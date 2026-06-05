import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class DesktopClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro Desktop Client")
        self.resize(800, 600)
        self.setStyleSheet("background-color: #121212; color: #ffffff;")
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Label
        label = QLabel("Macro Desktop Client")
        label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

def main():
    app = QApplication(sys.argv)
    win = DesktopClientWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
