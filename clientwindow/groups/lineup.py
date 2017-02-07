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

class LineupWidget(QtGui.QWidget):
    """Widget for Lineup graphics"""

    def __init__(self, main, parent=None, data=None):
        """init function fro NameWidget"""
        super(LineupWidget, self).__init__(parent)
        self.title = "Lineup"
        self.main = main
        self.comms = main.comms
        self.init_ui(data)

    def init_ui(self, data):
        """ sets base content of widget """

        # get data if required
        if not data:
            data = tools.get_json()

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        # add data section
        vbox.addWidget(QSectionLabel("Data"))
        self.data_section = DataSection(data=data, settings=self.main.settings, main=self.main)
        vbox.addWidget(self.data_section)

        # add templates sections

        vbox.addWidget(QSectionLabel("Templates"))
        self.templates_section = TemplatesSection(settings=self.main.settings, main=self.main)
        vbox.addWidget(self.templates_section)

        vbox.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))

    def refresh_data(self, data=None):
        """Function to refresh data from JSON"""

        # get data if required
        if not data:
            data = tools.get_json()

        self.data_section.refresh_data(data=data)
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

        self.sort_data(data)

        self.main_lineup = LineupTable(data=self.main_data, settings=self.main.settings)
        self.bench_lineup = LineupTable(data=self.bench_data, settings=self.main.settings)
        self.coach_lineup = LineupTable(data=self.coach_data, settings=self.main.settings)

        # create layout
        self.main_vbox = QtGui.QVBoxLayout()
        self.setLayout(self.main_vbox)

        container = QtGui.QWidget()
        self.vbox = QtGui.QVBoxLayout()
        container.setLayout(self.vbox)

        # add data section
        self.vbox.addWidget(QHeadingLabel('Main'))
        self.vbox.addWidget(self.main_lineup)

        self.vbox.addWidget(QHeadingLabel('Bench'))
        self.vbox.addWidget(self.bench_lineup)

        self.vbox.addWidget(QHeadingLabel('Coach'))
        self.vbox.addWidget(self.coach_lineup)

        scroll = QtGui.QScrollArea()
        scroll.setWidget(container)
        self.main_vbox.addWidget(scroll)

    def sort_data(self, data):
        """Function which sorts data for lineup page build"""
        show = self.main.settings['templates']['standard']['lineup']['show']

        # data
        self.main_data = [
            [
                [QtGui.QLabel(player['num']),
                 QtGui.QLabel(player['name']),
                 IndividualFireButton(text="Fire", data=player, show=show, main=self.main)
                 ] for player in team['main']
                ] for team in data['lineups']
            ]

        self.bench_data = [
            [
                [QtGui.QLabel(player['num']),
                 QtGui.QLabel(player['name']),
                 IndividualFireButton(text="Fire", data=player, show=show, main=self.main)
                 ] for player in team['bench']
                ] for team in data['lineups']
            ]

        self.coach_data = [
            [
                [QtGui.QLabel(player['num']),
                 QtGui.QLabel(player['name']),
                 IndividualFireButton(text="Fire", data=player, show=show, main=self.main)
                 ] for player in team['manager']
                ] for team in data['lineups']
            ]
        return

    def refresh_data(self, data):
        """Function to refresh lineup data"""
        data = self.sort_data(data)

        self.vbox.removeWidget(self.main_lineup)
        self.vbox.removeWidget(self.bench_lineup)
        self.vbox.removeWidget(self.coach_lineup)

        self.main_lineup.deleteLater()
        self.bench_lineup.deleteLater()
        self.coach_lineup.deleteLater()

        self.main_lineup = LineupTable(data=self.main_data, settings=self.main.settings)
        self.bench_lineup = LineupTable(data=self.bench_data, settings=self.main.settings)
        self.coach_lineup = LineupTable(data=self.coach_data, settings=self.main.settings)

        self.vbox.insertWidget(1, self.main_lineup)
        self.vbox.insertWidget(3, self.bench_lineup)
        self.vbox.insertWidget(5, self.coach_lineup)

class LineupTable(QtGui.QWidget):
    """Class which returns lineup table"""

    def __init__(self, data, settings, parent=None):
        """Initialise function for LineupTable class"""
        super(LineupTable, self).__init__(parent)
        self.init_ui(data, settings)

    def init_ui(self, data, settings):
        """Builds widget to return"""

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        for teams_num in range(len(data)):
            for players_num in range(len(data[teams_num])):
                grid.addWidget(data[teams_num][players_num][0], players_num, 0 + (3*teams_num))
                grid.addWidget(data[teams_num][players_num][1], players_num, 1 + (3*teams_num))
                if settings['templates']['standard']['lineup']:
                    grid.addWidget(data[teams_num][players_num][2], players_num, 2 + (3*teams_num))

class TemplatesSection(QtGui.QWidget):
    """Class which holds all of the available templates"""

    def __init__(self, settings, main, parent=None):
        """Funciton to initialise TempaltesSection Widget"""
        super(TemplatesSection, self).__init__(parent)
        self.settings = settings
        self.main = main
        self.init_ui()

    def init_ui(self):
        """Function to build TemplatesSection"""

        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)

        self.templates_container = QtGui.QWidget()
        templates_vbox = QtGui.QVBoxLayout()
        self.templates_container.setLayout(templates_vbox)
        self.vbox.addWidget(self.templates_container)

        for template in self.settings['templates']['lineup']:
            templates_vbox.addWidget(TemplateRow(template_data=template, main=self.main))

    def refresh_data(self, settings):
        """Function to refresh templates data"""


        self.vbox.removeWidget(self.templates_container)
        self.templates_container.deleteLater()

        self.templates_container = QtGui.QWidget()
        templates_vbox = QtGui.QVBoxLayout()
        self.templates_container.setLayout(templates_vbox)
        self.vbox.addWidget(self.templates_container)

        for template in settings['templates']['lineup']:
            templates_vbox.addWidget(TemplateRow(template_data=template, main=self.main))

