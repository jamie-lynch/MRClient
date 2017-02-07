"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui
from clientwindow import tools
from clientwindow.tools import QSectionLabel, QHeadingLabel
from clientwindow.groups.tables.standings import *

class TablesWidget(QtGui.QWidget):
    """Widget for University name graphics"""

    def __init__(self, main, data=None, parent=None):
        """init function fro NameWidget"""
        super(TablesWidget, self).__init__(parent)
        self.title = "Tables"
        self.main = main
        self.comms = main.comms
        self.init_ui(data)

    def init_ui(self, data):
        """ sets base content of widget """

        if not data:
            data = tools.get_json()

        vbox = QtGui.QGridLayout()
        self.setLayout(vbox)

        # Standings Section
        vbox.addWidget(QSectionLabel("Standings"))
        standings_tables = StandingsTablesSection(tables_section=self)
        vbox.addWidget(standings_tables)

        # Results Section
        #vbox.addWidget(QSectionLabel("Results"))

        # Fixtures Section
        #vbox.addWidget(QSectionLabel("Fixtures"))

        # spacer
        vbox.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))

    def refresh_data(self, data=None):
        """Function to refresh data from JSON"""
        pass




