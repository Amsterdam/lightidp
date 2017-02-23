"""
    auth.tests.web.test_jwtrequesthandler
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import pytest


def refreshtoken(app, data={}, headers={}):
    client = app.test_client()
    return client.get('/auth/refreshtoken', data=data, headers=headers)


def accesstoken(app, data={}, headers={}):
    client = app.test_client()
    return client.get('/auth/accesstoken', data=data, headers=headers)


@pytest.mark.usefixtures('app')
def test_refreshtoken(app):
    # 1. No Accept header
    response = refreshtoken(app)
    assert response.status_code == 406
    # 2. Wrong Accept header
    response = refreshtoken(app, headers={'Accept': 'application/json'})
    assert response.status_code == 406
    # 3. Multiple Accept header
    response = refreshtoken(app, headers={'Accept': 'text/plain'})
    assert response.status_code == 200
    (_, _, _) = response.data.split(b'.')


@pytest.mark.usefixtures('app')
def test_accesstoken(app):
    reftoken = str(refreshtoken(app, headers={'Accept': 'text/plain'}).data, 'utf-8')
    # 1. No Accept header
    response = accesstoken(app)
    assert response.status_code == 406
    # 2. No Authorization header
    response = accesstoken(app, headers={'Accept': 'text/plain'})
    assert response.status_code == 401
    assert 'WWW-Authenticate' in response.headers
    # 3. Wrong Authorization header
    response = accesstoken(app, headers={'Accept': 'text/plain', 'Authorization': 'bad'})
    assert response.status_code == 401
    assert 'WWW-Authenticate' in response.headers
    assert 'error="invalid_token"' in response.headers['WWW-Authenticate']
    # 4. Wrong prefix in Authorization header
    response = accesstoken(app, headers={'Accept': 'text/plain', 'Authorization': 'JWT token'})
    assert response.status_code == 401
    assert 'WWW-Authenticate' in response.headers
    assert 'error="invalid_token"' in response.headers['WWW-Authenticate']
    # 5. Wrong token in Authorization header
    response = accesstoken(app, headers={'Accept': 'text/plain', 'Authorization': 'Bearer token'})
    assert response.status_code == 401
    assert 'WWW-Authenticate' in response.headers
    assert 'error="invalid_token"' in response.headers['WWW-Authenticate']
    # 6. Valid token in Authorization header
    response = accesstoken(app, headers={'Accept': 'text/plain', 'Authorization': 'Bearer {}'.format(reftoken)})
    assert response.status_code == 200
    (_, _, _) = response.data.split(b'.')
