"""
The Big Match graphics client
written by Jamie Lynch & Jack Connor-Richards for LSU Media
"""

from os import path
import json
from clientwindow.tools.general import get_resources

def get_settings():
    """Function which returns settings"""
    resources = get_resources()

    if not path.isfile(path.join(resources, "settings")):
        settings = get_default_setttings()
        with open(path.join(resources, 'settings'), 'w') as f:
            json.dump(settings, f)

    with open(path.join(resources, 'settings'), 'r') as fp:
        settings = json.load(fp)

    if settings:
        settings['resources'] = resources
        return settings
    else:
        with open(path.join(resources, 'default_settings'), 'r') as fp:
            settings = json.load(fp)
            settings['resources'] = resources
        return settings

def store_settings(settings):
    """Function which writes settings to file"""
    resources = get_resources()
    with open(path.join(resources, 'settings'), 'w') as fp:
        json.dump(settings, fp, sort_keys=True, indent=4)
    return

def get_default_setttings():
    settings = {
        "caspar": {
            "address": "127.0.0.1",
            "port": 5250,
            "video_directory": "home"
        },
        "data": {
            "location": ""
        },
        "lineup": {
            "custom": True
        },
        "mode": "roundup",
        "resources": "C:\\Users\\Jamie\\Documents\\The Big Match\\TBM_CasparCG_Client\\resources",
        "show": {
            "lineup": True,
            "names": True,
            "production": True,
            "rundown": True,
            "score": True,
            "stats": True,
            "tables": True,
            "twitter": True,
            "vts": True
        },
        "tables": {
            "standings": {
                "1": {
                    "gender": "Choose gender...",
                    "level": "Choose team...",
                    "sport": "Overall",
                    "type": "BUCS",
                    "url": "http://bigmatch.jcrnet.uk/tabletojson/bucs_table.json"
                }
            }
        },
        "templates": {
            "events": [
                {
                    "channel": 0,
                    "data": [],
                    "filename": "filename",
                    "layer": 0,
                    "name": "name",
                    "section": "events",
                    "type": "single"
                }
            ],
            "lineup": [
                {
                    "channel": 0,
                    "data": [],
                    "filename": "filename",
                    "layer": 0,
                    "name": "name",
                    "section": "lineup",
                    "type": "single"
                }
            ],
            "names": [
                {
                    "channel": "1",
                    "data": [
                        "teams"
                    ],
                    "filename": "PALTest/PALTEST",
                    "layer": "10",
                    "name": "teams",
                    "section": "names",
                    "type": "single"
                },
                {
                    "channel": "1",
                    "data": [
                        "names"
                    ],
                    "filename": "PALTest/PALTEST",
                    "layer": "10",
                    "name": "PALTest/PALTEST",
                    "section": "names",
                    "type": "single"
                }
            ],
            "score": [],
            "standard": {
                "events": {
                    "channel": 0,
                    "filename": "individual_event",
                    "layer": 1,
                    "show": True
                },
                "lineup": {
                    "channel": 2,
                    "filename": "individual_lineup",
                    "layer": 3,
                    "show": True
                },
                "standings_table": {
                    "channel": 1,
                    "filename": "TBM_PointsTable_10Row/TBM_PointsTable_10Row",
                    "layer": 10,
                    "name": "Standings Table",
                    "show": True
                },
                "stats": {
                    "channel": 4,
                    "filename": "individual_stats",
                    "layer": 5,
                    "show": True
                },
                "strap_name_left": {
                    "channel": 1,
                    "filename": "TBM_StrapLeft/TBM_StrapLeft",
                    "layer": 10,
                    "name": "Lower Strap Left",
                    "show": True
                },
                "strap_name_right": {
                    "channel": 1,
                    "filename": "TBM_StrapRight/TBM_StrapRight",
                    "layer": 10,
                    "name": "Lower Strap Right",
                    "show": True
                }
            },
            "stats": [
                {
                    "channel": "10",
                    "data": [],
                    "filename": "filename",
                    "layer": "0",
                    "name": "name",
                    "section": "stats",
                    "type": "single"
                }
            ],
            "time": [
                {
                    "channel": 0,
                    "data": [],
                    "filename": "filename",
                    "layer": 0,
                    "name": "name",
                    "section": "time",
                    "type": "double"
                }
            ],
            "twitter": [
                {
                    "channel": 0,
                    "data": [
                        "twitter"
                    ],
                    "filename": "",
                    "layer": 0,
                    "name": "Lower Third",
                    "section": "twitter",
                    "type": "single"
                }
            ],
            "vts": []
        },
        "vt_gfx": {
            "Strap Left": {
                "filename": "TBM_StrapLeft/TBM_StrapLeft",
                "name": "Strap Left"
            }
        }
    }

    return settings
