"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow.tools import QSectionLabel, convert_checkstate

class SectionsSettings(QtGui.QWidget):
    """Widget for data settings tab"""

    def __init__(self, settings_window, parent=None):
        """Initialise function for DataSettings widget"""
        super(SectionsSettings, self).__init__(parent)
        self.settings_window = settings_window
        self.settings = self.settings_window.settings
        self.init_ui()

    def init_ui(self):
        """Function to initialise SectionsSettings class"""

        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)

        self.vbox.addWidget(QSectionLabel("Select tabs to display"))

        self.section_names = [
            "names",
            "lineup",
            "time",
            "score",
            "stats",
            "events",
            "twitter",
            "vts"
        ]

        self.show_buttons = [QtGui.QCheckBox(section_name) for section_name in self.section_names]
        self.button_group = QtGui.QButtonGroup()
        self.button_group.setExclusive(False)
        for button in self.show_buttons:
            if self.settings['show'][button.text()]:
                button.setChecked(True)
            self.button_group.addButton(button)
            self.vbox.addWidget(button)

        self.button_group.buttonClicked.connect(self.update_show_settings)

        self.vbox.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))

    def update_show_settings(self):
        """Function which controls the update of show settings"""

        settings = {}
        for num, button in enumerate(self.show_buttons):
            settings[self.section_names[num]] = convert_checkstate(button.checkState())
        self.settings_window.update_temp_settings("show", settings)

    def mousePressEvent(self, event):
        """Clear focus from QLineEdit"""
        try:
            self.focusWidget().clearFocus()
        except:
            pass
        QtGui.QWidget.mousePressEvent(self, event)