"""
Match Report CasparCG Client
Version 2.0
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This is the run file for the whole tool
"""

import sys
from PySide import QtGui
from clientwindow import ClientWindow, splash, tools
from os import path


def main():
    """Function to run the MRClient software"""

    # create application
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(path.join(tools.get_resources(), 'icon.ico')))

    # create a splash window
    splash_window = splash.ClientSplash(app=app)

    # change the splash message
    splash_window.change_message()

    # create an instance of the mainwindow
    client = ClientWindow(splash_window)

    # close the splash window
    splash_window.finish(client)

    # show the main window
    client.show()

    # handle close
    sys.exit(app.exec_())

# if the file is run from top-level call the main functions
if __name__ == "__main__":
    main()
