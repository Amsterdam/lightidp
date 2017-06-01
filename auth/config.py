"""
    .. _auth-config:

    auth.config
    ~~~~~~~~~~~

    Module that loads configuration settings from a yaml file.

    **Features**

    - Environment interpolation with defaults
    - JSON schema validation

    .. _default-config-locations:

    **Default config file locations**

    - ``/etc/datapuntauth/config.yml``
    - ``$PROJECT/config.yml``, where ``$PROJECT`` is the parent directory of
       :mod:`auth`, which is useful during development

    **Example usage**

    ::

        from auth.config import load
        settings = config.load()

"""
import json
import os
import pathlib
import string

import jsonschema
import yaml


_module_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_CONFIG_PATHS = [
    pathlib.Path('/etc') / 'datapuntauth' / 'config.yml',
    _module_path.parent / 'config.yml',
]

CONFIG_SCHEMA_V1_PATH = _module_path.parent / 'config_schema_v1.json'


class ConfigError(Exception):
    """ Configuration errors
    """


def load(configpath=None):
    """ Load, parse and validate a configuration file from the given
    ``configpath`` or one of the :ref:`default locations <default-config-locations>`

    :param configpath: path to the configuration file to load (optional)
    """
    config = _load_yaml(configpath)
    config = _interpolate_environment(config)
    _validate(config, CONFIG_SCHEMA_V1_PATH)
    return config


def _load_yaml(configpath=None):
    """ Read a yaml file from the given ``configpath`` or one of the
    :ref:`default locations <default-config-locations>`

    :param configpath: path to the yaml file to load (optional)
    """
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
        path = pathlib.Path(configpath)
        if path.exists() and path.is_file():
            conffile = path
        else:
            raise ConfigError('Cannot read config from {}'.format(configpath))
    with conffile.open() as f:
        parsed = yaml.load(f)
    return parsed


def _interpolate_environment(config):
    """ Recursively find string-type values in the given ``config``, and try to
    substitute them with values from :data:`os.environ`.

    **NOTE**: If a substituted value is a string containing only digits (i.e.
    `str.isdigit` == ``True``), then this function will cast it to an
    integer. It does not try to do any other type conversion.

    :param config: configuration mapping
    """

    def interpolate(value):
        try:
            result = TemplateWithDefaults(value).substitute(os.environ)
        except KeyError as e:
            error_msg = 'Could not substitute: {}'
            raise ConfigError(error_msg.format(value)) from e
        except ValueError as e:
            error_msg = 'Invalid substitution: {}'
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
    """ Validate the given ``config`` using the JSON schema given in
    ``schemafile``.

    :param config: configuration mapping
    :param str schemafile: path
    """
    try:
        with pathlib.Path(schemafile).open() as f:
            schema = json.load(f)
    except FileNotFoundError as e:
        raise ConfigError() from e
    except json.JSONDecodeError as e:
        raise ConfigError() from e
    try:
        jsonschema.validate(config, schema)
    except jsonschema.exceptions.ValidationError as e:
        raise ConfigError() from e


class TemplateWithDefaults(string.Template):
    """ String template that supports Bash-style default values for
    interpolation.

    Copied from `Docker Compose <https://github.com/docker/compose/blob/master/compose/config/interpolation.py>`_
    """

    # string.Template uses cls.idpattern to define identifiers:
    idpattern = r'[_a-z][_a-z0-9]*(?::?-[^}]+)?'

    # Modified from python2.7/string.py
    def substitute(self, mapping):
        # Helper function for .sub()
        def convert(mo):
            # Check the most common path first.
            named = mo.group('named') or mo.group('braced')
            if named is not None:
                if ':-' in named:
                    var, _, default = named.partition(':-')
                    return mapping.get(var) or default
                if '-' in named:
                    var, _, default = named.partition('-')
                    return mapping.get(var, default)
                val = mapping[named]
                return '%s' % (val,)
            if mo.group('escaped') is not None:
                return self.delimiter
            if mo.group('invalid') is not None:
                self._invalid(mo)
            raise ValueError('Unrecognized named group in pattern',
                             self.pattern)
        return self.pattern.sub(convert, self.template)
