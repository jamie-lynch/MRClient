"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow import tools
from clientwindow.tools import QSectionLabel, QHeadingLabel, TemplateRow, IndividualFireButton

class StatWidget(QtGui.QWidget):
    """Widget for Lineup graphics"""

    def __init__(self, main, parent=None, data=None):
        """init function fro NameWidget"""
        super(StatWidget, self).__init__(parent)
        self.title = "Stats"
        self.main = main
        self.comms = main.comms
        self.init_ui(data)

    def init_ui(self, data=None):
        """ sets base content of widget """

        # get data if required
        if not data:
            data = tools.get_json()

        # create layouts
        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)

        # data
        self.vbox.addWidget(QSectionLabel("Data"))
        self.data_section = DataSection(data=data, settings=self.main.settings, main=self.main)
        self.vbox.addWidget(self.data_section)

        # tempaltes
        self.vbox.addWidget(QSectionLabel("Templates"))
        self.templates_section = TemplatesSection(settings=self.main.settings, main=self.main)
        self.vbox.addWidget(self.templates_section)

        self.vbox.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))

    def refresh_data(self, data=None):
        """Function to refresh data from JSON"""

        # get data if required
        if not data:
            data = tools.get_json()

        self.data_section.refresh_data(data=data, settings=self.main.settings)
        self.templates_section.refresh_data(settings=self.main.settings)

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

        scroll = QtGui.QScrollArea()

        self.stats_container = QtGui.QWidget()
        container_vbox = QtGui.QGridLayout()
        self.stats_container.setLayout(container_vbox)



        # stats
        statnames = [QHeadingLabel(stat['name']) for stat in data['stats']]
        statunits = [QtGui.QLabel(stat['units']) for stat in data['stats']]

        statvals = [stat['vals'] for stat in data['stats']]
        statvals = [[QtGui.QLabel(val['statval']) for val in stat] for stat in statvals]

        for num, name in enumerate(statnames):
            container_vbox.addWidget(
                StatRow(
                    data={
                        'name': statnames[num],
                        'unit': statunits[num],
                        'vals': statvals[num]
                    },
                    main=self.main,
                    settings=settings
                )
            )

        scroll.setWidget(self.stats_container)
        self.vbox.addWidget(scroll)

    def refresh_data(self, data, settings):
        """Function to refresh data for data section"""

        self.vbox.removeWidget(self.stats_container)
        self.stats_container.deleteLater()

        self.stats_container = QtGui.QWidget()
        container_vbox = QtGui.QVBoxLayout()
        self.stats_container.setLayout(container_vbox)
        self.vbox.addWidget(self.stats_container)

        # stats
        statnames = [QHeadingLabel(stat['name']) for stat in data['stats']]
        statunits = [QtGui.QLabel(stat['units']) for stat in data['stats']]

        statvals = [stat['vals'] for stat in data['stats']]
        statvals = [[QtGui.QLabel(val['statval']) for val in stat] for stat in statvals]

        for num, name in enumerate(statnames):
            container_vbox.addWidget(
                StatRow(
                    data={
                        'name': statnames[num],
                        'unit': statunits[num],
                        'vals': statvals[num]
                    },
                    main=self.main,
                    settings=settings
                )
            )

class StatRow(QtGui.QWidget):
    """Class which holds the data for one statistic"""

    def __init__(self, data, main, settings, parent=None):
        """Function to initialise EventRow class"""
        super(StatRow, self).__init__(parent)
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        col = 0
        grid.addWidget(data['name'], 0, col)
        col += 1
        grid.addWidget(data['unit'], 0, col)
        col += 1
        for val in data['vals']:
            grid.addWidget(val, 0, col)
            col += 1
        grid.addWidget(IndividualFireButton(
            text='Fire',
            data=data,
            show=settings['templates']['standard']['stats']['show'],
            main=main
        ), 0, col)

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

        for template in settings['templates']['stats']:
            templates_vbox.addWidget(TemplateRow(template_data=template, main=self.main))

    def refresh_data(self, settings):
        """Function to refresh templates data"""

        self.vbox.removeWidget(self.templates_container)
        self.templates_container.deleteLater()

        self.templates_container = QtGui.QWidget()
        templates_vbox = QtGui.QVBoxLayout()
        self.templates_container.setLayout(templates_vbox)
        self.vbox.addWidget(self.templates_container)

        for template in settings['templates']['stats']:
            templates_vbox.addWidget(TemplateRow(template_data=template, main=self.main))
