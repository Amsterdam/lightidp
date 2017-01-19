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
from auth.siam import client


@pytest.mark.usefixtures('config', 'siamclient')
@responses.activate
def test_siam_server_error(config, siamclient):
    responses.add(responses.GET, config['SIAM_BASE_URL'], status=500)
    try:
        siamclient._request({}, 1.0)
    except client.RequestException:
        pass
    else:
        assert False, 'Client should have raised an exception'


@pytest.mark.usefixtures('config', 'siamclient')
@responses.activate
def test_get_authn_link(config, siamclient):
    rid = '1'

    # mock the response
    body = urllib.parse.urlencode({
        'as_url': config['SIAM_BASE_URL'] + '?request=login1',
        'a-select-server': config['SIAM_ASELECT_SERVER'],
        'rid': rid,
    })
    responses.add(responses.GET, config['SIAM_BASE_URL'], status=200, body=body)

    expected = '{}?request=login1&a-select-server={}&rid={}'.format(
        config['SIAM_BASE_URL'], config['SIAM_ASELECT_SERVER'], rid
    )
    resp = siamclient.get_authn_link(False, 'http://some.callback.url')
    assert resp == expected
