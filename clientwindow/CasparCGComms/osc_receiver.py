import sys
import threading
from PySide import QtCore, QtGui
from clientwindow.CasparCGComms import CasparOSC


class OSCReceiver(QtCore.QObject):

    def __init__(self):
        super(OSCReceiver, self).__init__()
        osc = CasparOSC()

        osc.osc_update.connect(self.print_output)

        t = threading.Thread(target=osc.process_osc, name="Process_OSC")
        t.daemon = True
        t.start()

    @QtCore.Slot(str)
    def print_output(self, oscdata):
        print("Received via OSC: " + oscdata)


