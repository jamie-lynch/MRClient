"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtCore

class Connected(QtCore.QObject):
    """Signal object for when caspar is connected"""
    signal = QtCore.Signal()
