"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow.tools import Connected
from clientwindow import tools


class CasparConnection(QtGui.QDialog):
    """Custom QDialog for client settings menu"""


    def __init__(self, main, comms, parent=None, ):
        """Function to initialise ClientSettings Class"""
        super(CasparConnection, self).__init__(parent)
        self.comms = comms
        self.main = main
        self.settings = main.settings
        self.init_ui(parent)

    def init_ui(self, parent):
        """Sets up ClientSettings"""

        # layout
        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(QtGui.QLabel("Address"), 0, 0)
        self.address_input = QtGui.QLineEdit()
        if self.settings['caspar']['address']:
            self.address_input.setText(self.settings['caspar']['address'])
        else:
            self.address_input.setPlaceholderText("xxx.xxx.xx.xxx")
        self.grid.addWidget(self.address_input, 0, 1, 1, 2)

        self.grid.addWidget(QtGui.QLabel("Port"), 1, 0)
        self.port_input = QtGui.QLineEdit()
        if self.settings['caspar']['port']:
            self.port_input.setText(str(self.settings['caspar']['port']))
        else:
            self.port_input.setPlaceholderText('xxxx')
        self.grid.addWidget(self.port_input, 1, 1, 1, 2)

        self.connection_button = QtGui.QPushButton("Connect")
        if self.comms.casparcg:
            self.connection_button.setDisabled(True)
        self.connection_button.clicked.connect(self.attempt_connection)
        self.grid.addWidget(self.connection_button, 2, 1)

        self.save_button = QtGui.QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.grid.addWidget(self.save_button, 2, 2)

        self.cancel_button = QtGui.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.grid.addWidget(self.cancel_button, 2, 3)


        # removes question mark thing
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)

        # set title
        self.setWindowTitle('Server Connection | The Big Match CasparCG Client')

        self.connection_button.setFocus()

        self.exec_()

    def attempt_connection(self):
        """Function which tries to connect"""

        self.save_settings()
        response = self.comms.caspar_connect(self.settings['caspar']['address'], self.settings['caspar']['port'])
        while "Failed" in response:
            msg = "Connection to CasparCG failed. Click to retry."
            retry = QtGui.QMessageBox.question(self, "Warning", msg, QtGui.QMessageBox.Retry | QtGui.QMessageBox.Cancel)
            if retry == QtGui.QMessageBox.Cancel:
                return
            response = self.comms.caspar_connect(self.settings['caspar']['address'], self.settings['caspar']['port'])
        self.main.status.setText("Connected")
        self.main.connected.signal.emit()
        self.accept()

    def save_settings(self):
        """Function to save the caspar connection settings"""

        self.main.settings['caspar']['address'] = self.address_input.text()
        self.main.settings['caspar']['port'] = int(self.port_input.text())
        tools.store_settings(self.main.settings)


