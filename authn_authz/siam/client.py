"""
    The SIAM client
    ~~~~~~~~~~~~~~~
"""
import logging
import requests
import urllib

logger = logging.getLogger(__name__)

# wrappers to keep the dependency on requests limited
Timeout = requests.Timeout
RequestException = requests.RequestException


class Client:
    """ Client bundles all runtime configuration parameters in it's constructor
    and provides methods for all four distinct requests supported by the
    service.

    :param base_url: base URL of the siam service.
    :param app_id: the app id of the calling application, as configured in the
        siam server.
    :param app_url: the app url that the siam server can redirect the client
        to after succesful authentication.
    :param aselect_server: the aselect_server identifier.
    :param shared_secret: the siam shared secret.
    """

    RESULT_CODE_OK = '0000'
    RESULT_CODE_INVALID_CREDENTIALS = '0007'

    def __init__(self, base_url, app_id, aselect_server,
                 shared_secret):
        self.base_url = base_url
        self.app_id = app_id
        self.aselect_server = aselect_server
        self.shared_secret = shared_secret

    def _request(self, params, timeout):
        """ Convenience method to make a GET request to SIAM.

        :param params: GET query string parameters, as a dictionary
        :param timeout: How long to wait for the server to send data before
            giving up, as a float, or a (connect timeout, read timeout) tuple.
        :see: http://docs.python-requests.org/en/master/user/advanced/#timeouts
        """
        url = '{}?{}'.format(self.base_url, urllib.parse.urlencode(params))
        r = requests.get(url, timeout=timeout)
        if r.status_code != 200:
            logger.critical('HTTP {} response from '
                            'SIAM for {}'.format(r.status_code, url))
            raise requests.RequestException()
        return r

    def get_authn_link(self, passive, callback_url, timeout=(3.05, 1)):
        """ Request an authn url from the IdP, either passive or not.

        :param passive: whether or not to request a passive URL
        :param timeout: How long to wait for the server to send data before
            giving up, as a float, or a (connect timeout, read timeout) tuple.
        :rtype: str
        :see: http://docs.python-requests.org/en/master/user/advanced/#timeouts
        """
        params = {
            'request': 'authenticate',
            'forced_logon': 'false',
            'app_id': self.app_id,
            'app_url': callback_url,
            'a-select-server': self.aselect_server,
            'shared_secret': self.shared_secret,
            'forced_passive': passive
        }
        r = self._request(params, timeout)
        response = urllib.parse.parse_qs(r.text)
        passive_authn_link = '{}&a-select-server={}&rid={}'.format(
            response['as_url'][0],
            response['a-select-server'][0],
            response['rid'][0])
        return passive_authn_link

    def verify_creds(self, aselect_credentials, rid, timeout=(3.05, 1)):
        """ Make a credential verification request to the IdP.

        :param timeout: How long to wait for the server to send data before
            giving up, as a float, or a (connect timeout, read timeout) tuple.
        :see: http://docs.python-requests.org/en/master/user/advanced/#timeouts
        """
        params = {
            'request': 'verify_credentials',
            'a-select-server': self.aselect_server,
            'shared_secret': self.shared_secret,
            'aselect_credentials': aselect_credentials,
            'rid': rid,
        }
        r = self._request(params, timeout)
        return urllib.parse.parse_qs(r.text)

    def renew_session(self, aselect_credentials, timeout=(3.05, 1)):
        params = {
            'request': 'upgrade_tgt',
            'a-select-server': self.aselect_server,
            'crypted_credentials': aselect_credentials,
        }
        r = self._request(params, timeout)
        return urllib.parse.parse_qs(r.text)

    def end_session(self, aselect_credentials, timeout=(3.05, 1)):
        params = {
            'request': 'kill_tgt',
            'a-select-server': self.aselect_server,
            'tgt_blob': aselect_credentials
        }
        r = self._request(params, timeout)
        return urllib.parse.parse_qs(r.text)
