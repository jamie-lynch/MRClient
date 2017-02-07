"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow.menubar.settings import data, sections, templates, caspar
from clientwindow import tools



class ClientSettings(QtGui.QDialog):
    """Custom QDialog for client settings menu"""

    def __init__(self, main, parent=None, focus=None):
        """Function to initialise ClientSettings Class"""
        super(ClientSettings, self).__init__(parent)
        self.settings = main.settings
        self.main = main
        self.init_ui(main, focus)

    def init_ui(self, main, focus):
        """Sets up ClientSettings"""

        # gets current settings
        self.temp_settings = main.settings.copy()

        # creates vbox layout and sets as layout of settings window
        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)

        # create tab widget
        self.tab_widget = QtGui.QTabWidget()

        # create buttons
        self.buttons = self.add_buttons()

        self.tabs = {}

        # create all the tabs
        if self.settings['mode'] == "live":
            self.tabs["Data"] = data.DataSettings(settings_window=self)
            self.tabs["Sections"] = sections.SectionsSettings(settings_window=self)
            self.tabs["Templates"] = templates.TemplateSettings(settings_window=self)

        elif self.settings['mode'] == "roundup":
            pass

            self.tabs["Caspar"] = caspar.CasparSettings(settings_window=self, settings=main.settings)


        # add all the tabs

        for name, tab in self.tabs.items():
            self.tab_widget.addTab(tab, name)

        # adds stuff to the vbox
        self.vbox.addWidget(self.tab_widget)
        self.vbox.addLayout(self.buttons)

        # removes question mark thing
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)

        #set title
        self.setWindowTitle("Settings | The Big Match CasparCG Client")

        if focus:
            self.tab_widget.setCurrentIndex(focus)
        # GO GO GO
        self.exec_()

    def add_buttons(self):
        """Function which adds the buttons at the bottom"""
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)

        okay = QtGui.QPushButton("Ok")
        okay.clicked.connect(lambda: self.save_settings(okay=True))
        hbox.addWidget(okay)

        self.apply = QtGui.QPushButton("Apply")
        self.apply.clicked.connect(lambda: self.save_settings(okay=False))
        self.apply.setDisabled(True)
        hbox.addWidget(self.apply)

        cancel = QtGui.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        hbox.addWidget(cancel)

        return hbox

    def update_temp_settings(self, setting, value):
        """Function which updates the settings dictionary"""
        self.temp_settings[setting] = value
        if not self.apply.isEnabled():
            self.apply.setEnabled(True)

    def save_settings(self, okay=True):
        """Function to save settings and close if required"""
        self.main.settings = self.temp_settings.copy()
        tools.store_settings(self.temp_settings)
        if okay:
            self.main.update_window()
            self.accept()





