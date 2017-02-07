"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui

class SaveRundown(QtGui.QFileDialog):
    """Class which allows user to save the current rundown"""

    def __init__(self, parent=None):
        """Function to initialise SaveRundown class"""
        super(SaveRundown, self).__init__(parent)
        pass

class LoadRundown(QtGui.QFileDialog):
    """Class which allows the user to load a rundown from file"""

    def __init__(self, parent=None):
        """Function to initialse LoadRundown class"""
        super(LoadRundown, self).__init__(parent)