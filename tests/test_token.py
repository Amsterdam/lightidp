"""
    auth.tests.test_token
    ~~~~~~~~~~~~~~~~~~~~~
"""
import authorization
import pytest
from auth import exceptions, token


def test_tokenbuilder_success():
    builder = token.AccessTokenBuilder('secret', 300, 'HS256')
    jwt = builder.create(authz=authorization.levels.LEVEL_DEFAULT).encode()
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
    assert data['authz'] == authorization.levels.LEVEL_DEFAULT
    assert data['exp'] - data['iat'] == 300 + 60  # add 60 because iat starts 60 seconds early
    # note that encoding `data` again may not reult in the same JWT, even though
    # it contains the same JOSE header and data. This is because we're working
    # with dictionaries / hash sets, which don't guarantee order.


def test_tokenbuilder_invalid_algorithm():
    builder = token.AccessTokenBuilder('secret', 300, 'invalid')
    with pytest.raises(NotImplementedError):
        builder.create(authz=authorization.levels.LEVEL_DEFAULT).encode()


def test_tokenbuilder_decode_error():
    builder1 = token.AccessTokenBuilder('secret1', 300, 'HS256')
    builder2 = token.AccessTokenBuilder('secret2', 300, 'HS256')
    jwt = builder1.create(authz=authorization.levels.LEVEL_DEFAULT).encode()
    with pytest.raises(exceptions.JWTDecodeException):
        builder2.decode(jwt)
