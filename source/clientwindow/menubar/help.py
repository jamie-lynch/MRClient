"""
Match Report CasparCG Client
Version 2.0
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file holds the two help based classes
"""

from PySide import QtGui, QtCore
import smtplib
from email.mime.text import MIMEText
from clientwindow.tools import QHeadingOne
from clientwindow import tools
from os import path


class ErrorReport(QtGui.QDialog):
    """Class to build and send error report"""

    def __init__(self, parent=None):
        """Function to initialise the class"""

        # calls the parent __init__ function
        super(ErrorReport, self).__init__(parent)

        # creates the UI elements
        self.init_ui()

        # removes question mark thing
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)

        # set title
        self.setWindowTitle('Report Error | Match Report CasparCG Client')

        # 3... 2... 1... GO!
        self.exec_()

    def init_ui(self):
        """Function to build ErrorReport class"""

        # Create and set layout
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # Add heading
        grid.addWidget(QHeadingOne("Send Error Report"), 0, 0, 1, 3)

        # Create the Name line edit
        grid.addWidget(QtGui.QLabel("Name"), 1, 0)
        self.name = QtGui.QLineEdit()
        self.name.setPlaceholderText("Your name")
        grid.addWidget(self.name, 1, 1, 1, 2)

        # Create the Subject line edit
        grid.addWidget(QtGui.QLabel("Subject"), 2, 0)
        self.subject = QtGui.QLineEdit()
        self.subject.setPlaceholderText("Your subject")
        grid.addWidget(self.subject, 2, 1, 1, 2)

        # Create the Message text edit
        grid.addWidget(QtGui.QLabel("Message"), 3, 0)
        self.message = QtGui.QTextEdit()
        grid.addWidget(self.message, 3, 1, 2, 2)

        # Create a button to confirm send
        okay = QtGui.QPushButton("Send")
        okay.clicked.connect(self.send)
        grid.addWidget(okay, 5, 1)

        # Create a button to cancel
        cancel = QtGui.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        grid.addWidget(cancel, 5, 2)

    def send(self):
        """Function to send email"""

        # Convert the message to plain text
        msg = MIMEText(self.message.toPlainText())

        # Set the email headers
        msg['Subject'] = "Error Report from {} - {}".format(self.name.text(), self.subject.text())
        msg['From'] = "{}@jamielynch.co.uk".format(self.name.text().replace(' ', '').lower())
        msg['To'] = "errorreports@jamielynch.co.uk"

        # Set the server details and connect
        server = smtplib.SMTP(host="mail.jamielynch.co.uk", port=587)
        server.starttls()
        server.login('thebigmatch@jamielynch.co.uk', 'Robe250AT')

        # Send the email
        server.sendmail("thebigmatch@jamielynch.co.uk", "thebigmatch@jamielynch.co.uk", msg.as_string())

        # Quit the server
        server.quit()

        # Close the dialog window
        self.accept()


class AboutClient(QtGui.QDialog):
    """Class which creates an About dialog window"""

    def __init__(self, main, parent=None):
        """Function to initialise the class"""

        # Calls the parent __init__ function
        super(AboutClient, self).__init__(parent)

        # Set the main window as an attribute
        self.main = main

        # Create the UI elements
        self.init_ui()

        # Set the window to be frameless and transparent
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Go Go Go!
        self.exec_()

    def init_ui(self):
        """Function to build AboutClient window"""

        # Find the width of the mainwindow
        width = self.main.frameGeometry().width()

        # Set the size of the dialog window
        self.setFixedSize(700, 409)

        # Set the window to be transparent
        self.setStyleSheet("background: transparent")

        # Create and set layout
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        # Add an X to allow window to be closed
        close = QtGui.QLabel('X')
        close.mouseReleaseEvent = self.close
        close.setAlignment(QtCore.Qt.AlignRight)
        vbox.addWidget(close)

        # Add some stretch to the layout
        vbox.addStretch(1)

        # Define the version
        version = QtGui.QLabel("Version 2.0 | 02/2017")
        version.setIndent(width*0.04)
        version.setAlignment(QtCore.Qt.AlignRight)
        vbox.addWidget(version)

        # Add a line edit to say who developed it
        developed = QtGui.QLabel("Developed by Jamie Lynch and Jack Connor-Richards for use by LSU Media")
        developed.setIndent(width*0.04)
        developed.setAlignment(QtCore.Qt.AlignRight)
        vbox.addWidget(developed)

    def paintEvent(self, event):
        """Function which sets the background image of the about window"""

        # get path to the resources directory
        resources = tools.get_resources()

        # get the path to the image
        image_url = path.join(resources, 'about.png')

        # set the image as the background
        tile = QtGui.QPixmap(image_url)
        tile.scaledToHeight(self.height())
        painter = QtGui.QPainter(self)
        painter.drawPixmap(self.rect(), tile)
        super(AboutClient, self).paintEvent(event)

    def close(self, e):
        """Function to try closing the window"""
        self.reject()
