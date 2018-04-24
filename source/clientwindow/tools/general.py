"""
Match Report CasparCG Client
Version 2.1
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file contains a number of helper functions
"""

from PySide import QtCore
from os import path, getcwd
import sys


def convert_checkstate(checkstate):
    """Function which returns a boolean based on the inputted checkstate"""
    if checkstate == QtCore.Qt.Checked:
        return True
    else:
        return False


def get_resources():
    """Function which returns the path of the datas directory"""
    resources = resource_path(path.join("datas"))
    return resources

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return path.join(path.dirname(sys.argv[0]), relative)
    return path.join(getcwd(), relative)