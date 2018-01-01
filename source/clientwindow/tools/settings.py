"""
Match Report CasparCG Client
Version 2.1
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file defines a number of helper functions around the settings
"""

from os import path
import json
from clientwindow.tools.general import get_resources


def get_settings():
    """Function which returns settings as a python dictionary"""

    # get the resources filepath
    resources = get_resources()

    # open the settings file
    with open(path.join(resources, 'settings.json'), 'r') as fp:
        settings = json.load(fp)

    return settings


def get_bucs_league_settings():
    """Return BUCS league settings as dictionary"""

    # get the resources filepath
    resources = get_resources()

    # open the settings file
    with open(path.join(resources, 'bucs_league_data.json'), 'r') as fp:
        league_settings = json.load(fp)

    return league_settings


def store_settings(settings):
    """Function which writes settings to file"""

    # get the resources filepath
    resources = get_resources()

    # write as a json file
    with open(path.join(resources, 'settings.json'), 'w') as fp:
        json.dump(settings, fp, sort_keys=True, indent=4)
