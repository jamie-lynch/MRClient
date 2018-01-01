"""
Match Report CasparCG Client
Version 2.1
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file contains a number of helper functions
"""

from PySide import QtCore
from os import path, getcwd


def convert_checkstate(checkstate):
    """Function which returns a boolean based on the inputted checkstate"""
    if checkstate == QtCore.Qt.Checked:
        return True
    else:
        return False


def get_resources():
    """Function which returns the path of the resources directory"""
    resources = path.join(getcwd(), "resources")
    return resources
