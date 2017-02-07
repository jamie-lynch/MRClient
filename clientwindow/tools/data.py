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


def get_json(comms=None):
    """Function to get current JSON file"""

    # get path to the resources directory
    resources = get_resources()

    # try getting the data, handle any errors
    try:
        settings = get_settings()
        standings_table_data = {}
        for table_id, table in settings['tables']['standings'].items():
            table_data = table.copy()
            table_data['data'] = get_table_data(table['url'])
            standings_table_data[str(table_id)] = table_data

        game_data['tables'] = {}
        game_data['tables']['standings'] = standings_table_data

        # local data
        local_data = get_local_data()
        game_data['straps'] = local_data['straps']
        game_data['rundown'] = local_data['rundown']
        game_data['centrescore'] = local_data['centrescore']
        game_data['topscore'] = local_data['topscore']

        print(game_data['straps'])



        store_json(game_data)
    except:
        print("Failed to get current data because:")
        traceback.print_exc()
        with open(path.join(resources, 'data'), 'r') as fp:
            game_data = json.load(fp)
    return game_data


def get_local_data():
    """Function to read the get data only available locally"""

    resources = get_resources()

    with open(path.join(resources, 'local_data'), 'r') as fp:
        local_data = json.load(fp)
    return local_data


def store_local_data(client):
    """Function to store the sections of data only available locally"""
    try:
        resources = get_resources()
        local_data = {}

        production = client.elements['production']['element'].get_local_data()

        local_data['straps'] = production['straps']
        local_data['centrescore'] = production['centrescore']
        local_data['topscore'] = production['topscore']

        local_data['rundown'] = client.elements['rundown']['element'].store_data

        local_data['videos'] = client.elements['vts']['element'].videos

        with open(path.join(resources, 'local_data'), 'w') as fp:
            json.dump(local_data, fp, sort_keys=True, indent=4)
    except AttributeError:
        traceback.print_exc()
    return

def get_video_data(comms):
    """Function to get the list of vts available from Caspar"""


    if comms:
        if comms.casparcg:
            videos = comms.get_video_list()
        else:
            game_data['videos'] = local_data['videos']
    else:
        game_data['videos'] = local_data['videos']


def store_json(data):
    """Function to write data dictionary to JSON file"""

    # get the path to the resources directory
    resources = get_resources()

    # store the file as data.json
    with open(path.join(resources, 'data.json'), 'w') as fp:
        json.dump(data, fp, sort_keys=True, indent=4)
    return


def get_table_data(url):
    """Function to get json data from a url"""
    resources = get_resources()
    try:
        table_data_url = url
        table_data = requests.get(table_data_url).json()
    except ValueError:
        table_data = None
    except requests.exceptions.MissingSchema:
        table_data = None
    return table_data