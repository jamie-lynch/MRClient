"""
Match Report CasparCG Client
Version 1.5
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file contains a class surrounding graphic templates
"""

from PySide import QtGui
from clientwindow.tools import get_json

class TemplateRow(QtGui.QWidget):
    """Class which holds one template label and button as well as the function for activating the template"""
    isrundown = False
    def __init__(self, template_data, main, parent=None):
        """Function to initialise TemplateRow class"""
        super(TemplateRow, self).__init__(parent)
        self.main = main
        self.main.connected.signal\
            .connect(self.set_disabled_enabled)
        self.template_data = template_data

        hbox = QtGui.QHBoxLayout()
        self.setLayout(hbox)

        hbox.addWidget(QtGui.QLabel(template_data['name']))

        if template_data['type'] == 'single':
            self.fire_button = QtGui.QPushButton('Fire')
            self.fire_status = 'Fire'
            self.fire_button.clicked.connect(self.fire)
            if not self.main.comms.casparcg:
                self.fire_button.setDisabled(True)
            hbox.addWidget(self.fire_button)

            self.add_to_rundown_button = QtGui.QPushButton("Add")
            self.add_to_rundown_button.clicked.connect(self.add_to_rundown)
            hbox.addWidget(self.add_to_rundown_button)

        else:
            self.fire1_button = QtGui.QPushButton('Fire')
            self.fire1_button.clicked.connect(self.fire1)
            self.fire2_button = QtGui.QPushButton('Fire')
            self.fire2_button.clicked.connect(self.fire2)
            self.fire1_status = 'Fire'
            self.fire2_status = 'Fire'

            if not self.main.comms.casparcg:
                self.fire1_button.setDisabled(True)
                self.fire2_button.setDisabled(True)

            hbox.addWidget(self.fire1_button)
            hbox.addWidget(self.fire2_button)

            self.add_to_rundown_button1 = QtGui.QPushButton("Add to rundown (team1)")
            self.add_to_rundown_button1.clicked.connect(lambda: self.add_to_rundown(part=1))
            hbox.addWidget(self.add_to_rundown_button1)

            self.add_to_rundown_button2 = QtGui.QPushButton("Add to rundown (team2)")
            self.add_to_rundown_button2.clicked.connect(lambda: self.add_to_rundown(part=2))
            hbox.addWidget(self.add_to_rundown_button2)

    def set_disabled_enabled(self):
        """Function to set the fire buttons either enabled or disbaled depending on connection status"""
        if self.main.comms.casparcg:
            enabled = True
        else:
            enabled = False

        if self.template_data['type'] == 'single':
            self.fire_button.setEnabled(enabled)

        else:
            self.fire1_button.setEnabled(enabled)
            self.fire2_button.setEnabled(enabled)

    def fire(self):
        """Function to fire graphic using both teams data"""

        if self.fire_status == 'Fire':
            response = self.main.comms.template(
                name=self.template_data['filename'],
                channel=self.template_data['channel'],
                layer=self.template_data['layer'],
                parameters=self.collect_data()
                )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Stop'
                self.fire_button.setText('Stop')

        else:
            response = self.main.comms.stop_template(
                channel=self.template_data['channel'],
                layer=self.template_data['layer']
            )
            print(response)

            if 'OK' in response:
                self.fire_status = 'Fire'
                self.fire_button.setText('Fire')

    def fire1(self):
        """Function to fire graphic using team 1 data"""

        if self.fire1_status == 'Fire':
            response = self.main.comms.template(
                name=self.template_data['filename'],
                channel=self.template_data['channel'],
                layer=self.template_data['layer'],
                parameters=self.get_parameters(req_teamnum=0)
            )
            print(response)



            if 'OK' in response:
                self.fire1_status = 'Stop'
                self.fire1_button.setText('Stop')

        else:
            response = self.main.comms.stop_template(
                channel=self.template_data['channel'],
                layer=self.template_data['layer']
            )
            print(response)

            if 'OK' in response:
                self.fire1_status = 'Fire'
                self.fire1_button.setText('Fire')

    def fire2(self):
        """Function to fire graphic using team 2 data"""
        if self.fire2_status == 'Fire':
            response = self.main.comms.template(
                name=self.template_data['filename'],
                channel=self.template_data['channel'],
                layer=self.template_data['layer'],
                parameters=self.get_parameters(req_teamnum=1)
            )
            print(response)

            if 'OK' in response:
                self.fire2_status = 'Stop'
                self.fire2_button.setText('Stop')

        else:
            response = self.main.comms.stop_template(
                channel=self.template_data['channel'],
                layer=self.template_data['layer']
            )
            print(response)

            if 'OK' in response:
                self.fire2_status = 'Fire'
                self.fire2_button.setText('Fire')

    def get_parameters(self, req_teamnum=None):
        """Function to collect the correct data and assemble as a string"""
        required = self.template_data['data']
        data = get_json()

        parameters = {}

        for item in required:

            if item == "names":
                for num, team in enumerate(data['teams']):
                    if req_teamnum != None:
                        if num != req_teamnum:
                            continue
                    parameters['team_id_{}'.format(num)] = str(team['id'])
                    parameters['team_name_{}'.format(num)] = str(team['name'])
                    parameters['team_shortname_{}'.format(num)] = str(team['shortname'])
                    parameters['team_colour_{}'.format(num)] = str(team['colour'])

            if item == "lineups":
                for teamnum, team_lineup in enumerate(data['lineups']):
                    if req_teamnum != None:
                        if teamnum != req_teamnum:
                            continue
                    for playernum, player in enumerate(team_lineup['main']):
                        parameters['lineup_main_id_{}_{}'.format(teamnum, playernum)] = str(player['id'])
                        parameters['lineup_main_num_{}_{}'.format(teamnum, playernum)] = str(player['num'])
                        parameters['lineup_main_name_{}_{}'.format(teamnum, playernum)] = str(player['name'])
                        parameters['lineup_main_subbed_{}_{}'.format(teamnum, playernum)] = str(player['subbed'])
                    for playernum, player in enumerate(team_lineup['bench']):
                        parameters['lineup_bench_id_{}_{}'.format(teamnum, playernum)] = str(player['id'])
                        parameters['lineup_bench_num_{}_{}'.format(teamnum, playernum)] = str(player['num'])
                        parameters['lineup_bench_name_{}_{}'.format(teamnum, playernum)] = str(player['name'])
                        parameters['lineup_bench_subbed_{}_{}'.format(teamnum, playernum)] = str(player['subbed'])
                    for playernum, player in enumerate(team_lineup['manager']):
                        parameters['lineup_coach_id_{}_{}'.format(teamnum, playernum)] = str(player['id'])
                        parameters['lineup_coach_num_{}_{}'.format(teamnum, playernum)] = str(player['num'])
                        parameters['lineup_coach_name_{}_{}'.format(teamnum, playernum)] = str(player['name'])
                        parameters['lineup_coach_subbed_{}_{}'.format(teamnum, playernum)] = str(player['subbed'])

            if item == "scores":
                for num, score in enumerate(data['scores']):
                    if req_teamnum != None:
                        if num != req_teamnum:
                            continue
                    parameters['score_id_{}'.format(num)] = str(score['id'])
                    parameters['score_score_{}'.format(num)] = str(score['score'])

            if item == "stats":
                for statnum, stat in enumerate(data['stats']):
                    for teamnum, _ in enumerate(data['teams']):
                        if req_teamnum != None:
                            if teamnum != req_teamnum:
                                continue
                        parameters['stat_id_{}_{}'.format(teamnum, statnum)] = str(stat['id'])
                        parameters['stat_name_{}_{}'.format(teamnum, statnum)] = str(stat['name'])
                        parameters['stat_units_{}_{}'.format(teamnum, statnum)] = str(stat['units'])
                        parameters['stat_val_{}_{}'.format(teamnum, statnum)] = str(stat['vals'][teamnum]['statval'])

            if item == "events":
                for num, event in enumerate(data['events']):
                    parameters['event_id_{}'.format(num)] = str(event['id'])
                    parameters['event_icon_{}'.format(num)] = str(event['icon'])
                    parameters['event_heading_{}'.format(num)] = str(event['heading'])
                    parameters['event_team_{}'.format(num)] = str(event['team'])
                    parameters['event_player1num_{}'.format(num)] = str(event['player1num'])
                    parameters['event_player1name_{}'.format(num)] = str(event['player1name'])
                    parameters['event_player2num_{}'.format(num)] = str(event['player2num'])
                    parameters['event_player2name_{}'.format(num)] = str(event['player2name'])
                    parameters['event_text_{}'.format(num)] = str(event['text'])
                    parameters['event_time_{}'.format(num)] = str(event['time'])

            if item == "time":
                parameters['length'] = str(data['time']['length'])
                parameters['periods'] = str(data['time']['length'])
                parameters['current'] = str(data['time']['length'])
                parameters['extra'] = str(data['time']['length'])
                parameters['running'] = str(data['time']['length'])
                parameters['minutes'] = str(data['time']['length'])
                parameters['seconds'] = str(data['time']['length'])
                parameters['tenths'] = str(data['time']['length'])
                parameters['starttext'] = str(data['time']['length'])
                parameters['starttime'] = str(data['time']['length'])

            if item == "twitter":
                parameters['full_name'] = str(data['tweets']['current']['tweet_data']['full_name'])
                parameters['handle'] = str(data['tweets']['current']['tweet_data']['handle'])
                parameters['text'] = str(data['tweets']['current']['tweet_data']['text'])
                parameters['avatar'] = str(data['tweets']['current']['tweet_data']['avatar'])
                parameters['media_present'] = str(data['tweets']['current']['tweet_data']['media_present'])
                parameters['media_url'] = str(data['tweets']['current']['tweet_data']['media_url'])

        parameters = ['{}={}'.format(key, val) for key, val in parameters.items()]
        parameters = '|'.join(parameters)
        return parameters

    def add_to_rundown(self, part=None):
        """Function to add current template to rundown"""
        settings = {
            "name": self.template_data['name'],
            "filename": self.template_data['filename'],
            "layer": self.template_data['layer'],
            "channel": self.template_data['channel'],
            "type": "graphic",
            "req_teamnum": part
        }

        parameters = self.get_parameters()
        self.isrundown = True
        self.main.rundown.add_row(settings=settings, button_widget=self, parameters=parameters)

class IndividualFireButton(QtGui.QPushButton):
    """Custom pushbutton for firing Lineup graphics"""

    def __init__(self, text, data, show, main, parent=None):
        """Function to initialise LineupFireButton"""
        super(IndividualFireButton, self).__init__(parent, text=text)

        self.data = data
        self.main = main
        self.clicked.connect(self.fire)
        self.main.connected.signal.connect(self.set_connect_disconnect)

        if not show:
            self.hide()

        if not self.main.comms.casparcg:
            self.setDisabled(True)

    def set_connect_disconnect(self):
        """Function to set the fire button as enabled or disabled"""
        if self.main.comms.casparcg:
            self.setEnabled(True)
        else:
            self.setEnabled(False)

    def fire(self):
        """Function to fire graphic"""
        pass

