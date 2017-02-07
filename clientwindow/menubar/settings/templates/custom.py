"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow.tools import QHeadingLabel, QSectionLabel
from clientwindow.menubar.settings.templates import new_templates

class CustomSettingsBox(QtGui.QWidget):
    """Class to hold custom settings"""

    def __init__(self, sections, settings_window, parent=None):
        """Function to initialise CustomSettingsBox"""

        self.sections = sections
        self.settings_window = settings_window
        super(CustomSettingsBox, self).__init__(parent)
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        add_new_button = QtGui.QPushButton("Add New")
        add_new_button.clicked.connect(self.add_new_section)
        vbox.addWidget(add_new_button)

        self.scroll_area = QtGui.QScrollArea()
        self.current_templates = CurrentCustomTemplates(sections = sections, settings_window=settings_window, custom_templates=self)
        self.scroll_area.setWidget(self.current_templates)
        vbox.addWidget(self.scroll_area)


    def add_new_section(self):
        """Function which opens AddNewTemplate dialog and handles response"""
        response = new_templates.AddorEditTemplateData(settings_window=self.settings_window, sections=self.sections, custom_templates=self)

    def rebuild_templates(self, template_data, edit=False, old_row=None):
        """Function which rebuilds the current custom settings box when new templates are added"""
        if edit:
            self.current_templates.templates_section[old_row.data['section']].remove_template_row(row=old_row)
        self.current_templates.add_template(template_data)

class CurrentCustomTemplates(QtGui.QWidget):
    """Class which holds all of the current custom templates"""

    def __init__(self, sections, settings_window, custom_templates, parent=None):
        """Function to initialise CurrentCustomTempaltes class"""

        super(CurrentCustomTemplates, self).__init__(parent)

        self.templates_section = {}
        self.custom_templates = custom_templates
        self.settings_window = settings_window

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        for section in sections:
            vbox.addWidget(QHeadingLabel(section.capitalize()))
            section_vbox = SectionVBox(section, settings_window, custom_templates=self.custom_templates)
            self.templates_section[section] = section_vbox
            vbox.addLayout(section_vbox)

    def add_template(self, template_data):
        """function to add template to section"""
        section_vbox = self.templates_section[template_data['section']]
        section_vbox.addWidget(TemplateRow(data=template_data, settings_window=self.settings_window, parent_vbox=section_vbox, custom_templates=self.custom_templates))

class SectionVBox(QtGui.QVBoxLayout):
    """Custom VBoxLayout class for current tempaltes"""

    def __init__(self, section, settings_window, custom_templates, parent=None):
        """Function to initialise SectionVBox"""

        super(SectionVBox, self).__init__(parent)
        data = settings_window.settings['templates'][section]

        self.settings_window = settings_window
        self.custom_templates = custom_templates

        self.setSpacing(0)

        for template in data:
            self.addWidget(TemplateRow(template, self, settings_window=settings_window, custom_templates=self.custom_templates))

    def remove_template_row(self, row):
        """Function to remove template row"""
        self.removeWidget(row)
        row.deleteLater()
        template_settings = self.settings_window.settings['templates']
        template_settings[row.data['section']].remove(row.data)
        self.settings_window.update_temp_settings('templates', template_settings)

class TemplateRow(QtGui.QWidget):
    """Class which holds parts for one template row"""

    def __init__(self, data, parent_vbox, settings_window, custom_templates, parent=None):
        """Function to initialise TemplateRow"""
        super(TemplateRow, self).__init__(parent)
        self.parent_vbox = parent_vbox
        self.data = data
        self.settings_window = settings_window
        self.custom_templates = custom_templates

        hbox = QtGui.QHBoxLayout()
        self.setLayout(hbox)

        hbox.addWidget(QtGui.QLabel(data['name']))

        edit = QtGui.QPushButton("Edit")
        edit.clicked.connect(self.edit_template_data)
        hbox.addWidget(edit)

        delete = QtGui.QPushButton("Delete")
        delete.clicked.connect(self.delete_template_row)
        hbox.addWidget(delete)

    def delete_template_row(self):
        """Function to remove the row from the vbox"""
        self.parent_vbox.remove_template_row(row=self)

    def edit_template_data(self):
        """Function to create edit template data window and handle response"""
        response = new_templates.AddorEditTemplateData(settings_window=self.settings_window, sections=self.custom_templates.sections,
                                                       custom_templates=self.custom_templates, row=self, edit=True)
