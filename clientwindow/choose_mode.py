from PySide import QtGui, QtCore
from clientwindow import tools

class ChooseMode(QtGui.QDialog):
    """Function which allows the user to choose the mode to launch to application in"""

    def __init__(self, settings, parent=None):
        """Function to initialise the ChooseMode class"""
        super(ChooseMode, self).__init__(parent)

        self.settings = settings

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        self.live = QtGui.QRadioButton("Live")
        self.roundup = QtGui.QRadioButton("Round Up")

        if settings['mode'] == "live":
            self.live.setChecked(True)
        else:
            self.roundup.setChecked(True)

        vbox.addWidget(self.live)
        vbox.addWidget(self.roundup)

        hbox = QtGui.QHBoxLayout()

        okay = QtGui.QPushButton("Ok")
        okay.clicked.connect(self.launch)
        hbox.addWidget(okay)

        close = QtGui.QPushButton("Close")
        close.clicked.connect(self.reject)
        hbox.addWidget(close)

        vbox.addLayout(hbox)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Choose Mode | The Big Match CasparCG Client')

    def launch(self):
        """Function to save settings and continue launching application"""

        if self.live.isChecked():
            checked = "live"
        else:
            checked = "roundup"

        self.settings['mode'] = checked
        tools.store_settings(self.settings)
        self.accept()
