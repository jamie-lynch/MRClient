"""
Match Report CasparCG Client
Version 2.0
written by Jamie Lynch & Jack Connor-Richards for LSU Media
This file holds the classes for caspar connection
"""

from PySide import QtGui, QtCore
from clientwindow import tools


class CasparConnection(QtGui.QDialog):
    """Class which creates a dialog window to allow connection to caspar"""

    def __init__(self, main, parent=None):
        """Function to initialise ClientSettings Class"""

        # call the parent __init__ function
        super(CasparConnection, self).__init__(parent)

        # add some attributes for convenience
        self.main = main
        self.comms = main.comms
        self.settings = main.settings

        # Create the UI elements
        self.init_ui( )

        # removes question mark thing
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)

        # set title
        self.setWindowTitle('Server Connection | The Big Match CasparCG Client')

        # Here we go!
        self.exec_()

    def init_ui(self):
        """Build the UI elements"""

        # Create the layout
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # Create an address Label and Line Edit
        grid.addWidget(QtGui.QLabel("Address"), 0, 0)
        self.address_input = QtGui.QLineEdit()
        if self.settings['caspar']['address']:
            self.address_input.setText(self.settings['caspar']['address'])
        else:
            self.address_input.setPlaceholderText("xxx.xxx.xx.xxx")
        grid.addWidget(self.address_input, 0, 1, 1, 2)

        # Create a port Label and Line Edit
        grid.addWidget(QtGui.QLabel("Port"), 1, 0)
        self.port_input = QtGui.QLineEdit()
        if self.settings['caspar']['port']:
            self.port_input.setText(str(self.settings['caspar']['port']))
        else:
            self.port_input.setPlaceholderText('xxxx')
        grid.addWidget(self.port_input, 1, 1, 1, 2)

        # Add a connection button
        connection_button = QtGui.QPushButton("Connect")
        if self.comms.casparcg:
            self.connection_button.setDisabled(True)
        connection_button.clicked.connect(self.attempt_connection)
        grid.addWidget(connection_button, 2, 1)
        connection_button.setFocus()

        # Create a save button
        save_button = QtGui.QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        grid.addWidget(save_button, 2, 2)

        cancel_button = QtGui.QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        grid.addWidget(cancel_button, 2, 3)

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

        # modify the main settings dictionary
        self.main.settings['caspar']['address'] = self.address_input.text()
        self.main.settings['caspar']['port'] = int(self.port_input.text())

        # write this dictionary to disk
        tools.store_settings(self.main.settings)


