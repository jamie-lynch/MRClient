"""
Match Report CasparCG Client
Version 2.0
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file contains the classes required to build the production tab
"""

from PySide import QtGui, QtCore
from clientwindow import tools
from clientwindow.tools import QHeadingOne


class ProductionWidget(QtGui.QWidget):
    """Widget for University name graphics"""

    def __init__(self, main, parent=None):
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
        self.sections_list = ['strapleft', 'centrescore', 'topscore']
        self.sections = []
        for num, section in enumerate(self.sections_list):
            self.graphics[section] = []
            self.sections.append(GFXSection(main=self.main, production=self, template=section))
            self.vbox.addWidget(self.sections[num])

        # add a spacer at the bottom
        self.vbox.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))

        # set the scroll widget to have a layout in it
        scroll_widget.setLayout(self.vbox)
        hbox.addWidget(scroll)

    def write_to_data(self):
        """Function to convert the graphics dictionary to the data required for a python dictionary"""
        for section in self.sections_list:
            self.main.data[section] = []
            for graphic in self.graphics[section]:
                temp = {
                    'channel': graphic.channel_edit.text(),
                    'layer': graphic.layer_edit.text(),
                    'parameters': {key: val.text() for key, val in graphic.parameters.items()}
                }
                self.main.data[section].append(temp)
        tools.store_data(self.main)


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
            self.add_row(data=item, save=False)

    def add_row(self, data=None, save=True):
        """Function to add new row to coming up section"""

        # create a new template row
        new = TemplateRow(main=self.main, production=self.production,
                          gfx_section=self, data=data, template=self.template)

        # add to templates vbox
        self.template_vbox.addWidget(new)

        # store the graphic item for reference
        self.production.graphics[self.template].append(new)

        # save the local data
        if save:
            self.production.write_to_data()

    def remove_row(self, widget):
        """Function to remove data row"""

        # remove the widget from the display
        self.template_vbox.removeWidget(widget)

        # remove the widget from the reference dictionary
        self.production.graphics[self.template].remove(widget)

        # delete the widget
        widget.deleteLater()

        # save the local data in case it all shits the bed
        self.production.write_to_data()


