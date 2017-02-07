"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow import tools
from clientwindow.tools import QSectionLabel, QHeadingLabel, TemplateRow

class ScoreWidget(QtGui.QWidget):
    """Widget for Lineup graphics"""

    def __init__(self, main, parent=None, data=None):
        """init function fro NameWidget"""
        super(ScoreWidget, self).__init__(parent)
        self.title = "Scores"
        self.main = main
        self.comms = main.comms
        self.init_ui(data)

    def init_ui(self, data=None):
        """ sets base content of widget """

        # get data if required
        if not data:
            data = tools.get_json()

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        # Data
        vbox.addWidget(QSectionLabel("Data"))
        self.data_section = DataSection(data=data)
        vbox.addWidget(self.data_section)

        # Templates
        vbox.addWidget(QSectionLabel("Templates"))
        self.tempaltes_section = TemplatesSection(settings=self.main.settings, main=self.main)
        vbox.addWidget(self.tempaltes_section)

        vbox.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))

    def refresh_data(self, data=None):
        """Function to refresh data from JSON"""
        if not data:
            data = tools.get_json()

        self.data_section.refresh_data(data)
        self.tempaltes_section.refresh_data(settings=self.main.settings)
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

        # score
        grid.addWidget(QHeadingLabel("Score"), 0, 0)
        self.scores = [QtGui.QLabel(score['score']) for score in data['scores']]
        for num, score in enumerate(self.scores):
            grid.addWidget(score, 0, num + 1)

    def refresh_data(self, data):
        """Function to update data"""
        for num, score in enumerate(self.scores):
            score.setText(data['scores'][num]['score'])


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

        for template in settings['templates']['score']:
            templates_vbox.addWidget(TemplateRow(template_data=template, main=self.main))

    def refresh_data(self, settings):
        """Function to refresh templates data"""

        self.vbox.removeWidget(self.templates_container)
        self.templates_container.deleteLater()

        self.templates_container = QtGui.QWidget()
        templates_vbox = QtGui.QVBoxLayout()
        self.templates_container.setLayout(templates_vbox)
        self.vbox.addWidget(self.templates_container)

        for template in settings['templates']['score']:
            templates_vbox.addWidget(TemplateRow(template_data=template, main=self.main))

