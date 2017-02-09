"""
    auth.tests.test_token
    ~~~~~~~~~~~~~~~~~~~~~
"""
import authorization_levels
import pytest
from auth import exceptions, token


def test_tokenbuilder_success():
    builder = token.AccessTokenBuilder('secret', 300, 'HS256')
    jwt = builder.create(authorization_levels.LEVEL_DEFAULT).encode()
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
    builder = token.AccessTokenBuilder('secret', 300, 'invalid')
    with pytest.raises(NotImplementedError):
        builder.create(authorization_levels.LEVEL_DEFAULT).encode()


def test_tokenbuilder_decode_error():
    builder1 = token.AccessTokenBuilder('secret1', 300, 'HS256')
    builder2 = token.AccessTokenBuilder('secret2', 300, 'HS256')
    jwt = builder1.accesstoken_for(authorization_levels.LEVEL_DEFAULT).encode()
    with pytest.raises(exceptions.JWTDecodeException):
        builder2.decode_accesstoken(jwt)
