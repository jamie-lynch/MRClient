"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui
from clientwindow import tools
from clientwindow.tools import QHeadingOne


class ProductionWidget(QtGui.QWidget):
    """Widget for University name graphics"""

    def __init__(self, main, parent=None, data=None):
        """init function fro NameWidget"""

        # call the parent __init__ function
        super(ProductionWidget, self).__init__(parent)

        # set the tab title
        self.title = "Production"

        # set values
        self.main = main
        self.settings = main.settings
        self.comms = main.comms

        # build the UI elements
        self.init_ui()

    def init_ui(self):
        """ sets base content of widget """

        # create and set layout
        hbox = QtGui.QHBoxLayout()
        self.setLayout(hbox)

        # create vbox to go in scroll
        self.vbox = QtGui.QVBoxLayout()

        # create scroll area
        scroll = QtGui.QScrollArea()
        scroll_widget = QtGui.QWidget()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)

        # add a graphics dictionary
        self.graphics = {}

        # add the three graphics sections
        self.sections = []
        for num, section in enumerate(['strapleft', 'centrescore', 'topscore']):
            self.graphics[section] = []
            self.sections.append(GFXSection(main=self.main, production=self, template=section))
            self.vbox.addWidget(self.sections[num])

        # add a spacer at the bottom
        self.vbox.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))

        # set the scroll widget to have a layout in it
        scroll_widget.setLayout(self.vbox)
        hbox.addWidget(scroll)

    def get_local_data(self):
        """Function to collect all local data"""

        """
        self.graphicss = {}

        self.graphicss['straps'] = []
        for strap in self.names:
            temp = {}
            temp['StrapUpper'] = strap.name_edit.text()
            temp['StrapLower'] = strap.label.text()
            self.graphicss['straps'].append(temp)

        self.graphicss['centrescore'] = []
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
        """


class GFXSection(QtGui.QWidget):
    """Class holding sections of graphics"""

    def __init__(self, main, production, template, parent=None):
        """Function to initialise ComingUpSection"""

        # call the parent __init__ function
        super(GFXSection, self).__init__(parent)

        # set values for convenience
        self.main = main
        self.production = production
        self.comms = main.comms
        self.template = template

        # create and set layout
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # add a heading
        grid.addWidget(QHeadingOne(self.main.settings['templates'][template]['name']), 0, 0)

        # add the Add Row button
        add_row_button = QtGui.QPushButton("Add Row")
        add_row_button.clicked.connect(self.add_row)
        grid.addWidget(add_row_button, 0, 1)

        # make a place to add templates too
        template_widget = QtGui.QWidget()
        self.template_vbox = QtGui.QVBoxLayout()
        template_widget.setLayout(self.template_vbox)
        grid.addWidget(template_widget, 1, 0, 1, 2)

        # add all of the items from last time the software was running
        for item in self.main.data[template]:
            self.add_row(item)

    def add_row(self, data=None):
        """Function to add new row to coming up section"""

        # create a new template row
        new = TemplateRow(main=self.main, production=self.production,
                          gfx_section=self, data=data, template=self.template)

        # add to templates vbox
        self.template_vbox.addWidget(new)

        # store the graphic item for reference
        self.production.graphics[self.template].append(new)

        # save the local data
        tools.store_local_data(self.main)

    def remove_widget(self, widget):
        """Function to remove data row"""

        # remove the widget from the display
        self.template_vbox.removeWidget(widget)

        # remove the widget from the reference dictionary
        self.production.graphics[self.template].remove(widget)

        # delete the widget
        widget.deleteLater()

        # save the local data in case it all shits the bed
        tools.store_local_data(self.main)


