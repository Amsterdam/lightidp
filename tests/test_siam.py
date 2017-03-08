"""
    auth.tests.test_siam
    ~~~~~~~~~~~~~~~~~~~~
"""
import pytest
import responses
import time
import urllib.parse
from auth import exceptions

# shorthand
uenc = urllib.parse.urlencode


@pytest.mark.usefixtures('config', 'client')
def test_siam_server_error(config, client):
    with responses.RequestsMock() as rsps:
        rsps.add(rsps.GET, config['siam']['base_url'], status=500)
        with pytest.raises(exceptions.GatewayRequestException):
            client._request({}, 1.0)


@pytest.mark.usefixtures('config', 'client')
def test_get_authn_link(config, client):
    base_url = config['siam']['base_url']
    aselect_server = config['siam']['aselect_server']
    rid = '1'
    body = uenc({
        'result_code': client.RESULT_OK,
        'as_url': base_url + '?request=login1',
        'a-select-server': aselect_server,
        'rid': rid,
    })
    expected = '{}?request=login1&a-select-server={}&rid={}'.format(
        base_url, aselect_server, rid
    )
    with responses.RequestsMock() as rsps:
        rsps.add(rsps.GET, base_url, status=200, body=body)
        resp = client.get_authn_redirect(False, 'http://some.callback.url')
    assert resp == expected


@pytest.mark.usefixtures('config', 'client')
def test_verify_creds(config, client):
    base_url = config['siam']['base_url']
    now = int(time.time())
    # 1. Test success
    with responses.RequestsMock() as rsps:
        siam_response = {
            'result_code': client.RESULT_OK,
            'tgt_exp_time': '{}'.format(now + 10),
            'uid': 'evert'}
        rsps.add(rsps.GET, base_url, body=uenc(siam_response))
        response = client.get_user_attributes('aselect_credentials', 'rid')
        assert response == {'uid': 'evert'}
    # 2. Test failure
    with responses.RequestsMock() as rsps:
        siam_response = {'result_code': client.RESULT_INVALID_CREDENTIALS}
        rsps.add(rsps.GET, base_url, body=uenc(siam_response))
        with pytest.raises(exceptions.GatewayBadCredentialsException):
            client.get_user_attributes('aselect_credentials', 'rid')
    # 3. Test malformed response I
    with responses.RequestsMock() as rsps:
        siam_response = {'result_code': client.RESULT_OK}
        rsps.add(rsps.GET, base_url, body=uenc(siam_response))
        with pytest.raises(exceptions.GatewayResponseException):
            client.get_user_attributes('aselect_credentials', 'rid')
    # 4. Test malformed response II
    with responses.RequestsMock() as rsps:
        siam_response = {}
        rsps.add(rsps.GET, base_url, body=uenc(siam_response))
        with pytest.raises(exceptions.GatewayResponseException):
            client.get_user_attributes('aselect_credentials', 'rid')
    # 5. Test malformed response III
    with responses.RequestsMock() as rsps:
        siam_response = {
            'result_code': client.RESULT_OK,
            'tgt_exp_time': '{}'.format(now - 10),
            'uid': 'evert'}
        rsps.add(rsps.GET, base_url, body=uenc(siam_response))
        with pytest.raises(exceptions.GatewayResponseException):
            client.get_user_attributes('aselect_credentials', 'rid')
