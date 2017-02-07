"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui
from clientwindow import tools
from clientwindow.tools import QSectionLabel, QHeadingLabel

class ProductionWidget(QtGui.QWidget):
    """Widget for University name graphics"""

    def __init__(self, main, parent=None, data=None):
        """init function fro NameWidget"""
        super(ProductionWidget, self).__init__(parent)
        self.title = "Production"
        self.main = main
        self.settings = main.settings
        self.comms = main.comms
        self.init_ui(data)

    def init_ui(self, data):
        """ sets base content of widget """

        # get data if required
        if not data:
            data = tools.get_json()
        self.data = data

        hbox = QtGui.QHBoxLayout()
        self.setLayout(hbox)

        self.vbox = QtGui.QVBoxLayout()

        scroll = QtGui.QScrollArea()
        scroll_widget = QtGui.QWidget()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)

        self.add_strap_section()

        self.centrescore_section = CentreScoreSection(production_widget=self)
        self.vbox.addWidget(self.centrescore_section)
        self.topscore_section = TopScoreSection(production_widget=self)
        self.vbox.addWidget(self.topscore_section)

        self.vbox.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))

        scroll_widget.setLayout(self.vbox)
        hbox.addWidget(scroll)

    def add_strap_section(self):
        """Function to create strap section"""
        self.name_vbox = QtGui.QVBoxLayout()

        hbox = QtGui.QHBoxLayout()

        # add headings
        hbox.addWidget(QSectionLabel("Lower Third Straps"))

        add = QtGui.QPushButton("Add Row")
        add.clicked.connect(self.add_strap_row)
        hbox.addWidget(add)
        self.vbox.addLayout(hbox)

        self.names = []
        for item in self.data['straps']:
            row = NameDataRow(production_widget=self, settings=self.settings, data=item)
            self.names.append(row)
            self.name_vbox.addWidget(row)

        self.vbox.addLayout(self.name_vbox)

    def add_strap_row(self, data=None):
        """Function to add data row"""
        new = NameDataRow(production_widget=self, settings=self.settings, data=data)
        self.names.append(new)
        self.name_vbox.addWidget(new)
        tools.store_local_data(self.main)

    def remove_strap_row(self, widget):
        """Function to remove data row"""
        self.name_vbox.removeWidget(widget)
        widget.deleteLater()
        self.names.remove(widget)
        tools.store_local_data(self.main)

    def refresh_data(self, data=None):
        """Function to refresh data"""
        pass

    def get_local_data(self):
        """Function to collect all local data"""
        self.graphics = {}

        self.graphics['straps'] = []
        for strap in self.names:
            temp = {}
            temp['StrapUpper'] = strap.name_edit.text()
            temp['StrapLower'] = strap.label.text()
            self.graphics['straps'].append(temp)

        self.graphics['centrescore'] = []
        for score in self.centrescore_section.centre_scores:
            temp = {}
            temp['team_left'] = score.team1_edit.text()
            temp['team_right'] = score.team2_edit.text()
            temp['score'] = score.score_edit.text()
            if score.infobar_edit.text():
                temp['show_infobar'] = 1
                temp['Infobar_info_text'] = score.infobar_edit.text()
            else:
                temp['show_infobar'] = 0
                temp['Infobar_info_text'] = ""
            self.graphics['centrescore'].append(temp)

        self.graphics['topscore'] = []
        for score in self.topscore_section.top_scores:
            temp = {}
            temp['topleft_team1'] = score.team1_edit.text()
            temp['topleft_team2'] = score.team2_edit.text()
            temp['topleft_score'] = score.score_edit.text()
            temp['topleft_team1_colour'] = score.colour1_edit.text()
            temp['topleft_team2_colour'] = score.colour2_edit.text()
            self.graphics['topscore'].append(temp)

        return self.graphics

