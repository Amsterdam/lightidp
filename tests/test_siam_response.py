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

# seed for json web tokens
secret_key = 'secret'


@pytest.fixture(scope="module")
def json_web_token():
    now = int(time.time())
    exp = now + 60  # we should be run all tests in this module within 60 secs
    return (jwt.encode({
        'exp': exp,
        'orig_iat': now,
        'username': 'whoami',
        'ass': 'aselect_credentials',
        'rid': 'rid'
    }, secret_key, algorithm='HS256'), exp)


@pytest.fixture(scope="module")
def json_web_token_expired():
    now = int(time.time())
    return jwt.encode({
        'exp': now - 10,
        'orig_iat': now,
        'username': 'whoami',
        'ass': 'aselect_credentials',
        'rid': 'rid'}, secret_key, algorithm='HS256')


@pytest.mark.usefixtures('siamclient')
@pytest.fixture(scope="module")
def response_builder(siamclient):
    return response.ResponseBuilder(siamclient)


@pytest.mark.usefixtures('config')
def test_server_errors(json_web_token, response_builder, config):
    tests = (
        (response_builder.authn_link, True, 'http://some.url'),
        (response_builder.authn_verify, 'aselect_credentials', 'rid', 'key'),
        (response_builder.session_renew, json_web_token[0], secret_key),
        (response_builder.session_end, json_web_token[0], secret_key),
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
    r = response_builder.authn_verify(ass, 'rid', secret_key)
    assert r[1] == 200
    decoded = jwt.decode(r[0], secret_key)
    assert decoded['exp'] == int(exp[:-3])
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
    r = response_builder.authn_verify('aselect_credentials', 'rid', secret_key)
    assert r == ('verification of credentials failed', 400)


@pytest.mark.usefixtures('config')
def test_authn_verify_malformed(response_builder, config):
    resp_malformed = urllib.parse.urlencode({
        'result_code': client.Client.RESULT_CODE_OK,
        'tgt_exp_time': "1",
        'uid': 'uid'
    })
    responses.add(responses.GET, config['SIAM_BASE_URL'], status=200, body=resp_malformed)
    r = response_builder.authn_verify('aselect_credentials', 'rid', secret_key)
    assert r == ('malformed response from SIAM', 502)
    resp_malformed = urllib.parse.urlencode({
        'i am empty': None,
    })
    responses.add(responses.GET, config['SIAM_BASE_URL'], status=200, body=resp_malformed)
    r = response_builder.authn_verify('aselect_credentials', 'rid', secret_key)
    assert r == ('malformed response from SIAM', 502)
