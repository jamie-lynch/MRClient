"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtCore, QtGui
from os import path, makedirs, getcwd
import ctypes.wintypes

def convert_checkstate(checkstate):
    """Function which returns a boolean based on the inputted checkstate"""
    if checkstate == QtCore.Qt.Checked:
        return True
    else:
        return False

def get_resources():
    """Function to get and if necessary make resources folder"""
    resources = path.join(getcwd(), "resources")
    #resources = r"C:\Users\Jamie\Documents\The Big Match\TBM_CasparCG_Client\clientwindow\resources"
    return resources

