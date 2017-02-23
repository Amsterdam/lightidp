"""
    auth.tests.test_token
    ~~~~~~~~~~~~~~~~~~~~~
"""
import authorization_levels
import pytest
from auth import exceptions, token


def test_tokenbuilder_success():
    builder = token.AccessTokenBuilder('secret', 300, 'HS256')
    jwt = builder.create(authz=authorization_levels.LEVEL_DEFAULT).encode()
    assert jwt
    data = builder.decode(jwt)
    # make sure we have something
    assert data
    # make sure we have an encode property
    assert data.encode
    # make sure we have a mapping and iat is in it
    assert 'iat' in data
    # make sure exp and sub are in there
    assert 'exp' in data
    assert 'authz' in data
    # make sure the data is what we want it to be
    assert data['authz'] == authorization_levels.LEVEL_DEFAULT
    assert data['exp'] - data['iat'] == 300
    # make sure the same data encodes the same jwt
    parts = data.encode().split(b'.')
    jwtparts = jwt.split(b'.')
    assert len(parts) == len(jwtparts) == 3
    assert parts[0] == jwtparts[0]
    assert parts[1] == jwtparts[1]
    # the MAC may differ, it is seeded by timestamp


def test_tokenbuilder_invalid_algorithm():
    builder = token.AccessTokenBuilder('secret', 300, 'invalid')
    with pytest.raises(NotImplementedError):
        builder.create(authz=authorization_levels.LEVEL_DEFAULT).encode()


def test_tokenbuilder_decode_error():
    builder1 = token.AccessTokenBuilder('secret1', 300, 'HS256')
    builder2 = token.AccessTokenBuilder('secret2', 300, 'HS256')
    jwt = builder1.create(authz=authorization_levels.LEVEL_DEFAULT).encode()
    with pytest.raises(exceptions.JWTDecodeException):
        builder2.decode(jwt)
