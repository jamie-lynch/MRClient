"""
Match Report CasparCG Client
Version 2.1
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file contains a number of helper classes for the rundown
"""

from PySide import QtGui, QtCore
from clientwindow.tools import QHeadingThree


class GetVTGraphics(QtGui.QDialog):
    """Dialog window for settings video graphics"""

    def __init__(self, main, video):
        """Function to initialise VideoGraphics widget"""

        # call to parent __init__ function
        super(GetVTGraphics, self).__init__()

        # create list to store graphics in
        self.graphics = []

        # set for convenience
        self.main = main
        self.video = video

        # create UI elements
        self.initUI()

        # add any elements that exist
        for item in self.video.settings['graphics']:
            self.add_graphic(item)

        # removes question mark thing
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)

        # set title
        self.setWindowTitle("VT Graphics | Match Report CasparCG Client")

        # set window size
        self.resize(600, 500)

        # GO!
        self.exec_()

    def initUI(self):
        """Function to create UI elements"""

        # create and set layout
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # name
        grid.addWidget(QHeadingThree("VT: "), 0, 0)
        name_label = QtGui.QLabel(self.video.data['name'])
        grid.addWidget(name_label, 0, 1)

        # length
        grid.addWidget(QHeadingThree("Length: "), 1, 0)
        length_label = QtGui.QLabel(self.video.data['length'])
        grid.addWidget(length_label, 1, 1)

        # GFX
        grid.addWidget(QHeadingThree("Graphics"), 2, 0)
        add_graphic_button = QtGui.QPushButton("Add")
        add_graphic_button.clicked.connect(self.add_graphic)
        grid.addWidget(add_graphic_button, 2, 1)

        scroll_area = QtGui.QScrollArea()

        # create widget for scroll area
        scroll_widget = QtGui.QWidget()
        self.graphics_vbox = QtGui.QVBoxLayout()
        scroll_widget.setLayout(self.graphics_vbox)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        self.graphics_vbox.setAlignment(QtCore.Qt.AlignTop)

        grid.addWidget(scroll_area, 3, 0, 1, 2)

        self.okay_button = QtGui.QPushButton("Ok")
        self.okay_button.clicked.connect(self.okay)
        grid.addWidget(self.okay_button, 5, 0)

        self.cancel_button = QtGui.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        grid.addWidget(self.cancel_button, 5, 1)

    def add_graphic(self, data=None):
        """Function to add graphic to vt rundown"""
        if data:
            new = GraphicItem(data=data, window=self)
            self.graphics.append(new)
            self.graphics_vbox.addWidget(new)
        else:
            EditGraphic(main=self.main, window=self)

    def remove_item(self, item):
        """Function to remove item from list and display"""
        self.graphics.remove(item)
        self.graphics_vbox.removeWidget(item)
        item.deleteLater()

    def okay(self):
        """Function to return the graphic options selected"""

        # create empty list
        settings = []

        # add data for each graphic
        for graphic in self.graphics:
            settings.append(graphic.data)

        # set to video settings
        self.video.settings['graphics'] = settings

        # close
        self.accept()


