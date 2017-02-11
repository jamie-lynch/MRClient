"""
Match Report CasparCG Client
Version 2.0
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file defines a number of helper functions around CasparCG
"""

from PySide import QtCore


class Connected(QtCore.QObject):
    """Class which defines a signal when a connection to CasparCG is established"""

    # create the signal
    signal = QtCore.Signal()