class NameDataRow(QtGui.QWidget):
    """Function which holds data and buttons for names"""
    isrundown = False

    def __init__(self, production_widget, settings, data):
        """Function to initialise class"""

        super(NameDataRow, self).__init__()

        self.production_widget = production_widget
        self.settings = settings
        self.main = self.production_widget.main
        self.main.connected.signal.connect(self.set_enabled_disabled)
        self.data = data

        hbox = QtGui.QHBoxLayout()
        self.setLayout(hbox)

        hbox.addWidget(QtGui.QLabel("Name:"))
        self.name_edit = QtGui.QLineEdit()
        if self.data:
            if self.data['StrapUpper'] == "":
                self.name_edit.setPlaceholderText("Insert Name...")
            else:
                self.name_edit.setText(self.data['StrapUpper'])
        else:
            self.name_edit.setPlaceholderText("Insert Name...")
        hbox.addWidget(self.name_edit)
        self.name_edit.editingFinished.connect(lambda: tools.store_local_data(self.main))

        hbox.addWidget(QtGui.QLabel("Title:"))
        self.label = QtGui.QLineEdit()
        if self.data:
            if self.data['StrapLower'] == "":
                self.label.setPlaceholderText("Insert Title...")
            else:
                self.label.setText(self.data['StrapLower'])
        else:
            self.label.setPlaceholderText("Insert Title...")
        hbox.addWidget(self.label)
        self.label.editingFinished.connect(lambda: tools.store_local_data(self.main))

        self.left_button = QtGui.QPushButton("Fire")
        self.left_status = "Fire"
        self.left_button.clicked.connect(self.fire_left)
        hbox.addWidget(self.left_button)

        self.add_button_fixed_left = QtGui.QPushButton("Add")
        self.add_button_fixed_left.clicked.connect(lambda: self.add_to_rundown(fixed=True, side="left"))
        hbox.addWidget(self.add_button_fixed_left)
        """
        self.right_button = QtGui.QPushButton("Fire Right")
        self.right_status = "Fire"
        self.right_button.clicked.connect(self.fire_right)
        hbox.addWidget(self.right_button)

        self.add_button_fixed = QtGui.QPushButton("Add")
        self.add_button_fixed.clicked.connect(lambda: self.add_to_rundown(side="right", fixed=True))
        hbox.addWidget(self.add_button_fixed)
        """
        remove = QtGui.QPushButton("Remove")
        remove.clicked.connect(self.remove_row)
        hbox.addWidget(remove)

        self.fire_buttons = [self.left_button]
        self.set_enabled_disabled()

    def set_enabled_disabled(self):
        """Function to set fire buttons as enabled or disabled"""
        if self.main.comms.casparcg:
            for button in self.fire_buttons:
                button.setEnabled(True)
        else:
            for button in self.fire_buttons:
                button.setDisabled(True)

    def add_to_rundown(self, side, fixed=False):
        """Function to add item to rundown"""
        self.get_template_data(side=side)
        settings = {}
        settings['channel'] = self.template_data['channel']
        settings['layer'] = self.template_data['layer']
        settings['filename'] = self.template_data['filename']
        settings['name'] = self.name_edit.text()
        settings['type'] = "graphic"

        if fixed:
            parameters = self.get_parameters()
        else:
            parameters = None

        self.isrundown = True
        self.main.rundown.add_row(settings=settings, button_widget=None, parameters=parameters)

    def fire_left(self):
        """Function to fire left graphic"""
        self.get_template_data("left")
        if self.left_status == 'Fire':
            response = self.main.comms.template(
                name=self.template_data['filename'],
                channel=self.template_data['channel'],
                layer=self.template_data['layer'],
                parameters=self.template_data['parameters']
            )

            if 'OK' in response:
                self.left_status = 'Stop'
                self.left_button.setText('Stop')

        else:
            response = self.main.comms.stop_template(
                channel=self.template_data['channel'],
                layer=self.template_data['layer']
            )
            print(response)

            if 'OK' in response:
                self.left_status = 'Fire'
                self.left_button.setText('Fire')

    def fire_right(self):
        """Function to fire right graphic"""
        self.get_template_data()
        if self.right_status == 'Fire':
            response = self.main.comms.template(
                name=self.template_data['filename'] + "Right",
                channel=self.template_data['channel'],
                layer=self.template_data['layer'],
                parameters=self.template_data['parameters']
            )
            print(response)

            if 'OK' in response:
                self.right_status = 'Stop'
                self.right_button.setText('Stop')

        else:
            response = self.main.comms.stop_template(
                channel=self.template_data['channel'],
                layer=self.template_data['layer']
            )
            print(response)

            if 'OK' in response:
                self.right_status = 'Fire'
                self.right_button.setText('Fire')

    def remove_row(self):
        """Function to remove row"""
        self.production_widget.remove_strap_row(self)

    def get_template_data(self, side):
        """Function to get template data"""

        if side == "left":
            self.template_data = self.settings['templates']['standard']['strap_name_left']
        else:
            self.template_data = self.settings['templates']['standard']['strap_name_right']

        parameters = {"StrapUpper": self.name_edit.text(), "StrapLower": self.label.text()}
        parameters = ['{}={}'.format(key, val) for key, val in parameters.items()]
        self.template_data['parameters'] = '|'.join(parameters)

    def get_parameters(self):
        """Function to get parameters"""
        parameters = {"StrapUpper": self.name_edit.text(), "StrapLower": self.label.text()}
        parameters = ['{}={}'.format(key, val) for key, val in parameters.items()]
        parameters = '|'.join(parameters)
        return parameters

