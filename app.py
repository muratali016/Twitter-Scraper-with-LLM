import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5 import QtCore
from pymongo import MongoClient
import os

# Importing SocialMediaScraperApp and SocialMediaScraperApp_WOUT from MAIN_UI and MAIN_UI_CHAT
from MAIN_UI import SocialMediaScraperApp_WOUT
from MAIN_UI_CHAT import SocialMediaScraperApp

basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'mycompany.myproduct.subproduct.version'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

class SignInApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sign In")
        self.setWindowIcon(QIcon(os.path.join(basedir, 'logo.png')))  # Setting the window icon
        self.setStyleSheet("background-color: #E0FFFF;")  # Setting light blue background
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Logo
        logo_label = QLabel(self)
        pixmap = QPixmap(os.path.join(basedir, 'logo.png'))
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(QtCore.Qt.AlignCenter)  # Align logo to center
        layout.addWidget(logo_label)

        # Username field
        self.username_label = QLabel("Username:", self)
        self.username_edit = QLineEdit(self)
        self.username_edit.setStyleSheet("background-color: white;")  # Set white background
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_edit)

        # Password field
        self.password_label = QLabel("Password:", self)
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet("background-color: white;")  # Set white background
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_edit)

        # Sign in button
        self.signin_button = QPushButton("Sign In", self)
        self.signin_button.setStyleSheet("background-color: #6495ED; color: white;")
        self.signin_button.clicked.connect(self.signin)
        layout.addWidget(self.signin_button)

        self.setLayout(layout)
        self.setFixedSize(600, 400)  # Set window size to 600x400

        # Enable proceeding with Enter button
        self.username_edit.returnPressed.connect(self.signin)
        self.password_edit.returnPressed.connect(self.signin)

    def signin(self):
        username = self.username_edit.text()
        password = self.password_edit.text()

        # Connect to MongoDB
        try:
            client = MongoClient("mongodb+srv://yourprofile@database1.xxxx.mongodb.net/")
            db = client.smartbids
            users_collection = db.users
            user = users_collection.find_one({"username": username, "password": password})

            if user:
                # Check if the user is a free user
                if user.get("subscription_status") == "free":
                    self.hide()
                    self.user_features_window = SocialMediaScraperApp_WOUT()
                    self.user_features_window.show()
                else:
                    self.hide()
                    self.user_features_window = SocialMediaScraperApp()
                    self.user_features_window.show()
            else:
                QMessageBox.warning(self, "Sign In Failed", "Invalid username or password.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    signin_app = SignInApp()
    signin_app.show()
    sys.exit(app.exec_())
