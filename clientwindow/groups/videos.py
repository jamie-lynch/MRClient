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

    def __init__(self, main, parent=None, data=None):
        """init function fro NameWidget"""
        super(VideoWidget, self).__init__(parent)

        self.title = "Video"
        self.comms = main.comms
        self.main = main

        self.main_vbox = QtGui.QVBoxLayout()
        self.main_vbox.addWidget(QHeadingOne("Videos"))
        self.setLayout(self.main_vbox)

        self.main.connected.signal.connect(self.refresh_data)
        self.init_ui(data)

    def init_ui(self, data=None):
        """ sets base content of widget """
        if not data:
            data = tools.get_json(comms=self.comms)

        # create layout
        self.vbox = QtGui.QVBoxLayout()
        self.vbox.setAlignment(QtCore.Qt.AlignTop)

        # create scroll area and add all the things
        self.scroll_area = QtGui.QScrollArea()
        scroll_widget = QtGui.QWidget()
        scroll_widget.setLayout(self.vbox)
        self.scroll_area.setWidget(scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.main_vbox.addWidget(self.scroll_area)

        self.videos = data['videos']

        for num, video in data['videos'].items():
            try:
                new = VideoItem(data=video, comms=self.comms, main=self.main)
                self.vbox.addWidget(new)
            except ZeroDivisionError:
                pass

    def refresh_data(self, data=None):
        """Function ro refresh video list"""
        # remove scroll area
        try:
            self.main_vbox.removeWidget(self.scroll_area)
            self.scroll_area.deleteLater()
        except AttributeError:
            pass
        finally:
            self.init_ui()

class VideoItem(QtGui.QFrame):
    """Class containing info for one video/still item"""

    channel_launched = None
    paused = False
    playing = False
    ready = True

    def __init__(self, data, comms, main, parent=None):
        """Function to initialise VideoWidget class"""
        super(VideoItem, self).__init__(parent)

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        self.data = data
        self.main = main
        self.comms = comms

        self.setFrameStyle(QtGui.QFrame.Box)

        self.threads = []

        # details

        self.name = QtGui.QLabel(data['name'])
        grid.addWidget(self.name, 0, 0, 1, 2)

        # type
        type = QtGui.QLabel(data['type'])
        grid.addWidget(type, 1, 0)

        # length
        grid.addWidget(QtGui.QLabel("Length"), 1, 3)
        self.data['length'], self.data['frames'], self.data['frame_rate'] = self.get_length_from_frames()
        length = QtGui.QLabel(self.data['length'])
        grid.addWidget(length, 1, 4)

        # current time
        grid.addWidget(QtGui.QLabel("Remaining"), 1, 5)
        self.data['remaining_time'] = self.data['length']
        self.time = QVTTextLabel(self.data['remaining_time'])
        grid.addWidget(self.time, 1, 6)

        channel_label = QtGui.QLabel("Channel")
        grid.addWidget(channel_label, 0, 2)

        channel = self.get_channel()
        self.channel_select = QtGui.QLineEdit(str(self.get_channel()))
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
        channel = self.channel_select.text()
        print(channel)
        print(self.data['type'])
        if self.data['type'] == "AUDIO":
            if channel != "4":
                self.channel_select.setText("4")
                error = QtGui.QErrorMessage()
                error.showMessage("Audio track must be on channel 4")
                error.exec_()
                return
        elif self.data['type'] == "MOVIE":
            if channel not in ["1","2"]:
                self.channel_select.setText("1")
                error = QtGui.QErrorMessage()
                error.showMessage("Movie/Still track must be on channels 1 or 2")
                error.exec_()
                return
        elif self.data['type'] == "STILL":
            if channel not in ["1", "2"]:
                self.channel_select.setText("1")
                error = QtGui.QErrorMessage()
                error.showMessage("Movie/Still track must be on channels 1 or 2")
                error.exec_()
                return


    def set_enabled_disabled(self):
        """Function to set whether the buttons are enabled or disabled"""
        if self.comms.casparcg:
            for button in self.buttons:
                button.setEnabled(True)
        else:
            for button in self.buttons:
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















