"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow import tools
from clientwindow.tools import QSectionLabel, QHeadingLabel, TemplateRow

class NameWidget(QtGui.QWidget):
    """Widget for University name graphics"""
    
    def __init__(self, main, parent=None, data=None):
        """init function fro NameWidget"""
        super(NameWidget, self).__init__(parent)
        self.title = "Names"
        self.main = main
        self.comms = main.comms
        self.init_ui(data)
        
    def init_ui(self, data):
        """ sets base content of widget """

        # get data if required
        if not data:
            data = tools.get_json()

        vbox = QtGui.QGridLayout()
        self.setLayout(vbox)

        # Data Section
        vbox.addWidget(QSectionLabel("Data"))
        self.data_section = DataSection(data=data)
        vbox.addWidget(self.data_section)

        # Templates Section
        vbox.addWidget(QSectionLabel("Templates"))
        self.templates_section = TemplatesSection(settings=self.main.settings, main=self.main)
        vbox.addWidget(self.templates_section)

        # spacer
        vbox.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))

    def refresh_data(self, data=None):
        """Function to refresh data from JSON"""

        # get data if required
        if not data:
            data = tools.get_json()

        self.data_section.refresh_data(data)
        self.templates_section.refresh_data(settings=self.main.settings)
        self.update()


class DataSection(QtGui.QWidget):
    """Class which hold the data parts of the names tab"""

    def __init__(self, data=None, parent=None):
        """Function to initialise DataSection class"""
        super(DataSection, self).__init__(parent)
        self.init_ui(data)

    def init_ui(self, data):
        """Function to build DataSection class"""

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # name
        grid.addWidget(QHeadingLabel("University Name"), 0, 0)
        self.names = [QtGui.QLabel(data['teams'][n]['name']) for n in range(len(data['teams']))]
        for num, name in enumerate(self.names):
            grid.addWidget(name, 0, num + 1)

        # shortnames
        grid.addWidget(QHeadingLabel("Shortname"), 1, 0)
        self.shortnames = [QtGui.QLabel(data['teams'][n]['shortname']) for n in range(len(data['teams']))]
        for num, shortname in enumerate(self.shortnames):
            grid.addWidget(shortname, 1, num + 1)

        # colour
        grid.addWidget(QHeadingLabel("Colour"), 2, 0)
        self.colours = [QtGui.QLabel(data['teams'][n]['colour']) for n in range(len(data['teams']))]
        for num, colour in enumerate(self.colours):
            grid.addWidget(colour, 2, num + 1)

    def refresh_data(self, data):
        """Function to update data"""
        for num in range(len(self.names)):
            self.names[num].setText(data['teams'][num]['name'])
            self.shortnames[num].setText(data['teams'][num]['shortname'])
            self.colours[num].setText(data['teams'][num]['colour'])

class TemplatesSection(QtGui.QWidget):
    """Class which hold the data parts of the names tab"""

    def __init__(self, settings, main, parent=None):
        """Function to initialise DataSection class"""
        super(TemplatesSection, self).__init__(parent)
        self.main = main
        self.init_ui(settings)

    def init_ui(self, settings):
        """Function to build DataSection class"""

        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)

        self.templates_container = QtGui.QWidget()
        templates_vbox = QtGui.QVBoxLayout()
        self.templates_container.setLayout(templates_vbox)
        self.vbox.addWidget(self.templates_container)

        for template in settings['templates']['names']:
            templates_vbox.addWidget(TemplateRow(template_data=template, main=self.main))

    def refresh_data(self, settings):
        """Function to refresh templates data"""

        self.vbox.removeWidget(self.templates_container)
        self.templates_container.deleteLater()

        self.templates_container = QtGui.QWidget()
        templates_vbox = QtGui.QVBoxLayout()
        self.templates_container.setLayout(templates_vbox)
        self.vbox.addWidget(self.templates_container)

        for template in settings['templates']['names']:
            templates_vbox.addWidget(TemplateRow(template_data=template, main=self.main))
