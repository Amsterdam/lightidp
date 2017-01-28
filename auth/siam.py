"""
    auth.siam
    ~~~~~~~~~
"""
import collections
import logging
import requests
import time
import urllib

from auth import exceptions

logger = logging.getLogger(__name__)

# Base class for Client, to make sure it's immutable after construction
_Client = collections.namedtuple(
    '_Client', 'base_url app_id aselect_server shared_secret'
)


class Client(_Client):
    """ Client bundles all runtime configuration parameters in it's constructor
    and provides methods for all four distinct requests supported by the
    service.

    :param base_url: base URL of the siam service.
    :param app_id: the app id of the calling application, as configured in the
        siam server.
    :param aselect_server: the aselect_server identifier.
    :param shared_secret: the siam shared secret.
    """

    RESULT_OK = '0000'
    RESULT_INVALID_CREDENTIALS = '0007'

    def _request(self, params, timeout):
        """ Convenience method to make a GET request to SIAM.

        :param params: GET query string parameters, as a dictionary
        :param timeout: How long to wait for the server to send data before
            giving up, as a float, or a (connect timeout, read timeout) tuple.
        :see: http://docs.python-requests.org/en/master/user/advanced/#timeouts
        """
        url = '{}?{}'.format(self.base_url, urllib.parse.urlencode(params))
        try:
            r = requests.get(url, timeout=timeout)
        except requests.Timeout as e:
            raise exceptions.GatewayTimeoutException() from e
        except requests.RequestException as e:
            raise exceptions.GatewayRequestException() from e
        except requests.ConnectionError as e:
            raise exceptions.GatewayConnectionException() from e
        if r.status_code >= 400:
            logger.critical('HTTP {} response from '
                            'SIAM for {}'.format(r.status_code, url))
            raise exceptions.GatewayRequestException()
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

        This method also reports malformed responses from SIAM. A response is
        considered correct if it contains:

        1. a result_code other than 0000
        2. a result_code 0000, a uid and a tgt_exp_time that is larger than now

        :param timeout: How long to wait for the server to send data before
            giving up, as a float, or a (connect timeout, read timeout) tuple.
        :see: http://docs.python-requests.org/en/master/user/advanced/#timeouts
        """
        request_params = {
            'request': 'verify_credentials',
            'a-select-server': self.aselect_server,
            'shared_secret': self.shared_secret,
            'aselect_credentials': aselect_credentials,
            'rid': rid,
        }
        r = self._request(request_params, timeout)
        parsed = urllib.parse.parse_qs(r.text)
        expected_param_keys = {'result_code', 'tgt_exp_time', 'uid'}
        result = {k: parsed[k][0] for k in expected_param_keys if k in parsed}
        has_missing_params = len(expected_param_keys) - len(result)
        resultcode = result.get('result_code')
        valid_exp = int(time.time()) < int(result.get('tgt_exp_time', 0))
        if has_missing_params:
            malformed = resultcode is None or resultcode == self.RESULT_OK
            if malformed:
                raise exceptions.GatewayResponseException(
                    'Malformed response: {}'.format(parsed)
                )
        elif resultcode == self.RESULT_OK and not valid_exp:
            raise exceptions.GatewayResponseException('tgt_exp_time expired')
        return result

    def renew_session(self, aselect_credentials, timeout=(3.05, 1)):
        params = {
            'request': 'upgrade_tgt',
            'a-select-server': self.aselect_server,
            'crypted_credentials': aselect_credentials,
        }
        r = self._request(params, timeout)
        parsed = urllib.parse.parse_qs(r.text)
        if 'result_code' not in parsed:
            raise exceptions.GatewayResponseException(
                'Malformed response: {}'.format(parsed))
        return parsed['result_code'][0] == self.RESULT_OK

    def end_session(self, aselect_credentials, timeout=(3.05, 1)):
        params = {
            'request': 'kill_tgt',
            'a-select-server': self.aselect_server,
            'tgt_blob': aselect_credentials
        }
        r = self._request(params, timeout)
        return r.status_code
