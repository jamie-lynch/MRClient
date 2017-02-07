"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow import tools, caspar_comms
from clientwindow.tools import QSectionLabel, QHeadingLabel, TemplateRow

class TimeWidget(QtGui.QWidget):
    """Widget containing time data related control"""

    def __init__(self, main, parent=None, data=None):
        """initialise function of TimeWidget"""
        super(TimeWidget, self).__init__(parent)
        self.title = "Time"
        self.main = main
        self.comms = main.comms
        self.init_ui(data)

    def init_ui(self, data=None):
         """Function to create TimeWidget layout"""

         if not data:
             data = tools.get_json()

         self.vbox = QtGui.QVBoxLayout()
         self.setLayout(self.vbox)

         # Data
         self.vbox.addWidget(QSectionLabel("Data"))
         self.data_section = DataSection(data=data)
         self.vbox.addWidget(self.data_section)

         # Templates
         self.vbox.addWidget(QSectionLabel("Templates"))
         self.templates_section = TemplatesSection(settings=self.main.settings, main=self.main)
         self.vbox.addWidget(self.templates_section)

         self.vbox.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))


    def refresh_data(self, data=None):
        """Function to refresh data from JSON"""
        if not data:
            data = tools.get_json()

        self.vbox.removeWidget(self.data_section)
        self.data_section.deleteLater()
        self.data_section = DataSection(data=data)
        self.vbox.insertWidget(1, self.data_section)

        self.templates_section.refresh_data(settings=self.main.settings)

        self.update()

class DataSection(QtGui.QWidget):
    """Class which holds all of the time data"""

    def __init__(self, data, parent=None):
        """Function to initialise DataSection class"""
        super(DataSection, self).__init__(parent)
        self.init_ui(data)

    def init_ui(self, data):
        """Function which builds DataSection class"""

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        row = 0

        # length
        grid.addWidget(QHeadingLabel("Period Length"), row, 0)
        grid.addWidget(QtGui.QLabel(data['time']['length']), row, 1)
        row += 1

        # periods
        grid.addWidget(QHeadingLabel("Number of Periods"), row, 0)
        grid.addWidget(QtGui.QLabel(data['time']['periods']), row, 1)
        row += 1

        # current
        grid.addWidget(QHeadingLabel("Current Period"), row, 0)
        grid.addWidget(QtGui.QLabel(data['time']['current']), row, 1)
        row += 1

        # extra
        grid.addWidget(QHeadingLabel("Extra Time"), row, 0)
        grid.addWidget(QtGui.QLabel(data['time']['extra']), row, 1)
        row += 1

        # running
        grid.addWidget(QHeadingLabel("Time On?"), row, 0)
        grid.addWidget(QtGui.QLabel(str(data['time']['running'])), row, 1)
        row += 1

        # time
        grid.addWidget(QHeadingLabel("Current Time"), row, 0)
        if data['time']['tenths']:
            split = ":"
        else:
            split = ""
        grid.addWidget(QtGui.QLabel(
            "{}:{}{}{}".format(
                data['time']['minutes'],
                data['time']['seconds'],
                split,
                data['time']['tenths']
            )
        ), row, 1)
        row += 1

        # starttext
        grid.addWidget(QHeadingLabel("Countdown Text"), row, 0)
        grid.addWidget(QtGui.QLabel(data['time']['starttext']), row, 1)
        row += 1

        # starttime
        grid.addWidget(QHeadingLabel("Game Start Time"), row, 0)
        grid.addWidget(QtGui.QLabel(data['time']['starttime']), row, 1)
        row += 1

class TemplatesSection(QtGui.QWidget):
    """Class which holds all of the time data"""

    def __init__(self, settings, main, parent=None):
        """Function to initialise DataSection class"""
        super(TemplatesSection, self).__init__(parent)
        self.main = main
        self.init_ui(settings)

    def init_ui(self, settings):
        """Function which builds DataSection class"""

        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)

        self.templates_container = QtGui.QWidget()
        templates_vbox = QtGui.QVBoxLayout()
        self.templates_container.setLayout(templates_vbox)
        self.vbox.addWidget(self.templates_container)

        for template in settings['templates']['time']:
            templates_vbox.addWidget(TemplateRow(template_data=template, main=self.main))

    def refresh_data(self, settings):
        """Function to refresh templates data"""

        self.vbox.removeWidget(self.templates_container)
        self.templates_container.deleteLater()

        self.templates_container = QtGui.QWidget()
        templates_vbox = QtGui.QVBoxLayout()
        self.templates_container.setLayout(templates_vbox)
        self.vbox.addWidget(self.templates_container)

        for template in settings['templates']['time']:
            templates_vbox.addWidget(TemplateRow(template_data=template, main=self.main))