class GraphicItem(QtGui.QFrame):
    """Widget to hold data for one graphic"""

    def __init__(self, data, window):
        """Function to initialise GraphicItem"""

        # call the parent __init__ function
        super(GraphicItem, self).__init__()

        # set for convenience
        self.data = data
        self.window = window

        # create UI elements
        self.initUI()

        # set border
        self.setFrameStyle(QtGui.QFrame.Box)

    def initUI(self):
        """Function to create UI elements"""

        # create and set layout
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # add the name of the data
        grid.addWidget(QHeadingThree("Name: "), 0, 0)
        self.name = QtGui.QLabel(self.data['name'])
        grid.addWidget(self.name, 0, 1)

        # add the template
        grid.addWidget(QHeadingThree("Template: "), 1, 0)
        self.template = QtGui.QLabel(self.data['template'])
        grid.addWidget(self.template, 1, 1)

        # add the start time
        grid.addWidget(QHeadingThree("Start: "), 0, 2)
        self.start = QtGui.QLabel(self.data['start'])
        grid.addWidget(self.start, 0, 3)

        # add the end time
        grid.addWidget(QHeadingThree("End: "), 1, 2)
        self.end = QtGui.QLabel(self.data['end'])
        grid.addWidget(self.end, 1, 3)

        # add the channel
        grid.addWidget(QHeadingThree("Channel: "), 0, 4)
        self.channel = QtGui.QLabel(str(self.data['channel']))
        grid.addWidget(self.channel, 0, 5)

        # add the layer
        grid.addWidget(QHeadingThree("Layer: "), 1, 4)
        self.layer = QtGui.QLabel(str(self.data['layer']))
        grid.addWidget(self.layer, 1, 5)

        # add the remove button
        remove_button = QtGui.QPushButton("Delete")
        remove_button.clicked.connect(lambda: self.window.remove_item(self))
        grid.addWidget(remove_button, 0, 6)

        # add the edit button
        edit_button = QtGui.QPushButton("Edit")
        edit_button.clicked.connect(self.edit)
        grid.addWidget(edit_button, 1, 6)

    def edit(self):
        """Function to allow editing of a GraphicItem"""

        # open dialog to allow editing
        EditGraphic(main=self.window.main, item=self)

        # reset the labels
        self.name.setText(self.data['name'])
        self.filename.setText(self.data['filename'])
        self.start.setText(self.data['start'])
        self.end.setText(self.data['end'])
        self.channel.setText(str(self.data['channel']))
        self.layer.setText(str(self.data['layer']))