class ComingUpSection(QtGui.QWidget):
    """Class which builds the coming up templates section"""
    coming_up = []
    def __init__(self, production_widget, parent=None):
        """Function to initialise ComingUpSection"""
        super(ComingUpSection, self).__init__(parent)

        self.production_widget = production_widget
        self.main = self.production_widget.main

        self.comms = self.production_widget.comms

        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        grid.addWidget(QSectionLabel("Coming Up"), 0, 0)

        add_row_button = QtGui.QPushButton("Add Row")
        add_row_button.clicked.connect(self.add_row)
        grid.addWidget(add_row_button, 0, 1)

        template_widget = QtGui.QWidget()
        self.template_vbox = QtGui.QVBoxLayout()
        template_widget.setLayout(self.template_vbox)
        grid.addWidget(template_widget, 1, 0, 1, 2)

        for item in self.main.data['comingup']:
            self.add_row(item)

    def add_row(self, data=None):
        """Function to add new row to coming up section"""
        new = ComingUpRow(comingup_widget=self, settings=self.main.settings['templates']['standard']['coming_up'], data=data)
        self.coming_up.append(new)
        self.template_vbox.addWidget(new)
        tools.store_local_data(self.main)

    def remove_widget(self, widget):
        """Function to remove data row"""
        self.template_vbox.removeWidget(widget)
        self.coming_up.remove(widget)
        widget.deleteLater()
        tools.store_local_data(self.main)

