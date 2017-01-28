"""
    auth.tests.test_jwtutils
    ~~~~~~~~~~~~~~~~~~~~~~~~
"""
import pytest
from auth import exceptions, token


def test_tokenbuilder_success():
    builder = token.Builder(None, 'at_secret', None, 300, 'HS256')
    jwt = builder.accesstoken_for('sub').encode()
    assert jwt
    data = builder.decode_accesstoken(jwt)
    # make sure we have something
    assert data
    # make sure we have an encode property
    assert data.encode
    # make sure we have a mapping and iat is in it
    assert 'iat' in data
    # make sure exp and sub are in there
    assert 'exp' in data
    assert 'sub' in data
    # make sure the data is what we want it to be
    assert data['sub'] == 'sub'
    assert data['exp'] - data['iat'] == 300
    # make sure the same data encodes the same jwt
    assert data.encode() == jwt


def test_tokenbuilder_invalid_algorithm():
    builder = token.Builder(None, 'at_secret', None, 300, 'invalid')
    with pytest.raises(NotImplementedError):
        builder.accesstoken_for('sub').encode()


def test_tokenbuilder_decode_error():
    builder1 = token.Builder(None, 'key1', None, 300, 'HS256')
    builder2 = token.Builder(None, 'key2', None, 300, 'HS256')
    with pytest.raises(exceptions.JWTDecodeException):
        builder2.decode_accesstoken(builder1.accesstoken_for('sub').encode())
