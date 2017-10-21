# Jack Connor-Richards - 22nd March 2017 - v0.3.0
# CasparCG OSC class to be used with The Big Match CasparCG Custom Client
# written by Jamie Lynch and Jack Connor-Richards for LSU Media

# Version History:
#
# v0.1.0:
# (JCR) Initial release
# (JCR) Added to the CasparCGComms package
#
# v0.2.0:
# (JCR) Added support for sending clip name and audio level data
#
# v0.3.0:
# (JCR) Changed osc threading model to resolve performance issues over a network
#

from osc4py3.as_comthreads import *
from osc4py3 import oscmethod as osm
from PySide.QtCore import *
import time


class CasparOSC(QObject):

    osc_framedata = Signal(str)
    osc_pathdata = Signal(str)
    osc_leveldata = Signal(str)

    def __init__(self):
        super(CasparOSC, self).__init__()

        # For debugging
        print("Init CasparOSC")

        self.osc_framedata_str = ""
        self.osc_pathdata_str = ""
        self.osc_leveldata_str = ""
        self.finished = False

    def framedata_handler(self, address, argument):
        self.osc_framedata_str = ""

        address = address.split("/")

        if len(argument) > 1:
            self.osc_framedata_str += str(address[2]) + "|"
            self.osc_framedata_str += str(address[5]) + "|"
            self.osc_framedata_str += str(argument[0]) + "|"
            self.osc_framedata_str += str(argument[1])

        self.osc_framedata.emit(self.osc_framedata_str)

    def pathdata_handler(self, address, argument):
        self.osc_pathdata_str = ""

        address = address.split("/")

        if len(argument) > 1:
            self.osc_pathdata_str += str(address[2]) + "|"
            self.osc_pathdata_str += str(address[5]) + "|"
            self.osc_pathdata_str += str(argument[0]) + "|"
            self.osc_pathdata_str += str(argument[1])
        elif len(argument) == 1:
            self.osc_pathdata_str += str(address[2]) + "|"
            self.osc_pathdata_str += str(address[5]) + "|"
            self.osc_pathdata_str += str(argument[0])
        else:
            pass

        self.osc_pathdata.emit(self.osc_pathdata_str)

    def leveldata_handler(self, address, argument):
        self.osc_leveldata_str = ""

        address = address.split("/")

        if len(argument) > 1:
            self.osc_leveldata_str += str(address[2]) + "|"
            self.osc_leveldata_str += str(address[5]) + "|"
            self.osc_leveldata_str += str(argument[0]) + "|"
            self.osc_leveldata_str += str(argument[1])
        elif len(argument) == 1:
            self.osc_leveldata_str += str(address[2]) + "|"
            self.osc_leveldata_str += str(address[5]) + "|"
            self.osc_leveldata_str += str(argument[0])
        else:
            pass

        self.osc_leveldata.emit(self.osc_leveldata_str)

    def process_osc(self):

        # For debugging
        print("Starting Process_OSC thread")

        osc_startup()
        osc_udp_server("0.0.0.0", 6250, "CasparOSC")

        osc_method("/channel/*/stage/layer/*/file/frame", self.framedata_handler, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
        osc_method("/channel/*/stage/layer/*/file/path", self.pathdata_handler, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)
        osc_method("/channel/*/mixer/audio/*/dBFS", self.leveldata_handler, argscheme=osm.OSCARG_ADDRESS + osm.OSCARG_DATA)

        while not self.finished:
            osc_process()
            time.sleep(0.08)

        osc_terminate()
