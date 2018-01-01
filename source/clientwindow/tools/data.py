"""
Match Report CasparCG Client
Version 2.1
written by Jamie Lynch & Jack Connor-Richards for LSU Media

This file contains a number of helper functions around data
"""

from os import path
import requests
from clientwindow.tools.general import get_resources
from clientwindow.tools.settings import get_settings
import json
from bs4 import BeautifulSoup
import html5lib
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


def get_video_data(main):
    """Function to get the list of vts available from Caspar"""
    if main.comms.casparcg:
        main.data['videos'] = main.comms.get_video_list()


def get_table_data(url):
    """Function to get json data from a url"""

    try:
        table_data_url = url
        table_data = requests.get(table_data_url).json()

    except requests.exceptions.ConnectionError:
        table_data = None

    except ValueError:
        table_data = None

    return table_data


def get_bucs_data(url, sport, gender, team):
    """Function to get league table data from the BUCS website"""

    table_data = dict()
    table_headers_keys = dict()
    tableform_headers_keys = dict()
    table_data_keys = dict()
    tableform_data_keys = dict()
    row = 0
    column = 1

    # Set the keys for the return data
    table_headers_keys[1] = ""
    table_headers_keys[2] = "data_updated"
    table_headers_keys[3] = "table_table_header_stat_1_title"
    table_headers_keys[4] = "table_table_header_stat_2_title"
    table_headers_keys[5] = "table_table_header_stat_3_title"
    table_headers_keys[6] = "table_table_header_stat_4_title"
    table_headers_keys[7] = "table_table_header_stat_5_title"
    table_headers_keys[8] = "table_table_header_points_title"

    tableform_headers_keys[1] = ""
    tableform_headers_keys[2] = "data_updated"
    tableform_headers_keys[3] = "tableform_table_header_form_stat_1_title"
    tableform_headers_keys[4] = "tableform_table_header_form_stat_3_title"
    tableform_headers_keys[5] = "tableform_table_header_form_stat_4_title"
    tableform_headers_keys[6] = "tableform_table_header_form_stat_5_title"
    tableform_headers_keys[7] = "tableform_table_header_form_stat_2_title"
    tableform_headers_keys[8] = "tableform_table_header_form_points_title"

    table_data_keys[1] = "position"
    table_data_keys[2] = "team_name"
    table_data_keys[3] = "stat_1"
    table_data_keys[4] = "stat_2"
    table_data_keys[5] = "stat_3"
    table_data_keys[6] = "stat_4"
    table_data_keys[7] = "stat_5"
    table_data_keys[8] = "points"

    tableform_data_keys[1] = "position"
    tableform_data_keys[2] = "team_name"
    tableform_data_keys[3] = "stat_1"
    tableform_data_keys[4] = "stat_3"
    tableform_data_keys[5] = "stat_4"
    tableform_data_keys[6] = "stat_5"
    tableform_data_keys[7] = "stat_2"
    tableform_data_keys[8] = "points"

    table_data["sport"] = sport
    table_data["gender"] = gender
    table_data["team"] = team
    table_data["type"] = "BUCS"

    try:
        page_data = requests.get(url).text
        soup = BeautifulSoup(page_data, "html5lib")

        # Parse HTML league table data and convert to dictionary
        table = soup.find('table')
        title = soup.find('h2')
        title, subtitle = title.text.split(" - ")
        table_data["title"] = title
        table_data["table_table_header_subtitle"] = subtitle
        table_data["tableform_table_header_form_subtitle"] = subtitle
        rows = table.findAll('tr')
        for tr in rows:
            fields = tr.findAll(['th', 'td'])
            for th in fields:
                # Fix some weird HTML stuff they put in the tables
                for descendant in th.descendants:
                    try:
                        if descendant.name != "a":
                            descendant.clear()
                    except AttributeError:
                        # We don't care if it can't clear them, probably because it's already None
                        pass
                value = th.text.strip().replace("\t", "").replace("\n", " ")
                if th.name == "th" and value:
                    table_data[table_headers_keys[column]] = value
                    table_data[tableform_headers_keys[column]] = value
                elif th.name == "td" and value:
                    table_data["table_table_row_{}_{}".format(row, table_data_keys[column])] = value
                    table_data["tableform_table_row_{}_form_{}".format(row, tableform_data_keys[column])] = value
                column += 1
            column = 1
            row += 1
        row = 1

        # Parse HTML form table data and convert to dictionary
        form = soup.find("div", {"id": "tab30"})
        rows = form.findAll('tr')
        for tr in rows:
            fields = tr.findAll(['th', 'td'])
            for td in fields:
                value = td.text.strip().replace("\t", "").replace("\n", " ")
                if td.name == "td" and value and column == 2:
                    table_data["tableform_table_row_{}_form_form".format(row)] = value
                column += 1
            column = 1
            row += 1

        # Set league table to show form
        table_data["show_form"] = True

    except requests.RequestException:
        table_data = None

    except:
        table_data = None

    finally:
        return table_data
