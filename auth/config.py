"""
    auth.config
    ~~~~~~~~~~~

    Module that loads configuration settings from a yaml file.

    Features:

    - Environment interpolation
    - JSON schema validation
"""
import json
import os
import pathlib
import string

import jsonschema
import yaml


_module_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_CONFIG_PATHS = [
    _module_path.parent / 'datapuntauth.yml',
    pathlib.Path('/etc') / 'datapuntauth.yml',
]

CONFIG_SCHEMA_V1_PATH = _module_path.parent / 'config_schema_v1.json'


class ConfigError(Exception):
    """ Configuration errors.
    """


def load(configpath=None):
    config = _load_yaml(configpath)
    config = _interpolate_environment(config)
    _validate(config, CONFIG_SCHEMA_V1_PATH)
    return config


def _load_yaml(configpath=None):
    if not configpath:
        for path in DEFAULT_CONFIG_PATHS:
            if path.exists() and path.is_file():
                conffile = path
                break
        else:
            error_msg = 'No configfile found (none given and none found at {})'
            paths_as_string = ', '.join(str(p) for p in DEFAULT_CONFIG_PATHS)
            raise ConfigError(error_msg.format(paths_as_string))
    else:
        conffile = pathlib.Path(configpath)
    with conffile.open() as f:
        parsed = yaml.load(f)
    return parsed


def _interpolate_environment(config):

    def interpolate(value):
        try:
            result = string.Template(value).substitute(os.environ)
        except KeyError as e:
            error_msg = 'Could not resolve {}'
            raise ConfigError(error_msg.format(value)) from e
        return (result.isdigit() and int(result)) or result

    def interpolate_recursive(obj):
        if isinstance(obj, str):
            return interpolate(obj)
        if isinstance(obj, dict):
            return {key: interpolate_recursive(obj[key]) for key in obj}
        if isinstance(obj, list):
            return [interpolate_recursive(val) for val in obj]
        return obj

    return {key: interpolate_recursive(config[key]) for key in config}


def _validate(config, schemafile):
    """ Validate using JSON schema
    """
    with pathlib.Path(schemafile).open() as f:
        schema = json.load(f)
    jsonschema.validate(config, schema)
