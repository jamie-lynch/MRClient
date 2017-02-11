"""
Match Report CasparCG Client
Version 2.0
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file holds the classes to build the videos tab
"""

from PySide import QtGui, QtCore
from clientwindow.tools import QHeadingOne, QVTLabel
from clientwindow import tools


class VideoWidget(QtGui.QWidget):
    """Widget for VT Playback"""

    def __init__(self, main, parent=None):
        """Function to initialise the class"""

        # call to the __init__ if the parent function
        super(VideoWidget, self).__init__(parent)

        # set the widget title
        self.title = "Video"

        # set for convenience
        self.main = main
        self.comms = main.comms

        # connect to the connected signal so that data is refreshed
        self.main.connected.signal.connect(self.refresh_data)

        # Build the UI elements
        self.init_ui()

    def init_ui(self):
        """Create the UI elements"""

        # create the main layout
        main_vbox = QtGui.QVBoxLayout()
        main_vbox.addWidget(QHeadingOne("Videos"))
        self.setLayout(main_vbox)

        # create layout to go in the scroll area
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.setAlignment(QtCore.Qt.AlignTop)

        # create a list to store widgets in to allow vbox to be cleared
        self.videos = []

        # create scroll area and add all the things
        scroll = QtGui.QScrollArea()
        scroll_widget = QtGui.QWidget()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)
        scroll_widget.setLayout(self.vbox)
        main_vbox.addWidget(scroll)

        # get the video list
        tools.get_video_data(self.main)

        # add each of the videos from the list
        for num in sorted(self.main.data['videos'].keys()):
            self.add_video_item(self.main.data['videos'][num])

    def refresh_data(self):
        """Function ro refresh video list"""
        # clear the list widget
        self.clear()

        # set videos to be empty
        self.videos = []

        # get the video list
        tools.get_video_data(self.main)

        # add each of the videos from the list
        for num in sorted(self.main.data['videos'].keys()):
            self.add_video_item(self.main.data['videos'][num])

    def add_video_item(self, item):
        """Function to add one item to the list widget"""
        new = VideoItem(main=self.main, data=item)
        self.vbox.addWidget(new)
        self.videos.append(new)

    def clear(self):
        """Function to remove all of the elements from the vbox"""

        for item in self.videos:
            self.vbox.removeWidget(item)
            item.deleteLater()


