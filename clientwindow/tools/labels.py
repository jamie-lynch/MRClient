"""
Match Report CasparCG Client
Version 1.5
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file contains a number of custom labels
"""

from PySide import QtGui


class QHeadingOne(QtGui.QLabel):
    """Class based on QLabel to create <h1> heading"""

    def __init__(self, parent=None):
        super(QHeadingOne, self).__init__(parent)
        self.setStyleSheet('QHeadingLabel{font: bold 15px}')


class QHeadingThree(QtGui.QLabel):
    """Class based on QLabel to create <h3> heading"""

    def __init__(self, parent=None):
        super(QHeadingThree, self).__init__(parent)
        self.setStyleSheet('QSectionLabel{font: bold}')


class QVTTextLabel(QtGui.QLabel):
    """Class based on QLabel to create text which changes colour when VT plays"""

    def __init__(self, parent=None):
        super(QVTTextLabel, self).__init__(parent)

    def set_playing_style(self):
        """Function to set the style to the playing format"""
        self.setStyleSheet('QVTTextLabel{color: red}')

    def set_stopped_style(self):
        """Function to set the style to standard"""
        self.setStyleSheet('QVTTextLabel{color: black}')
