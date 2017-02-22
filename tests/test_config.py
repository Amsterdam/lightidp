"""
    auth.tests.test_config
    ~~~~~~~~~~~~~~~~~~~~~~
"""
import pathlib

import pytest

from auth import config


def test__load_yaml(tmpdir, monkeypatch):
    p = tmpdir.join('testconfig.yml')
    p.write('key: value')
    configpath = p.dirname + '/' + p.basename
    # 1. test with explicit path
    assert config._load_yaml(configpath)['key'] == 'value'
    # 2. test with implicit path
    monkeypatch.setattr(config, 'DEFAULT_CONFIG_PATHS', (pathlib.Path(configpath),))
    assert config._load_yaml()['key'] == 'value'
    # 3. given path is a directory
    with pytest.raises(config.ConfigError):
        config._load_yaml(p.dirname)
    # 4. given path does not exist
    p.remove()
    with pytest.raises(config.ConfigError):
        config._load_yaml(configpath)
    # 5. no file found at all
    with pytest.raises(config.ConfigError):
        config._load_yaml()


def test__interpolate_environment(monkeypatch):
    monkeypatch.setenv('TEST_SUBSTITUTE', 'string')
    # 1. no substitution
    data = {'key': 'value'}
    assert config._interpolate_environment(data) == data
    data = {'key': True}
    assert config._interpolate_environment(data) == data
    data = {'key': 1}
    assert config._interpolate_environment(data) == data
    # 2. simple substitution
    data = {'key': '$TEST_SUBSTITUTE'}
    assert config._interpolate_environment(data) == {'key': 'string'}
    data = {'key': '${TEST_SUBSTITUTE}s'}
    assert config._interpolate_environment(data) == {'key': 'strings'}
    data = {'key': '${TEST_SUBSTITUTE-default}s'}
    assert config._interpolate_environment(data) == {'key': 'strings'}
    data = {'key': '${TEST_SUBSTITUTE:-default}s'}
    assert config._interpolate_environment(data) == {'key': 'strings'}
    # 3. substitution with defaults
    data = {'key': '${GHOST:-default}'}
    assert config._interpolate_environment(data) == {'key': 'default'}
    data = {'key': '${GHOST:-/non:-alphanumeric}'}
    assert config._interpolate_environment(data) == {'key': '/non:-alphanumeric'}
    # 4. missing substitute
    data = {'key': '$GHOST'}
    with pytest.raises(config.ConfigError):
        config._interpolate_environment(data)
    # 5. escaped values
    data = {'key': '$$ESC'}
    assert config._interpolate_environment(data) == {'key': '$ESC'}
    # 6. invalid substitution
    data = {'key': '${'}
    with pytest.raises(config.ConfigError):
        config._interpolate_environment(data)
    data = {'key': '${ TEST_SUBSTITUTE}'}
    with pytest.raises(config.ConfigError):
        config._interpolate_environment(data)
    data = {'key': '${TEST_SUBSTITUTE }'}
    with pytest.raises(config.ConfigError):
        config._interpolate_environment(data)
    data = {'key': '${ }'}
    with pytest.raises(config.ConfigError):
        config._interpolate_environment(data)
    # 7. nested substitution
    data = {'key': ['$TEST_SUBSTITUTE']}
    assert config._interpolate_environment(data) == {'key': ['string']}
    data = {'key': {'test': '$TEST_SUBSTITUTE'}}
    assert config._interpolate_environment(data) == {'key': {'test': 'string'}}
    data = {'key': [{'test': '$TEST_SUBSTITUTE'}]}
    assert config._interpolate_environment(data) == {'key': [{'test': 'string'}]}


def test__validate(tmpdir):
    invalid_schema = "}"
    valid_schema = """
    {
      "$schema": "http://json-schema.org/draft-04/schema#",
      "type": "object",
      "required": ["test"],
      "properties": {
        "test": {"type": "string"}
      }
    }
    """

    p = tmpdir.join('testschema.json')
    schemapath = p.dirname + '/' + p.basename

    # 1. missing schema
    with pytest.raises(config.ConfigError):
        config._validate({}, schemapath)
    # 2. invalid schema
    p.write(invalid_schema)
    with pytest.raises(config.ConfigError):
        config._validate({}, schemapath)
    # 3. invalid data
    p = tmpdir.join('testschema.json')
    p.write(valid_schema)
    with pytest.raises(config.ConfigError):
        config._validate({}, schemapath)
    # 4. valid everything
    config._validate({'test': 'string'}, schemapath)


def test_load(tmpdir, monkeypatch):
    valid_schema = """
    {
      "$schema": "http://json-schema.org/draft-04/schema#",
      "type": "object",
      "required": ["test"],
      "properties": {
        "test": {"type": "string"}
      }
    }
    """
    valid_yaml = "test: ${GHOST-default}\noptional: abcd"
    expected = {'test': 'default', 'optional': 'abcd'}
    conf = tmpdir.join('testconfig.yml')
    conf.write(valid_yaml)
    confpath = conf.dirname + '/' + conf.basename
    schema = tmpdir.join('testschema.json')
    schema.write(valid_schema)
    schemapath = schema.dirname + '/' + schema.basename
    monkeypatch.setattr(config, 'CONFIG_SCHEMA_V1_PATH', pathlib.Path(schemapath))
    assert config.load(confpath) == expected
