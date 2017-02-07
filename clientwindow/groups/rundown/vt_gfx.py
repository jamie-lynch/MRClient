"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow.tools import QHeadingLabel, QSectionLabel


class VideoGraphics(QtGui.QDialog):
    """Dialog window for settings video graphics"""
    graphic_items = []
    def __init__(self, settings, button_widget, parameters, main):
        """Function to initialise VideoGraphics widget"""
        super(VideoGraphics, self).__init__()

        self.graphic_items = []


        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        self.main = main
        self.vt_data = settings

        # name
        grid.addWidget(QtGui.QLabel("VT: "), 0, 0)
        name_label = QtGui.QLabel(self.vt_data['name'])
        grid.addWidget(name_label, 0, 1)

        # length
        grid.addWidget(QtGui.QLabel("Length: "), 1, 0)
        length_label = QtGui.QLabel(self.vt_data['length'])
        grid.addWidget(length_label, 1, 1)

        # GFX
        grid.addWidget(QHeadingLabel("Graphics"), 2, 0)
        add_graphic_button = QtGui.QPushButton("Add Graphic")
        add_graphic_button.clicked.connect(self.add_graphic)
        grid.addWidget(add_graphic_button, 2, 1)

        scroll_area = QtGui.QScrollArea()

        # create widget for scroll area
        scroll_widget = QtGui.QWidget()
        self.graphics_vbox = QtGui.QVBoxLayout()
        scroll_widget.setLayout(self.graphics_vbox)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        self.graphics_vbox.setAlignment(QtCore.Qt.AlignTop)

        grid.addWidget(scroll_area, 3, 0, 1, 2)

        self.okay_button = QtGui.QPushButton("Ok")
        self.okay_button.clicked.connect(self.add_vtgfx_item)
        grid.addWidget(self.okay_button, 5, 0)

        self.cancel_button = QtGui.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        grid.addWidget(self.cancel_button, 5, 1)

        # removes question mark thing
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)

        # set title
        self.setWindowTitle("Settings | The Big Match CasparCG Client")
        self.exec_()

    def add_graphic(self, gfx_data=None):
        """Function to add graphic to vt rundown"""
        if gfx_data:
            new = GraphicItem(vt_data=self.vt_data, gfx_data=gfx_data, vtgfx_window=self)
            self.graphic_items.append(new)
            self.graphics_vbox.addWidget(new)
        else:
            response = NewGraphic(main=self.main, video_graphics=self)
            print(response)

    def remove_item(self, item):
        """Function to remove item from list and display"""
        self.graphic_items.remove(item)
        self.graphics_vbox.removeWidget(item)
        item.deleteLater()

    def add_vtgfx_item(self):
        """Function to add this item to the rundown"""
        settings = {}
        settings['type'] = "vtwithgfx"
        settings['build'] = True
        settings['vt_data'] = self.vt_data
        settings['graphics'] = []

        for graphic in self.graphic_items:
            settings['graphics'].append(graphic.data)


        self.main.rundown.add_row(settings=settings)
        self.accept()

class GraphicItem(QtGui.QWidget):
    """Widget to hold data for one graphic"""

    def __init__(self, vt_data, gfx_data, vtgfx_window):
        """Function to initialise GraphicItem"""
        super(GraphicItem, self).__init__()
        self.vtgfx_window = vtgfx_window
        self.data = gfx_data
        hbox = QtGui.QHBoxLayout()
        self.setLayout(hbox)

        hbox.addWidget(QtGui.QLabel(gfx_data['label']))
        hbox.addWidget(QtGui.QLabel(gfx_data['name']))
        hbox.addWidget(QtGui.QLabel(gfx_data['starttime']))
        hbox.addWidget(QtGui.QLabel(gfx_data['endtime']))

        remove_button = QtGui.QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.vtgfx_window.remove_item(self))
        hbox.addWidget(remove_button)

class NewGraphic(QtGui.QDialog):
    """Dialog for setting new graphic settings"""

    def __init__(self, main, video_graphics):
        """Function to initialise NewGraphic dialog"""
        super(NewGraphic, self).__init__()

        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)
        self.main = main
        self.graphics = self.main.settings['vt_gfx']
        self.video_graphics = video_graphics


        # Label
        self.grid.addWidget(QtGui.QLabel("Label:"), 0, 0)
        self.label_edit = QtGui.QLineEdit()
        self.grid.addWidget(self.label_edit, 0, 1)

        # Start Time
        self.grid.addWidget(QtGui.QLabel("Start time: "), 1, 0)
        self.time_edit = QtGui.QLineEdit("00:00:00:00")
        self.grid.addWidget(self.time_edit, 1, 1)

        # End time
        self.grid.addWidget(QtGui.QLabel("End Time: "), 2, 0)
        self.end_time = QtGui.QLineEdit("")
        self.grid.addWidget(self.end_time, 2, 1)

        # Name
        self.grid.addWidget(QtGui.QLabel("Graphic: "), 3, 0)
        self.name_select = QtGui.QComboBox()
        self.name_select.addItem("Select Graphic...")
        for _, item in self.graphics.items():
            self.name_select.addItem(item['name'])
        self.grid.addWidget(self.name_select, 3, 1)

        # Layer
        self.grid.addWidget(QtGui.QLabel("Layer: "), 5, 0)
        self.layer_edit = QtGui.QLineEdit("10")
        self.grid.addWidget(self.layer_edit, 5, 1)

        # Parameters
        self.grid.addWidget(QtGui.QLabel("Parameters:"), 6, 0)
        self.graphics_widget = QtGui.QWidget()
        self.name_select.currentIndexChanged.connect(lambda: self.add_parameters(self.name_select.currentText()))
        self.grid.addWidget(self.graphics_widget, 7, 0, 2, 1)

        # Buttons
        okay = QtGui.QPushButton("Okay")
        okay.clicked.connect(self.add_graphics)
        self.grid.addWidget(okay, 10, 0)

        cancel = QtGui.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        self.grid.addWidget(cancel, 10, 1)



        # removes question mark thing
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)

        # set title
        self.setWindowTitle("Settings | The Big Match CasparCG Client")
        self.exec_()

    def add_parameters(self, name):
        """Function to display corresponding parameters to name chosen"""
        self.grid.removeWidget(self.graphics_widget)
        self.graphics_widget.deleteLater()
        self.graphics_widget = QtGui.QWidget()
        gfx_grid = QtGui.QGridLayout()
        self.graphics_widget.setLayout(gfx_grid)
        self.current = self.graphics[name]
        self.parameters = {}
        for num, parameter in enumerate(self.current['parameters']):
            parameter_name = QtGui.QLabel(parameter)
            parameter_edit = QtGui.QLineEdit()
            self.parameters[parameter] = parameter_edit
            gfx_grid.addWidget(parameter_name, num, 0)
            gfx_grid.addWidget(parameter_edit, num, 1)
        self.grid.addWidget(self.graphics_widget, 7, 0, 2, 2)

    def add_graphics(self):
        """Function to add current graphic"""
        data = {}
        data['starttime'] = self.time_edit.text()
        data['endtime'] = self.end_time.text()
        data['name'] = self.name_select.currentText()
        data['channel'] = self.video_graphics.vt_data['channel']
        data['layer'] = self.layer_edit.text()
        data['label'] = self.label_edit.text()
        data['filename'] = self.graphics[self.name_select.currentText()]['filename']
        temp_data = {}
        for name, edit in self.parameters.items():
            temp_data[name] = edit.text()
        data['parameters'] = temp_data
        self.video_graphics.add_graphic(gfx_data=data)
        self.accept()
