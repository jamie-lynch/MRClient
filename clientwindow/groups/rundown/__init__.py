"""
Match Report CasparCG Client
Version 2.0
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file holds the classes to define the rundown tab
"""

from PySide import QtGui, QtCore
from clientwindow import tools


class RundownWidget(QtGui.QWidget):
    """Class to define custom widget for rundown tab"""

    def __init__(self, main, parent=None):
        """Function to initialise the class"""

        # call to the parent __init__ function
        super(RundownWidget, self).__init__(parent)

        # set title
        self.title = "Rundown"

        # set for convenience
        self.main = main
        self.settings = main.settings
        self.data = main.data
        self.comms = main.comms

        # keep reference to each widget
        self.items = {}

        # get the current id number
        try:
            self.curr_id = max(map(int, list(self.main.data['rundown']['positions'].values()))) + 1
        except ValueError:
            self.curr_id = 0

        # create the UI elements
        self.init_ui()

    def init_ui(self):
        """Creates the UI elements"""

        # create and set the layout
        main_vbox = QtGui.QVBoxLayout()
        self.setLayout(main_vbox)

        # create a heading
        main_vbox.addWidget(tools.QHeadingOne("Rundown"))

        # make the scroll area
        scroll_area = QtGui.QScrollArea()
        scroll_widget = QtGui.QWidget()
        self.rundown_vbox = QtGui.QVBoxLayout()
        self.rundown_vbox.setAlignment(QtCore.Qt.AlignTop)
        scroll_widget.setLayout(self.rundown_vbox)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_vbox.addWidget(scroll_area)

        # add the elements from file
        for position in sorted(list(self.data['rundown']['positions'].keys())):
            self.add_row(self.data['rundown']['items'][self.data['rundown']['positions'][position]], save=False)

    def add_row(self, settings, save=True):
        """Function to append a RundownItem to the Rundown"""

        # create a RundownItem
        new = RundownItem(self.main, self, settings, id=self.curr_id)

        # add to items list
        self.items[self.curr_id] = new

        # show the item
        self.rundown_vbox.addWidget(new)

        # get the current order
        self.get_positions()

        # increase current id
        self.curr_id += 1

        if save:
            self.write_to_file()

    def remove_row(self, widget):
        """Function to remove a RundownItem from the Rundown"""

        # remove widget from display
        self.rundown_vbox.removeWidget(widget)

        # remove from items
        del self.items[widget.id]

        # delete the widget
        widget.deleteLater()

        # refresh the positions
        self.get_positions()

        # write to file
        self.write_to_file()

    def move_row(self, widget, direction):
        """Function to move a RundownItem within the Rundown"""

        # find the current position of the widget
        curr_pos = int(self.id_to_position[widget.id])

        # find the new position
        if direction == "up":
            if curr_pos != 0:
                new_pos = curr_pos - 1
            else:
                new_pos = curr_pos
        else:
            new_pos = curr_pos + 1

        # remove the widget from the rundown
        self.rundown_vbox.removeWidget(widget)

        # insert it in its new place
        self.rundown_vbox.insertWidget(new_pos, widget)

        # find the new positions
        self.get_positions()

        # write to file
        self.write_to_file()

    def get_positions(self):
        """Function to get the current position of each widget"""

        # find how many widgets are in the list
        count = self.rundown_vbox.count()

        # create a dictionary to reference the positions
        self.positions = {}
        self.id_to_positions = {}

        # for each widget in the rundown
        for num in range(0, count):

            # add to the positions dictionary
            self.positions[num] = str(self.rundown_vbox.itemAt(num).widget().id)
            self.id_to_positions[str(self.rundown_vbox.itemAt(num).widget().id)] = num

    def write_to_file(self):
        """Function to record the current state of the Rundown"""
        self.main.data['rundown'] = {}
        self.main.data['rundown']['items'] = {item.id: item.settings for item in self.items}
        print(self.main.data['rundown']['items'])
        self.main.data['rundown']['positions'] = self.positions
        tools.store_data(self.main)


