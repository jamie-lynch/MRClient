"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow.tools import QHeadingLabel, \
        QSectionLabel, \
        QVTTextLabel
import time
import threading

class VTGFXRundownItem(QtGui.QFrame):
    """Item containing all data for a rundown item"""

    def __init__(self, settings, main, curr_id, parent=None):
        """Function to intialise RundownItem"""
        super(VTGFXRundownItem, self).__init__(parent)

        self.threads = []
        self.stopped = True
        self.ready = True

        self.id = curr_id

        self.set_background_colour()

        self.settings = settings

        self.main = main

        self.setFrameStyle(QtGui.QFrame.Box)

        self.rundown = main.rundown
        self.settings = settings

        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)
        self.vt_item = VTRundownItem(vt_data=self.settings['vt_data'], vtgfx_item=self)
        self.vbox.addWidget(self.vt_item)

        self.graphic_items = []
        self.graphic_times = {}
        self.command_num = 0
        for graphic in self.settings['graphics']:
            new = GraphicRundownItem(gfx_data=graphic, vtgfx_item=self)
            self.graphic_items.append(new)
            self.vbox.addWidget(new)
            self.add_to_command_list(graphic)

    def set_background_colour(self):
        """Function to set the correct background colour"""
        if self.stopped:
            if int(self.id) % 2:
                self.setStyleSheet('VTGFXRundownItem{background-color: #f4a4f4}')
            else:
                self.setStyleSheet('VTGFXRundownItem{background-color: #b386ef}')
        else:
            self.setStyleSheet('VTGFXRundownItem{background-color: #81f76f}')

    def add_to_command_list(self, graphic):
        """Function to create a list of commands"""
        temp = {}
        temp['command'] = "play"
        temp['channel'] = graphic['channel']
        temp['layer'] = graphic['layer']
        temp['filename'] = graphic['filename']

        parameters = graphic['parameters']
        parameters = ['{}={}'.format(key, val) for key, val in parameters.items()]
        parameters = '|'.join(parameters)
        temp['parameters'] = parameters

        temp['frames'] = self.get_frames_from_length(length=graphic['starttime'], frame_rate=self.settings['vt_data']['frame_rate'])

        self.graphic_times[self.command_num] = temp
        self.command_num += 1

        if graphic['endtime']:
            temp = {}
            temp['command'] = "stop"
            temp['channel'] = graphic['channel']
            temp['layer'] = graphic['layer']
            temp['filename'] = graphic['filename']

            parameters = graphic['parameters']
            parameters = ['{}={}'.format(key, val) for key, val in parameters.items()]
            parameters = '|'.join(parameters)
            temp['parameters'] = parameters

            temp['frames'] = self.get_frames_from_length(length=graphic['endtime'],
                                                         frame_rate=self.settings['vt_data']['frame_rate'])

            self.graphic_times[self.command_num] = temp
            self.command_num += 1

    def update_command_list(self):
        """Function to update command list when graphic is removed"""
        self.graphic_times = {}
        self.command_num = 0
        for graphic in self.graphic_items:
            self.add_to_command_list(graphic.settings)

    def get_frames_from_length(self, length, frame_rate):
        """Function to return the length based on the number of frames"""
        hours, minutes, seconds, smpte_frames = length.split(':')

        hours = int(hours) * frame_rate * 60 * 60
        minutes = int(minutes) * frame_rate * 60
        seconds = int(seconds) * frame_rate

        frames = hours + minutes + seconds + int(smpte_frames)

        return frames

    def remove_graphic(self, item):
        """Function to remove a graphic item"""
        if self.vt_item.playing:
            error = QtGui.QErrorMessage()
            error.showMessage("Cannot remove item while playing")
            error.exec_()
            return

        self.graphic_items.remove(item)
        self.vbox.removeWidget(item)
        item.deleteLater()

    def execute_commands(self):
        """Function to execute graphic commands"""
        frames_elapsed = 0
        self.to_play = self.graphic_times.copy()
        self.stopped = False

        to_discard = []
        while frames_elapsed < self.vt_item.data['frames']:
            if self.stopped:
                self.ready = True
                self.threads = []
                return
            if self.vt_item.paused:
                time.sleep(1.0)
                continue
            starttime = time.time()
            for num, command in self.to_play.items():
                if command['frames'] <= frames_elapsed:
                    if command['command'] == "play":
                        response = self.main.comms.template(
                                name=command['filename'],
                                channel=command['channel'],
                                layer=command['layer'],
                                parameters=command['parameters']
                        )
                        print(response)
                        to_discard.append(num)
                    elif command['command'] == "stop":
                        self.main.comms.stop_template(
                            channel=command['channel'],
                            layer=command['layer']
                        )
                        to_discard.append(num)
                    else:
                        pass
            for num in to_discard:
                del self.to_play[num]
            to_discard = []

            frames_elapsed += self.vt_item.data['frame_rate']
            time.sleep(1.0 - ((time.time() - starttime) % 60.0))

        self.threads = []
        self.ready = True

    def stop_vt(self):
        """Function to call vt stop function when required"""
        self.vt_item.stop_vt()
        if self.threads:
            self.ready = False
        else:
            self.ready = True
        self.stopped = True

        while not self.ready or not self.vt_item.ready:
            time.sleep(0.05)

        self.threads = []
        self.set_background_colour()

