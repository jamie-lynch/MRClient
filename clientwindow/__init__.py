"""
Match Report CasparCG Client
Version 2.0
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file defines the mainwindow class
"""


from PySide import QtGui, QtCore
from clientwindow import tools
from clientwindow.CasparCGComms import casparcg_amcp as caspar_comms
from clientwindow.CasparCGComms.osc_receiver import OSCReceiver
from clientwindow.groups import videos, rundown, tables, production
from clientwindow.menubar import ClientMenu


class ClientWindow(QtGui.QMainWindow):
    """Class which defines the mainwindow for the MRClient"""

    # creates an instance of the CasparCG connect signal class
    connected = tools.Connected()

    def __init__(self, splash_window, parent=None):
        """Function which initialises the class"""

        # call the parent __init__ function
        super(ClientWindow, self).__init__(parent)

        # call the function to begin startup
        self.startup(splash_window)

        # Set window to be full size and central
        self.setWindowState(QtCore.Qt.WindowMaximized)

        # set title
        self.setWindowTitle('Match Report CasparCG Client')

    def startup(self, splash_window):
        """Function to carry out all startup procedures"""

        # create reference to the splash window
        self.splash = splash_window

        # create instance of CasparAMCP class
        self.comms = caspar_comms.CasparAMCP()

        # create an osc reviever
        self.osc = OSCReceiver()

        # get json data
        self.data = tools.get_startup_data()
        self.splash.change_message()

        # get client settings
        self.settings = tools.get_settings()
        self.splash.change_message()

        # call the init_ui function to build the ui elements
        self.init_ui()
        self.splash.change_message()

        # attempt to connect to caspar
        self.attempt_startup_connect()

    def init_ui(self):
        """setups the top level window with the required parts"""

        # create central widget
        central = QtGui.QWidget()
        self.setCentralWidget(central)

        # layout for central widget
        vbox = QtGui.QVBoxLayout()
        central.setLayout(vbox)

        # tab widget
        self.tab_widget = QtGui.QTabWidget()
        vbox.addWidget(self.tab_widget)

        # refresh button
        self.refresh_button = QtGui.QPushButton('Refresh')
        self.refresh_button.clicked.connect(self.refresh_video_list)
        vbox.addWidget(self.refresh_button)

        # shit the bed
        kill_button = QtGui.QPushButton("Clear All")
        kill_button.clicked.connect(self.comms.kill_switch)
        vbox.addWidget(kill_button)

        # set element list
        elements = ['production', 'tables', 'vts', "rundown"]

        # create the poodown
        self.rundown = rundown.RundownWidget(main=self)

        # create a dictionary of elements
        self.elements = {
            "production": {"element": production.ProductionWidget(main=self), "index": 0, "name": "Production"},
            "vts": {"element": videos.VideoWidget(main=self), "index": 1, "name": "VTs"},
            "tables": {"element": tables.TablesWidget(main=self), "index": 2, "name": "Tables"},
            "rundown": {"element": self.rundown, "index": 3, "name": "Rundown"}
        }

        # add each element to the tab widget
        for num, element_name in enumerate(elements):
            self.tab_widget.addTab(
                self.elements[element_name]["element"],
                self.elements[element_name]["name"]
            )

        # add menu
        menu_bar = ClientMenu(main=self)
        self.setMenuBar(menu_bar)

        # status bar
        self.status_bar = QtGui.QStatusBar()
        self.status = QtGui.QLabel("Disconnected")
        self.status_bar.addPermanentWidget(self.status)
        self.setStatusBar(self.status_bar)

    def refresh_video_list(self):
        """Function which passes the refresh command onto the video element"""
        self.elements['vts']['element'].refresh_data()

    def set_refresh_button(self):
        """Function to decide whether the refresh button should be enabled or disabled"""
        playing = [len(self.osc.videos[key].keys()) for key in self.osc.videos.keys()]
        if sum(playing):
            self.refresh_button.setDisabled(True)
        else:
            self.refresh_button.setEnabled(True)

    def attempt_startup_connect(self):
        """Function which attempts to connect to Caspar on startup"""
        if not self.comms.casparcg:
            response = self.comms.caspar_connect(self.settings['caspar']['address'], self.settings['caspar']['port'])
            print(response)
        else:
            return

        if "Failed" not in response:
            self.status.setText("Connected")
            self.connected.signal.emit()

    def closeEvent(self, event, direct=False):
        """Function which re-implements the built in close function to add extra features"""

        # if the close function is called programmatically then just do it
        if direct:
            self.comms.caspar_disconnect()
            event.accept()
            return

        # check if they really want to quit
        quit_msg = "Are you sure you want to quit?"
        reply = QtGui.QMessageBox.question(self, 'Close',
                                           quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        # if they do then close, if not then abort closure
        if reply == QtGui.QMessageBox.Yes:
            if self.comms.casparcg:
                    self.comms.caspar_disconnect()
            tools.store_data(self)
            tools.store_settings(self.settings)
            event.accept()
        else:
            event.ignore()
