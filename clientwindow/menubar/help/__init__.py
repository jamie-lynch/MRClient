"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
import smtplib
from email.mime.text import MIMEText
from clientwindow.tools import QSectionLabel
from clientwindow import tools
from os import path



class ErrorReport(QtGui.QDialog):
    """Class to build and send error report"""

    def __init__(self, parent=None):
        """Initialise function for ErrorReport class"""
        super(ErrorReport, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Function to build ErrorReport class"""

        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(QSectionLabel("Send Error Report"), 0, 0, 1, 3)

        self.grid.addWidget(QtGui.QLabel("Name"), 1, 0)
        self.name = QtGui.QLineEdit()
        self.name.setPlaceholderText("Your name")
        self.grid.addWidget(self.name, 1, 1, 1, 2)

        self.grid.addWidget(QtGui.QLabel("Subject"), 2, 0)
        self.subject = QtGui.QLineEdit()
        self.subject.setPlaceholderText("Your subject")
        self.grid.addWidget(self.subject, 2, 1, 1, 2)

        self.grid.addWidget(QtGui.QLabel("Message"), 3, 0)
        self.message = QtGui.QTextEdit()
        self.grid.addWidget(self.message, 3, 1, 2, 2)

        self.okay = QtGui.QPushButton("Send")
        self.okay.clicked.connect(self.send)
        self.grid.addWidget(self.okay, 5, 1)

        self.cancel = QtGui.QPushButton("Cancel")
        self.cancel.clicked.connect(self.reject)
        self.grid.addWidget(self.cancel, 5, 2)

        # removes question mark thing
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)

        # set title
        self.setWindowTitle('Report Error | The Big Match CasparCG Client')

        self.exec_()


    def send(self):
        """Function to send email"""

        msg = MIMEText(self.message.toPlainText())

        # me == the sender's email address
        # you == the recipient's email address
        msg['Subject'] = "Error Report from {} - {}".format(self.name.text(), self.subject.text())
        msg['From'] = "{}@jamielynch.co.uk".format(self.name.text().replace(' ', '').lower())
        msg['To'] = "errorreports@jamielynch.co.uk"

        server = smtplib.SMTP(host="mail.jamielynch.co.uk", port=587)
        "New part"
        server.starttls()
        server.login('thebigmatch@jamielynch.co.uk', 'Robe250AT')
        server.sendmail("thebigmatch@jamielynch.co.uk", "thebigmatch@jamielynch.co.uk", msg.as_string())
        server.quit()

        self.accept()

class AboutClient(QtGui.QDialog):
    """Class to build and send error report"""

    def __init__(self, main, parent=None):
        """Initialise function for ErrorReport class"""
        super(AboutClient, self).__init__(parent)
        self.main = main
        self.init_ui()

    def init_ui(self):
        """Function to build AboutClient window"""

        width = self.main.frameGeometry().width()
        height = self.main.frameGeometry().height()

        self.setFixedSize(700, 409)
        self.setStyleSheet("background: transparent")

        self.vbox = QtGui.QVBoxLayout()

        close = QtGui.QLabel('X')
        close.mouseReleaseEvent = self.close_event
        close.setAlignment(QtCore.Qt.AlignRight)
        self.vbox.addWidget(close)

        self.vbox.addStretch(1)

        version = QtGui.QLabel("Version 1.0 | 08/2016")
        version.setIndent(width*0.04)
        version.setAlignment(QtCore.Qt.AlignRight)
        self.vbox.addWidget(version)

        developed = QtGui.QLabel("Developed by Jamie Lynch and Jack Connor-Richards for use by LSU Media")
        developed.setIndent(width*0.04)
        developed.setAlignment(QtCore.Qt.AlignRight)
        self.vbox.addWidget(developed)

        self.setLayout(self.vbox)

        # removes question mark thing
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.exec_()

    def paintEvent(self, event):


        resources = tools.get_resources()
        image_url = path.join(resources, 'images', 'about.png')
        self.tile = QtGui.QPixmap(image_url)
        self.tile.scaledToHeight(self.height())
        painter = QtGui.QPainter(self)
        painter.drawPixmap(self.rect(), self.tile)
        super(AboutClient, self).paintEvent(event)

    def close_event(self, event):
        self.close()
