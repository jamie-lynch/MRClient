"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from PySide import QtGui, QtCore
from clientwindow import tools
from clientwindow.tools import QSectionLabel, QHeadingLabel, TemplateRow
from os import path


class TwitterWidget(QtGui.QWidget):
    """Widget for Lineup graphics"""

    def __init__(self, main, parent=None, data=None):
        """init function fro NameWidget"""
        super(TwitterWidget, self).__init__(parent)
        self.title = "Twitter"
        self.main = main
        self.comms = main.comms
        self.init_ui(data)

    def init_ui(self, data=None):
        """ sets base content of widget """

        # get data if required
        if not data:
            data = tools.get_json()

        # create layout
        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)

        # Data
        self.vbox.addWidget(QSectionLabel("Data"))
        self.data_section = DataSection(data=data, settings=self.main.settings, main=self.main)
        self.vbox.addWidget(self.data_section)

        # Templates
        self.vbox.addWidget(QSectionLabel("Templates"))
        self.templates_section = TemplatesSection(settings=self.main.settings, twitter=self, main=self.main)
        self.vbox.addWidget(self.templates_section)

        self.vbox.addItem(QtGui.QSpacerItem(1, 1, vData=QtGui.QSizePolicy.Expanding))

    def refresh_data(self, data=None):
        """Function to refresh data from JSON"""

        if not data:
            data = tools.get_json()

        self.vbox.removeWidget(self.data_section)
        self.data_section.deleteLater()
        self.data_section = DataSection(data=data, settings=self.main.settings, main=self.main)
        self.vbox.insertWidget(1, self.data_section)

class DataSection(QtGui.QWidget):
    """Class which holds all of the time data"""

    def __init__(self, data, settings, main, parent=None):
        """Function to initialise DataSection class"""
        super(DataSection, self).__init__(parent)
        self.init_ui(data, settings, main)

    def init_ui(self, data, settings, main):
        """Function which builds DataSection class"""

        self.main = main

        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        # Current Live Tweets
        vbox.addWidget(QSectionLabel("Current"))

        try:
            self.current = TweetDataWidget(
                data=data['tweets']['current']['tweet_data'],
                resources=settings['resources'],
                data_section=self,
                main=self.main,
                fire=False
            )

        except KeyError:
            self.current = TweetDataWidget(
                data=data['tweets']['shortlist'][0]['tweet']['tweet_data'],
                resources=settings['resources'],
                data_section=self,
                main=self.main,
                fire=False
            )
            self.main.data['tweets']['current'] = {}
            self.main.data['tweets']['current']['tweet_data'] = data['tweets']['shortlist'][0]['tweet']['tweet_data']


        vbox.addWidget(self.current)

        # shortlist
        vbox.addWidget(QSectionLabel("Shortlist"))


        scroll = QtGui.QScrollArea()
        shortlist = QtGui.QWidget()

        shortlist_vbox = QtGui.QVBoxLayout()
        shortlist.setLayout(shortlist_vbox)

        for num, tweet in enumerate(data['tweets']['shortlist']):
            shortlist_vbox.addWidget(TweetDataWidget(
                data=tweet['tweet']['tweet_data'],
                resources=settings['resources'],
                data_section=self,
                main=self.main
                )
            )

        scroll.setWidget(shortlist)
        vbox.addWidget(scroll)

    def make_live(self, data):
        """Function to change current tweet"""
        self.main.data['tweets']['current']['tweet_data'] = data
        tools.store_json(self.main.data)
        self.current.update_values(data, fire=False)
        self.update()

class TweetDataWidget(QtGui.QGroupBox):
    """Class which holds all of the tweet data for one occurrence"""

    def __init__(self, data, resources, data_section, main, fire=True, parent=None):
        """Function to initialise the TweetDataWidget"""
        super(TweetDataWidget, self).__init__(parent)

        self.resources = tools.get_resources()

        self.data_section = data_section
        self.data = data
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        self.avatar = QtGui.QLabel()
        self.avatar.setPixmap(
            QtGui.QPixmap(
                path.join(
                    resources,
                    'twitter_avatars',
                    path.split(data['avatar'])[1]
                )
            ).scaledToHeight(40)
        )

        grid.addWidget(self.avatar, 0, 0, 2, 1)

        self.full_name = QtGui.QLabel(data['full_name'])
        grid.addWidget(self.full_name, 0, 1)

        self.handle = QtGui.QLabel(data['handle'])
        grid.addWidget(self.handle, 1, 1)


        self.text = QtGui.QLabel()
        self.text.setFont(QtGui.QFont('OpenSansEmoji'))
        self.text.setText(data['text'])
        grid.addWidget(self.text, 0, 2, 2, 1)

        self.media = QtGui.QLabel()
        self.media.setMinimumWidth(100)
        if data['media_present'] == "1":
            self.media.setPixmap(
                QtGui.QPixmap(
                    path.join(
                        resources,
                        'twitter_media',
                        path.split(data['media_url'])[1]
                    )
                ).scaledToHeight(60)
            )
        grid.addWidget(self.media, 0, 3, 2, 1)

        self.fire_button = QtGui.QPushButton("Make Live")
        self.fire_button.clicked.connect(self.make_live)
        grid.addWidget(self.fire_button, 0, 4)

        if not fire:
            self.fire_button.hide()

        self.fire_button.setMaximumWidth(100)

    def make_live(self):
        """Function to make the current tweet live"""
        self.data_section.make_live(self.data)

    def update_values(self, data, fire=True):
        """Function to update the values to something new"""

        self.avatar.setPixmap(
            QtGui.QPixmap(
                path.join(
                    self.resources,
                    'twitter_avatars',
                    path.split(data['avatar'])[1]
                )
            )
        )

        self.full_name.setText(data['full_name'])
        self.handle.setText(data['handle'])
        self.text.setText(data['text'])

        if not fire:
            self.fire_button.hide()

        if data['media_present'] == "1":
            self.media.setPixmap(
                QtGui.QPixmap(
                    path.join(
                        self.resources,
                        'twitter_media',
                        path.split(data['media_url'])[1]
                    )
                ).scaledToHeight(60)
            )
        else:
            self.media.setText(" ")

class TemplatesSection(QtGui.QWidget):
    """Class which holds all of the time data"""

    def __init__(self, settings, twitter, main, parent=None):
        """Function to initialise DataSection class"""
        super(TemplatesSection, self).__init__(parent)
        self.twitter = twitter
        self.main = main
        self.init_ui(settings)

    def init_ui(self, settings):
        """Function which builds DataSection class"""

        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)

        self.templates_container = QtGui.QWidget()
        templates_vbox = QtGui.QVBoxLayout()
        self.templates_container.setLayout(templates_vbox)
        self.vbox.addWidget(self.templates_container)

        for template in settings['templates']['twitter']:
            templates_vbox.addWidget(TemplateRow(template_data=template, main=self.main))

    def refresh_data(self, settings):
        """Function to refresh templates data"""

        self.vbox.removeWidget(self.templates_container)
        self.templates_container.deleteLater()

        self.templates_container = QtGui.QWidget()
        templates_vbox = QtGui.QVBoxLayout()
        self.templates_container.setLayout(templates_vbox)
        self.vbox.addWidget(self.templates_container)

        for template in settings['templates']['twitter']:
            templates_vbox.addWidget(TemplateRow(template_data=template, main=self.main))







