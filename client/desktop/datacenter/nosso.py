import hashlib
import sys
import requests
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton

class NoSSO:
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

class NoSSOUi(QDialog):
    def __init__(self, app_name):
        super().__init__()
        self.setWindowTitle("NoSSO Authorization")
        
        layout = QVBoxLayout()
        title = QLabel("NoSSO Authorization")
        #TODO, create an image for the NoSSO authorization
        redesc = QLabel(f"Would you like to authorize {app_name} to access your Macro server?")
        
        button_layout = QHBoxLayout()
        small_text = QLabel("This will allow this app to access all of the files on your Macro server")
        button_yes = QPushButton("Yes")
        button_no = QPushButton("No")
        button_layout.addWidget(button_yes)
        button_layout.addWidget(button_no)

        layout.addWidget(title)
        layout.addWidget(redesc)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        button_yes.clicked.connect(self.accept)
        button_no.clicked.connect(self.reject)

    @staticmethod
    def run(app_name):
        # Ensure a QApplication instance exists.
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
            
        dialog = NoSSOUi(app_name)
        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted

        #TODO: Make this app look more advanced than it acutally is