import PyQt6.QtWidgets as QtWidgets
import sys

class MClient_Login(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login to Macro Music")
        self.nosso = QtWidgets.QPushButton("Sign in with Macro Server")
        self.username_slot = QtWidgets.QLineEdit()
        self.password_slot = QtWidgets.QlineEdit()
        self.signin_button = QtWidgets.QPushButton("Sign in")

class MClient_Music(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro Music")