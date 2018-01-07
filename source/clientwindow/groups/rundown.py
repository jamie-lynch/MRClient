"""
Match Report CasparCG Client
Version 2.1
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
        self.list_items = {}

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
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # create a heading
        grid.addWidget(tools.QHeadingOne("Rundown"), 0, 0)

        # make the list widget
        self.list_widget = RundownList(rundown=self)
        self.list_widget.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        grid.addWidget(self.list_widget, 1, 0)

        # add the elements from file
        for position in sorted(map(int, list(self.data['rundown']['positions'].keys()))):
            self.add_row(self.data['rundown']['items'][self.data['rundown']['positions'][str(position)]], save=False)

        # get the current reference
        self.get_positions()

        # create another heading
        grid.addWidget(tools.QHeadingOne("Item Graphics"), 0, 1)

        # add edit button
        edit_button = QtGui.QPushButton("Edit")
        edit_button.clicked.connect(self.edit)
        grid.addWidget(edit_button, 0, 2)

        # create an item graphics elements
        self.item_graphics = ItemGraphics(rundown=self)
        grid.addWidget(self.item_graphics, 1, 1, 1, 2)

    def add_row(self, settings, save=True):
        """Function to append a RundownItem to the Rundown"""

        # create a RundownItem
        new = RundownItem(self.main, self, settings, item_id=str(self.curr_id))

        # add to items list
        self.items[str(self.curr_id)] = new

        item = QtGui.QListWidgetItem(self.list_widget)
        item.setSizeHint(QtCore.QSize(new.width(), new.height()))
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, new)

        self.list_items[str(self.curr_id)] = item

        # get the current order
        self.get_positions()

        # increase current id
        self.curr_id += 1

        if save:
            self.write_to_file()

    def remove_row(self, widget):
        """Function to remove a RundownItem from the Rundown"""

        # find the it of the widget to remove
        item_id = widget.item_id

        # remove from the list widget
        item = self.list_widget.takeItem(self.id_to_positions[item_id])

        # remove from items
        del self.items[item_id]
        del self.list_items[item_id]

        # delete the widget
        widget.deleteLater()
        del item

        # refresh the positions
        self.get_positions()

        # write to file
        self.write_to_file()

    def get_positions(self):
        """Function to get the current position of each widget"""
        # create a dictionary to reference the positions
        self.positions = {}
        self.id_to_positions = {}

        # for each item in the rundown
        for item in self.list_items.values():

            index = self.list_widget.indexFromItem(item)

            # find the widget of the item
            widget = self.list_widget.itemWidget(item)

            # add to the positions dictionary
            self.positions[index.row()] = str(widget.item_id)
            self.id_to_positions[str(widget.item_id)] = index.row()

    def write_to_file(self):
        """Function to record the current state of the Rundown"""
        self.main.data['rundown'] = {}
        self.main.data['rundown']['items'] = {item.item_id: item.settings for item in self.items.values()}
        self.main.data['rundown']['positions'] = self.positions
        tools.store_data(self.main)

    def edit(self):
        """Function to edit the item graphics for the currently selected item"""
        video = self.item_graphics.video
        try:
            _ = video.settings['graphics']
        except KeyError:
            if video.settings['type'] == 'vt':
                video.settings['graphics'] = []
            else:
                return

        tools.GetVTGraphics(main=self.main, video=video)
        self.item_graphics.update_graphics(video=video)


class RundownList(QtGui.QListWidget):

    def __init__(self, rundown, parent=None):
        super(RundownList, self).__init__(parent)
        self.rundown = rundown

    def dropEvent(self, event):
        """Function which calls the get positions function when a widget is dropped"""
        super(RundownList, self).dropEvent(event)
        self.rundown.get_positions()
        self.rundown.write_to_file()


class RundownItem(QtGui.QFrame):
    """Item containing all data for a rundown item"""

    playing_signal = QtCore.Signal(object)
    stopped_signal = QtCore.Signal(object)

    def __init__(self, main, rundown, settings, item_id, parent=None):
        """Function to initialise the class"""

        # call to parent __init__ function
        super(RundownItem, self).__init__(parent)

        # set for reference
        self.item_id = item_id

        # set for convenience
        self.main = main
        self.rundown = rundown
        self.settings = settings
        self.data = settings
        self.osc = self.main.osc
        self.comms = self.main.comms

        # create reference values
        self.channel_launched = None
        self.layer_launched = None
        self.playing = False
        self.paused = False
        self.loaded = False
        self.fired_graphics = []

        # call the correct create UI function
        if self.settings['type'] == "graphic":
            self.init_graphic_ui()
        elif self.settings['type'] in ['vt', 'vtgfx']:
            self.init_vt_ui()

        # connect to the connected signal to un-freeze buttons when caspar is connected
        self.main.connected.signal.connect(self.set_enabled_disabled)

        # set the frame style
        self.setFrameStyle(QtGui.QFrame.Box)

        # set the height
        self.setFixedHeight(76)

    def init_graphic_ui(self):
        """Function to create the UI elements for a graphic"""

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # Create name label
        name_label = tools.QVTLabel(self, "Name: ", bold=True)
        name_label.setFixedWidth(50)
        grid.addWidget(name_label, 0, 0)
        name = tools.QVTLabel(self, self.settings['name'])
        name.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        name.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        grid.addWidget(name, 0, 1)

        # Create graphic label
        grid.addWidget(tools.QVTLabel(self, "Graphic: ", bold=True), 1, 0)
        grid.addWidget(tools.QVTLabel(self, self.settings['template']), 1, 1)

        # Create channel edit
        grid.addWidget(tools.QVTLabel(self, "Channel:", bold=True), 0, 2)
        self.channel_edit = tools.QVTLabel(self, str(self.settings['channel']))
        self.channel_edit.setFixedWidth(40)
        self.channel_edit.setAlignment(QtCore.Qt.AlignCenter)
        grid.addWidget(self.channel_edit, 0, 3)

        # Create layer edit
        grid.addWidget(tools.QVTLabel(self, "Layer:", bold=True), 1, 2)
        self.layer_edit = tools.QVTLabel(self, str(self.settings['layer']))
        self.layer_edit.setFixedWidth(40)
        self.layer_edit.setAlignment(QtCore.Qt.AlignCenter)
        grid.addWidget(self.layer_edit, 1, 3)

        label1 = QtGui.QLabel('')
        label2 = QtGui.QLabel('')
        label3 = QtGui.QLabel('')
        label4 = QtGui.QLabel('')
        label1.setFixedWidth(80)
        label2.setFixedWidth(75)
        label3.setFixedWidth(90)
        label4.setFixedWidth(90)
        grid.addWidget(label1, 0, 4)
        grid.addWidget(label2, 0, 5)
        grid.addWidget(label3, 0, 6)
        grid.addWidget(label4, 0, 7)

        # Create buttons
        self.fire_button = QtGui.QPushButton("Fire")
        self.fire_status = "Fire"
        self.fire_button.setFixedWidth(185)
        self.fire_button.clicked.connect(self.fire_graphic)
        grid.addWidget(self.fire_button, 0, 8, 1, 2)

        self.remove_button = QtGui.QPushButton("Delete")
        self.remove_button.setFixedWidth(185)
        self.remove_button.clicked.connect(self.remove_row)
        grid.addWidget(self.remove_button, 1, 8, 1, 2)

        self.fire_buttons = [self.fire_button]
        self.set_enabled_disabled()

    def init_vt_ui(self):
        """Function to create the UI elements for a graphic"""

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # Create name label
        name_label = tools.QVTLabel(self, "Name: ", bold=True)
        name_label.setFixedWidth(50)
        grid.addWidget(name_label, 0, 0)
        name = tools.QVTLabel(self, self.settings['name'])
        name.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        name.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        grid.addWidget(name, 0, 1)

        # Create graphic label
        grid.addWidget(tools.QVTLabel(self, "Type: ", bold=True), 1, 0)
        grid.addWidget(tools.QVTLabel(self, self.settings['template']), 1, 1)

        # Create channel edit
        grid.addWidget(tools.QVTLabel(self, "Channel:", bold=True), 0, 2)
        self.channel_edit = tools.QVTLabel(self, str(self.settings['channel']))
        self.channel_edit.setFixedWidth(40)
        self.channel_edit.setAlignment(QtCore.Qt.AlignCenter)
        grid.addWidget(self.channel_edit, 0, 3)

        # Create layer edit
        grid.addWidget(tools.QVTLabel(self, "Layer:", bold=True), 1, 2)
        self.layer_edit = tools.QVTLabel(self, str(self.settings['layer']))
        self.layer_edit.setFixedWidth(40)
        self.layer_edit.setAlignment(QtCore.Qt.AlignCenter)
        grid.addWidget(self.layer_edit, 1, 3)

        # Create length label
        length_label = tools.QVTLabel(self, "Length: ", bold=True)
        length_label.setFixedWidth(80)
        grid.addWidget(length_label, 0, 4)
        length = tools.QVTLabel(self, self.settings['length'])
        length.setFixedWidth(75)
        grid.addWidget(length, 0, 5)

        # Create remaining label
        grid.addWidget(tools.QVTLabel(self, "Remaining: ", bold=True), 1, 4)
        self.time = tools.QVTLabel(self, "")
        grid.addWidget(self.time, 1, 5)

        # add the loop label and checkbox
        loop = tools.QVTLabel(self, "Loop?")
        grid.addWidget(loop, 1, 6)
        grid.setAlignment(loop, QtCore.Qt.AlignCenter)
        self.loop_select = QtGui.QCheckBox()
        grid.addWidget(self.loop_select, 1, 7)
        grid.setAlignment(self.loop_select, QtCore.Qt.AlignCenter)

        # Create buttons
        load_button = QtGui.QPushButton("Load")
        load_button.clicked.connect(self.load_vt)
        load_button.setFixedWidth(90)
        grid.addWidget(load_button, 0, 6)

        play_button = QtGui.QPushButton("Play")
        play_button.setFixedWidth(90)
        play_button.clicked.connect(self.play_vt)
        grid.addWidget(play_button, 0, 7)

        pause_button = QtGui.QPushButton("Pause/Resume")
        pause_button.clicked.connect(self.pause_vt)
        pause_button.setFixedWidth(90)
        grid.addWidget(pause_button, 0, 8)

        stop_button = QtGui.QPushButton("Stop")
        stop_button.clicked.connect(self.stop_vt)
        stop_button.setFixedWidth(90)
        grid.addWidget(stop_button, 0, 9)

        remove_button = QtGui.QPushButton("Delete")
        remove_button.clicked.connect(self.remove_row)
        remove_button.setFixedWidth(185)
        grid.addWidget(remove_button, 1, 8, 1, 2)

        self.fire_buttons = [load_button, play_button, pause_button, stop_button]
        self.set_enabled_disabled()

    def fire_graphic(self):
        """Function to fire graphic"""

        if self.fire_status == 'Fire':
            response = self.main.comms.template(
                name=self.settings['filename'],
                channel=self.channel_edit.text(),
                layer=self.layer_edit.text(),
                parameters=self.settings['parameters'],
                playonload=0
            )

            if 'OK' in response:
                self.fire_status = 'Stop'
                self.fire_button.setText('Stop')
                self.channel_launched = self.channel_edit.text()
                self.layer_launched = self.layer_edit.text()
                self.playing_signal.emit(self)
                self.playing = True
                self.set_background_colour()


        else:
            response = self.main.comms.stop_template(
                channel=self.channel_launched,
                layer=self.layer_launched
            )

            if 'OK' in response:
                self.fire_status = 'Fire'
                self.fire_button.setText('Fire')
                self.stopped_signal.emit(self)
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
            self.setStyleSheet('RundownItem{background-color: #009600}')
        else:
            self.setStyleSheet('RundownItem{background-color: transparent}')

    def remove_row(self):
        """Function to remove row"""
        if self.playing:
            error = QtGui.QErrorMessage()
            error.showMessage("Cannot remove item while playing")
            error.exec_()
            return
        else:
            self.rundown.remove_row(self)

    def load_vt(self):
        """Function to load current VT"""
        try:
            channel = int(self.channel_edit.text())
            self.channel_launched = channel

            self.osc.videos[int(self.channel_launched)][0].stop_vt()

            self.comms.load_video(name=self.data['name'], channel=channel)
            self.osc.videos[int(self.channel_launched)][0] = self
            self.playing = True
            self.playing_signal.emit(self)
            self.loaded = True
            self.set_background_colour()

        except ValueError:
            QtGui.QErrorMessage("Please select a valid channel (1-2)")

    def play_vt(self):
        """Function to play current VT"""
        try:

            channel = int(self.channel_edit.text())
            self.channel_launched = channel

            # kill current things on this channel
            try:
                self.osc.videos[int(self.channel_launched)][0].stop_vt()
            except KeyError:
                pass

            if self.loop_select.isChecked():
                loop = 1
            else:
                loop = 0
            self.channel_launched = channel

            response, message = self.comms.play_video(name=self.data['name'], channel=channel, loop=loop)
            if response:
                self.playing = True
                self.playing_signal.emit(self)
                self.paused = False
                self.loaded = False
                self.osc.videos[int(self.channel_launched)][0] = self
                self.set_background_colour()
                try:
                    self.graphics_remaining = self.settings['graphics'].copy()
                    self.fired_graphics = []
                    self.stopped_graphics = []
                except KeyError:
                    pass

        except ValueError:
            QtGui.QErrorMessage("Please select a valid channel (1-2)")

    def pause_vt(self):
        """Function to pause/resume current VT"""
        if self.playing:
            if self.paused:
                self.comms.resume_video(channel=self.channel_launched)
                self.paused = False
            else:
                self.comms.pause_video(channel=self.channel_launched)
                self.paused = True

    def stop_vt(self):
        """Function to stop current VT"""
        if self.playing:
            self.comms.stop_video(channel=self.channel_launched)
            for graphic in self.fired_graphics:
                _ = self.main.comms.stop_template(
                    channel=graphic['channel'],
                    layer=graphic['layer'],
                )
            del self.osc.videos[int(self.channel_launched)][0]
            self.channel_launched = None
            self.time.setText("")
            self.playing = False
            self.stopped_signal.emit(self)
            self.loaded = False
            self.set_background_colour()

    def get_length_from_frames(self, frames=None, frame_rate=None):
        """Function to return the length based on the number of frames"""
        if not frames:
            frames = float(self.data['frames'])

        if not frame_rate:
            frame_rate = self.data['frame_rate']
            if type(frame_rate) != float and type(frame_rate) != int:
                try:
                    frame_rate = float(frame_rate.split('/')[1]) / float(frame_rate.split('/')[0])
                except IndexError:
                    return " ", 1, 1
                except ZeroDivisionError:
                    return " ", 1, 1
                if frame_rate == 0.0:
                    return " ", 1, 1

        hours = int(frames / 60 / 60 / frame_rate)
        minutes = int((frames - (hours * 60 * 60 * frame_rate)) / 60 / frame_rate)
        seconds = int((frames - hours * 60 * 60 * frame_rate - minutes * 60 * frame_rate) / frame_rate)
        smpte_frames = int((frames - hours * 60 * 60 * frame_rate - minutes * 60 * frame_rate - seconds * frame_rate))

        time = "%02d:%02d:%02d:%02d" % (hours, minutes, seconds, smpte_frames)

        return time, frames, frame_rate

    def set_remaining_time(self, current_frame, total_frames):
        """Function to set the time remaining"""

        if not self.loaded:

            try:
                _ = self.settings['graphics']

                # call to fire graphics function
                self.automagical_graphics(current_frame)

            except KeyError:
                pass

            # find the number of frames remaining
            remaining_frames = int(total_frames) - int(current_frame)

            # find the time remaining
            remaining_time, _, _ = self.get_length_from_frames(frames=remaining_frames,
                                                               frame_rate=self.data['frame_rate'])

            # sets the time
            self.time.setText(remaining_time)

    def automagical_graphics(self, current_frame):
        """Function to play graphics if there are any"""
        for graphic in self.graphics_remaining:
            if int(current_frame) >= int(graphic['start_frames']):
                _ = self.main.comms.template(
                    name=graphic['filename'],
                    channel=graphic['channel'],
                    layer=graphic['layer'],
                    parameters=graphic['parameters'],
                    playonload=0
                )
                self.fired_graphics.append(graphic)

        for graphic in self.fired_graphics:
            try:
                self.graphics_remaining.remove(graphic)
            except ValueError:
                pass
            if graphic['end_frames']:
                if int(current_frame) >= int(graphic['end_frames']):
                    _ = self.main.comms.stop_template(
                        channel=graphic['channel'],
                        layer=graphic['layer'],
                    )
                    self.stopped_graphics.append(graphic)

        for graphic in self.stopped_graphics:
            try:
                self.fired_graphics.remove(graphic)
            except ValueError:
                pass


class ItemGraphics(QtGui.QListWidget):
    """Class which holds a list of the graphic items for the selected item"""

    def __init__(self, rundown, parent=None):
        """Function to initialise the class"""

        # call the parent __init__ function
        super(ItemGraphics, self).__init__(parent)

        # set for convenience
        self.rundown = rundown

        # connect to signal
        self.rundown.list_widget.currentRowChanged.connect(self.update_graphics)

        # create list
        self.setFixedWidth(275)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)

        # create list of items
        self.list_items = []

    @QtCore.Slot(int)
    def update_graphics(self, current_row=None, video=None):
        """Function to show the graphics"""

        # remove all of the current items
        self.clear()

        self.list_items = []

        if not video:
            # get the rundown item
            try:
                rundown_item = self.rundown.items[self.rundown.positions[current_row]]
            except KeyError:
                pass

            # get video for edit reference
            self.video = rundown_item

        else:
            rundown_item = video
            self.video = video

        # get graphics elements if available
        try:
            graphics = rundown_item.settings['graphics']
        except KeyError:
            return

        # add the graphics
        for graphic in graphics:

            new = ItemGraphic(graphic)

            item = QtGui.QListWidgetItem(self)
            item.setSizeHint(QtCore.QSize(new.width(), new.height()))
            self.addItem(item)
            self.setItemWidget(item, new)

            self.list_items.append(item)


class ItemGraphic(QtGui.QFrame):
    """Class which holds the information for one item graphic"""

    def __init__(self, data, parent=None):
        """Function to initialise the class"""

        # call the parent __init__ function
        super(ItemGraphic, self).__init__(parent)

        # set for convenience
        self.data = data

        # create UI elements
        self.initUI()

        # set the frame style
        self.setFrameStyle(QtGui.QFrame.Box)

        # set the height
        self.setFixedHeight(70)
        self.resize(240, 70)

    def initUI(self):
        """Function to build the UI elements"""

        # create and set layout
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # add the name of the data
        grid.addWidget(tools.QHeadingThree("Name: "), 0, 0)
        self.name = QtGui.QLabel(self.data['name'])
        self.name.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        grid.addWidget(self.name, 0, 1)

        # add the filename
        grid.addWidget(tools.QHeadingThree("Graphic: "), 1, 0)
        self.filename = QtGui.QLabel(self.data['template'])
        grid.addWidget(self.filename, 1, 1)

        # add the start time
        grid.addWidget(tools.QHeadingThree("Start: "), 0, 2)
        self.start = QtGui.QLabel(self.data['start'])
        grid.addWidget(self.start, 0, 3)

        # add the end time
        end_label = tools.QHeadingThree("End: ")
        grid.addWidget(end_label, 1, 2)
        self.end = QtGui.QLabel(self.data['end'])
        grid.addWidget(self.end, 1, 3)