class EditGraphic(QtGui.QDialog):
    """Dialog for setting new graphic settings"""

    def __init__(self, main, window=None, item=None):
        """Function to initialise NewGraphic dialog"""

        # call the parent __init__ function
        super(EditGraphic, self).__init__()

        # set for convenience
        self.main = main
        self.window = window
        self.item = item

        # split parameters if item
        if self.item:
            self.split_parameters()

        # create UI elements
        self.initUI()

        # removes question mark thing
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)

        # set title
        self.setWindowTitle("New Graphic | Match Report CasparCG Client")
        self.exec_()

    def initUI(self):
        """Function to create UI elements"""

        # create and set layout
        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)

        # Label
        self.grid.addWidget(QtGui.QLabel("Label:"), 0, 0)
        self.label_edit = QtGui.QLineEdit()
        self.label_edit.setMaxLength(16)
        if self.item:
            self.label_edit.setText(self.item.data['name'])
        self.grid.addWidget(self.label_edit, 0, 1)

        # Start Time
        self.grid.addWidget(QtGui.QLabel("Start time: "), 1, 0)
        self.time_edit = QtGui.QLineEdit("00:00:00:00")
        if self.item:
            self.time_edit.setText(self.item.data['start'])
        self.grid.addWidget(self.time_edit, 1, 1)

        # End time
        self.grid.addWidget(QtGui.QLabel("End Time: "), 2, 0)
        self.end_time = QtGui.QLineEdit("")
        if self.item:
            self.end_time.setText(self.item.data['end'])
        self.grid.addWidget(self.end_time, 2, 1)

        # Template
        self.grid.addWidget(QtGui.QLabel("Graphic: "), 3, 0)
        self.name_select = QtGui.QComboBox()
        self.name_select.addItem("Select Graphic...")
        for temp in self.main.settings['vt_templates']:
            self.name_select.addItem(temp)
        if self.item:
            self.name_select.setCurrentIndex(self.main.settings['vt_templates'].index(self.item.data['template'])+1)
        self.grid.addWidget(self.name_select, 3, 1)

        # Layer
        self.grid.addWidget(QtGui.QLabel("Layer: "), 5, 0)
        self.layer_edit = QtGui.QLineEdit("10")
        if self.item:
            self.layer_edit.setText(self.item.data['layer'])
        self.grid.addWidget(self.layer_edit, 5, 1)

        # Parameters
        self.grid.addWidget(QtGui.QLabel("Parameters:"), 6, 0)
        self.graphics_widget = QtGui.QWidget()
        self.name_select.currentIndexChanged.connect(lambda: self.add_parameters(self.name_select.currentText()))
        if self.item:
            gfx_grid = QtGui.QGridLayout()
            self.graphics_widget.setLayout(gfx_grid)

            # add the parameter labels and edits
            self.parameters = {}
            for num, parameter in enumerate(self.main.settings['templates'][self.name_select.currentText()]['parameters']):
                parameter_name = QtGui.QLabel(parameter)
                parameter_edit = QtGui.QLineEdit()
                self.parameters[parameter] = parameter_edit
                try:
                    self.parameters[parameter].setText(self.curr_parameters[parameter])
                except KeyError:
                    pass

                gfx_grid.addWidget(parameter_name, num, 0)
                gfx_grid.addWidget(parameter_edit, num, 1)
        self.grid.addWidget(self.graphics_widget, 7, 0, 2, 2)

        # Buttons
        okay = QtGui.QPushButton("Okay")
        okay.clicked.connect(self.add_graphics)
        self.grid.addWidget(okay, 10, 0)

        cancel = QtGui.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        self.grid.addWidget(cancel, 10, 1)

    def add_parameters(self, name):
        """Function to display corresponding parameters to name chosen"""

        # remove current elements
        self.grid.removeWidget(self.graphics_widget)
        self.graphics_widget.deleteLater()

        # make a new things
        self.graphics_widget = QtGui.QWidget()
        gfx_grid = QtGui.QGridLayout()
        self.graphics_widget.setLayout(gfx_grid)

        # add the parameter labels and edits
        self.parameters = {}
        for num, parameter in enumerate(self.main.settings['templates'][self.name_select.currentText()]['parameters']):
            parameter_name = QtGui.QLabel(parameter)
            parameter_edit = QtGui.QLineEdit()
            self.parameters[parameter] = parameter_edit
            if self.item:
                try:
                    self.parameters[parameter].setText(self.curr_parameters[parameter])
                except KeyError:
                    pass

            gfx_grid.addWidget(parameter_name, num, 0)
            gfx_grid.addWidget(parameter_edit, num, 1)
        self.grid.addWidget(self.graphics_widget, 7, 0, 2, 2)

    def add_graphics(self):
        """Function to add current graphic"""
        data = {}

        data['template'] = self.name_select.currentText()
        if data['template'] == 'Select Graphic...':
            return

        data['start'] = self.time_edit.text()
        if self.item:
            data['start_frames'] = self.get_frames_from_length(data['start'], self.item.window.video.settings['frame_rate'])
        else:
            data['start_frames'] = self.get_frames_from_length(data['start'], self.window.video.settings['frame_rate'])
        data['end'] = self.end_time.text()

        if self.item:
            if data['end']:
                data['end_frames'] = self.get_frames_from_length(data['end'], self.item.window.video.settings['frame_rate'])
            else:
                data['end_frames'] = None
        else:
            if data['end']:
                data['end_frames'] = self.get_frames_from_length(data['end'], self.window.video.settings['frame_rate'])
            else:
                data['end_frames'] = None

        if self.item:
            data['channel'] = self.item.data['channel']
        else:
            data['channel'] = self.window.video.settings['channel']
        data['layer'] = self.layer_edit.text()
        data['name'] = self.label_edit.text()
        data['filename'] = self.main.settings['templates'][data['template']]['filename']
        parameters = {key: val.text() for key, val in self.parameters.items()}
        parameters = ['{}={}'.format(key, val) for key, val in parameters.items()]
        parameters = '|'.join(parameters)
        data['parameters'] = parameters

        if self.window:
            self.window.add_graphic(data=data)
        else:
            self.item.data = data

        self.accept()

    def split_parameters(self):
        """Function to split a Caspar formatted parameters string"""
        items = self.item.data['parameters'].split("|")
        self.curr_parameters = {item.split("=")[0]: item.split("=")[1] for item in items}

    @staticmethod
    def get_frames_from_length(length, frame_rate):
        """Function to return the length based on the number of frames"""
        hours, minutes, seconds, smpte_frames = length.split(':')

        hours = int(hours) * frame_rate * 60 * 60
        minutes = int(minutes) * frame_rate * 60
        seconds = int(seconds) * frame_rate

        frames = hours + minutes + seconds + int(smpte_frames)

        return frames
