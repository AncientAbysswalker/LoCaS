# -*- coding: utf-8 -*-
import yaml

def load_config():
    """Read a yaml file into config variables

    Attributes:
        config_variables (list: str): List of config variables to import. Variable names listed as strings.
    """

    # Config variables to load into memory.
    config_variables = \
        [
            "tryp",
            "directory_split",
            "db_location",
            "img_archive",
            "sql_type"
        ]

    # Read YAML file into temporary variable
    with open('config.yaml', 'r', encoding='utf8') as stream:
        _loaded = yaml.safe_load(stream)
    print(_loaded)

    # Try to import each config variable
    for variable_name in config_variables:
        print(variable_name)
        commit_to_variable(variable_name, _loaded)

    if sql_type == "sqlite3":
        import sqlite3
        globals()["sql_db"] = sqlite3
        print(globals()["sql_db"])
    elif sql_type == "psycopg2":
        import psycopg2
        globals()["sql_db"] = psycopg2
    else:
        raise Exception("An invalid SQL database management system: " + sql_type)


def commit_to_variable(variable_name, loaded_data):
    """Generate a config.py variable to correspond to those desired in load_config"""

    try:
        if loaded_data[variable_name]:
            globals()[variable_name] = loaded_data[variable_name]
            print("LOADED A VARIABLE")
        else:
            print("HMM. Empty Variable??")
    except KeyError:
        print("Missing config variable in YAML")


