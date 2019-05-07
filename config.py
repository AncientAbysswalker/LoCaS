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
            "tryp"
        ]

    # Read YAML file into temporary variable
    with open('config.yaml', 'r', encoding='utf8') as stream:
        _loaded = yaml.safe_load(stream)
    print(_loaded)

    # Try to import each config variable
    for variable_name in config_variables:
        commit_to_variable(variable_name, _loaded)


def commit_to_variable(variable_name, loaded_data):
    """Generate a config.py variable to correspond to those desired in load_config"""

    try:
        if loaded_data[variable_name]:
            globals()[variable_name] = loaded_data[variable_name]
        else:
            print("HMM. Empty Variable??")
    except KeyError:
        print("Missing config variable in YAML")