class ComingUpRow(QtGui.QWidget):
    """Class holding data for one coming up row graphic"""

    def __init__(self, comingup_widget, settings, data, parent=None):
        """Function to initialise ComingUpRow"""
        super(ComingUpRow, self).__init__(parent)

        self.comingup_widget = comingup_widget
        self.production_widget = comingup_widget.production_widget
        self.main = self.production_widget.main
        self.main.connected.signal.connect(self.set_enabled_disabled)
        self.comms = self.production_widget.comms
        self.data = data
        self.settings = settings

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        grid.addWidget(QtGui.QLabel("Event"), 0, 0)
        self.event_edit = QtGui.QLineEdit()
        if self.data:
            self.event_edit.setText(self.data['name'])
        grid.addWidget(self.event_edit, 0, 1)

        self.fire_button = QtGui.QPushButton("Fire")
        self.fire_status = "Fire"
        self.fire_button.clicked.connect(self.fire_graphic)
        grid.addWidget(self.fire_button, 0, 2)

        self.add = QtGui.QPushButton("Add")
        self.add.clicked.connect(self.add_graphic)
        grid.addWidget(self.add, 0, 3)

        self.remove_button = QtGui.QPushButton("Remove")
        self.remove_button.clicked.connect(lambda: self.comingup_widget.remove_widget(self))
        grid.addWidget(self.remove_button, 0, 4)

        self.fire_buttons = [self.fire_button]
        self.set_enabled_disabled()

    def fire_graphic(self):
        """Function to fire graphic"""

        if self.fire_status == 'Fire':
            response = self.main.comms.template(
                name=self.settings['filename'],
                channel=self.settings['channel'],
                layer=self.settings['layer'],
                parameters="name={}".format(self.event_edit.text())
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Stop'
                self.fire_button.setText('Stop')

        else:
            response = self.main.comms.stop_template(
                channel=self.settings['channel'],
                layer=self.settings['layer']
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Fire'
                self.fire_button.setText('Fire')

    def add_graphic(self):
        """Function to add graphic to rundown"""
        settings = {}
        settings['channel'] = self.settings['channel']
        settings['layer'] = self.settings['layer']
        settings['filename'] = self.settings['filename']
        settings['name'] = self.event_edit.text()
        settings['type'] = "graphic"
        parameters = "name={}".format(self.event_edit.text())
        self.main.rundown.add_row(settings=settings, button_widget=None, parameters=parameters)

    def set_enabled_disabled(self):
        """Function to set fire buttons as enabled or disabled"""
        if self.main.comms.casparcg:
            for button in self.fire_buttons:
                button.setEnabled(True)
        else:
            for button in self.fire_buttons:
                button.setDisabled(True)

class LogoSection(QtGui.QWidget):
    """Class which builds the coming up templates section"""
    coming_up = []
    def __init__(self, production_widget, parent=None):
        """Function to initialise ComingUpSection"""
        super(LogoSection, self).__init__(parent)

        self.production_widget = production_widget
        self.main = self.production_widget.main

        self.comms = self.production_widget.comms

        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        grid.addWidget(QSectionLabel("Logo"), 0, 0)

        template = LogoRow(logo_widget=self, settings=self.main.settings['templates']['standard']['logo'], data=None)
        grid.addWidget(template, 1, 0, 1, 2)

class LogoRow(QtGui.QWidget):
    """Class holding data for one coming up row graphic"""

    def __init__(self, logo_widget, settings, data, parent=None):
        """Function to initialise ComingUpRow"""
        super(LogoRow, self).__init__(parent)

        self.logo_widget = logo_widget
        self.production_widget = logo_widget.production_widget
        self.main = self.production_widget.main
        self.main.connected.signal.connect(self.set_enabled_disabled)
        self.comms = self.production_widget.comms
        self.data = data
        self.settings = settings

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        grid.addWidget(QtGui.QLabel("Logo"), 0, 0)

        self.fire_button = QtGui.QPushButton("Fire")
        self.fire_status = "Fire"
        self.fire_button.clicked.connect(self.fire_graphic)
        grid.addWidget(self.fire_button, 0, 2)

        self.add = QtGui.QPushButton("Add")
        self.add.clicked.connect(self.add_graphic)
        grid.addWidget(self.add, 0, 3)

        self.fire_buttons = [self.fire_button]
        self.set_enabled_disabled()

    def fire_graphic(self):
        """Function to fire graphic"""

        if self.fire_status == 'Fire':
            response = self.main.comms.template(
                name=self.settings['filename'],
                channel=self.settings['channel'],
                layer=self.settings['layer'],
                parameters=""
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Stop'
                self.fire_button.setText('Stop')

        else:
            response = self.main.comms.stop_template(
                channel=self.settings['channel'],
                layer=self.settings['layer']
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Fire'
                self.fire_button.setText('Fire')

    def add_graphic(self):
        """Function to add graphic to rundown"""
        settings = {}
        settings['channel'] = self.settings['channel']
        settings['layer'] = self.settings['layer']
        settings['filename'] = self.settings['filename']
        settings['name'] = self.settings['name']
        settings['type'] = "graphic"
        parameters = ""
        self.main.rundown.add_row(settings=settings, button_widget=None, parameters=parameters)

    def set_enabled_disabled(self):
        """Function to set fire buttons as enabled or disabled"""
        if self.main.comms.casparcg:
            for button in self.fire_buttons:
                button.setEnabled(True)
        else:
            for button in self.fire_buttons:
                button.setDisabled(True)

class CreditsSection(QtGui.QWidget):
    """Class which builds the coming up templates section"""

    def __init__(self, production_widget, parent=None):
        """Function to initialise ComingUpSection"""
        super(CreditsSection, self).__init__(parent)

        self.production_widget = production_widget
        self.main = self.production_widget.main

        self.comms = self.production_widget.comms

        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        grid.addWidget(QSectionLabel("Credits"), 0, 0)

        template = CreditsRow(credits_widget=self, settings=self.main.settings['templates']['standard']['credits'], data=None)
        grid.addWidget(template, 1, 0, 1, 2)

class CreditsRow(QtGui.QWidget):
    """Class holding data for one coming up row graphic"""

    def __init__(self, credits_widget, settings, data, parent=None):
        """Function to initialise ComingUpRow"""
        super(CreditsRow, self).__init__(parent)

        self.credits_widget = credits_widget
        self.production_widget = credits_widget.production_widget
        self.main = self.production_widget.main
        self.main.connected.signal.connect(self.set_enabled_disabled)
        self.comms = self.production_widget.comms
        self.data = data
        self.settings = settings

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        grid.addWidget(QtGui.QLabel("Credits"), 0, 0)

        self.fire_button = QtGui.QPushButton("Fire")
        self.fire_status = "Fire"
        self.fire_button.clicked.connect(self.fire_graphic)
        grid.addWidget(self.fire_button, 0, 2)

        self.add = QtGui.QPushButton("Add")
        self.add.clicked.connect(self.add_graphic)
        grid.addWidget(self.add, 0, 3)

        self.fire_buttons = [self.fire_button]
        self.set_enabled_disabled()

    def fire_graphic(self):
        """Function to fire graphic"""

        if self.fire_status == 'Fire':
            response = self.main.comms.template(
                name=self.settings['filename'],
                channel=self.settings['channel'],
                layer=self.settings['layer'],
                parameters=""
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Stop'
                self.fire_button.setText('Stop')

        else:
            response = self.main.comms.stop_template(
                channel=self.settings['channel'],
                layer=self.settings['layer']
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Fire'
                self.fire_button.setText('Fire')

    def add_graphic(self):
        """Function to add graphic to rundown"""
        settings = {}
        settings['channel'] = self.settings['channel']
        settings['layer'] = self.settings['layer']
        settings['filename'] = self.settings['filename']
        settings['name'] = self.settings['name']
        settings['type'] = "graphic"
        parameters = ""
        self.main.rundown.add_row(settings=settings, button_widget=None, parameters=parameters)

    def set_enabled_disabled(self):
        """Function to set fire buttons as enabled or disabled"""
        if self.main.comms.casparcg:
            for button in self.fire_buttons:
                button.setEnabled(True)
        else:
            for button in self.fire_buttons:
                button.setDisabled(True)

class CentreScoreSection(QtGui.QWidget):
    """Class which builds the coming up templates section"""
    centre_scores = []
    def __init__(self, production_widget, parent=None):
        """Function to initialise ComingUpSection"""
        super(CentreScoreSection, self).__init__(parent)

        self.production_widget = production_widget
        self.main = self.production_widget.main

        self.comms = self.production_widget.comms

        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        grid.addWidget(QSectionLabel("Centre Score"), 0, 0)

        add_row_button = QtGui.QPushButton("Add Row")
        add_row_button.clicked.connect(self.add_row)
        grid.addWidget(add_row_button, 0, 1)

        template_widget = QtGui.QWidget()
        self.template_vbox = QtGui.QVBoxLayout()
        template_widget.setLayout(self.template_vbox)
        grid.addWidget(template_widget, 1, 0, 1, 2)

        for item in self.main.data['centrescore']:
            self.add_row(item)

    def add_row(self, data=None):
        """Function to add new row to coming up section"""
        new = CentreScoreRow(centrescore_widget=self, settings=self.main.settings['templates']['standard']['centrescore'], data=data)
        self.centre_scores.append(new)
        self.template_vbox.addWidget(new)
        tools.store_local_data(self.main)

    def remove_widget(self, widget):
        """Function to remove data row"""
        self.template_vbox.removeWidget(widget)
        self.centre_scores.remove(widget)
        widget.deleteLater()
        tools.store_local_data(self.main)

class CentreScoreRow(QtGui.QWidget):
    """Class holding data for one coming up row graphic"""

    def __init__(self, centrescore_widget, settings, data, parent=None):
        """Function to initialise ComingUpRow"""
        super(CentreScoreRow, self).__init__(parent)

        self.centrescore_widget = centrescore_widget
        self.production_widget = centrescore_widget.production_widget
        self.main = self.production_widget.main
        self.main.connected.signal.connect(self.set_enabled_disabled)
        self.comms = self.production_widget.comms
        self.data = data
        self.settings = settings

        grid = QtGui.QGridLayout()
        self.setLayout(grid)


        grid.addWidget(QtGui.QLabel("Team 1:"), 0, 0)
        self.team1_edit = QtGui.QLineEdit()
        if self.data:
            self.team1_edit.setText(self.data['team_left'])
        grid.addWidget(self.team1_edit, 0, 1)

        grid.addWidget(QtGui.QLabel("Team 2:"), 1, 0)
        self.team2_edit = QtGui.QLineEdit()
        if self.data:
            self.team2_edit.setText(self.data['team_right'])
        grid.addWidget(self.team2_edit, 1, 1)

        grid.addWidget(QtGui.QLabel("Score:"), 0, 2)
        self.score_edit = QtGui.QLineEdit()
        if self.data:
            self.score_edit.setText(self.data['score'])
        grid.addWidget(self.score_edit, 0, 3)

        grid.addWidget(QtGui.QLabel("Infobar:"), 1, 2)
        self.infobar_edit = QtGui.QLineEdit()
        if self.data and self.data['show_infobar']:
            self.infobar_edit.setText(self.data['Infobar_info_text'])
        grid.addWidget(self.infobar_edit, 1, 3)

        self.fire_button = QtGui.QPushButton("Fire")
        self.fire_status = "Fire"
        self.fire_button.clicked.connect(self.fire_graphic)
        grid.addWidget(self.fire_button, 0, 4)

        self.add = QtGui.QPushButton("Add")
        self.add.clicked.connect(self.add_graphic)
        grid.addWidget(self.add, 1, 4)

        self.remove_button = QtGui.QPushButton("Remove")
        self.remove_button.clicked.connect(lambda: self.centrescore_widget.remove_widget(self))
        grid.addWidget(self.remove_button, 0, 5)

        self.update_button = QtGui.QPushButton("Update")
        self.update_button.clicked.connect(self.update_graphic)
        grid.addWidget(self.update_button, 1, 5)

        self.fire_buttons = [self.fire_button]
        self.set_enabled_disabled()

    def get_parameters(self):
        """Function to get the parameters"""
        parameters = {}
        parameters['team_left'] = self.team1_edit.text()
        parameters['team_right'] = self.team2_edit.text()
        parameters['score'] = self.score_edit.text()
        if self.infobar_edit.text() and self.infobar_edit.text() != "":
            parameters['show_infobar'] = 1
            parameters['Infobar_info_text'] = self.infobar_edit.text()
        else:
            parameters['show_infobar'] = 0
            parameters['Infobar_info_text'] = ""

        parameters = ['{}={}'.format(key, val) for key, val in parameters.items()]
        parameters = '|'.join(parameters)
        return parameters

    def update_graphic(self):
        """Function to update graphic"""
        response = self.main.comms.template(
            name=self.settings['filename'],
            channel=self.settings['channel'],
            layer=self.settings['layer'],
            parameters=self.get_parameters()
        )
        print(response)

    def fire_graphic(self):
        """Function to fire graphic"""

        if self.fire_status == 'Fire':
            response = self.main.comms.template(
                name=self.settings['filename'],
                channel=self.settings['channel'],
                layer=self.settings['layer'],
                parameters=self.get_parameters()
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Stop'
                self.fire_button.setText('Stop')

        else:
            response = self.main.comms.stop_template(
                channel=self.settings['channel'],
                layer=self.settings['layer']
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Fire'
                self.fire_button.setText('Fire')

    def add_graphic(self):
        """Function to add graphic to rundown"""
        settings = {}
        settings['channel'] = self.settings['channel']
        settings['layer'] = self.settings['layer']
        settings['filename'] = self.settings['filename']
        settings['name'] = self.get_name()
        settings['type'] = "graphic"
        parameters = self.get_parameters()
        self.main.rundown.add_row(settings=settings, button_widget=None, parameters=parameters)

    def set_enabled_disabled(self):
        """Function to set fire buttons as enabled or disabled"""
        if self.main.comms.casparcg:
            for button in self.fire_buttons:
                button.setEnabled(True)
        else:
            for button in self.fire_buttons:
                button.setDisabled(True)

    def get_name(self):
        """Function to build a name for the rundown"""
        parameters = {}
        parameters['team_left'] = self.team1_edit.text()
        parameters['team_right'] = self.team2_edit.text()
        parameters['score'] = self.score_edit.text()
        try:
            return "Cent: {} {} {}".format(parameters['team_left'][0], parameters['score'], parameters['team_right'][0])
        except IndexError:
            return "Centre"

class TopScoreSection(QtGui.QWidget):
    """Class which builds the coming up templates section"""
    top_scores = []

    def __init__(self, production_widget, parent=None):
        """Function to initialise ComingUpSection"""
        super(TopScoreSection, self).__init__(parent)

        self.production_widget = production_widget
        self.main = self.production_widget.main

        self.comms = self.production_widget.comms

        grid = QtGui.QGridLayout()
        self.setLayout(grid)
        grid.addWidget(QSectionLabel("Top Score"), 0, 0)

        add_row_button = QtGui.QPushButton("Add Row")
        add_row_button.clicked.connect(self.add_row)
        grid.addWidget(add_row_button, 0, 1)

        template_widget = QtGui.QWidget()
        self.template_vbox = QtGui.QVBoxLayout()
        template_widget.setLayout(self.template_vbox)
        grid.addWidget(template_widget, 1, 0, 1, 2)

        for item in self.main.data['topscore']:
            self.add_row(item)

    def add_row(self, data=None):
        """Function to add new row to coming up section"""
        new = TopScoreRow(topscore_widget=self,
                             settings=self.main.settings['templates']['standard']['topscore'], data=data)
        self.top_scores.append(new)
        self.template_vbox.addWidget(new)
        tools.store_local_data(self.main)

    def remove_widget(self, widget):
        """Function to remove data row"""
        self.template_vbox.removeWidget(widget)
        self.top_scores.remove(widget)
        widget.deleteLater()
        tools.store_local_data(self.main)

class TopScoreRow(QtGui.QWidget):
    """Class holding data for one coming up row graphic"""

    def __init__(self, topscore_widget, settings, data, parent=None):
        """Function to initialise ComingUpRow"""
        super(TopScoreRow, self).__init__(parent)

        self.topscore_widget = topscore_widget
        self.production_widget = topscore_widget.production_widget
        self.main = self.production_widget.main
        self.main.connected.signal.connect(self.set_enabled_disabled)
        self.comms = self.production_widget.comms
        self.data = data
        self.settings = settings

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        grid.addWidget(QtGui.QLabel("Team 1:"), 0, 0)
        self.team1_edit = QtGui.QLineEdit()
        if self.data:
            self.team1_edit.setText(self.data['topleft_team1'])
        grid.addWidget(self.team1_edit, 0, 1)

        grid.addWidget(QtGui.QLabel("Team 2:"), 1, 0)
        self.team2_edit = QtGui.QLineEdit()
        if self.data:
            self.team2_edit.setText(self.data['topleft_team2'])
        grid.addWidget(self.team2_edit, 1, 1)

        grid.addWidget(QtGui.QLabel("Score:"), 2, 0)
        self.score_edit = QtGui.QLineEdit()
        if self.data:
            self.score_edit.setText(self.data['topleft_score'])
        grid.addWidget(self.score_edit, 2, 1)

        grid.addWidget(QtGui.QLabel("Colour1:"), 0, 2)
        self.colour1_edit = QtGui.QLineEdit()
        if self.data:
            self.colour1_edit.setText(self.data['topleft_team1_colour'])
        grid.addWidget(self.colour1_edit, 0, 3)

        grid.addWidget(QtGui.QLabel("Colour2:"), 1, 2)
        self.colour2_edit = QtGui.QLineEdit()
        if self.data:
            self.colour2_edit.setText(self.data['topleft_team2_colour'])
        grid.addWidget(self.colour2_edit, 1, 3)

        self.fire_button = QtGui.QPushButton("Fire")
        self.fire_status = "Fire"
        self.fire_button.clicked.connect(self.fire_graphic)
        grid.addWidget(self.fire_button, 0, 4)

        self.add = QtGui.QPushButton("Add")
        self.add.clicked.connect(self.add_graphic)
        grid.addWidget(self.add, 1, 4)

        self.remove_button = QtGui.QPushButton("Remove")
        self.remove_button.clicked.connect(lambda: self.topscore_widget.remove_widget(self))
        grid.addWidget(self.remove_button, 0, 5)

        self.update_button = QtGui.QPushButton("Update")
        self.update_button.clicked.connect(self.update_graphic)
        grid.addWidget(self.update_button, 1, 5)

        self.fire_buttons = [self.fire_button]
        self.set_enabled_disabled()

    def get_parameters(self):
        """Function to get the parameters"""
        parameters = {}
        parameters['topleft_team1'] = self.team1_edit.text()
        parameters['topleft_team2'] = self.team2_edit.text()
        parameters['topleft_score'] = self.score_edit.text()
        parameters['team1_colour'] = self.colour1_edit.text()
        parameters['team2_colour'] = self.colour2_edit.text()

        parameters = ['{}={}'.format(key, val) for key, val in parameters.items()]
        parameters = '|'.join(parameters)
        return parameters

    def update_graphic(self):
        """Function to update graphic"""
        response = self.main.comms.template(
            name=self.settings['filename'],
            channel=self.settings['channel'],
            layer=self.settings['layer'],
            parameters=self.get_parameters()
        )
        print(response)

    def fire_graphic(self):
        """Function to fire graphic"""

        if self.fire_status == 'Fire':
            response = self.main.comms.template(
                name=self.settings['filename'],
                channel=self.settings['channel'],
                layer=self.settings['layer'],
                parameters=self.get_parameters()
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Stop'
                self.fire_button.setText('Stop')

        else:
            response = self.main.comms.stop_template(
                channel=self.settings['channel'],
                layer=self.settings['layer']
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Fire'
                self.fire_button.setText('Fire')

    def add_graphic(self):
        """Function to add graphic to rundown"""
        settings = {}
        settings['channel'] = self.settings['channel']
        settings['layer'] = self.settings['layer']
        settings['filename'] = self.settings['filename']
        settings['name'] = self.get_name()
        settings['type'] = "graphic"
        parameters = self.get_parameters()
        self.main.rundown.add_row(settings=settings, button_widget=None, parameters=parameters)

    def set_enabled_disabled(self):
        """Function to set fire buttons as enabled or disabled"""
        if self.main.comms.casparcg:
            for button in self.fire_buttons:
                button.setEnabled(True)
        else:
            for button in self.fire_buttons:
                button.setDisabled(True)

    def get_name(self):
        """Function to build a name for the rundown"""
        parameters = {}
        parameters['team_left'] = self.team1_edit.text()
        parameters['team_right'] = self.team2_edit.text()
        parameters['score'] = self.score_edit.text()
        try:
            return "Top: {} {} {}".format(parameters['team_left'][0], parameters['score'],
                                     parameters['team_right'][0])
        except IndexError:
            return "Top"