class VTRundownItem(QtGui.QWidget):
    """Class to show data and control buttons for VT item in rundown"""

    def __init__(self, vt_data, vtgfx_item, parent=None):
        """Function to initialise VTRundownItem"""
        super(VTRundownItem, self).__init__(parent)

        self.channel_launched = None
        self.paused = False
        self.playing = False
        self.threads = []
        self.ready = True

        self.vtgfx_item = vtgfx_item
        self.rundown = vtgfx_item.rundown
        self.settings = vt_data
        self.main = vtgfx_item.main
        self.comms = self.main.comms
        self.main.connected.signal.connect(self.set_enabled_disabled)

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        data = vt_data
        self.data = data

        self.name = QtGui.QLabel(data['name'])
        grid.addWidget(self.name, 0, 0, 1, 2)

        # type
        type = QtGui.QLabel(data['vt_type'])
        grid.addWidget(type, 1, 0)

        # length
        grid.addWidget(QtGui.QLabel("Length"), 1, 3)
        self.data['length'], _, _ = self.get_length_from_frames(frames=self.data['frames'],
                                                                frame_rate=self.data['frame_rate'])
        length = QtGui.QLabel(self.data['length'])
        grid.addWidget(length, 1, 4)

        # current time
        grid.addWidget(QtGui.QLabel("Remaining"), 1, 5)
        self.data['remaining_time'] = self.data['length']
        self.time = QVTTextLabel(self.data['remaining_time'])
        grid.addWidget(self.time, 1, 6)

        channel_label = QtGui.QLabel("Channel")
        grid.addWidget(channel_label, 0, 2)


        self.channel_select = QtGui.QLineEdit(str(self.settings['channel']))
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
        stop_button.clicked.connect(self.vtgfx_item.stop_vt)
        grid.addWidget(stop_button, 0, 10)

        # edit
        self.edit_button = QtGui.QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_vt_item)
        self.edit_button.hide()
        grid.addWidget(self.edit_button, 1, 7)

        # remove
        self.remove_button = QtGui.QPushButton("Remove")
        self.remove_button.clicked.connect(lambda: self.remove_row(self.vtgfx_item))
        grid.addWidget(self.remove_button, 1, 8)

        # up & down
        self.up_button = QtGui.QPushButton("Up")
        self.up_button.clicked.connect(lambda: self.rundown.move_row(widget=self.vtgfx_item, direction="up"))
        grid.addWidget(self.up_button, 1, 9)

        self.down_button = QtGui.QPushButton("Down")
        self.down_button.clicked.connect(lambda: self.rundown.move_row(widget=self.vtgfx_item, direction="down"))
        grid.addWidget(self.down_button, 1, 10)

        self.fire_buttons = [load_button, play_button, pause_button, stop_button]
        self.set_enabled_disabled()

    def remove_row(self, widget):
        """Function to remove row"""
        if self.playing:
            error = QtGui.QErrorMessage()
            error.showMessage("Cannot remove item while playing")
            error.exec_()
            return
        else:
            self.rundown.remove_row(widget=widget)

    def check_channel(self):
        """Function to check channel set to something sensible"""
        if self.playing:
            self.channel_select.setText(str(self.settings['channel']))
            error = QtGui.QErrorMessage()
            error.showMessage("Cannot change channel while playing")
            error.exec_()
            return
        channel = int(self.channel_select.text())
        if self.settings['type'] == "AUDIO" and channel != 4:
            self.channel_select.setText("4")
            self.settings['channel'] = 4
            error = QtGui.QErrorMessage()
            error.showMessage("Audio track must be on channel 4")
            error.exec_()
            return
        else:
            if channel not in [1, 2]:
                self.channel_select.setText("1")
                self.settings['channel'] = 1
                error = QtGui.QErrorMessage()
                error.showMessage("Movie/Still track must be on channels 1 or 2")
                error.exec_()
                return
        for graphic in self.vtgfx_item.graphic_items:
            graphic.set_channel(int(channel))
            self.settings['channel'] = int(channel)
        self.vtgfx_item.update_command_list()

    def edit_vt_item(self):
        """Function to edit settings for vt item"""
        pass

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
                self.vtgfx_item.threads.append(threading.Thread(target=self.vtgfx_item.execute_commands))
                for thread in self.threads:
                    thread.start()
                for thread in self.vtgfx_item.threads:
                    thread.start()
                self.comms.playing_vts[self.channel_launched] = self.vtgfx_item
                self.time.set_playing_style()
                self.vtgfx_item.set_background_colour()

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
                while not self.ready:
                    time.sleep(0.05)
                self.time.set_stopped_style()
                self.comms.clear_channel(self.channel_launched)
                self.channel_launched = None

    def set_enabled_disabled(self):
        """Function to set fire buttons enabled or disabled"""
        if self.main.comms.casparcg:
            for button in self.fire_buttons:
                button.setEnabled(True)
        else:
            for button in self.fire_buttons:
                button.setDisabled(True)

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

    def start_timer(self):
        """Function to start a timer showing how long the video has been playing for"""

        frames_remaining  = self.data['frames']

        while frames_remaining > 0:
            if not self.playing:
                self.time.setText(self.data['length'])
                self.threads = []
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
        self.ready = True
        self.threads = []
        return

