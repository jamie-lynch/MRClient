"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow.tools import QHeadingOne, QVTTextLabel
from clientwindow import tools
import time
import threading


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

        # create scroll area and add all the things
        scroll_area = QtGui.QScrollArea()
        scroll_widget = QtGui.QListWidget()
        scroll_widget.setLayout(self.vbox)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_vbox.addWidget(self.scroll_area)

        # create a list widget to hold the video items
        self.list_widget = QtGui.QListWidget()
        self.vbox.addWidget(self.list_widget)

        # get the video list
        tools.get_video_data(self.main)

        # add each of the videos from the list
        for num in sorted(self.main.data['videos'].keys()):
            self.add_video_item(self.main.data['videos'][num])

    def refresh_data(self):
        """Function ro refresh video list"""
        # clear the list widget
        self.list_widget.clear()

        # get the video list
        tools.get_video_data(self.main)

        # add each of the videos from the list
        for num in sorted(self.main.data['videos'].keys()):
            self.add_video_item(self.main.data['videos'][num])

    def add_video_item(self, item):
        """Function to add one item to the list widget"""
        new = VideoItem(main=self.main, data=item)
        self.list_widget.addItem(new)


class VideoItem(QtGui.QListWidgetItem):
    """Class containing info for one video/still item"""

    def __init__(self, main, data, parent=None):
        """Function to initialise VideoWidget class"""

        # Call the parent __init__ function
        super(VideoItem, self).__init__(parent)

        # set for convenience
        self.data = data
        self.main = main

        # create the UI elements
        self.initUI()

        # self.setFrameStyle(QtGui.QFrame.Box)

    def initUI(self):
        """Function to create the UI elements"""

        # create the layout
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # add the type and name details
        grid.addWidget(QtGui.QLabel(self.data['type']), 0, 0)
        grid.addWidget(QtGui.QLabel(self.data['name']), 1, 0)

        # add channel elements
        grid.addWidget(QtGui.QLabel("Channel"), 0, 1)
        self.channel_edit = QtGui.QLineEdit(str(self.get_channel()))
        self.channel_edit.textChanged.connect(self.check_channel)
        grid.addWidget(self.channel_select, 0, 2)

        # add the loop label and checkbox
        grid.addWidget(QtGui.QLabel("Loop?"), 1, 1)
        self.loop_select = QtGui.QCheckBox()
        grid.addWidget(self.loop_select, 1, 2)

        # length
        grid.addWidget(QtGui.QLabel("Length"), 0, 3)
        self.data['length'], self.data['frames'], self.data['frame_rate'] = self.get_length_from_frames()
        length = QtGui.QLabel(self.data['length'])
        grid.addWidget(length, 1, 4)

        # current time
        grid.addWidget(QtGui.QLabel("Remaining"), 1, 5)
        self.data['remaining_time'] = self.data['length']
        self.time = QVTTextLabel(self.data['remaining_time'])
        grid.addWidget(self.time, 1, 6)





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

        add_button = QtGui.QPushButton("Add")
        add_button.clicked.connect(self.add_vt)
        grid.addWidget(add_button, 1, 7, 1, 2)

        add_GFX_button = QtGui.QPushButton("Add w/ GFX")
        add_GFX_button.clicked.connect(self.add_GFX_vt)
        grid.addWidget(add_GFX_button, 1, 9, 1, 2)

        self.buttons = [load_button, play_button, pause_button, stop_button]
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
                self.time.set_playing_style()
                self.paused = False
                self.playing = True

                self.threads.append(threading.Thread(target=self.start_timer))
                for thread in self.threads:
                    thread.start()
                self.comms.playing_vts[self.channel_launched] = self

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

        pass

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

    def add_vt(self):
        """Function o add current VT to rundown"""

        settings = self.data.copy()
        settings['filename'] = self.data['name']
        settings['vt_type'] = self.data['type']
        settings['type'] = "vt"

        try:
            settings['channel'] = int(self.channel_select.text())
        except ValueError:
            QtGui.QErrorMessage("Please select a valid channel (1-2)")

        self.main.rundown.add_row(settings=settings, parameters=None, button_widget=None)

    def add_GFX_vt(self):
        """Function to add current VT to rundown with graphics"""
        settings = self.data.copy()
        settings['filename'] = self.data['name']
        settings['vt_type'] = self.data['type']
        settings['type'] = "vtwithgfx"
        try:
            settings['channel'] = int(self.channel_select.text())
        except ValueError:
            QtGui.QErrorMessage("Please select a valid channel (1-2)")

        self.main.rundown.add_row(settings=settings, parameters=None, button_widget=None)

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

        time = "%d:%02d:%02d:%d" % (hours, minutes, seconds, smpte_frames)

        return time, frames, frame_rate

    def start_timer(self):
        """Function to start a timer showing how long the video has been playing for"""
        frames_remaining = self.data['frames']

        while frames_remaining > 0:
            if not self.playing:
                self.time.setText(self.data['length'])
                self.ready = True
                return
            if self.paused:
                time.sleep(1.0)
                continue
            starttime = time.time()
            length, _, _ = self.get_length_from_frames(frames=frames_remaining, frame_rate=self.data['frame_rate'])
            self.time.setText(length)
            frames_remaining -= self.data['frame_rate']
            time.sleep(1.0 - ((time.time() - starttime) % 60.0))

        self.threads = []
        self.ready = True
        return