class RundownItem(QtGui.QFrame):
    """Item containing all data for a rundown item"""

    playing_signal = QtCore.Signal(object)
    stopped_signal = QtCore.Signal(object)

    def __init__(self, main, rundown, settings, id, parent=None):
        """Function to initialise the class"""

        # call to parent __init__ function
        super(RundownItem, self).__init__(parent)

        # set for reference
        self.id = id

        # set for convenience
        self.main = main
        self.rundown = rundown
        self.settings = settings

        # create reference values
        self.channel_launched = None
        self.layer_launched = None
        self.playing = False
        self.paused = False
        self.loaded = False

        # call the correct create UI function
        if self.settings['type'] == "graphic":
            self.init_graphic_ui()

        # connect to the connected signal to un-freeze buttons when caspar is connected
        self.main.connected.signal.connect(self.set_enabled_disabled)

        # set the frame style
        self.setFrameStyle(QtGui.QFrame.Box)

    def init_graphic_ui(self):
        """Function to create the UI elements for a graphic"""

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # Create name label
        grid.addWidget(tools.QVTLabel(self, "Name: "), 0, 0)
        grid.addWidget(tools.QVTLabel(self, self.settings['name']), 0, 1)

        # Create graphic label
        grid.addWidget(tools.QVTLabel(self, "Graphic: "), 1, 0)
        grid.addWidget(tools.QVTLabel(self, self.settings['template']), 1, 1)

        # Create channel edit
        grid.addWidget(tools.QVTLabel(self, "Channel"), 0, 2)
        self.channel_edit = QtGui.QLineEdit(self.settings['channel'])
        self.channel_edit.textChanged.connect(self.check_channel)
        self.channel_edit.setFixedWidth(60)
        grid.addWidget(self.channel_edit, 0, 3)

        # Create layer edit
        grid.addWidget(tools.QVTLabel(self, "Layer"), 1, 2)
        self.layer_edit = QtGui.QLineEdit(self.settings['layer'])
        self.layer_edit.setFixedWidth(60)
        grid.addWidget(self.layer_edit, 1, 3)

        # Create buttons
        self.fire_button = QtGui.QPushButton("Fire")
        self.fire_status = "Fire"
        self.fire_button.clicked.connect(self.fire_graphic)
        grid.addWidget(self.fire_button, 0, 4)

        self.remove_button = QtGui.QPushButton("Delete")
        self.remove_button.clicked.connect(self.remove_row)
        grid.addWidget(self.remove_button, 1, 4)

        self.fire_buttons = [self.fire_button]
        self.set_enabled_disabled()

    def check_channel(self):
        """Function to check channel set to something sensible"""

        # find what the channel is set to
        channel = int(self.channel_select.text())

        # if its a VT
        if self.settings['type'] == "vt":

            # if its AUDIO
            if self.settings['vt_type'] == "AUDIO" and channel != 4:

                self.channel_select.setText("4")
                msg = "Audio tracks must be on channel 4"

            # if its VIDEO
            else:

                # check if the channel is 1 or 2
                if channel not in [1, 2]:

                    self.channel_select.setText("1")
                    msg = "Movie/Still track must be on channels 1 or 2"

        # if its a graphic
        else:

            # if its not on channel 3
            if channel != 3:
                self.channel_select.setText("3")

        if msg:
            error = QtGui.QErrorMessage()
            error.showMessage(msg)
            error.exec_()

    def fire_graphic(self):
        """Function to fire graphic"""

        if self.fire_status == 'Fire':
            response = self.main.comms.template(
                name=self.settings['filename'],
                channel=self.channel_edit.text(),
                layer=self.layer_edit.text(),
                parameters=self.settings['parameters']
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Stop'
                self.fire_button.setText('Stop')
                self.fire_channel_and_layer = self.fire_channel_and_layer[0], self.fire_channel_and_layer[1]
                self.playing_signal.emit()
                self.playing = True
                self.set_background_colour()

        else:
            response = self.main.comms.stop_template(
                channel=self.channel_launched,
                layer=self.layer_launched
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Fire'
                self.fire_button.setText('Fire')
                self.stopped_signal.emit()
                self.playing = False
                self.set_background_colour()

    def set_enabled_disabled(self):
        """Function to set fire buttons as enabled or disabled"""
        if self.main.comms.casparcg:
            for button in self.fire_buttons:
                button.setEnabled(True)
        else:
            for button in self.fire_buttons:
                button.setDisabled(True)

    def set_background_colour(self):
        """Function to set the correct background colour"""
        if self.playing:
            self.setStyleSheet('VideoItem{background-color: #009600}')
        else:
            self.setStyleSheet('VideoItem{background-color: #f0f0f0}')

    def remove_row(self):
        """Function to remove row"""
        if self.playing:
            error = QtGui.QErrorMessage()
            error.showMessage("Cannot remove item while playing")
            error.exec_()
            return
        else:
            self.rundown.remove_row(self)




