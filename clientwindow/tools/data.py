"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from os import path
import requests
import urllib
from clientwindow.tools.general import get_resources
from clientwindow.tools.settings import get_settings
import json
import traceback
import sys

def get_json(comms=None):
    """Function to get current JSON file"""
    resources = get_resources()

    try:
        game_data_url = "http://bigmatch.jamielynch.net/data/lsutv001/data.json"
        game_data = requests.get(game_data_url).json()

        shortlist_url = "http://twitterdev.jcrnet.co.uk/shortlisted_tweets.json"
        shortlist_data = requests.get(shortlist_url).json()

        game_data['tweets'] = {}
        game_data['tweets']['shortlist'] = shortlist_data
        #get_twitter_images(game_data)

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

        # video data
        if comms:
            if comms.casparcg:
                videos = comms.get_video_list()
                game_data['videos'] = videos
            else:
                game_data['videos'] = local_data['videos']
        else:
            game_data['videos'] = local_data['videos']

        store_json(game_data)
    except:
        print("Failed to get current data because:")
        traceback.print_exc()
        with open(path.join(resources, 'data'), 'r') as fp:
            game_data = json.load(fp)
    return game_data

def get_local_data():
    """Function to get data only available locally"""
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

def get_twitter_images(game_data):
    """Function to store twitter media locally"""
    resources = get_resources()

    for num, tweet in enumerate(game_data['tweets']['shortlist']):

        tweet = tweet['tweet']['tweet_data']
        try:
            urllib.request.urlretrieve(
                tweet['avatar'],
                path.join(
                    resources,
                    'twitter_avatars',
                    path.split(tweet['avatar'])[1]
                )
            )
        except urllib.error.HTTPError:
            print("Failed to get image from {}".format(tweet['avatar']))

        if tweet['media_present'] == "1":
            try:
                urllib.request.urlretrieve(
                    tweet['media_url'],
                    path.join(
                        resources,
                        'twitter_media',
                        path.split(tweet['media_url'])[1]
                    )
                )
            except urllib.error.HTTPError:
                print("Failed to get image from {}".format(tweet['media_url']))

    tweet = game_data['tweets']['current']['tweet_data']
    try:
        urllib.request.urlretrieve(
            tweet['avatar'],
            path.join(
                resources,
                'twitter_avatars',
                path.split(tweet['avatar'])[1]
            )
        )
    except urllib.error.HTTPError:
        print("Failed to get image from {}".format(tweet['avatar']))

    if tweet['media_present'] == "1":
        try:
            urllib.request.urlretrieve(
                tweet['media_url'],
                path.join(
                    resources,
                    'twitter_media',
                    path.split(tweet['media_url'])[1]
                )
            )
        except urllib.error.HTTPError:
            print("Failed to get image from {}".format(tweet['media_url']))

def store_json(data):
    """Function to store data to disk"""
    resources = get_resources()
    with open(path.join(resources, 'data'), 'w') as fp:
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