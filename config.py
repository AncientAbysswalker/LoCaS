# -*- coding: utf-8 -*-

import yaml
import os

# Defining & Initializing config variables
cfg_import = [
            "directory_split",
            "db_location",
            "img_archive",
            "sql_db",
            "sql_type",
            "dlg_hide_change_mugshot",
            "dlg_hide_remove_image"

            ]


def load_config():
    """Read a yaml file into config variables

    Attributes:
        TODO: Proper attributes
        config_variables (list: str): List of config variables to import. Variable names listed as strings.
    """

    # Read YAML file into config variables
    try:
        with open(os.path.join(app_root, 'app_config.yaml'), 'r', encoding='utf8') as stream:
            _loaded = yaml.safe_load(stream)

            # Load in variables that match those defined above and are not modules or the like
            _keys = list(_loaded.keys())
            globals()['cfg'] = {x: _loaded[x] for x in set(cfg_import).intersection(_keys)}

    except FileNotFoundError:
        print("File not found - generate new config file? Or find file and move to home?")

    # Special handling for missing required variables

    # Special handling for missing optional variables

    # Special handling for sql type
    if globals()['cfg']['sql_type'] == "sqlite3":  # SQLite
        import sqlite3
        globals()['sql_db'] = sqlite3
    elif globals()['cfg']['sql_type'] == "psycopg2":  # PostgreSQL
        import psycopg2
        globals()['sql_db'] = psycopg2
    else:
        raise Exception("An invalid SQL database management system provided: " + sql_type)

    "testing kanban 2.9"
