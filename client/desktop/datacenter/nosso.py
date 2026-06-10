import hashlib
import sys
import requests
import PyQt6.QtWidgets as QtWidgets
import os

class NoSSO():
    @staticmethod
    def CheckNoSSO():
        print("NoSSO is checking if this machine is compatible with NoSSO sign in")
        url_array = ["http://localhost:1470", "http://127.0.0.1:1470"]
        for url in url_array:
            try:
                requests.get(url)
                print("NoSSO has determined that it will be able to work with your computer.")
                return
            except requests.exceptions.ConnectionError:
                pass
        print("NoSSO isn't compatible with your computer")

class NoSSOUi():
    def __init__(self, app_name):
        app = QtWidgets.QApplication(sys.argv)
        window = QtWidgets.QWidget()
        window.setWindowTitle("NoSSO Authorization")
        
        layout = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("NoSSO Authorization")
        #TODO, create an image for the NoSSO authorization
        redesc = QtWidgets.QLabel(f"Would you like to continue to {app_name}?")
        
        button_layout = QtWidgets.QHBoxLayout()
        button_yes = QtWidgets.QPushButton("Yes")
        button_no = QtWidgets.QPushButton("No")
        button_layout.addWidget(button_yes)
        button_layout.addWidget(button_no)

        layout.addWidget(title)
        layout.addWidget(redesc)
        layout.addLayout(button_layout)

        window.setLayout(layout)
        window.show()
        sys.exit(app.exec())
