"""
Match Report CasparCG Client
Version 2.1
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This package creates the top level menu bar
It also holds the all of the extra windows created from this menu
"""

from PySide import QtGui
from clientwindow.menubar.caspar import CasparConnection
from clientwindow.menubar.help import ErrorReport, AboutClient
import webbrowser


class ClientMenu(QtGui.QMenuBar):
    """Class to create a custom menu for the MRClient"""

    def __init__(self, main, parent=None):
        """Function to initialise the class"""

        # class the parent __init__ function
        super(ClientMenu, self).__init__(parent)

        # add main attribute as attributes for convenience
        self.main = main
        self.comms = main.comms
        self.settings = main.settings

        # create the UI elements
        self.init_ui()

    def init_ui(self):
        """Build the UI elements"""

        # Create the file menu and corresponding actions
        file_menu = self.addMenu('&File')

        # create an exit action
        exit_action = QtGui.QAction("Exit", self)
        exit_action.triggered.connect(self.main.close)
        file_menu.addAction(exit_action)

        # create the caspar menu and corresponding actions
        caspar_menu = self.addMenu('&Caspar')

        # create the connection action
        connection_action = QtGui.QAction("Connection", self)
        connection_action.triggered.connect(self.open_connection_dialog)
        caspar_menu.addAction(connection_action)

        # Create the help menu and corresponding actions
        help_menu = self.addMenu('&Help')

        # create the documentation action
        help_action = QtGui.QAction("Documentation", self)
        help_action.triggered.connect(lambda: webbrowser.open('http://bigmatch.jamielynch.net/client'))
        help_menu.addAction(help_action)

        # create the report action
        report_action = QtGui.QAction("Report Bug", self)
        report_action.triggered.connect(self.send_error_report)
        help_menu.addAction(report_action)

        # create the about action
        about_action = QtGui.QAction("About", self)
        about_action.triggered.connect(self.open_about_dialog)
        help_menu.addAction(about_action)

    def open_connection_dialog(self):
        """Function to open the caspar connection dialog"""
        CasparConnection(main=self.main)

    def send_error_report(self):
        """Function to open error report window and send"""
        ErrorReport(parent=self)

    def open_about_dialog(self):
        """Function to open the caspar connection dialog"""
        AboutClient(main=self.main, parent=self)
