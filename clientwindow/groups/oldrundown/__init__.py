"""
Match Report CasparCG Client
Version 2.0
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file holds the classes to define the rundown tab
"""

from clientwindow import tools
from clientwindow.groups.oldrundown.vt_gfx import *
from clientwindow.groups.oldrundown.vtgfx_item import *
import threading
import time


class RundownWidget(QtGui.QWidget):
    """Widget for University name graphics"""

    def __init__(self, main, parent=None):
        """init function fro NameWidget"""
        super(RundownWidget, self).__init__(parent)
        self.setStyleSheet("RundownItem{border:2px solid black;}")
        self.title = "Rundown"
        self.main = main
        self.settings = main.settings
        self.comms = main.comms
        self.positions = {}
        self.curr_pos = 0


        try:
            self.curr_id = max(map(int, list(self.main.data['rundown']['positions'].values()))) + 1
        except IndexError:
            self.curr_id = 0

        self.init_ui()

    def init_ui(self):
        """ sets base content of widget """

        main_vbox = QtGui.QVBoxLayout()
        self.setLayout(main_vbox)

        main_vbox.addWidget(QHeadingOne("Rundown"))

        scroll_area = QtGui.QScrollArea()

        scroll_widget = QtGui.QWidget()
        self.rundown_vbox = QtGui.QVBoxLayout()
        self.rundown_vbox.setAlignment(QtCore.Qt.AlignTop)
        scroll_widget.setLayout(self.rundown_vbox)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_vbox.addWidget(scroll_area)

        self.items = []

    def build_from_file(self):
        """Function to build the thing from file"""
        items = self.main.data['rundown'].copy()
        self.positions_temp = self.main.data['rundown']['positions'].copy()

        keys = list(self.positions_temp.keys())
        keys = [int(val) for val in keys]
        keys.sort()
        for key in keys:
            item = items[self.positions_temp[str(key)]]
            self.add_row(settings=item['settings'], parameters=item['parameters'], old=True, old_id=self.positions_temp[str(key)])

    def add_row(self, settings, parameters=None, button_widget=None, old=False, old_id=None):
        """Function to add data row"""

        if settings['type'] == 'vtwithgfx':
            if "build" in settings.keys():
                if old_id:
                    new = VTGFXRundownItem(settings=settings, main=self.main, curr_id=old_id)
                else:
                    new = VTGFXRundownItem(settings=settings, main=self.main, curr_id=self.curr_id)
                self.items.append(new)
                self.rundown_vbox.addWidget(new)
                if not old:
                    self.store_rundown_item(settings=settings, button_widget=None, parameters=None)
                self.curr_id += 1
                self.get_current_widget_list()
            else:
                response = VideoGraphics(settings=settings, button_widget=button_widget, parameters=parameters, main=self.main)
                print(response)
        else:
            if old_id:
                new = RundownItem(settings=settings, button_widget=button_widget, parameters=parameters, main=self.main, curr_id=old_id)
            else:
                new = RundownItem(settings=settings, button_widget=button_widget, parameters=parameters, main=self.main,
                                  curr_id=self.curr_id)
            self.items.append(new)
            self.rundown_vbox.addWidget(new)
            if not old:
                self.store_rundown_item(settings=settings, button_widget=None, parameters=parameters)
            self.curr_id += 1
            self.get_current_widget_list()

    def store_rundown_item(self, settings, button_widget, parameters):
        """Function to write rundown item to a settings"""
        temp_store_data = {}
        temp_store_data['settings'] = settings
        temp_store_data['button_wdiget'] = button_widget
        temp_store_data['parameters'] = parameters
        self.store_data[str(self.curr_id)] = temp_store_data

        try:
            tools.store_local_data(self.main)
            print("Rundown Saved")
        except AttributeError:
            print("Warning: Data not saved")

    def remove_row(self, widget):
        """Function to remove data row"""
        self.rundown_vbox.removeWidget(widget)
        del self.store_data[str(widget.id)]
        widget.deleteLater()
        self.get_current_widget_list()

    def get_current_widget_list(self):
        """Function which creates a dictionary showing which objects are at each index"""
        count = self.rundown_vbox.count()
        self.positions = {}
        for num in range(0, count):
            self.positions[num] = str(self.rundown_vbox.itemAt(num).widget().id)
        self.store_data['positions'] = self.positions
        try:
            tools.store_local_data(self.main)
            print("Rundown Saved")
        except AttributeError:
            print("Warning, Data not saved.")

    def move_row(self, widget, direction):
        """Function to move datarow up or down"""
        print(widget.id)
        print(self.positions)
        for key, val in self.positions.items():
            print("key,val", key, val)
            print("widget id", widget.id)
            if val == str(widget.id):
                curr_pos = key
                break

        curr_pos = int(curr_pos)
        if direction == "up":
            if curr_pos != 0:
                new_pos = curr_pos - 1
            else:
                new_pos = curr_pos
        else:
            new_pos = curr_pos + 1

        self.rundown_vbox.removeWidget(widget)
        self.rundown_vbox.insertWidget(new_pos, widget)
        self.get_current_widget_list()

