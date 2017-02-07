"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui

class QSectionLabel(QtGui.QLabel):
    """Section label with stylesheet"""

    def __init__(self, parent=None):
        super(QSectionLabel, self).__init__(parent)
        self.setStyleSheet('QSectionLabel{font: bold 15px}')

class QHeadingLabel(QtGui.QLabel):
    """Section label with stylesheet"""

    def __init__(self, parent=None):
        super(QHeadingLabel, self).__init__(parent)
        self.setStyleSheet('QHeadingLabel{font: bold}')

class QVTTextLabel(QtGui.QLabel):
    """Section label with stylesheet"""

    def __init__(self, parent=None):
        super(QVTTextLabel, self).__init__(parent)

    def set_playing_style(self):
        """Function to set the style to the playing format"""
        self.setStyleSheet('QVTTextLabel{color: red}')

    def set_stopped_style(self):
        """Function to set the style to standard"""
        self.setStyleSheet('QVTTextLabel{color: black}')
