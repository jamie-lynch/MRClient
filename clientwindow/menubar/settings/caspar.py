"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow.tools import QSectionLabel
from clientwindow import tools

class CasparSettings(QtGui.QWidget):
    """Widget for data settings tab"""

    def __init__(self, settings_window, settings, parent=None):
        """Initialise function for DataSettings widget"""
        super(CasparSettings, self).__init__(parent)
        self.settings_window = settings_window
        self.main = self.settings_window.main
        self.settings = settings
        self.init_ui()

    def init_ui(self):
        """Builds data settings widget"""

        self.grid = QtGui.QGridLayout()

        self.grid.addWidget(QSectionLabel("Connection"), 0, 0)

        self.grid.addWidget(QtGui.QLabel("Address"), 1, 0)
        self.address_input = QtGui.QLineEdit()
        if self.settings['caspar']['address']:
            self.address_input.setText(self.settings['caspar']['address'])
        else:
            self.address_input.setPlaceholderText("xxx.xxx.xx.xxx")
        self.address_input.editingFinished.connect(self.update_settings)
        self.grid.addWidget(self.address_input, 1,1)

        self.grid.addWidget(QtGui.QLabel("Port"), 2, 0)
        self.port_input = QtGui.QLineEdit()
        if self.settings['caspar']['port']:
            self.port_input.setText(str(self.settings['caspar']['port']))
        else:
            self.port_input.setPlaceholderText('xxxx')
        self.port_input.editingFinished.connect(self.update_settings)
        self.grid.addWidget(self.port_input, 2, 1)

        self.connect_button = QtGui.QPushButton("Connect")
        if self.main.comms.casparcg:
            self.connect_button.setDisabled(True)
        self.connect_button.clicked.connect(self.attempt_connection)
        self.grid.addWidget(self.connect_button, 3, 0)

        self.grid.addWidget(QSectionLabel("VTs"), 4, 0)

        self.grid.addWidget(QtGui.QLabel("Directory"), 5, 0)
        self.directory = QtGui.QLineEdit()
        if self.settings['caspar']['video_directory']:
            self.directory.setText(self.settings['caspar']['video_directory'])
        else:
            self.directory.editingFinished.connect(self.update_settings)
        self.grid.addWidget(self.directory, 5, 1)

        self.directory.setPlaceholderText("directory/subdirectory")
        self.grid.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))
        self.setLayout(self.grid)

    def attempt_connection(self):
        """Function to try connecting to caspar"""
        self.update_settings()
        response = self.main.comms.caspar_connect(self.caspar_settings['address'], self.caspar_settings['port'])
        while "Failed" in response:
            msg = "Connection to CasparCG failed. Click to retry."
            retry = QtGui.QMessageBox.question(self, "Warning", msg,
                                               QtGui.QMessageBox.Retry | QtGui.QMessageBox.Cancel)
            if retry == QtGui.QMessageBox.Cancel:
                return
            response = self.comms.caspar_connect(self.settings['caspar']['address'],
                                                 self.settings['caspar']['port'])
        self.main.status.setText("Connected")
        self.main.connected.signal.emit()
        self.connect_button.setDisabled(True)

    def mousePressEvent(self, event):
        """Clear focus from QLineEdit"""
        try:
            self.focusWidget().clearFocus()
        except:
            pass
        QtGui.QWidget.mousePressEvent(self, event)

    def update_settings(self):
        """Function to build and update caspar settings"""
        settings = {
            'address': self.address_input.text(),
            'port': self.port_input.text(),
            'video_directory': self.directory.text()
        }
        self.caspar_settings = settings
        self.settings_window.update_temp_settings('caspar', settings)

