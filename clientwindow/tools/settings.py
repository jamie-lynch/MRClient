"""
Match Report CasparCG Client
Version 1.5
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
    with open(path.join(resources, 'settings'), 'r') as fp:
        settings = json.load(fp)

    return settings


def store_settings(settings):
    """Function which writes settings to file"""

    # get the resources filepath
    resources = get_resources()

    # write as a json file
    with open(path.join(resources, 'settings'), 'w') as fp:
        json.dump(settings, fp, sort_keys=True, indent=4)
