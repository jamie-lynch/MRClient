"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow.tools import QSectionLabel, QHeadingLabel
from clientwindow import tools

class AddorEditTemplateData(QtGui.QDialog):
    """Widget for adding a new setting"""

    def __init__(self, settings_window, sections, custom_templates, row=None, edit=False, parent=None):
        """Function to initialise AddNewTemplate window"""
        super(AddorEditTemplateData, self).__init__(parent)
        self.settings_window = settings_window
        self.custom_templates = custom_templates
        self.sections = sections
        self.row = row
        if self.row:
            self.data = row.data
        else:
            self.data = None
        self.init_ui(edit)

    def init_ui(self, edit):
        """Function to build AddNewTemplate window"""

        if self.data == None:
            self.data = {
                "name": None,
                "filename": None,
                "channel": None,
                "layer": None,
                "section": None,
                "data": None,
                "type": None
            }

        self.grid = QtGui.QGridLayout()
        self.setLayout(self.grid)

        row = 0

        # Details

        self.grid.addWidget(QSectionLabel("Template Details"))
        row += 1

        # template label
        self.grid.addWidget(QtGui.QLabel("Name"), row, 0)
        self.template_label = QtGui.QLineEdit()
        if self.data['name']:
            self.template_label.setText(self.data['name'])
        else:
            self.template_label.setPlaceholderText("Enter name...")
        self.grid.addWidget(self.template_label, row, 1, 1, 2)
        row += 1

        # template filename
        self.grid.addWidget(QtGui.QLabel("Filename"), row, 0)
        self.template_filename = QtGui.QLineEdit()
        if self.data['filename']:
            self.template_filename.setText(self.data['filename'])
        else:
            self.template_filename.setPlaceholderText("Enter filename...")
        self.grid.addWidget(self.template_filename, row, 1, 1, 2)
        row += 1

        # template section
        self.grid.addWidget(QtGui.QLabel("Section"), row, 0)
        self.template_section = QtGui.QComboBox()
        self.template_section.addItem("Select section...")
        for section in self.sections:
            self.template_section.addItem(section.capitalize())
        if self.data['section']:
            self.template_section.setCurrentIndex(self.sections.index(self.data['section'])+1)
        self.grid.addWidget(self.template_section, row, 1, 1, 2)
        row += 1

        # template channel
        self.grid.addWidget(QtGui.QLabel("Channel"), row, 0)
        self.template_channel = QtGui.QLineEdit()
        if self.data['channel'] or self.data['channel'] == 0:
            self.template_channel.setText(str(self.data['channel']))
        else:
            self.template_channel.setPlaceholderText("Enter Channel...")
        self.grid.addWidget(self.template_channel, row, 1, 1, 2)
        row += 1

        # template layer
        self.grid.addWidget(QtGui.QLabel("Layer"), row, 0)
        self.template_layer = QtGui.QLineEdit()
        if self.data['layer'] or self.data['layer'] == 0:
            self.template_layer.setText(str(self.data['layer']))
        else:
            self.template_layer.setPlaceholderText("Enter Layer...")
        self.grid.addWidget(self.template_layer, row, 1, 1, 2)
        row += 1

        # template type
        self.grid.addWidget(QtGui.QLabel("Type"), row, 0)
        self.template_type = QtGui.QComboBox()
        type_options = ['Select type...', 'Single', 'Double']
        for option in type_options:
            self.template_type.addItem(option)
        if self.data['type']:
            self.template_type.setCurrentIndex(type_options.index(self.data['type'].capitalize()))
        self.grid.addWidget(self.template_type, row, 1, 1, 2)
        row += 1

        # data section
        self.grid.addWidget(QSectionLabel("Data"), row, 0)
        row += 1

        # data

        self.data_box = TemplateDataBox(data=self.data)
        scroll = QtGui.QScrollArea(parent=self)
        scroll.setWidget(self.data_box)
        self.grid.addWidget(scroll, row, 0, 1, 3)
        row += 1

        # add and cancel buttons
        if edit:
            accept = QtGui.QPushButton("Okay")
            accept.clicked.connect(self.edit_template)
        else:
            accept = QtGui.QPushButton("Add")
            accept.clicked.connect(self.add_template)

        self.grid.addWidget(accept, row, 1)

        cancel = QtGui.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        self.grid.addWidget(cancel, row, 2)

        # removes question mark thing
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)

        # set title
        self.setWindowTitle('Template Settings | The Big Match CasparCG Client')

        self.setFocus()
        self.exec_()

    def mousePressEvent(self, event):
        """Clear focus from QLineEdit"""
        try:
            self.focusWidget().clearFocus()
        except:
            pass
        QtGui.QWidget.mousePressEvent(self, event)

    def edit_template(self):
        """function to confirm edit template and save settings"""
        template_data = {
            'name': self.template_label.text(),
            'filename': self.template_filename.text(),
            'section': self.template_section.currentText().lower(),
            'data': self.data_box.whats_checked(),
            'layer': self.template_layer.text(),
            'channel': self.template_channel.text(),
            'type': self.template_type.currentText().lower()
        }

        template_settings = self.settings_window.settings['templates']
        template_settings[template_data['section']].append(template_data)

        self.settings_window.update_temp_settings('templates', template_settings)
        self.accept()
        self.custom_templates.rebuild_templates(template_data, edit=True, old_row=self.row)

    def add_template(self):
        """Function to add template to system"""

        template_data = {
            'name': self.template_label.text(),
            'filename': self.template_filename.text(),
            'section': self.template_section.currentText().lower(),
            'data': self.data_box.whats_checked(),
            'layer': self.template_layer.text(),
            'channel': self.template_channel.text(),
            'type': self.template_type.currentText().lower()
        }

        template_settings = self.settings_window.settings['templates']
        template_settings[template_data['section']].append(template_data)

        self.settings_window.update_temp_settings('templates', template_settings)
        self.accept()
        self.custom_templates.rebuild_templates(template_data)


