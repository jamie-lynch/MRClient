"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui
from clientwindow.menubar.settings import ClientSettings
from clientwindow.menubar.caspar import CasparConnection
from clientwindow.menubar.help import ErrorReport, AboutClient
from clientwindow.menubar.rundown import SaveRundown, LoadRundown
import webbrowser

class ClientMenu(QtGui.QMenuBar):
    """Custom menubar for Clientwindow"""

    def __init__(self, comms, main, parent=None):
        """Initialise function of ClientMenu class"""
        super(ClientMenu, self).__init__(parent)
        self.comms = comms
        self.settings = main.settings
        self.main = main
        self.init_ui(parent)


    def init_ui(self, parent):
        """Builds Menu Bar"""


        # FILE

        # actions
        settingsAction = QtGui.QAction("Settings", self)
        settingsAction.triggered.connect(self.open_settings)

        exitAction = QtGui.QAction("Exit", self)
        exitAction.triggered.connect(self.main.close)

        #menubutton
        fileMenu = self.addMenu('&File')
        fileMenu.addAction(settingsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        # CASPAR

        # actions
        settingsAction = QtGui.QAction("Settings", self)
        settingsAction.triggered.connect(lambda: self.open_settings(focus=2))

        connectionAction = QtGui.QAction("Connection", self)
        connectionAction.triggered.connect(self.open_connection_dialog)

        # menubutton
        casparMenu = self.addMenu('&Caspar')
        casparMenu.addAction(settingsAction)
        casparMenu.addAction(connectionAction)

        # VIEW


        # HELP

        helpAction = QtGui.QAction("Documentation", self)
        helpAction.triggered.connect(lambda: webbrowser.open('http://bigmatch.jamielynch.net/client'))

        reportAction = QtGui.QAction("Report Bug", self)
        reportAction.triggered.connect(self.send_error_report)

        aboutAction = QtGui.QAction("About", self)
        aboutAction.triggered.connect(self.open_about_dialog)

        helpMenu = self.addMenu('&Help')
        helpMenu.addAction(helpAction)
        helpMenu.addAction(reportAction)
        helpMenu.addAction(aboutAction)

        # POODOWN

        saveAction = QtGui.QAction("Save Rundown", self)
        saveAction.triggered.connect(self.save_rundown)

        loadAction = QtGui.QAction("About", self)
        loadAction.triggered.connect(self.load_rundown)

        rundownMenu = self.addMenu('&Rundown')
        rundownMenu.addAction(saveAction)
        rundownMenu.addAction(loadAction)

    def open_settings(self, focus=0):
        """functions which loads the settings window and handles responses"""
        response = ClientSettings(self.main, parent=self, focus=focus)

    def open_connection_dialog(self):
        """Function to open the caspar connection dialog"""
        response = CasparConnection(comms=self.comms, main=self.main)

    def send_error_report(self):
        """Function to open error report window and send"""
        response = ErrorReport(parent=self)

    def open_about_dialog(self):
        """Function to open the caspar connection dialog"""
        response = AboutClient(main=self.main, parent=self)

    def save_rundown(self):
        """Function to save rundown"""
        pass

    def load_rundown(self):
        """Function to load rundown"""
        pass