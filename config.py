# -*- coding: utf-8 -*-
"""This module defines and imports configuration variables

        Attributes:
            directory_split (str): Used for RegEx on part numbers. Currently unused
            db_location (str): Path to SQL database file or server
            img_archive (str): Location of image database (storage)
            sql_type (str): Type of SQL database being used
            dlg_hide_change_mugshot (bool): Should the dialog warning mugshot change show?
            dlg_hide_remove_image (bool): Should the dialog warning image deletion show?
"""

import yaml
import os

# Defining & Initializing config variables
cfg = None
sql_db = None
cfg_import = [
            "directory_split",
            "db_location",
            "img_archive",
            "sql_type",
            "dlg_hide_change_mugshot",
            "dlg_hide_remove_image"

            ]


def load_config():
    """Read a yaml file into config dictionary"""

    # Read YAML file into config.cfg dictionary, and prompt to create if absent
    try:
        with open(os.path.join(app_root, 'app_config.yaml'), 'r', encoding='utf8') as stream:
            _loaded = yaml.safe_load(stream)

            # Load in variables intended for import if available
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
