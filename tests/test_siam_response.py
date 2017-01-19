"""
    Tests for SIAM-specific responses
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import jwt
import pytest
import responses
import time
import urllib

from auth.siam import client, response


@pytest.mark.usefixtures('config')
@pytest.fixture(scope="module")
def token(config):
    now = int(time.time())
    return jwt.encode({
        'exp': now + config['JWT_LIFETIME'],
        'orig_iat': now,
        'username': 'whoami',
        'ass': 'aselect_credentials',
        'rid': 'rid'
    }, config['JWT_SECRET'], algorithm='HS256')


@pytest.mark.usefixtures('config')
@pytest.fixture(scope="module")
def token_expired(config):
    now = int(time.time())
    return jwt.encode({
        'exp': now - 10,
        'orig_iat': now - 20,
        'username': 'whoami',
        'ass': 'aselect_credentials',
        'rid': 'rid'
    }, config['JWT_SECRET'], algorithm='HS256')


@pytest.mark.usefixtures('config', 'siamclient')
@pytest.fixture(scope="module")
def response_builder(config, siamclient):
    return response.ResponseBuilder(
        siamclient, config['JWT_SECRET'], config['JWT_LIFETIME']
    )


@pytest.mark.usefixtures('config')
def test_server_errors(token, response_builder, config):
    tests = (
        (response_builder.authn_link, True, 'http://some.url'),
        (response_builder.authn_verify, 'aselect_credentials', 'rid'),
    )
    # Test that result codes other than 200 result in a 502
    with responses.RequestsMock() as rsps:
        for t in tests:
            rsps.add(rsps.GET, config['SIAM_BASE_URL'], status=400)
            response = t[0](*t[1:])
            assert response == ('problem communicating with the IdP', 502)
    # Test that RequestExceptions result in a 502
    with responses.RequestsMock() as rsps:
        for t in tests:
            rsps.add(rsps.GET, config['SIAM_BASE_URL'],
                     body=client.RequestException('REQUEST EXCEPTION'))
            response = t[0](*t[1:])
            assert response == ('problem communicating with the IdP', 502)
    # Test that Timeouts result in a 504
    with responses.RequestsMock() as rsps:
        for t in tests:
            rsps.add(rsps.GET, config['SIAM_BASE_URL'],
                     body=client.Timeout('TIMEOUT'))
            response = t[0](*t[1:])
            assert response == ('timeout while contacting the IdP', 504)


@responses.activate
def test_authn_link(response_builder, config):
    rid = '1'

    # mock the response
    body = urllib.parse.urlencode({
        'as_url': config['SIAM_BASE_URL'] + '?request=login1',
        'a-select-server': config['SIAM_ASELECT_SERVER'],
        'rid': rid,
    })
    responses.add(responses.GET, config['SIAM_BASE_URL'], status=200, body=body)

    location = '{}?request=login1&a-select-server={}&rid={}'.format(
        config['SIAM_BASE_URL'], config['SIAM_ASELECT_SERVER'], rid
    )
    assert response_builder.authn_link(False, '') == ('', 307, {'Location': location})


@pytest.mark.usefixtures('config')
@responses.activate
def test_authn_verify_success(response_builder, config):
    uid = '1'
    exp = str((int(time.time()) + 10) * 1000)
    ass = 'aselect_credentials'
    # STEP 1:
    resp_success = urllib.parse.urlencode({
        'result_code': client.Client.RESULT_CODE_OK,
        'tgt_exp_time': exp,
        'uid': uid
    })
    responses.add(responses.GET, config['SIAM_BASE_URL'], status=200, body=resp_success)
    r = response_builder.authn_verify(ass, 'rid')
    assert r[1] == 200
    decoded = jwt.decode(r[0], config['JWT_SECRET'])
    assert decoded['username'] == '1'
    assert decoded['ass'] == ass


@pytest.mark.usefixtures('config')
@responses.activate
def test_authn_verify_fail(response_builder, config):
    resp_fail = urllib.parse.urlencode({
        'result_code': client.Client.RESULT_CODE_INVALID_CREDENTIALS,
        'tgt_exp_time': str((int(time.time()) + 10) * 1000),
        'uid': 'uid'
    })
    responses.add(responses.GET, config['SIAM_BASE_URL'], status=200, body=resp_fail)
    r = response_builder.authn_verify('aselect_credentials', 'rid')
    assert r == ('verification of credentials failed', 400)


@pytest.mark.usefixtures('config')
def test_authn_verify_malformed(response_builder, config):
    resp_malformed = urllib.parse.urlencode({
        'result_code': client.Client.RESULT_CODE_OK,
        'tgt_exp_time': "1",
        'uid': 'uid'
    })
    with responses.RequestsMock() as rsps:
        rsps.add(rsps.GET, config['SIAM_BASE_URL'], status=200, body=resp_malformed)
        r = response_builder.authn_verify('aselect_credentials', 'rid')
    assert r == ('problem between auth server and SIAM', 502)

    resp_malformed = urllib.parse.urlencode({
        'i am empty': None,
    })
    with responses.RequestsMock() as rsps:
        rsps.add(rsps.GET, config['SIAM_BASE_URL'], status=200, body=resp_malformed)
        r = response_builder.authn_verify('aselect_credentials', 'rid')
    assert r == ('malformed response from SIAM', 502)


@pytest.mark.usefixtures('config')
@responses.activate
def test_session_renew(token, response_builder, config):
    ok = urllib.parse.urlencode({'result_code': client.Client.RESULT_CODE_OK})
    responses.add(responses.GET, config['SIAM_BASE_URL'], status=200, body=ok)
    r = response_builder.session_renew(token)
