"""
Match Report CasparCG Client
Version 1.5
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file contains a number of helper functions around data
"""

from os import path
import requests
from clientwindow.tools.general import get_resources
from clientwindow.tools.settings import get_settings
import json
import traceback


def get_startup_data():
    """Function to get data on startup"""

    # get the resources directory
    resources = get_resources()

    # open the file
    with open(path.join(resources, 'data.json'), 'r') as fp:
        data = json.load(fp)
    return data


def store_data(main):
    """Function to store the data file"""

    # get the path to the resources directory
    resources = get_resources()

    # store the file as data.json
    with open(path.join(resources, 'data.json'), 'w') as fp:
        json.dump(main.data, fp, sort_keys=True, indent=4)
    return


def get_video_data(main, comms=None):
    """Function to get the list of vts available from Caspar"""
    if comms:
        if comms.casparcg:
            main.data['videos'] = comms.get_video_list()


def get_table_data(url):
    """Function to get json data from a url"""

    try:
        table_data_url = url
        table_data = requests.get(table_data_url).json()

    except requests.exceptions.ConnectionError:
        table_data = None

    return table_data
