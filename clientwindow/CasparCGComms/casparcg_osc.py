# Jack Connor-Richards - 15th December 2016 - v0.1.0
# CasparCG OSC class to be used with The Match Report CasparCG Custom Client
# written by Jamie Lynch and Jack Connor-Richards for LSU Media

# Version History:
#
# v0.1.0:
# (JCR) Initial release
# (JCR) Added to the CasparCGComms package
#

from osc4py3.as_eventloop import *
from osc4py3 import oscmethod as osm
from PySide import QtCore
import time


class CasparOSC(QtCore.QObject):

    osc_update = QtCore.Signal(str)

    def __init__(self):
        super(CasparOSC, self).__init__()

        # For debugging
        print("Init CasparOSC")

        self.osc_data = ""
        self.finished = False

    def handler(self, address, argument):
        self.osc_data = ""

        address = address.split("/")

        if len(argument) > 1:
            self.osc_data += str(address[2]) + "|"
            self.osc_data += str(address[5]) + "|"
            self.osc_data += str(argument[0]) + "|"
            self.osc_data += str(argument[1])

        self.osc_update.emit(self.osc_data)

    def process_osc(self):

        # For debugging
        print("Starting Process_OSC thread")

        osc_startup()
        osc_udp_server("127.0.0.1", 6250, "CasparOSC")

        osc_method("/channel/*/stage/layer/*/file/frame", self.handler, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)

        while not self.finished:
            osc_process()
            time.sleep(0.001)

        osc_terminate()
