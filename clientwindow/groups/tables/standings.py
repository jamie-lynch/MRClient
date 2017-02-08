"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow import tools


class StandingsTablesSection(QtGui.QWidget):
    """Custom class which holds standings table templates"""

    def __init__(self, tables_section, parent=None):
        """Function to initialise StandingsTablesSection"""

        super(StandingsTablesSection, self).__init__(parent)

        self.settings = tables_section.main.settings
        self.tables_section = tables_section
        self.main = tables_section.main
        self.table_rows = []

        # vbox containing templates
        self.vbox = QtGui.QVBoxLayout()

        self.table_id = 0
        for table_id, table in self.settings['tables']['standings'].items():
            row = StandingsTableDataRow(table_id=table_id, settings=table, standings_tables_section=self)
            self.vbox.addWidget(row)
            self.table_id = int(table_id) + 1

        # vbox for templates vbox and add button
        main_vbox = QtGui.QVBoxLayout()
        self.setLayout(main_vbox)

        # add heading labels
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QLabel("Type"))
        hbox.addWidget(QtGui.QLabel("Sport"))
        hbox.addWidget(QtGui.QLabel("Gender"))
        hbox.addWidget(QtGui.QLabel("Level"))
        main_vbox.addLayout(hbox)

        # add templates to main_vbox
        main_vbox.addLayout(self.vbox)

        # add add button
        main_vbox.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))
        add = QtGui.QPushButton("Add new")
        add.clicked.connect(self.add_new_table)
        main_vbox.addWidget(add)

    def add_new_table(self, settings=None):
        """Function to add new table"""
        if settings:

            data, url = self.get_data(settings)
            if not data:
                return False
            else:
                row = StandingsTableDataRow(table_id=self.table_id, settings=settings, data=data, standings_tables_section=self)
                self.table_rows.append(row)
                self.vbox.addWidget(row)

                settings['url'] = url
                self.tables_section.main.settings['tables']['standings'][str(self.table_id)] = settings
                tools.store_json(self.tables_section.main.data)
                tools.store_settings(self.tables_section.main.settings)

                table_data = settings.copy()
                table_data['data'] = data
                self.tables_section.main.data['tables']['standings'][str(self.table_id)] = table_data
                tools.store_json(self.tables_section.main.data)

                self.table_id += 1
                return True

        else:
            response = AddNewStandingsTable(standings_table_section=self)
            print(response)

    def get_data(self, settings):
        """Function to get current data from the internet and save to data file"""

        if settings['type'] == "BUCS":
            # bucs sports
            if settings['sport'] == "Overall":
                url = "http://bigmatch.jcrnet.uk/tabletojson/bucs_table.json"
            else:
                url = ""

        else:
            # ims sports
            url = ""

        table_data = tools.get_table_data(url)

        if not table_data:
            url = "http://bigmatch.jamielynch.net/client/tabledata/data/{}_{}_{}_{}.json".format(
                settings['type'],
                settings['sport'].lower().replace(" ", "_"),
                settings['gender'],
                settings['level']
            )
            table_data = tools.get_table_data(url)

        if not table_data:
            error = QtGui.QErrorMessage()
            error.showMessage("Data cannot be found for this condition. Please create data file and try again.")
            error.setWindowTitle("Error | TBM")
            error.setModal(True)

            # removes question mark thing
            error.setWindowFlags(error.windowFlags()
                                ^ QtCore.Qt.WindowContextHelpButtonHint)
            error.exec_()

        return table_data, url

    def remove_table(self, widget):
        """function to remove table row"""

        del self.tables_section.main.settings['tables']['standings'][str(widget.table_id)]
        del self.tables_section.main.data['tables']['standings'][str(widget.table_id)]
        tools.store_json(self.tables_section.main.data)
        tools.store_settings(self.tables_section.main.settings)
        self.vbox.removeWidget(widget)
        widget.deleteLater()