class TemplateDataBox(QtGui.QWidget):
    """class which holds the data for the checkboxes"""

    def __init__(self, data, parent=None):
        """Function to initialise TemplateDataBox class"""
        super(TemplateDataBox, self).__init__(parent)
        self.data = data
        self.init_ui()

    def init_ui(self):
        """Function to construct TemplateDataBox class"""
        options = ["names", "lineups", "scores", "stats", "events", "time"]

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        self.boxes = {}
        for option in options:
            box = QtGui.QCheckBox(option)
            if option in self.data['data']:
                box.setChecked(True)
            self.boxes[option] = box
            vbox.addWidget(box)

    def generate_data_box(self):
        """Function which looks at all of the available data and build the grid based on it"""

        data_box = QtGui.QWidget()
        grid = QtGui.QGridLayout()
        data_box.setLayout(grid)

        options = self.get_options()

        row = 0
        for title in options:
            col = 0

            grid.addWidget(title['widget'], row, col)

            col += 1
            row += 1

            if type(title['keys']) == list:
                for sub in title['keys']:
                    grid.addWidget(sub['widget'], row, col)
                    row += 1
                col += 1

            if type(title['keys']) == dict:
                grid.addWidget(title['keys']['widget'], row, col)
                row += 1
                col += 1

                if type(title['keys']['keys']) == list:
                    for sub in title['keys']['keys']:
                        grid.addWidget(sub['widget'], row, col)
                        row += 1
                    col += 1

        return data_box

    def get_options(self):
        """Function which returns a dictionary of options and keys"""
        data = tools.get_json()

        options = []

        for key in data.keys():

            curr = {}
            curr['name'] = key
            curr['widget'] = QtGui.QCheckBox(key)

            curr['keys'] = []

            if type(data[key]) == dict:
                for key2 in data[key].keys():
                    curr_2 = {}
                    curr_2['name'] = key2
                    curr_2['widget'] = QtGui.QCheckBox(key2)
                    curr_2['keys'] = []
                    curr['keys'].append(curr_2)

            elif type(data[key]) == list:
                curr_data = data[key][0]

                curr_2 = {}
                curr_2['name'] = key[:-1]
                curr_2['widget'] = QtGui.QCheckBox(key[:-1])
                curr_2['keys'] = []
                curr['keys'] = curr_2

                for key3 in curr_data.keys():
                    curr_3 = {}
                    curr_3['name'] = key3
                    curr_3['widget'] = QtGui.QCheckBox(key3)
                    curr_3['keys'] = []

                    curr_2['keys'].append(curr_3)

            else:
                curr['keys'] = ""

            options.append(curr)

        return options

    def whats_checked(self):
        """Function which returns the data element of the template settings"""
        checked = []
        for key, val in self.boxes.items():
            if val.isChecked():
                checked.append(key)
        return checked

