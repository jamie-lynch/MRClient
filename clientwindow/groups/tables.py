"""
Match Report CasparCG Client
Version 1.5
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file defines the table tab widget
"""

from PySide import QtGui, QtCore
from clientwindow import tools


class TablesWidget(QtGui.QWidget):
    """Class to define the TablesWidget"""

    def __init__(self, main, parent=None):
        """Function to initialise the class"""

        # call the parent __init__ function
        super(TablesWidget, self).__init__(parent)

        # set the tab title
        self.title = "Tables"

        # set values for convenience
        self.main = main
        self.settings = main.settings
        self.comms = main.comms

        # build the UI elements
        self.init_ui()

    def init_ui(self):
        """Function to create the UI elements"""

        # create and set layout
        hbox = QtGui.QHBoxLayout()
        self.setLayout(hbox)

        # create vbox to go in scroll
        self.vbox = QtGui.QVBoxLayout()

        # create scroll area
        scroll = QtGui.QScrollArea()
        scroll_widget = QtGui.QWidget()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)

        # add a graphics dictionary
        self.graphics = {}

        # add the three graphics sections
        self.sections_list = ['standingstable']
        self.sections = []
        for num, section in enumerate(self.sections_list):
            self.graphics[section] = []
            self.sections.append(TableGFXSection(main=self.main, tables_section=self, template=section))
            self.vbox.addWidget(self.sections[num])

        # add a spacer at the bottom
        self.vbox.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))

        # set the scroll widget to have a layout in it
        scroll_widget.setLayout(self.vbox)
        hbox.addWidget(scroll)

    def write_to_data(self):
        """Function to convert the graphics dictionary to the data required for a python dictionary"""

        # for each section in sections list
        for section in self.sections_list:
            self.main.data[section] = []

            # for each graphic
            for graphic in self.graphics[section]:

                item = graphic.tablesettings.copy()
                item['channel'] = graphic.channel_edit.text()
                item['layer'] = graphic.layer_edit.text()
                self.main.data[section].append(item)

        tools.store_data(self.main)


class TableGFXSection(QtGui.QWidget):
    """Custom class which holds standings table templates"""

    def __init__(self, main, tables_section, template, parent=None):
        """Function to initialise StandingsTablesSection"""

        # call the parent __init__ function
        super(TableGFXSection, self).__init__(parent)

        # set values for convenience
        self.main = main
        self.tables_section = tables_section
        self.comms = main.comms
        self.template = template

        # create and set layout
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # add a heading
        grid.addWidget(
            tools.QHeadingOne(
                template[0:template.index('table')].capitalize() + ' ' + template[template.index('table'):].capitalize()
            ), 0, 0
        )

        # add the Add Row button
        add_row_button = QtGui.QPushButton("Add Table")
        add_row_button.clicked.connect(self.add_row)
        grid.addWidget(add_row_button, 0, 1)

        # make a place to add templates too
        template_widget = QtGui.QWidget()
        self.template_vbox = QtGui.QVBoxLayout()
        template_widget.setLayout(self.template_vbox)
        grid.addWidget(template_widget, 1, 0, 1, 2)

        # add all of the items from last time the software was running
        for item in self.main.data[template]:
            self.add_row(tablesettings=item, save=False)

    def add_row(self, tablesettings=None, save=True):
        """Function to add new table"""

        # if settings are provided then build a new row and add to the client
        if tablesettings:

            # create a new row
            row = StandingsTableDataRow(main=self.main, tables_section=self.tables_section, gfx_section=self,
                                        template=self.template, tablesettings=tablesettings)

            # add to the graphics dictionary
            self.tables_section.graphics[self.template].append(row)

            # add to the display
            self.template_vbox.addWidget(row)

            # save the local data
            if save:
                self.tables_section.write_to_data()

        # if settings are not provided then create an instance of the AddNewStandingsTable dialog
        else:
            AddNewStandingsTable(main=self.main, gfx_section=self)

    def remove_widget(self, widget):
        """function to remove table row"""

        # remove from display
        self.template_vbox.removeWidget(widget)

        # remove from graphics dictionary
        self.tables_section.graphics[self.template].remove(widget)

        # delete object
        widget.deleteLater()

        # rewrite graphics data
        self.tables_section.write_to_data()


