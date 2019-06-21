# -*- coding: utf-8 -*-

import yaml

# Defining & Initializing config variables
directory_split = None
db_location = None
img_archive = None
sql_db = None
sql_type = None
dlg_hide_change_mugshot = None
dlg_hide_remove_image = None


def load_config():
    """Read a yaml file into config variables

    Attributes:
        TODO: Proper attributes
        config_variables (list: str): List of config variables to import. Variable names listed as strings.
    """

    # Read YAML file into config variables
    try:
        with open('config.yaml', 'r', encoding='utf8') as stream:
            _loaded = yaml.safe_load(stream)

            # Load in variables that match those defined above and are not modules or the like
            for k in globals():
                if k[:2] != "__" and k not in ['yaml', 'load_config', 'sql_db']:
                    globals()[k] = _loaded[k]

        print(_loaded)
    except FileNotFoundError:
        print("File not found - generate new config file? Or find file and move to home?")

    # Special handling for certain imported variables
    if sql_type == "sqlite3":
        import sqlite3
        globals()["sql_db"] = sqlite3
        print(globals()["sql_db"])
    elif sql_type == "psycopg2":
        import psycopg2
        globals()["sql_db"] = psycopg2
    else:
        raise Exception("An invalid SQL database management system: " + sql_type)