class RundownItem(QtGui.QFrame):
    """Item containing all data for a rundown item"""

    playing_signal = QtCore.Signal(object)
    stopped_signal = QtCore.Signal(object)

    def __init__(self, settings, button_widget, parameters, main, curr_id, parent=None):
        """Function to intialise RundownItem"""
        super(RundownItem, self).__init__(parent)

        self.channel_launched = None
        self.layer_launched = None
        self.paused = False
        self.playing = False
        self.ready = True
        self.threads = []

        self.id = curr_id

        self.set_background_colour()

        self.main = main
        self.comms = self.main.comms
        self.main.connected.signal.connect(self.set_enabled_disabled)
        self.setFrameStyle(QtGui.QFrame.Box)

        self.rundown = main.rundown
        self.widget = button_widget
        self.settings = settings
        self.parameters = parameters

        if self.settings['type'] == "graphic":
            self.build_graphic_item()
        elif self.settings['type'] == "vt":
            self.build_vt_item()

        self.setFixedHeight(100)
        self.set_enabled_disabled()

    def build_vt_item(self):
        """Function to build rundown item if item is a vt"""
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        self.data = self.settings
        data = self.data

        self.name = QtGui.QLabel(data['name'])
        grid.addWidget(self.name, 0, 0, 1, 2)

        # type
        type = QtGui.QLabel(data['vt_type'])
        grid.addWidget(type, 1, 0)

        # length
        grid.addWidget(QtGui.QLabel("Length"), 1, 3)
        self.data['length'], _, _ = self.get_length_from_frames(frames=self.data['frames'], frame_rate=self.data['frame_rate'])
        length = QtGui.QLabel(self.data['length'])
        grid.addWidget(length, 1, 4)

        # current time
        grid.addWidget(QtGui.QLabel("Remaining"), 1, 5)
        self.data['remaining_time'] = self.data['length']
        self.time = QVTLabel(self, self.data['remaining_time'])
        grid.addWidget(self.time, 1, 6)

        channel_label = QtGui.QLabel("Channel")
        grid.addWidget(channel_label, 0, 2)
        self.channel_select = QtGui.QLineEdit(str(self.data['channel']))
        self.channel_select.textChanged.connect(self.check_channel)
        grid.addWidget(self.channel_select, 0, 3, 1, 4)

        loop_label = QtGui.QLabel("Loop")
        grid.addWidget(loop_label, 1, 1)

        self.loop_select = QtGui.QCheckBox()
        grid.addWidget(self.loop_select, 1, 2)

        # buttons

        load_button = QtGui.QPushButton("Load")
        load_button.clicked.connect(self.load_vt)
        grid.addWidget(load_button, 0, 7)

        play_button = QtGui.QPushButton("Play")
        play_button.clicked.connect(self.play_vt)
        grid.addWidget(play_button, 0, 8)

        pause_button = QtGui.QPushButton("Pause/Resume")
        pause_button.clicked.connect(self.pause_vt)
        grid.addWidget(pause_button, 0, 9)

        stop_button = QtGui.QPushButton("Stop")
        stop_button.clicked.connect(self.stop_vt)
        grid.addWidget(stop_button, 0, 10)

        # edit
        self.edit_button = QtGui.QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_graphic_item)
        self.edit_button.hide()
        grid.addWidget(self.edit_button, 1, 7)

        # remove
        self.remove_button = QtGui.QPushButton("Remove")
        self.remove_button.clicked.connect(lambda: self.remove_row(self))
        grid.addWidget(self.remove_button, 1, 8)

        # up & down
        self.up_button = QtGui.QPushButton("Up")
        self.up_button.clicked.connect(lambda: self.rundown.move_row(widget=self, direction="up"))
        grid.addWidget(self.up_button, 1, 9)

        self.down_button = QtGui.QPushButton("Down")
        self.down_button.clicked.connect(lambda: self.rundown.move_row(widget=self, direction="down"))
        grid.addWidget(self.down_button, 1, 10)

        self.fire_buttons = [load_button, play_button, pause_button, stop_button]

    def load_vt(self):
        """Function to load current VT"""
        try:
            name = self.name.text()
            channel = int(self.channel_select.text())
            self.channel_launched = channel

            self.comms.load_video(name=name, channel=channel)

        except ValueError:
            QtGui.QErrorMessage("Please select a valid channel (1-2)")

    def play_vt(self):
        """Function to play current VT"""

        try:

            name = self.name.text()
            channel = int(self.channel_select.text())
            self.channel_launched = channel



            try:
                # kill current things on this channel
                self.comms.playing_vts[self.channel_launched].stop_vt()
            except KeyError:
                pass
            except AttributeError:
                pass

            if self.loop_select.isChecked():
                loop = 1
            else:
                loop = 0



            self.channel_launched = channel

            response, message = self.comms.play_video(name=name, channel=channel, loop=loop)
            print(response)
            if response:
                self.paused = False
                self.playing = True

                self.threads.append(threading.Thread(target=self.start_timer))
                for thread in self.threads:
                    thread.start()
                self.comms.playing_vts[self.channel_launched] = self
                self.time.set_playing_style()
                self.set_background_colour()


        except ValueError:
            QtGui.QErrorMessage("Please select a valid channel (1-2)")

    def pause_vt(self):
        """Function to pause/resume current VT"""
        if self.channel_launched:
            if self.playing:
                if self.paused:
                    self.comms.resume_video(channel=self.channel_launched)
                    self.paused = False
                else:
                    self.comms.pause_video(channel=self.channel_launched)
                    self.paused = True

    def stop_vt(self):
        """Function to stop current VT"""

        if self.channel_launched:
            if self.playing:
                self.paused = False
                self.playing = False
                if self.threads:
                    self.ready = False
                else:
                    self.ready = True
                self.comms.stop_video(channel=self.channel_launched)
                self.comms.playing_vts[self.channel_launched] = None
                self.channel_launched = None
                while not self.ready:
                    time.sleep(0.05)
                self.threads = []
                self.time.set_stopped_style()
                self.set_background_colour()

    def get_length_from_frames(self, frames=None, frame_rate=None):
        """Function to return the length based on the number of frames"""
        if not frames:
            frames = float(self.data['frames'])

        if not frame_rate:
            frame_rate = self.data['frame_rate']
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

        time = "%d:%02d:%02d:%d" % (hours, minutes, seconds, smpte_frames)

        return time, frames, frame_rate