class TemplateRow(QtGui.QFrame):
    """Class holding data for one production graphic"""

    playing_signal = QtCore.Signal(object)
    stopped_signal = QtCore.Signal(object)

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
        self.data = data

        # connect to the connected signal to un-freeze buttons when caspar is connected
        self.main.connected.signal.connect(self.set_enabled_disabled)

        # create tuple to keep reference to channel and layer when graphics fired
        self.fire_channel_and_layer = None, None

        # create variable to track if playing
        self.playing = False

        # build UI elements
        self.initUI()

        # set border
        self.setFrameStyle(QtGui.QFrame.Box)

    def initUI(self):
        """Function to create UI elements"""

        # create and set layout
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        parameters_grid = QtGui.QGridLayout()
        control_grid = QtGui.QGridLayout()

        grid.addLayout(parameters_grid, 0, 0)
        grid.addLayout(control_grid, 0, 1)

        # add edits for parameters
        self.parameters_list = self.main.settings['templates'][self.template]['parameters']
        self.parameters = {key: 0 for key in self.main.settings['templates'][self.template]['parameters']}

        for num, key in enumerate(self.parameters_list):

            # for even numbers
            if not num % 2:
                heading = tools.QVTLabel(self, key)
                heading.setFixedWidth(120)
                heading.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
                parameters_grid.addWidget(heading, num//2, 0)
                self.parameters[key] = QtGui.QLineEdit()
                self.parameters[key].setFixedWidth(160)
                parameters_grid.addWidget(self.parameters[key], num//2, 1)
            # for odd numbers
            else:
                heading = tools.QVTLabel(self, key)
                heading.setFixedWidth(120)
                heading.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
                parameters_grid.addWidget(heading, num//2, 2)
                self.parameters[key] = QtGui.QLineEdit()
                self.parameters[key].setFixedWidth(160)
                parameters_grid.addWidget(self.parameters[key], num // 2, 3)

            # add the text if data exists
            if self.data:
                self.parameters[key].setText(self.data['parameters'][key])

            # set the data to update if the line edit is changes
            self.parameters[key].editingFinished.connect(self.production.write_to_data)

        # add channel and layer edits
        channel = tools.QVTLabel(self, 'Channel')
        channel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        channel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        control_grid.addWidget(channel, 0, 4)

        layer = tools.QVTLabel(self, 'Layer')
        layer.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        layer.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        control_grid.addWidget(layer, 1, 4)

        self.channel_edit = QtGui.QLineEdit()
        self.channel_edit.setFixedWidth(60)
        if self.data:
            self.channel_edit.setText(self.data['channel'])
        else:
            self.channel_edit.setText(str(self.main.settings['templates'][self.template]['channel']))
        self.channel_edit.editingFinished.connect(self.production.write_to_data)

        self.layer_edit = QtGui.QLineEdit()
        self.layer_edit.setFixedWidth(60)
        if self.data:
            self.layer_edit.setText(self.data['layer'])
        else:
            self.layer_edit.setText(str(self.main.settings['templates'][self.template]['layer']))
        self.layer_edit.editingFinished.connect(self.production.write_to_data)
        control_grid.addWidget(self.channel_edit, 0, 5)
        control_grid.addWidget(self.layer_edit, 1, 5)

        # add the control buttons
        self.fire_button = QtGui.QPushButton("Fire")
        self.fire_status = "Fire"
        self.fire_button.clicked.connect(self.fire_graphic)
        control_grid.addWidget(self.fire_button, 0, 6)

        self.update_button = QtGui.QPushButton("Update")
        self.update_button.clicked.connect(self.update_graphic)
        control_grid.addWidget(self.update_button, 0, 7)

        self.add = QtGui.QPushButton("Add")
        self.add.clicked.connect(self.add_graphic)
        control_grid.addWidget(self.add, 1, 6)

        self.remove_button = QtGui.QPushButton("Delete")
        self.remove_button.clicked.connect(self.remove_row)
        control_grid.addWidget(self.remove_button, 1, 7)

        self.fire_buttons = [self.fire_button, self.update_button]
        self.set_enabled_disabled()

    def remove_row(self):
        """Function to remove row"""
        if self.playing:
            error = QtGui.QErrorMessage()
            error.showMessage("Cannot remove item while playing")
            error.exec_()
            return
        else:
            self.gfx_section.remove_row(widget=self)

    def fire_graphic(self):
        """Function to fire graphic"""

        if self.fire_status == 'Fire':
            response = self.main.comms.template(
                name=self.main.settings['templates'][self.template]['filename'],
                channel=self.channel_edit.text(),
                layer=self.layer_edit.text(),
                parameters=self.get_parameters(),
                playonload=1
            )

            if 'OK' in response:
                self.fire_status = 'Stop'
                self.fire_button.setText('Stop')
                self.fire_channel_and_layer = self.channel_edit.text(), self.layer_edit.text()
                self.playing_signal.emit(self)
                self.playing = True
                self.set_background_colour()

        else:
            response = self.main.comms.stop_template(
                channel=self.fire_channel_and_layer[0],
                layer=self.fire_channel_and_layer[1]
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Fire'
                self.fire_button.setText('Fire')
                self.stopped_signal.emit(self)
                self.playing = False
                self.set_background_colour()

    def update_graphic(self):
        """Function to update graphic"""
        response = self.main.comms.template(
            name=self.main.settings['templates'][self.template]['filename'],
            channel=self.fire_channel_and_layer[0],
            layer=self.fire_channel_and_layer[1],
            parameters=self.get_parameters()
        )
        print(response)

    def add_graphic(self):
        """Function to add graphic to rundown"""

        # create a settings dictionary to allow it to be added
        settings = {
            'channel': self.channel_edit.text(),
            'layer': self.layer_edit.text(),
            'filename': self.main.settings['templates'][self.template]['filename'],
            'name': self.get_name(),
            'type': "graphic",
            'parameters': self.get_parameters(),
            'template': self.template
        }

        # add to rundown
        self.main.rundown.add_row(settings=settings)

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
        parameters = {key: val.text() for key, val in self.parameters.items()}
        parameters = ['{}={}'.format(key, val) for key, val in parameters.items()]
        parameters = '|'.join(parameters)
        return parameters

    def get_name(self):
        """Function to build a name for the rundown"""
        return self.parameters[self.main.settings['templates'][self.template]['rundownname']].text()

    def set_background_colour(self):
        """Function to set the correct background colour"""
        if self.playing:
            self.setStyleSheet('TemplateRow{background-color: #009600}')
        else:
            self.setStyleSheet('TemplateRow{background-color: #f0f0f0}')
