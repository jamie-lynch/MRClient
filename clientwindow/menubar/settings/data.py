"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow.tools import QSectionLabel

class DataSettings(QtGui.QWidget):
    """Widget for data settings tab"""

    def __init__(self, settings_window, parent=None):
        """Initialise function for DataSettings widget"""
        super(DataSettings, self).__init__(parent)
        self.settings_window = settings_window
        self.settings = self.settings_window.settings
        self.init_ui()

    def init_ui(self):
        """Builds data settings widget"""

        self.grid = QtGui.QGridLayout()

        self.grid.addWidget(QSectionLabel("Data"), 0, 0)

        # default location
        self.default = QtGui.QCheckBox("Default / Auto", parent=self)
        if self.settings['data']['location']:
            self.default.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.default.setCheckState(QtCore.Qt.Checked)
        self.default.stateChanged.connect(self.check_changed)
        self.grid.addWidget(self.default, 1,0)

        # specify url
        self.grid.addWidget(QtGui.QLabel("Manual"), 2, 0)
        self.url_location = QtGui.QLineEdit(parent=self)
        self.url_location.setPlaceholderText("Enter url")
        if self.default.isChecked():
            self.url_location.setDisabled(True)
        else:
            self.url_location.setEnabled(True)
            self.url_location.setText(self.settings['data']['location'])
        self.grid.addWidget(self.url_location, 2, 1)
        self.url_location.editingFinished.connect(self.check_changed)

        self.grid.addItem(QtGui.QSpacerItem(1,1, vData=QtGui.QSizePolicy.Expanding))
        self.setLayout(self.grid)

    def mousePressEvent(self, event):
        """Clear focus from QLineEdit"""
        try:
            self.focusWidget().clearFocus()
        except:
            pass
        QtGui.QWidget.mousePressEvent(self, event)

    def check_changed(self):
        """Function which sets the url input to disable if default is checked"""
        settings = {}
        if self.default.isChecked():
            self.url_location.setDisabled(True)
            settings['location'] = ""
        else:
            self.url_location.setDisabled(False)
            settings['location'] = self.url_location.text()

        self.settings_window.update_temp_settings("data", settings)
