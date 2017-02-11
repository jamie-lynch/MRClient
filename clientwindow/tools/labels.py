"""
Match Report CasparCG Client
Version 2.0
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file contains a number of custom labels
"""

from PySide import QtGui, QtCore


class QHeadingOne(QtGui.QLabel):
    """Class based on QLabel to create <h1> heading"""

    def __init__(self, parent=None):
        super(QHeadingOne, self).__init__(parent)
        self.setStyleSheet('QHeadingOne{font: bold 15px}')


class QHeadingThree(QtGui.QLabel):
    """Class based on QLabel to create <h3> heading"""

    def __init__(self, parent=None):
        super(QHeadingThree, self).__init__(parent)
        self.setStyleSheet('QHeadingThree{font: bold}')


class QVTLabel(QtGui.QLabel):
    """Class based on QLabel to create text which changes colour when VT plays"""

    def __init__(self, videoitem, text, bold=False, parent=None):
        super(QVTLabel, self).__init__(text, parent)

        self.bold = bold

        if bold:
            self.setStyleSheet('QVTLabel{font: bold}')

        self.videoitem = videoitem
        self.videoitem.playing_signal.connect(self.set_playing_style)
        self.videoitem.stopped_signal.connect(self.set_stopped_style)

    @QtCore.Slot(object)
    def set_playing_style(self, videoitem):
        """Function to set the style to the playing format"""
        if self.videoitem == videoitem:
            if self.bold:
                self.setStyleSheet('QVTLabel{color: white; font: bold}')
            else:
                self.setStyleSheet('QVTLabel{color: white}')

    @QtCore.Slot(object)
    def set_stopped_style(self, videoitem):
        """Function to set the style to standard"""
        if self.videoitem == videoitem:
            if self.bold:
                self.setStyleSheet('QVTLabel{color: black; font: bold}')
            else:
                self.setStyleSheet('QVTLabel{color: black}')




