"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

import sys
from PySide import QtGui, QtCore
from clientwindow.groups import names, \
                                lineup, \
                                time, \
                                score, \
                                stats, \
                                twitter, \
                                events, \
                                videos, \
                                rundown, \
                                tables, \
                                production
from clientwindow.menubar import ClientMenu
from clientwindow import tools, caspar_comms
from os import path


class ClientWindow(QtGui.QMainWindow):
        """top level class defining the mainwindow"""

        settings = tools.get_settings()
        connected = tools.Connected()

        def __init__(self, splash_window, parent=None):
                """init for the ClientWindow class"""
                super(ClientWindow, self).__init__(parent)
                self.connected.signal.connect(self.print_connected)

                self.startup(splash_window)

        def startup(self, splash_window):
                """Function to carry out all startup procedures"""
                # create splash window
                self.splash = splash_window
                # initialise caspar comms class
                self.comms = caspar_comms.CasparComms()
                # get json data
                self.data = tools.get_json(comms=self.comms)

                self.splash.change_message()
                # get client settings
                self.settings = tools.get_settings()

                self.splash.change_message()
                # add font to database to show emojis
                self.font_database = QtGui.QFontDatabase()
                self.font_database.addApplicationFont(
                        path.join(
                                self.settings['resources'],
                                'OpenSansEmoji.ttf'
                        )
                )

                self.splash.change_message()
                # start building the thing
                self.init_ui()

                # attempt to connect to caspar
                try:
                        self.attempt_startup_connect()
                except:
                        pass

                self.splash.change_message()

        def init_ui(self):
                """setups the top level window with the required parts"""

                # create central widget
                self.central = QtGui.QWidget()
                self.setCentralWidget(self.central)

                # layout for central widget
                self.vbox = QtGui.QVBoxLayout()
                self.central.setLayout(self.vbox)

                # tab widget
                self.tab_widget = QtGui.QTabWidget()
                self.vbox.addWidget(self.tab_widget)

                # refresh button
                self.refresh_button = QtGui.QPushButton('Refresh')
                self.refresh_button.clicked.connect(self.refresh_live_data)
                self.vbox.addWidget(self.refresh_button)

                # shit the bed
                self.kill_button = QtGui.QPushButton("PANIC!!!")
                self.kill_button.clicked.connect(self.comms.kill_switch)
                self.vbox.addWidget(self.kill_button)

                # get and add elements
                self.elements, self.ref = self.generate_data_elements(comms = self.comms)
                for num, element_name in enumerate(self.ref):
                        self.tab_widget.insertTab(num, self.elements[element_name]["element"], element_name.capitalize())

                for num, element_name in enumerate(self.ref):
                        if not self.settings['show'][element_name]:
                                if self.tab_widget.currentIndex() == num:
                                        if num == 0:
                                                self.tab_widget.setCurrentIndex(1)
                                        else:
                                                self.tab_widget.setCurrentIndex(num-1)
                                self.tab_widget.setTabEnabled(num, False)

                # add menu
                self.menubar = ClientMenu(comms=self.comms, main = self, parent=self)
                self.setMenuBar(self.menubar)

                # status bar
                self.status_bar = QtGui.QStatusBar()
                self.status = QtGui.QLabel("")
                self.status_bar.addPermanentWidget(self.status)
                if self.comms.casparcg:
                        self.status.setText("Connected")
                else:
                        self.status.setText("Disconnected")
                self.setStatusBar(self.status_bar)

                # Set window to be full size and central
                self.setWindowState(QtCore.Qt.WindowMaximized)

                # set title
                self.setWindowTitle('The Big Match CasparCG Client')

        def generate_data_elements(self, comms):
                """Function which returns the required elements to the grid manager"""

                data = self.data

                # create list for elements
                elements = {}

                if self.settings['mode'] == "live":

                        # appends name list with required settings
                        elements["names"] = {"element":(names.NameWidget(main=self, data=data)), "index":0, "visable":self.settings['show']['names']}
                        elements["lineup"] = {"element":(lineup.LineupWidget(main=self, data=data)), "index":1, "visable":self.settings['show']['lineup']}
                        elements["time"] = {"element":(time.TimeWidget(main=self, data=data)), "index":2, "visable":self.settings['show']['time']}
                        elements["score"] = {"element":(score.ScoreWidget(main=self, data=data)), "index":3, "visable":self.settings['show']['score']}
                        elements["stats"] = {"element":(stats.StatWidget(main=self, data=data)), "index":4, "visable":self.settings['show']['stats']}
                        elements["events"] = {"element":(events.EventWidget(main=self, data=data)), "index":5, "visable":self.settings['show']['events']}
                        elements["twitter"] = {"element":(twitter.TwitterWidget(main=self, data=data)), "index":6, "visable":self.settings['show']['twitter']}
                        elements["vts"] = {"element": videos.VideoWidget(main=self, data=data), "index":7, "visable":self.settings['show']['vts']}

                        ref = ["names", "lineup", "time", "score", "stats", "events", "twitter", "vts"]

                else:

                        # appends name list with required settings
                        elements["production"] = {"element": production.ProductionWidget(main=self, data=data), "index": 0, "visable": True}
                        elements["twitter"] = {"element": twitter.TwitterWidget(main=self, data=data), "index": 1, "visable": self.settings['show']['twitter']}
                        elements["vts"] = {"element": videos.VideoWidget(main=self, data=data), "index": 2, "visable": self.settings['show']['vts']}
                        elements["tables"] = {"element": tables.TablesWidget(main=self), "index": 3, "visable": self.settings['show']['tables']}
                        elements["rundown"] = {"element": rundown.RundownWidget(main=self), "index": 4, "visable": self.settings['show']['rundown']}

                        self.rundown = elements['rundown']['element']
                        self.rundown.build_from_file()

                        ref = ["production", "twitter", "vts", "tables", "rundown"]

                return elements, ref

        def refresh_live_data(self):
                """ Function which calls refresh functions of each data section"""

                # get the data
                data = tools.get_json(comms=self.comms)

                # call refresh_data function of each element
                for key in self.elements.keys():
                        self.elements[key]['element'].refresh_data(data = data)

        def attempt_startup_connect(self):
                """Function which attempts to connect to Caspar on startup"""
                if not self.comms.casparcg:
                        response = self.comms.caspar_connect(self.settings['caspar']['address'], self.settings['caspar']['port'])
                        print(response)
                if "Failed" not in response:
                        self.status.setText("Connected")
                        self.connected.signal.emit()

        def print_connected(self):
            """"Function to print when the connected signal is received"""
            print("I've just connected to CasparCG")

        def closeEvent(self, event, direct=False):
                """Reused close event"""

                if direct:
                        self.comms.caspar_disconnect()
                        event.accept()
                        return

                quit_msg = "Are you sure you want to quit?"
                reply = QtGui.QMessageBox.question(self, 'Close',
                                                   quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

                if reply == QtGui.QMessageBox.Yes:
                        if self.comms.casparcg:
                                self.comms.caspar_disconnect()
                        tools.store_local_data(self)
                        event.accept()
                else:
                        event.ignore()

        def update_window(self):
                """Function which updates the window when settings are changed"""
                for num, element_name in enumerate(self.ref):
                        if not self.settings['show'][element_name]:
                                if self.tab_widget.isTabEnabled(num):
                                        if self.tab_widget.currentIndex() == num:
                                                if num == 0:
                                                        self.tab_widget.setCurrentIndex(1)
                                                else:
                                                        self.tab_widget.setCurrentIndex(num - 1)
                                        self.tab_widget.setTabEnabled(num, False)
                        else:
                                if not self.tab_widget.isTabEnabled(num):
                                        self.tab_widget.setTabEnabled(num, True)

                # update templates
                for section in self.ref:
                        self.elements[section]['element'].refresh_data(data=tools.get_json(comms=self.comms))