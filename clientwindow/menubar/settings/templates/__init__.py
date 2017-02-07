"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow.tools import QSectionLabel, QHeadingLabel
from clientwindow import tools
from clientwindow.menubar.settings.templates import custom, standard

class TemplateSettings(QtGui.QWidget):
    """Widget for data settings tab"""

    def __init__(self, settings_window, parent=None):
        """Initialise function for DataSettings widget"""
        super(TemplateSettings, self).__init__(parent)

        self.settings_window = settings_window
        self.settings = self.settings_window.settings
        self.template_settings = self.settings['templates']
        self.sections = [setting for setting in self.settings['show'].keys() if self.settings['show'][setting]]

        self.init_ui()

    def init_ui(self):
        """Function to initialise SectionsSettings class"""

        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)

        # Standard Settings

        self.vbox.addWidget(QSectionLabel("Standard"))
        self.standard_box = standard.StandardSettingsBox(settings_window=self.settings_window)
        self.vbox.addWidget(self.standard_box)

        # Custom Settings

        self.vbox.addWidget(QSectionLabel("Custom"))
        self.custom_box = custom.CustomSettingsBox(sections=self.sections, settings_window=self.settings_window)
        self.vbox.addWidget(self.custom_box)