class TemplateRow(QtGui.QWidget):
    """Class holding data for one production graphic"""

    def __init__(self, main, production, gfx_section, template, data, parent=None):
        """Function to initialise class"""

        # call the parent __init__ function
        super(TemplateRow, self).__init__(parent)

        # set values for convenience
        self.main = main
        self.production = production
        self.gfx_section = gfx_section
        self.comms = main.comms
        self.template = template

        # create tuple to keep reference to channel and layer when graphics fired
        self.fire_channel_and_layer = None, None

    def initUI(self):
        """Function to create UI elements"""

        # create and set layout
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # add edits for parameters
        parameters = {key: 0 for key in self.main.settings['templates'][self.template]['parameters']}

        for num, key in enumerate(parameters.keys()):

            # for even numbers
            if num % 2:
                grid.addWidget(QtGui.QLabel(key), num//2, 0)
                parameters[key] = QtGui.QLineEdit()
                grid.addWidget(parameters[key], num//2, 1)
            else:
                grid.addWidget(QtGui.QLabel(key), num//2, 2)
                parameters[key] = QtGui.QLineEdit()
                grid.addWidget(parameters[key], num // 2, 1)

        # add channel and layer edits
        grid.addWidget(QtGui.QLabel('Channel'), 0, 4)
        grid.addWidget(QtGui.QLabel('Layer'), 1, 4)
        self.channel_edit = QtGui.QLineEdit()
        self.layer_edit = QtGui.QLineEdit()
        grid.addWidget(self.channel_edit, 0, 5)
        grid.addWidget(self.layer_edit, 1, 5)

        # add the control buttons
        self.fire_button = QtGui.QPushButton("Fire")
        self.fire_status = "Fire"
        self.fire_button.clicked.connect(self.fire_graphic)
        grid.addWidget(self.fire_button, 0, 6)

        self.update_button = QtGui.QPushButton("Update")
        self.update_button.clicked.connect(self.update_graphic)
        grid.addWidget(self.update_button, 0, 7)

        self.add = QtGui.QPushButton("Add")
        self.add.clicked.connect(self.add_graphic)
        grid.addWidget(self.add, 1, 6)

        self.remove_button = QtGui.QPushButton("Delete")
        self.remove_button.clicked.connect(lambda: self.gfx_section.remove_widget(self))
        grid.addWidget(self.remove_button, 1, 7)

        self.fire_buttons = [self.fire_button]
        self.set_enabled_disabled()

    def update_graphic(self):
        """Function to update graphic"""
        response = self.main.comms.template(
            name=self.main.settings['templates'][self.template]['filename'],
            channel=self.fire_channel_and_layer[0],
            layer=self.fire_channel_and_layer[1],
            parameters=''
        )
        print(response)

    def fire_graphic(self):
        """Function to fire graphic"""

        if self.fire_status == 'Fire':
            response = self.main.comms.template(
                name=self.main.settings['templates'][self.template]['filename'],
                channel=self.channel_edit.text(),
                layer=self.layer_edit.text(),
                parameters=''
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Stop'
                self.fire_button.setText('Stop')
                self.fire_channel_and_layer = self.fire_channel_and_layer[0], self.fire_channel_and_layer[1]

        else:
            response = self.main.comms.stop_template(
                channel=self.fire_channel_and_layer[0],
                layer=self.fire_channel_and_layer[1]
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Fire'
                self.fire_button.setText('Fire')

    def add_graphic(self):
        """Function to add graphic to rundown"""

        # create a settings dictionary to allow it to be added
        settings = {}
        settings['channel'] = self.channel_edit.text()
        settings['layer'] = self.layer_edit.text()
        settings['filename'] = self.main.settings['templates'][self.template]['filename']
        settings['name'] = ''
        settings['type'] = "graphic"
        parameters = ''

        # add to rundown
        self.main.rundown.add_row(settings=settings, parameters=parameters)

    def set_enabled_disabled(self):
        """Function to set fire buttons as enabled or disabled"""
        if self.main.comms.casparcg:
            for button in self.fire_buttons:
                button.setEnabled(True)
        else:
            for button in self.fire_buttons:
                button.setDisabled(True)

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





