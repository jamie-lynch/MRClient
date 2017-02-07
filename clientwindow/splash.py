"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtCore, QtGui
from os import path
from clientwindow import tools
import random

class ClientSplash(QtGui.QSplashScreen):
    """Custom splashscreen for The Big Match CasparCG Client"""

    def __init__(self, app):
        super(ClientSplash, self).__init__()

        # set background image
        image = path.join(tools.get_resources(), 'images', 'splash.png')
        pixmap = QtGui.QPixmap(image)
        #pixmap = pixmap.scaledToHeight(app.desktop().screenGeometry().height() * 0.6)
        self.setPixmap(pixmap)

        # set tranparency and frameless
        #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet('background:transparent')
        self.show()

        self.set_message_data()
        self.change_message()
        app.processEvents()

    def change_message(self):
        """Function which changes message being displayed"""

        self.showMessage(self.messages[self.current], QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)
        self.messages.pop(self.current)
        self.current += 1

    def set_message_data(self):
        """Function to set message data"""
        self.current = 0
        self.used_messages = []
        self.messages = [
            "Polishing shiny Dan's head...",
            "Fetching presenters from burger van...",
            "Checking your cameras...",
            "Asking commentators to commentate...",
            "Searching for effects in Audition...",
            "Operating static camera...",
            "Loading biscuit preferences...",
            "Removing 11kHz low pass...",
            "Plugging in good pre-amps...",
            "Loading banter...",
            "Fetching PG58s",
            "Stealing other departments budgets...",
            "Connecting the footpedal...",
            "Making another video player...",
            "Criticising the infrastructure..."
        ]
        random.shuffle(self.messages)


