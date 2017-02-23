"""
    auth.tests.web.test_siamrequesthandler
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import pytest


def siam_authenticate(app, data={}, headers={}):
    client = app.test_client()
    return client.get('/auth/siam/authenticate', data=data, headers=headers, follow_redirects=False)


def siam_token(app, data={}, headers={}):
    client = app.test_client()
    return client.get('/auth/siam/token', data=data, headers=headers)


@pytest.mark.usefixtures('app')
def test_siam_authenticate(app):
    # 1. No callback param in query
    response = siam_authenticate(app)
    assert response.status_code == 400
    # 2. No callback param in query
    response = siam_authenticate(app)
    assert response.status_code == 400


@pytest.mark.usefixtures('app')
def test_siam_token(app):
    ...
