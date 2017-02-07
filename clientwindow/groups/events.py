"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow import tools
from clientwindow.tools import QSectionLabel, \
                                QHeadingLabel, \
                                TemplateRow, \
                                IndividualFireButton

class EventWidget(QtGui.QWidget):
    """Widget for Lineup graphics"""

    def __init__(self, main, parent=None, data=None):
        """init function fro NameWidget"""
        super(EventWidget, self).__init__(parent)
        self.title = "Events"
        self.main = main
        self.comms = main.comms
        self.init_ui(data)

    def init_ui(self, data=None):
        """ sets base content of widget """

        # get data if required
        if not data:
            data = tools.get_json()

        # create layout
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        # Data
        vbox.addWidget(QSectionLabel("Data"))
        self.data_section = DataSection(data=data, settings=self.main.settings, main=self.main)
        vbox.addWidget(self.data_section)

        # Templates
        vbox.addWidget(QSectionLabel("Templates"))
        self.templates_section = TemplatesSection(settings=self.main.settings, main=self.main)
        vbox.addWidget(self.templates_section)

        vbox.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))

    def refresh_data(self, data=None):
        """Function to refresh data from JSON"""

        # get data if required
        if not data:
            data = tools.get_json()

        self.data_section.refresh_data(data, settings=self.main.settings)
        self.templates_section.refresh_data(settings=self.main.settings)
        self.update()

class DataSection(QtGui.QWidget):
    """Class which holds all of the time data"""

    def __init__(self, data, settings, main, parent=None):
        """Function to initialise DataSection class"""
        super(DataSection, self).__init__(parent)
        self.main = main
        self.init_ui(data, settings)

    def init_ui(self, data, settings):
        """Function which builds DataSection class"""

        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)


        self.event_container = QtGui.QWidget()
        container_vbox = QtGui.QVBoxLayout()
        self.event_container.setLayout(container_vbox)

        for event in data['events']:
            container_vbox.addWidget(EventDataWidget(data=event, show=settings['templates']['events'], main=self.main))

        scroll = QtGui.QScrollArea()
        scroll.setWidget(self.event_container)
        self.vbox.addWidget(scroll)

    def refresh_data(self, data, settings):

        self.vbox.removeWidget(self.event_container)
        self.event_container.deleteLater()

        self.event_container = QtGui.QWidget()
        container_vbox = QtGui.QVBoxLayout()
        self.event_container.setLayout(container_vbox)

        for event in data['events']:
            container_vbox.addWidget(
                EventDataWidget(
                    event,
                    show=settings['templates']['standard']['events']['show'],
                    main=self.main
                )
            )

        self.vbox.addWidget(self.event_container)

class EventDataWidget(QtGui.QGroupBox):
    """Class which defines one event set of data"""
    def __init__(self, data, main, parent=None, show=True):
        """Function to initialise widget"""
        super(EventDataWidget, self).__init__(parent)
        self.setTitle(data['heading'])
        self.main = main

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # Team
        grid.addWidget(QHeadingLabel("Team: "), 0, 0)
        grid.addWidget(QtGui.QLabel(data['team']), 0, 1, 1, 2)

        # Player 1
        grid.addWidget(QHeadingLabel("Player: "), 1, 0)
        grid.addWidget(QtGui.QLabel(data['player1num']), 1, 1)
        grid.addWidget(QtGui.QLabel(data['player1name']), 1, 2)

        # Player 2
        if data['player2num'] and data['player2name']:
            grid.addWidget(QHeadingLabel("Player: "), 2, 0)
            grid.addWidget(QtGui.QLabel(data['player2num']), 2, 1)
            grid.addWidget(QtGui.QLabel(data['player2name']), 2, 2)

        # Time
        grid.addWidget(QHeadingLabel("Time: "), 0, 3)
        grid.addWidget(QtGui.QLabel(data['time']), 0, 4)

        # Text
        grid.addWidget(QHeadingLabel("Text: "), 1, 3)
        grid.addWidget(QtGui.QLabel(data['text']), 1, 4)

        # button
        self.fire_button = IndividualFireButton(text="Fire", data=data, show=show, main=self.main)
        grid.addWidget(self.fire_button, 0, 5)

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

        for template in settings['templates']['events']:
            templates_vbox.addWidget(TemplateRow(template_data=template, main=self.main))

    def refresh_data(self, settings):

        self.vbox.removeWidget(self.templates_container)
        self.templates_container.deleteLater()

        self.templates_container = QtGui.QWidget()
        templates_vbox = QtGui.QVBoxLayout()
        self.templates_container.setLayout(templates_vbox)
        self.vbox.addWidget(self.templates_container)

        for template in settings['templates']['events']:
            templates_vbox.addWidget(TemplateRow(template_data=template, main=self.main))




