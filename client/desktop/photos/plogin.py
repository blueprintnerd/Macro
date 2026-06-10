import PyQt6.QtWidgets as QtWidgets
import sys
import requests

class Login_to_photos(QtWidgets.QWidget):
    def __init__(self, parent=None): 
        super().__init__(parent)
        
        self.ip_address_port = QtWidgets.QLineEdit()
        self.username_field = QtWidgets.QLineEdit()
        self.password_field = QtWidgets.QLineEdit()
        self.login_button = QtWidgets.QPushButton("Login")

    def check_thru_server(self):
        url = self.ip_address_port.text()
        #TODO: make it so that if server is on the same server it automatically authenti
        if url == "127.0.0.1:1470":
            print("Server was found locally, disconnecting from the API")
        else:
            print("Attempting to connect")
