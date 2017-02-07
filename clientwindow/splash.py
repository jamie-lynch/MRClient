"""
Match Report CasparCG Client
Version 1.5
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file contains the class which displays a splash window
"""
from PySide import QtCore, QtGui
from os import path
from clientwindow import tools
import random


class ClientSplash(QtGui.QSplashScreen):
    """Custom splash screen for the Match Report CasparCG Client"""

    # create a list of available messages
    messages = [
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

    def __init__(self, app):
        """Function which initialises the class"""

        # calls the parent init functions
        super(ClientSplash, self).__init__()

        # set background image
        self.setPixmap(QtGui.QPixmap(path.join(tools.get_resources(), 'images', 'splash.png')))

        # set transparency and frameless
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet('background:transparent')

        # handle any events (stops it not responding)
        app.processEvents()

        # show the splash screen
        self.show()

        # create variables to track messages and set the first message
        self.current = 0
        random.shuffle(self.messages)
        self.change_message()

    def change_message(self):
        """Function which changes message being displayed"""

        # set the current message
        self.showMessage(self.messages[self.current], QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)

        # add 1 to the current variable so that the same message isn't shown twice
        self.current += 1