class GraphicRundownItem(QtGui.QFrame):
    """Class to hold all graphic data and controls for rundown item"""

    def __init__(self, gfx_data, vtgfx_item, parent=None):
        """Function to initialise GraphicRundownItem"""
        super(GraphicRundownItem, self).__init__(parent)

        self.setFrameStyle(QtGui.QFrame.Box)
        self.setLineWidth(0)

        self.settings = gfx_data
        self.vtgfx_item = vtgfx_item
        self.rundown = vtgfx_item.rundown
        self.main = vtgfx_item.main
        self.main.connected.signal.connect(self.set_enabled_disabled)

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # name
        grid.addWidget(QtGui.QLabel("Label: "), 0, 0)
        grid.addWidget(QtGui.QLabel(self.settings['label']), 0, 1)

        # filename
        grid.addWidget(QtGui.QLabel("Name: "), 1, 0)
        grid.addWidget(QtGui.QLabel(self.settings['name']), 1, 1)

        # fire
        self.fire_button = QtGui.QPushButton("Fire")
        self.fire_status = "Fire"
        self.fire_button.clicked.connect(self.fire_graphic)
        grid.addWidget(self.fire_button, 0, 2)

        # time
        grid.addWidget(QtGui.QLabel("Time: "), 0, 3)
        grid.addWidget(QtGui.QLabel(self.settings['starttime']), 0, 4)

        # end
        grid.addWidget(QtGui.QLabel(self.settings['endtime']), 1, 4)


        # edit
        self.edit_button = QtGui.QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_graphic_item)
        self.edit_button.hide()
        grid.addWidget(self.edit_button, 0, 5)

        # remove
        self.remove_button = QtGui.QPushButton("Remove")
        #self.remove_button.clicked.connect(lambda: self.vtgfx_item.remove_graphic(self))
        grid.addWidget(self.remove_button, 0, 6)
        self.remove_button.hide()

        # channel
        grid.addWidget(QtGui.QLabel("Channel: "), 1, 2)
        self.channel_label = QtGui.QLabel(str(self.settings['channel']))
        grid.addWidget(self.channel_label, 1, 3)

        # layer
        grid.addWidget(QtGui.QLabel("Layer: "), 1, 5)
        grid.addWidget(QtGui.QLabel(str(self.settings['layer'])), 1, 6)

        self.fire_buttons = [self.fire_button]
        self.set_enabled_disabled()

    def set_channel(self, channel):
        """Function to set channel and update settings"""
        self.settings['channel'] = channel
        self.channel_label.setText(str(self.settings['channel']))

    def fire_graphic(self):
        """function to fire graphic"""
        settings = self.settings
        parameters = self.settings['parameters']


        if self.fire_status == 'Fire':
            response = self.main.comms.template(
                name=settings['filename'],
                channel=settings['channel'],
                layer=settings['layer'],
                parameters=parameters
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Stop'
                self.fire_button.setText('Stop')

        else:
            response = self.main.comms.stop_template(
                channel=settings['channel'],
                layer=settings['layer']
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Fire'
                self.fire_button.setText('Fire')

    def edit_graphic_item(self):
        """function to edit rundown item"""
        pass

    def set_enabled_disabled(self):
        """Function to set fire buttons enabled or disabled"""
        if self.main.comms.casparcg:
            for button in self.fire_buttons:
                button.setEnabled(True)
        else:
            for button in self.fire_buttons:
                button.setDisabled(True)