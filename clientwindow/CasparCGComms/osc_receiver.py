import sys
import threading
from PySide import QtCore, QtGui
from clientwindow.CasparCGComms import CasparOSC


class OSCReceiver(QtCore.QObject):

    def __init__(self):
        super(OSCReceiver, self).__init__()
        self.osc = CasparOSC()

        self.videos = {1: {}, 2: {}, 3: {}, 4: {}}

        self.osc.osc_framedata.connect(self.process_output)

        t = threading.Thread(target=self.osc.process_osc, name="Process_OSC")
        t.daemon = True
        t.start()

    @QtCore.Slot(str)
    def process_output(self, oscdata):

        # split on pipe
        oscdata = oscdata.split('|')

        # pass the current frames to the video playing on the channel from the osc data
        try:
            self.videos[int(oscdata[0])][0].set_remaining_time(oscdata[2], oscdata[3])
        # catch the stray messages after you click stop
        except KeyError:
            pass
