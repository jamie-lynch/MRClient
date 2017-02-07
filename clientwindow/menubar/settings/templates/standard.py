"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow.tools import QHeadingLabel, QSectionLabel
from clientwindow import tools

class StandardSettingsBox(QtGui.QWidget):
    """Class which holds the standard template settings"""

    standard_templates = ['events', 'stats', 'lineup']

    def __init__(self, settings_window, parent=None):
        """Function to initialise StandardSettingsBox"""
        super(StandardSettingsBox, self).__init__(parent)
        self.settings_window = settings_window
        self.init_ui()

    def init_ui(self):
        """Function to build StandardSettingsBox"""

        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        grid.setSpacing(0)

        row = 0
        for setting in self.standard_templates:
            grid.addWidget(StandardTemplateOption(setting=setting, settings_window=self.settings_window), row, 0)
            row += 1

        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

class StandardTemplateOption(QtGui.QWidget):
    """Class which proivde standard template option row"""

    def __init__(self, setting, settings_window, parent=None):
        """Function to initialise StandardTemplateOption class"""
        super(StandardTemplateOption, self).__init__(parent)

        self.setting = setting
        self.settings_window = settings_window

        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        col = 0

        grid.addWidget(QtGui.QLabel(setting.capitalize()), 0, col)
        col += 1

        self.details = self.settings_window.settings['templates']['standard'][self.setting]

        self.show_checkbox = QtGui.QCheckBox("Show")
        if self.details['show']:
            self.show_checkbox.setChecked(True)
        grid.addWidget(self.show_checkbox, 0, col)
        self.show_checkbox.stateChanged.connect(self.check_changed)
        col += 1

        edit = QtGui.QPushButton("Edit")
        edit.clicked.connect(lambda: self.edit_standard_template(self.setting, self.details))
        grid.addWidget(edit, 0, col)
        col += 1


    def edit_standard_template(self, setting, data):
        """Function to open edit settings window"""
        response = EditStandardTemplate(settings_window=self.settings_window, setting=setting, data=data)

    def check_changed(self):
        """Function to update temp settings if checkbox changed"""
        if self.show_checkbox.isChecked():
            value = True
        else:
            value = False

        settings = self.settings_window.settings['templates']
        settings['standard'][self.setting]['show'] = value

        self.settings_window.update_temp_settings(
            setting='templates',
            value=settings
        )

class EditStandardTemplate(QtGui.QDialog):
    """Widget for adding a new setting"""

    def __init__(self, settings_window, setting, data, parent=None):
        """Function to initialise EditStandardTemplate window"""
        super(EditStandardTemplate, self).__init__(parent)
        self.settings_window = settings_window
        self.setting = setting
        self.init_ui(setting, data)

    def init_ui(self, setting, data):
        """Function to build EditStandardTemplate dialog"""
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        self.filename = QtGui.QLineEdit()
        if data['filename']:
            self.filename.setText(data['filename'])
        else:
            self.filename.setPlaceholderText("Enter filename...")
        grid.addWidget(QtGui.QLabel("Filename"), 0, 0)
        grid.addWidget(self.filename, 0, 1, 1, 2)

        self.layer = QtGui.QLineEdit()
        if data['layer'] or data['layer'] == 0:
            self.layer.setText(str(data['layer']))
        else:
            self.layer.setPlaceholderText("Enter layer number...")
        grid.addWidget(QtGui.QLabel("Layer"), 1, 0)
        grid.addWidget(self.layer, 1, 1, 1, 2)

        self.channel = QtGui.QLineEdit()
        if data['channel'] or data['channel'] == 0:
            self.channel.setText(str(data['channel']))
        else:
            self.channel.setPlaceholderText("Enter Channel number...")
        grid.addWidget(QtGui.QLabel("Channel"), 2, 0)
        grid.addWidget(self.channel, 2, 1, 1, 2)

        # add and cancel buttons
        ok = QtGui.QPushButton("Ok")
        ok.clicked.connect(self.save_settings)
        grid.addWidget(ok, 3, 1)

        cancel = QtGui.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        grid.addWidget(cancel, 3, 2)

        # removes question mark thing
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)

        # set title
        self.setWindowTitle("Template Settings | The Big Match CasparCG Client")

        self.setFocus()

        self.exec_()

    def mousePressEvent(self, event):
        """Clear focus from QLineEdit"""
        try:
            self.focusWidget().clearFocus()
        except:
            pass
        QtGui.QWidget.mousePressEvent(self, event)

    def save_settings(self):
        """Function to save layer and channel settings"""

        self.settings_window.settings['templates']['standard'][self.setting]['channel'] = self.channel.text()
        self.settings_window.settings['templates']['standard'][self.setting]['layer'] = self.layer.text()
        self.settings_window.settings['templates']['standard'][self.setting]['filename'] = self.filename.text()
        tools.store_settings(self.settings_window.settings)
        self.accept()