"""
    Tests for the SIAM client
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Note that this only tests :meth:`~auth.siam.client.Client._request` and
    :meth:`~auth.siam.client.Client.get_authn_link`. The other methods are just
    convenient wrappers for :meth:`~auth.siam.client.Client._request`.
"""
import pytest
import responses
import urllib.parse
import auth.siam.client

SIAM_BASE_URL = 'http://fake.siam'
SIAM_APP_ID = 'fake'
SIAM_ASELECT_SERVER = 'fake.siam'
SIAM_SHARED_SECRET = 'fake.secret'


@pytest.fixture(scope="module")
def siamclient():
    client = auth.siam.client.Client(
        base_url=SIAM_BASE_URL,
        app_id=SIAM_APP_ID,
        aselect_server=SIAM_ASELECT_SERVER,
        shared_secret=SIAM_SHARED_SECRET
    )
    return client


@responses.activate
def test_siam_server_error(siamclient):
    responses.add(responses.GET, SIAM_BASE_URL, status=500)
    try:
        siamclient._request({}, 1.0)
    except auth.siam.client.RequestException:
        pass
    else:
        assert False, 'Client should have raised an exception'


@responses.activate
def test_get_authn_link(siamclient):
    rid = '1'

    # mock the response
    body = urllib.parse.urlencode({
        'as_url': SIAM_BASE_URL + '?request=login1',
        'a-select-server': SIAM_ASELECT_SERVER,
        'rid': rid,
    })
    responses.add(responses.GET, SIAM_BASE_URL, status=200, body=body)

    expected = '{}?request=login1&a-select-server={}&rid={}'.format(
        SIAM_BASE_URL, SIAM_ASELECT_SERVER, rid
    )
    resp = siamclient.get_authn_link(False, 'http://some.callback.url')
    assert resp == expected
