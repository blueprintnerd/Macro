import PyQt6.QtWidgets as QtWidgets
import PyQt6.QtCore as QtCore

class ServerManager():
    def main_server_ui():
        app = QtWidgets.QApplication([])
        window = QtWidgets.QMainWindow()
        window.setWindowTitle("Blank Window")
        window.resize(800, 600)
        window.show()
        app.exec()