class VideoItem(QtGui.QFrame):
    """Class containing info for one video/still item"""

    playing_signal = QtCore.Signal(object)
    stopped_signal = QtCore.Signal(object)

    def __init__(self, main, data, parent=None):
        """Function to initialise VideoWidget class"""

        # Call the parent __init__ function
        super(VideoItem, self).__init__(parent)

        # set for convenience
        self.data = data
        self.main = main
        self.osc = self.main.osc
        self.comms = self.main.comms

        # set values
        self.playing = False
        self.paused = False
        self.loaded = False

        # create the UI elements
        self.initUI()

        # set border
        self.setFrameStyle(QtGui.QFrame.Box)

    def initUI(self):
        """Function to create the UI elements"""

        # create the layout
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # add the type and name details
        grid.addWidget(QVTLabel(self, self.data['type']), 0, 0)
        name = QVTLabel(self, self.data['name'])
        name.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        grid.addWidget(name, 0, 1)

        # add the loop label and checkbox
        grid.addWidget(QVTLabel(self, "Loop?"), 1, 0)
        self.loop_select = QtGui.QCheckBox()
        grid.addWidget(self.loop_select, 1, 1)

        # add channel elements
        channel = QVTLabel(self, "Channel")
        grid.addWidget(channel, 0, 2)
        self.channel_edit = QtGui.QLineEdit(str(self.get_channel()))
        self.channel_edit.textChanged.connect(self.check_channel)
        self.channel_edit.setFixedWidth(60)
        grid.addWidget(self.channel_edit, 0, 3)

        # add layer elements
        grid.addWidget(QVTLabel(self, "Layer"), 1, 2)
        self.layer_edit = QtGui.QLineEdit("0")
        self.layer_edit.setFixedWidth(60)
        grid.addWidget(self.layer_edit, 1, 3)

        # length
        grid.addWidget(QVTLabel(self, "Length", bold=True), 0, 4)
        self.data['length'], self.data['frames'], self.data['frame_rate'] = self.get_length_from_frames()
        length = QVTLabel(self, self.data['length'])
        length.setFixedWidth(80)
        length.setAlignment(QtCore.Qt.AlignCenter)
        grid.addWidget(length, 0, 5)

        # current time
        grid.addWidget(QVTLabel(self, "Remaining", bold=True), 1, 4)
        self.time = QVTLabel(self, "")
        self.time.setFixedWidth(80)
        self.time.setAlignment(QtCore.Qt.AlignCenter)
        grid.addWidget(self.time, 1, 5)

        # buttons

        load_button = QtGui.QPushButton("Load")
        load_button.clicked.connect(self.load_vt)
        grid.addWidget(load_button, 0, 6)

        play_button = QtGui.QPushButton("Play")
        play_button.clicked.connect(self.play_vt)
        grid.addWidget(play_button, 0, 7)

        pause_button = QtGui.QPushButton("Pause/Resume")
        pause_button.clicked.connect(self.pause_vt)
        grid.addWidget(pause_button, 0, 8)

        stop_button = QtGui.QPushButton("Stop")
        stop_button.clicked.connect(self.stop_vt)
        grid.addWidget(stop_button, 0, 9)

        add_button = QtGui.QPushButton("Add")
        add_button.clicked.connect(self.add_vt)
        grid.addWidget(add_button, 1, 6, 1, 2)

        add_GFX_button = QtGui.QPushButton("Add with Graphics")
        add_GFX_button.clicked.connect(lambda: self.add_vt(gfx=True))
        grid.addWidget(add_GFX_button, 1, 8, 1, 2)

        self.fire_buttons = [load_button, play_button, pause_button, stop_button]
        self.set_enabled_disabled()

    def get_channel(self):
        """Function to return default channel"""
        if self.data['type'] == "AUDIO":
            return 4
        else:
            return 1

    def check_channel(self):
        """Function to check channel set to something sensible"""

        # set the message and channel number
        msg = None
        channel = self.channel_edit.text()

        # do some checks
        if self.data['type'] == "AUDIO" and channel != "4":
                self.channel_select.setText("4")
                msg = "Audio track must be on channel 4"

        elif self.data['type'] == "MOVIE" and channel not in ["1","2"]:
                self.channel_select.setText("1")
                msg = "Movie/Still track must be on channels 1 or 2"

        elif self.data['type'] == "STILL" and channel not in ["1", "2"]:
                self.channel_select.setText("1")
                msg = "Movie/Still track must be on channels 1 or 2"

        # if there's an error then report it
        if msg:
            error = QtGui.QErrorMessage(msg)
            error.showMessage()
            error.exec_()

    def set_enabled_disabled(self):
        """Function to set whether the buttons are enabled or disabled"""
        if self.comms.casparcg:
            for button in self.fire_buttons:
                button.setEnabled(True)
        else:
            for button in self.fire_buttons:
                button.setDisabled(True)

    def load_vt(self):
        """Function to load current VT"""
        try:
            channel = int(self.channel_edit.text())
            self.channel_launched = channel

            self.osc.videos[int(self.channel_launched)].stop_vt()

            self.comms.load_video(name=self.data['name'], channel=channel)
            self.osc.videos[int(self.channel_launched)] = self
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
                self.osc.videos[int(self.channel_launched)].stop_vt()
            except KeyError:
                print("No video on channel {} to stop".format(self.channel_launched))

            if self.loop_select.isChecked():
                loop = 1
            else:
                loop = 0
            self.channel_launched = channel

            response, message = self.comms.play_video(name=self.data['name'], channel=channel, loop=loop)
            print(response)
            if response:
                self.playing = True
                self.playing_signal.emit(self)
                self.paused = False
                self.loaded = False
                self.osc.videos[int(self.channel_launched)] = self
                self.set_background_colour()

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
            print("stop: {}".format(self.data['name']))
            self.comms.stop_video(channel=self.channel_launched)
            del self.osc.videos[int(self.channel_launched)]
            self.channel_launched = None
            self.time.setText("")
            self.playing = False
            self.stopped_signal.emit(self)
            self.loaded = False
            self.set_background_colour()

    def add_vt(self, gfx=False):
        """Function to add current VT to rundown"""

        self.settings = self.data.copy()
        self.settings['filename'] = self.data['name']
        self.settings['template'] = self.data['type']

        try:
            self.settings['channel'] = int(self.channel_edit.text())
            self.settings['layer'] = int(self.layer_edit.text())
        except ValueError:
            QtGui.QErrorMessage("Please select a valid channel (1-2)")

        if gfx:
            self.settings['type'] = "vtgfx"
            self.settings['graphics'] = []
            response = tools.GetVTGraphics(main=self.main, video=self)
            if not response.result():
                return
            print(self.settings['graphics'])
        else:
            self.settings['type'] = 'vt'

        self.main.rundown.add_row(settings=self.settings)

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
        seconds = int((frames-hours*60*60*frame_rate - minutes*60*frame_rate) / frame_rate)
        smpte_frames = int((frames-hours*60*60*frame_rate - minutes*60*frame_rate - seconds*frame_rate))

        time = "%02d:%02d:%02d:%02d" % (hours, minutes, seconds, smpte_frames)

        return time, frames, frame_rate

    def set_remaining_time(self, current_frame, total_frames):
        """Function to set the time remaining"""

        if not self.loaded:

            # find the number of frames remaining
            remaining_frames = int(total_frames) - int(current_frame)

            # find the time remaining
            remaining_time, _, _ = self.get_length_from_frames(frames=remaining_frames, frame_rate=self.data['frame_rate'])

            # sets the time
            self.time.setText(remaining_time)

    def set_background_colour(self):
        """Function to set the correct background colour"""
        if self.playing:
            self.setStyleSheet('VideoItem{background-color: #009600}')
        else:
            self.setStyleSheet('VideoItem{background-color: #f0f0f0}')
