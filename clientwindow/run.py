"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

import sys

from PySide import QtGui

from clientwindow import ClientWindow
from clientwindow import splash, choose_mode, tools
from clientwindow.login import LoginWindow


def main(login=True):

    app = QtGui.QApplication(sys.argv)

    if login:

        login = LoginWindow()

        if login.exec_() != QtGui.QDialog.Accepted:
            pass

    splash_window = splash.ClientSplash(app=app)
    settings = tools.get_settings()

    choose = choose_mode.ChooseMode(settings=settings)

    if not choose.exec_():
            return

    splash_window.change_message()
    client = ClientWindow(splash_window)
    splash_window.finish(client)
    client.show()
    sys.exit(app.exec_())

main(login=False)

