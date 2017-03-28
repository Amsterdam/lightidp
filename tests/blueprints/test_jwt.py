"""
    auth.tests.web.test_jwtrequesthandler
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import pytest


def accesstoken(app, headers={}):
    client = app.test_client()
    return client.get('/auth/accesstoken', headers=headers)


@pytest.mark.usefixtures('app', 'refreshtokenbuilder')
def test_accesstoken(app, refreshtokenbuilder):
    reftoken = str(refreshtokenbuilder.create(sub='evert').encode(), 'utf-8')
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