class StandingsTableDataRow(QtGui.QWidget):
    """Widget containing all data for a table row"""

    def __init__(self, table_id, settings, standings_tables_section, data=None, parent=None):
        """Function to initialise TableDataRow"""
        super(StandingsTableDataRow, self).__init__(parent)

        self.main = standings_tables_section.main
        self.main.connected.signal.connect(self.set_enabled_disabled)

        self.settings = settings
        self.table_id = table_id
        if data:
            self.data = data
        else:
            self.data = tools.get_json()
            self.data = self.data['tables']['standings'][table_id]


        self.hbox = QtGui.QHBoxLayout()
        self.setLayout(self.hbox)
        self.template_section = standings_tables_section
        self.main = self.template_section.main

        self.type_label = QtGui.QLabel(self.settings['type'])
        self.sport_label = QtGui.QLabel(self.settings['sport'])
        self.gender_label = QtGui.QLabel(self.settings['gender'])
        self.level_label = QtGui.QLabel(self.settings['level'])

        self.hbox.addWidget(self.type_label)
        self.hbox.addWidget(self.sport_label)
        self.hbox.addWidget(self.gender_label)
        self.hbox.addWidget(self.level_label)

        self.fire_button = QtGui.QPushButton("Fire")
        self.fire_status = "Fire"
        self.fire_button.clicked.connect(self.fire_graphic)
        self.hbox.addWidget(self.fire_button)

        self.add_to_button = QtGui.QPushButton("Add")
        self.add_to_button.clicked.connect(self.add_to_rundown)
        self.hbox.addWidget(self.add_to_button)

        self.remove_button = QtGui.QPushButton("Remove")
        self.remove_button.clicked.connect(lambda: self.template_section.remove_table(widget=self))
        self.hbox.addWidget(self.remove_button)

        self.set_enabled_disabled()

    def set_enabled_disabled(self):
        """Function to set fire button as enabled or disabled"""
        if self.main.comms.casparcg:
            self.fire_button.setEnabled(True)
        else:
            self.fire_button.setDisabled(True)

    def get_data(self):
        """Function to get data from the internets"""
        self.data = tools.get_json()
        self.data = self.data['tables']['standings'][str(self.table_id)]

    def get_parameters(self):
        """Function to sort data into parameters"""
        self.get_data()
        data = self.data

        parameters = {}

        if "table_header_subtitle" not in data['data'].keys():

            parameters['title'] = "BUCS 2016-17 Championship"

            parameters['table_header_subtitle'] = "Overall Standings"
            parameters['table_header_stat_1_title'] = ""
            parameters['table_header_stat_2_tiz tle'] = ""
            parameters['table_header_stat_3_title'] = ""
            parameters['table_header_stat_4_title'] = ""
            parameters['table_header_stat_5_title'] = ""
            parameters['table_header_points_title'] = "Points"

            for num in range(1, 11):
                parameters['table_row_{}_position'.format(num)] = data['data'][str(num)]['Position']
                parameters['table_row_{}_team_name'.format(num)] = data['data'][str(num)]['University']
                parameters['table_row_{}_stat_1'.format(num)] = ""
                parameters['table_row_{}_stat_2'.format(num)] = ""
                parameters['table_row_{}_stat_3'.format(num)] = ""
                parameters['table_row_{}_stat_4'.format(num)] = ""
                parameters['table_row_{}_stat_5'.format(num)] = ""
                parameters['table_row_{}_points'.format(num)] = data['data'][str(num)]['Total']

        else:
            parameters = self.data['data']

        parameters = ['{}={}'.format(key, val) for key, val in parameters.items()]
        parameters = '|'.join(parameters)
        return parameters

    def add_to_rundown(self):
        """Function to add standings table to rundown"""

        template_settings = self.template_section.main.settings['templates']['standard']['standings_table{}'.format(self.settings['rows'])]

        name = "{}{}{}{}".format(
            self.settings['type'],
            self.settings['sport'],
            self.settings['gender'][0].capitalize(),
            self.settings['level']
        )

        settings = {}
        settings['channel'] = template_settings['channel']
        settings['layer'] = template_settings['layer']
        settings['filename'] = template_settings['filename']
        settings['name'] = name
        settings['type'] = "graphic"



        parameters = self.get_parameters()

        self.main.rundown.add_row(settings=settings, button_widget=None, parameters=parameters)

    def fire_graphic(self):
        """Function to fire graphic for table"""

        template_settings = self.template_section.main.settings['templates']['standard']['standings_table{}'.format(self.settings['rows'])]
        # format parameters data
        parameters = self.get_parameters()

        if self.fire_status == 'Fire':
            response = self.main.comms.template(
                name=template_settings['filename'],
                channel=template_settings['channel'],
                layer=template_settings['layer'],
                parameters=parameters
            )
            print(response)


            if 'OK' in response:
                self.fire_status = 'Stop'
                self.fire_button.setText('Stop')

        else:
            response = self.main.comms.stop_template(
                channel=template_settings['channel'],
                layer=template_settings['layer']
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Fire'
                self.fire_button.setText('Fire')

class AddNewStandingsTable(QtGui.QDialog):
    """Custom dialog window to add new table"""

    def __init__(self, standings_table_section, parent=None):
        """Function to initialise table"""

        super(AddNewStandingsTable, self).__init__(parent)

        # removes question mark thing
        self.setWindowFlags(self.windowFlags()
                            ^ QtCore.Qt.WindowContextHelpButtonHint)

        # set title
        self.setWindowTitle("Settings | The Big Match CasparCG Client")

        self.standings_table_section = standings_table_section

        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        row = 0

        grid.addWidget(QtGui.QLabel("Rows"))
        self.rows_choose = QtGui.QComboBox()
        self.rows_choose.addItem("Choose rows...")
        self.rows_choose.addItem("6")
        self.rows_choose.addItem("10")
        grid.addWidget(self.rows_choose, row, 1)
        row += 1

        # league
        grid.addWidget(QtGui.QLabel("League"), row, 0)
        self.league_combo = QtGui.QComboBox()
        self.league_options = ["Choose league...", "BUCS", "IMS"]
        for item in self.league_options:
            self.league_combo.addItem(item)
        grid.addWidget(self.league_combo, row, 1)
        row += 1

        # sport
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

        # gender
        grid.addWidget(QtGui.QLabel("Gender"), row, 0)
        self.gender_combo = QtGui.QComboBox()
        self.gender_combo.addItem("Choose gender...")
        grid.addWidget(self.gender_combo, row, 1)
        row += 1

        # team
        grid.addWidget(QtGui.QLabel("Level"), row, 0)
        self.team_combo = QtGui.QComboBox()
        self.team_combo.addItem("Choose team...")
        grid.addWidget(self.team_combo, row, 1)
        row += 1

        self.league_combo.currentIndexChanged.connect(self.setup_sport_combo)
        self.sport_combo.currentIndexChanged.connect(self.setup_gender_combo)
        self.gender_combo.currentIndexChanged.connect(self.setup_team_combo)

        # control buttons
        add = QtGui.QPushButton("Add")
        add.clicked.connect(self.add_table)
        grid.addWidget(add, row, 0)

        cancel = QtGui.QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        grid.addWidget(cancel, row, 1)

        self.exec_()

    def setup_sport_combo(self):
        """Function to setup sport combo"""
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

    def add_table(self):
        """Function to add row to client"""
        settings = {
            "type": self.league_combo.currentText(),
            "sport": self.sport_combo.currentText(),
            "gender": self.gender_combo.currentText(),
            "level": self.team_combo.currentText(),
            "rows": self.rows_choose.currentText()
        }


        response = self.standings_table_section.add_new_table(settings=settings)
        print(response)
        if response:
            self.accept()