class StandingsTableDataRow(QtGui.QWidget):
    """Widget containing all data for a table row"""

    def __init__(self, main, tables_section, gfx_section, template, tablesettings, parent=None):
        """Function to initialise TableDataRow"""

        # call to parent __init__ function
        super(StandingsTableDataRow, self).__init__(parent)

        # set values for convenience
        self.main = main
        self.tables_section = tables_section
        self.gfx_section = gfx_section
        self.comms = main.comms
        self.template = template
        self.tablesettings = tablesettings

        # connect to the connected signal to un-freeze buttons when caspar is connected
        self.main.connected.signal.connect(self.set_enabled_disabled)

        # create tuple to keep reference to channel and layer when graphics fired
        self.fire_channel_and_layer = None, None

        # build UI elements
        self.initUI()

    def initUI(self):
        """Function to create the UI elements"""

        # create and set layout
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # add the parameters chosen
        grid.addWidget(tools.QHeadingThree('League: '), 0, 0)
        grid.addWidget(tools.QHeadingThree('Sport: '), 1, 0)
        grid.addWidget(tools.QHeadingThree('Gender: '), 0, 2)
        grid.addWidget(tools.QHeadingThree('Team: '), 1, 2)
        grid.addWidget(QtGui.QLabel(self.tablesettings['league']), 0, 1)
        grid.addWidget(QtGui.QLabel(self.tablesettings['sport']), 1, 1)
        grid.addWidget(QtGui.QLabel(self.tablesettings['gender']), 0, 3)
        grid.addWidget(QtGui.QLabel(self.tablesettings['team']), 1, 3)

        # add channel and layer edits
        grid.addWidget(QtGui.QLabel('Channel'), 0, 4)
        grid.addWidget(QtGui.QLabel('Layer'), 1, 4)
        self.channel_edit = QtGui.QLineEdit()
        self.channel_edit.setText(str(self.tablesettings['channel']))
        self.channel_edit.editingFinished.connect(self.tables_section.write_to_data)
        self.layer_edit = QtGui.QLineEdit()
        self.layer_edit.setText(str(self.tablesettings['layer']))
        self.layer_edit.editingFinished.connect(self.tables_section.write_to_data)
        grid.addWidget(self.channel_edit, 0, 5)
        grid.addWidget(self.layer_edit, 1, 5)

        # add the control buttons
        self.fire_button = QtGui.QPushButton("Fire")
        self.fire_status = "Fire"
        self.fire_button.clicked.connect(self.fire_graphic)
        grid.addWidget(self.fire_button, 0, 6)

        self.update_button = QtGui.QPushButton("Update")
        self.update_button.clicked.connect(self.update_graphic)
        grid.addWidget(self.update_button, 0, 7)

        self.add = QtGui.QPushButton("Add")
        self.add.clicked.connect(self.add_graphic)
        grid.addWidget(self.add, 1, 6)

        self.remove_button = QtGui.QPushButton("Delete")
        self.remove_button.clicked.connect(lambda: self.gfx_section.remove_widget(self))
        grid.addWidget(self.remove_button, 1, 7)

        self.fire_buttons = [self.fire_button, self.update_button]
        self.set_enabled_disabled()

    def set_enabled_disabled(self):
        """Function to set fire buttons as enabled or disabled"""
        if self.main.comms.casparcg:
            for button in self.fire_buttons:
                button.setEnabled(True)
        else:
            for button in self.fire_buttons:
                button.setDisabled(True)

    def get_parameters(self):
        """Function to sort data into parameters"""

        # try to get the data from the internet
        table_data = tools.get_table_data(self.tablesettings['url'])
        if not table_data:
            # if that doesn't work then try getting a cached copy
            try:
                table_data = self.tablesettings['data']
            except KeyError:
                pass
        # check that the data retrieved is actually a thing
        if not table_data:
            print("No data available for this table")
            return

        # if BUCS Overall data
        if "table_header_subtitle" not in table_data.keys():

            temp = {}

            temp['title'] = "BUCS 2016-17 Championship"

            temp['table_header_subtitle'] = "Overall Standings"
            temp['table_header_stat_1_title'] = ""
            temp['table_header_stat_2_tiz tle'] = ""
            temp['table_header_stat_3_title'] = ""
            temp['table_header_stat_4_title'] = ""
            temp['table_header_stat_5_title'] = ""
            temp['table_header_points_title'] = "Points"

            for num in range(1, 11):
                temp['table_row_{}_position'.format(num)] = table_data[str(num)]['Position']
                temp['table_row_{}_team_name'.format(num)] = table_data[str(num)]['University']
                temp['table_row_{}_stat_1'.format(num)] = ""
                temp['table_row_{}_stat_2'.format(num)] = ""
                temp['table_row_{}_stat_3'.format(num)] = ""
                temp['table_row_{}_stat_4'.format(num)] = ""
                temp['table_row_{}_stat_5'.format(num)] = ""
                temp['table_row_{}_points'.format(num)] = table_data[str(num)]['Total']

            table_data = temp

        parameters = ['{}={}'.format(key, val) for key, val in table_data.items()]
        parameters = '|'.join(parameters)
        return parameters

    def fire_graphic(self):
        """Function to fire graphic for table"""

        # get the parameters
        parameters = self.get_parameters()

        # if the graphic is not live
        if self.fire_status == 'Fire':

            # if the parameters were retrieved successfully, fire the graphic
            if parameters:
                response = self.main.comms.template(
                    name=self.tablesettings['filename'],
                    channel=self.channel_edit.text(),
                    layer=self.layer_edit.text(),
                    parameters=parameters
                )
                print(response)

                if 'OK' in response:
                    self.fire_status = 'Stop'
                    self.fire_button.setText('Stop')
                    self.fire_channel_and_layer = self.fire_channel_and_layer[0], self.fire_channel_and_layer[1]

        else:
            response = self.main.comms.stop_template(
                channel=self.fire_channel_and_layer[0],
                layer=self.fire_channel_and_layer[1]
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Fire'
                self.fire_button.setText('Fire')

    def update_graphic(self):
        """Function to update graphic"""
        parameters = self.get_parameters()
        if parameters:
            response = self.main.comms.template(
                name=self.tablesettings['filename'],
                channel=self.fire_channel_and_layer[0],
                layer=self.fire_channel_and_layer[1],
                parameters=parameters
            )
            print(response)

    def add_graphic(self):
        """Function to add standings table to rundown"""

        # get the parameters
        parameters = self.get_parameters()

        if parameters:
            settings = {
                'channel': self.channel_edit.text(),
                'layer': self.layer_edit.text(),
                'filename': self.tablesettings['filename'],
                'name': self.get_name(),
                'type': "graphic",
                "parameters": parameters
            }

            print(settings)
            self.main.rundown.add_row(settings=settings, button_widget=None, parameters=parameters)

    def get_name(self):
        """Function to build a name for the rundown"""
        return "{}{}{}{}".format(self.tablesettings['league'], self.tablesettings['sport'],
                                 self.tablesettings['gender'][0].capitalize(), self.tablesettings['team'])


class AddNewStandingsTable(QtGui.QDialog):
    """Class which defines a custom dialog window to define a new table graphic"""

    def __init__(self, main, gfx_section, parent=None):
        """Function to initialise the class"""

        # call parent __init_ function
        super(AddNewStandingsTable, self).__init__(parent)

        # set for convenience
        self.main = main
        self.gfx_section = gfx_section

        # create UI elements
        self.initUI()

        # removes question mark thing
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)

        # set title
        self.setWindowTitle("Settings | The Big Match CasparCG Client")

        # here goes nothing...
        self.exec_()

    def initUI(self):
        """Function to create the UI elements"""

        # create and set the layout
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        # start a row counter for adding elements to the UI
        row = 0

        # elements to choose the number of table rows
        grid.addWidget(QtGui.QLabel("Rows"))
        self.rows_choose = QtGui.QComboBox()
        self.rows_choose.addItem("Choose rows...")
        self.rows_choose.addItem("6")
        self.rows_choose.addItem("10")
        grid.addWidget(self.rows_choose, row, 1)
        row += 1

        # elements to choose the league
        grid.addWidget(QtGui.QLabel("League"), row, 0)
        self.league_combo = QtGui.QComboBox()
        self.league_options = ["Choose league...", "BUCS", "IMS"]
        for item in self.league_options:
            self.league_combo.addItem(item)
        grid.addWidget(self.league_combo, row, 1)
        row += 1

        # elements to choose the sport
        grid.addWidget(QtGui.QLabel("Sport"), row, 0)
        self.sport_combo = QtGui.QComboBox()
        self.sport_combo.addItem("Choose sport...")
        self.ims_options = [
            {"sport": "Overall", "mens": False, "womens": False, "mixed": False, "gender_options": []},
            {"sport": "Football A League", "mens": 1, "womens": False, "mixed": False, "gender_options": ["mens"]},
            {"sport": "Football B League", "mens": 1, "womens": False, "mixed": False, "gender_options": ["mens"]},
            {"sport": "Basketball", "mens": 1, "womens": 1, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Futsal", "mens": 1, "womens": False, "mixed": False, "gender_options": ["mens"]},
            {"sport": "Hockey", "mens": 1, "womens": 1, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Rugby 13's", "mens": 1, "womens": False, "mixed": False, "gender_options": ["mens"]},
            {"sport": "Softball", "mens": False, "womens": False, "mixed": 1, "gender_options": ["mixed"]},
            {"sport": "Squash", "mens": 1, "womens": 1, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "5-a-side Football", "mens": False, "womens": 1, "mixed": False, "gender_options": ["womens"]},
            {"sport": "Netball", "mens": False, "womens": 1, "mixed": False, "gender_options": ["womens"]},
            {"sport": "Rounders", "mens": False, "womens": 1, "mixed": False, "gender_options": ["womens"]},
            {"sport": "Badminton", "mens": False, "womens": False, "mixed": 1, "gender_options": ["mixed"]},
            {"sport": "Tennis", "mens": False, "womens": False, "mixed": 1, "gender_options": ["mixed"]},
            {"sport": "Volleyball", "mens": False, "womens": False, "mixed": 1, "gender_options": ["mixed"]},
            {"sport": "Lacrosee", "mens": False, "womens": False, "mixed": 1, "gender_options": ["mixed"]}
        ]
        self.bucs_options = [
            {"sport": "Overall", "mens": False, "womens": False, "mixed": False, "gender_options": []},
            {"sport": "Badminton", "mens": 4, "womens": 2, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Basketball", "mens": 4, "womens": 3, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Cricket", "mens": 1, "womens": 2, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Fencing", "mens": 1, "womens": 1, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Football", "mens": 4, "womens": 4, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Futsal", "mens": 3, "womens": 2, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Golf", "mens": False, "womens": False, "mixed": 3, "gender_options": ["mixed"]},
            {"sport": "Hockey", "mens": 5, "womens": 5, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Lacrosse", "mens": 2, "womens": 3, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Netball", "mens": False, "womens": 5, "mixed": False, "gender_options": ["womens"]},
            {"sport": "Rugby League", "mens": 3, "womens": False, "mixed": False, "gender_options": ["mens"]},
            {"sport": "Rugby Union", "mens": 4, "womens": 2, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Squash", "mens": 3, "womens": 1, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Table Tennis", "mens": 4, "womens": 2, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Tennis", "mens": 3, "womens": 3, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Volleyball", "mens": 2, "womens": 2, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "Water Polo", "mens": 1, "womens": 1, "mixed": False, "gender_options": ["mens", "womens"]},
            {"sport": "American Football", "mens": False, "womens": False, "mixed": 1, "gender_options": ["mixed"]},
            {"sport": "Ultimate Frisbee", "mens": 3, "womens": False, "mixed": False, "gender_options": ["mens", "womens"]},

        ]
        self.setup_sport_combo()
        grid.addWidget(self.sport_combo, row, 1)
        row += 1

        # elements to choose the gender
        grid.addWidget(QtGui.QLabel("Gender"), row, 0)
        self.gender_combo = QtGui.QComboBox()
        self.gender_combo.addItem("Choose gender...")
        grid.addWidget(self.gender_combo, row, 1)
        row += 1

        # elements to choose the team
        grid.addWidget(QtGui.QLabel("Level"), row, 0)
        self.team_combo = QtGui.QComboBox()
        self.team_combo.addItem("Choose team...")
        grid.addWidget(self.team_combo, row, 1)
        row += 1

        # connect the combo boxes to functions so that when changes occur, the available options are updated
        self.league_combo.currentIndexChanged.connect(self.setup_sport_combo)
        self.sport_combo.currentIndexChanged.connect(self.setup_gender_combo)
        self.gender_combo.currentIndexChanged.connect(self.setup_team_combo)

        # element to allow adding of table
        add = QtGui.QPushButton("Add")
        add.clicked.connect(self.add_table)
        grid.addWidget(add, row, 0)

        # element to cancel proceudre
        cancel = QtGui.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        grid.addWidget(cancel, row, 1)

    def setup_sport_combo(self):
        """Function which sets the available options of the sports combo box"""

        if self.league_combo.currentText() == "BUCS":
            self.sport_combo.clear()
            self.sport_combo.addItem("Choose sport...")
            for item in self.bucs_options:
                self.sport_combo.addItem(item['sport'])
        elif self.league_combo.currentText() == "IMS":
            self.sport_combo.clear()
            self.sport_combo.addItem("Choose sport...")
            for item in self.ims_options:
                self.sport_combo.addItem(item['sport'])
        else:
            self.sport_combo.clear()
            self.sport_combo.addItem("Choose sport...")

    def setup_gender_combo(self):
        """Function to setup gender combo"""
        if self.sport_combo.currentText() == "Choose sport..." or self.sport_combo.currentText() == "":
            self.gender_combo.clear()
            self.gender_combo.addItem("Choose gender...")
        else:
            type = self.league_combo.currentText()
            sport = self.sport_combo.currentText()
            if type == "BUCS":
                gender_options = [option['gender_options'] for option in self.bucs_options if option['sport'] == sport]
            else:
                gender_options = [option['gender_options'] for option in self.ims_options if option['sport'] == sport]
            self.gender_combo.clear()
            self.gender_combo.addItem("Choose gender...")
            if gender_options:
                for item in gender_options[0]:
                    self.gender_combo.addItem(item)

    def setup_team_combo(self):
        """Function to setup sport combo"""
        if self.gender_combo.currentText() == "Choose gender..." or self.gender_combo.currentText() == "":
            self.team_combo.clear()
            self.team_combo.addItem("Choose team...")
        else:
            type = self.league_combo.currentText()
            sport = self.sport_combo.currentText()
            gender = self.gender_combo.currentText()
            if type == "BUCS":
                team_options = [option[gender] for option in self.bucs_options if option['sport'] == sport]
            else:
                team_options = [option[gender] for option in self.ims_options if option['sport'] == sport]
            self.team_combo.clear()
            self.team_combo.addItem("Choose team...")
            if team_options:
                for n in range(team_options[0]):
                    self.team_combo.addItem(str(n+1))

    def get_url(self, settings):
        """Function to get the url of the json data"""

        # if its the BUCS overall table look at Jack's website
        if settings['league'] == "BUCS" and settings['sport'] == "Overall":
            url = "http://bigmatch.jcrnet.uk/tabletojson/bucs_table.json"
        # otherwise look at my website
        else:
            url = "http://bigmatch.jamielynch.net/client/tabledata/data/{}_{}_{}_{}.json".format(
                settings['league'],
                settings['sport'].lower().replace(" ", "_"),
                settings['gender'],
                settings['team']
            )

        # try getting the table data from the url
        table_data = tools.get_table_data(url)

        # if BUCS Overall data
        if "table_header_subtitle" not in table_data.keys():

            temp = {}

            temp['title'] = "BUCS 2016-17 Championship"

            temp['table_header_subtitle'] = "Overall Standings"
            temp['table_header_stat_1_title'] = ""
            temp['table_header_stat_2_tiz tle'] = ""
            temp['table_header_stat_3_title'] = ""
            temp['table_header_stat_4_title'] = ""
            temp['table_header_stat_5_title'] = ""
            temp['table_header_points_title'] = "Points"

            for num in range(1, 11):
                temp['table_row_{}_position'.format(num)] = table_data[str(num)]['Position']
                temp['table_row_{}_team_name'.format(num)] = table_data[str(num)]['University']
                temp['table_row_{}_stat_1'.format(num)] = ""
                temp['table_row_{}_stat_2'.format(num)] = ""
                temp['table_row_{}_stat_3'.format(num)] = ""
                temp['table_row_{}_stat_4'.format(num)] = ""
                temp['table_row_{}_stat_5'.format(num)] = ""
                temp['table_row_{}_points'.format(num)] = table_data[str(num)]['Total']

            table_data = temp

        # if it doesn't exist then tell the user that its not there via a dialog window
        if not table_data:
            error = QtGui.QErrorMessage()
            error.showMessage("Data cannot be found for this condition. Please create data file and try again.")
            error.setWindowTitle("Error | TBM")
            error.setModal(True)

            # removes question mark thing
            error.setWindowFlags(error.windowFlags()
                                 ^ QtCore.Qt.WindowContextHelpButtonHint)
            # show
            error.exec_()

        return url, table_data

    def add_table(self):
        """Function to add row to client"""

        # collate the settings from the combo boxes
        settings = {
            "league": self.league_combo.currentText(),
            "sport": self.sport_combo.currentText(),
            "gender": self.gender_combo.currentText(),
            "team": self.team_combo.currentText(),
            "rows": self.rows_choose.currentText()
        }

        # find the url and add to the settings
        settings['url'], settings['data'] = self.get_url(settings)

        # get the filename and default channel and layer for the corresponding number of tables
        settings['filename'] = self.main.settings['templates']['standingstable{}'.format(settings['rows'])]['filename']
        settings['channel'] = self.main.settings['templates']['standingstable{}'.format(settings['rows'])]['channel']
        settings['layer'] = self.main.settings['templates']['standingstable{}'.format(settings['rows'])]['layer']

        # tries to add the table to the client and close
        self.gfx_section.add_row(tablesettings=settings)
        if settings['data']:
            self.accept()
