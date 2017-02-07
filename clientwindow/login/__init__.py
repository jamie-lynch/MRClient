"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from datetime import datetime

class LoginWindow(QtGui.QDialog):
    """top level class defining the mainwindow"""

    def __init__(self, parent=None):
        """init for the ClientWindow class"""
        super(LoginWindow, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        """setups the top level window with the required parts"""

        # create grid
        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)

        # username and password
        self.username = QtGui.QLineEdit(parent=self)
        self.username.setPlaceholderText("Username")
        self.password = QtGui.QLineEdit(parent=self)
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QtGui.QLineEdit.Password) # displays asterisks

        self.grid.addWidget(self.username, 0, 0)
        self.grid.addWidget(self.password, 1, 0)

        # login button
        self.login_button = QtGui.QPushButton("Login")
        self.login_button.clicked.connect(self.login)


        self.grid.addWidget(self.login_button, 2, 0)

        # error label
        self.error_label = QtGui.QLabel()
        self.error_label.setObjectName("error_label")
        self.error_label.setStyleSheet('QLabel#error_label {color: red}')
        self.grid.addWidget(self.error_label, 3, 0)


        # general stuff
        self.resize(300, 150)
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # set title
        self.setWindowTitle('The Big Match CasparCG Client | Login')

        self.login_button.setFocus()

        # show window
        self.show()


    def login(self):
        """Function to complete login"""
        username = self.username.text()
        password = self.password.text()

        login_details = {"username":"password"}

        if username in login_details.keys():
            if password == login_details['username']:
                self.log_login_attempt(True, username, password)
                self.accept()
            else:
                self.log_login_attempt(False, username, password)
                self.error_label.setText("Username or password incorrect")
        else:
            self.log_login_attempt(False, username, password)
            self.error_label.setText("Username or password incorrect")


    def log_login_attempt(self, success, username, password):
        """Function to log login attempt to file"""
        outcome = ['Unsuccessful', 'Successful']


