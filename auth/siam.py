"""
    auth.siam
    ~~~~~~~~~
"""
import collections
import logging
import sys
import time
import urllib

import requests

from auth import exceptions

# Base class for Client, to make sure it's immutable after construction
_Client = collections.namedtuple(
    '_Client', 'base_url app_id aselect_server shared_secret'
)

# Shouldn't there be a _logger object, like in server.py? --PvB

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

    # Unused: --PvB
    RESULT_INVALID_CREDENTIALS = '0007'


    def _request(self, query_parameters, timeout):
        """ Convenience method to make a GET request to SIAM.

        :param query_parameters: GET query string parameters, as a dictionary
        :param timeout: How long to wait for the server to send data before
            giving up, as a float, or a (connect timeout, read timeout) tuple.
        :see: http://docs.python-requests.org/en/master/user/advanced/#timeouts
        :raise exceptions.GatewayTimeoutException: TODO --PvB
        :raise exceptions.GatewayRequestException: TODO --PvB
        :raise exceptions.GatewayConnectionException: TODO --PvB
        :return: decoded `application/x-www-form-urlencoded` response body, as a
            dict.
        """
        url = '{}?{}'.format(self.base_url, urllib.parse.urlencode(query_parameters))
        try: # <-- To log any raised exceptions.
            try: # <-- To rewrite requests.* exceptions to our own exception types.
                response = requests.get(url, timeout=timeout)
            except requests.Timeout as e:
                raise exceptions.GatewayTimeoutException() from e
            except requests.RequestException as e:
                raise exceptions.GatewayRequestException() from e
            except requests.ConnectionError as e:
                raise exceptions.GatewayConnectionException() from e

            # Was: >= 400   Hope this is ok? --PvB
            if response.status_code != 200:
                raise exceptions.GatewayRequestException(
                    'non-200 response code from SIAM: {}'.format(response.status_code)
                )
            try:
                retval = urllib.parse.parse_qs(response.text)
            except Exception as e:
                raise exceptions.GatewayResponseException(
                    'Couldn\'t decode SIAM response body: {}'.format(response.text)
                ) from e
            if 'result_code' in retval and retval['result_code'][0] != self.RESULT_OK:
                raise exceptions.GatewayResponseException(
                    'Unexpected result_code "{}" in response: "{}". Request URL: {}'.
                    format(retval['result_code'][0], response.text, url)
                )
        except exceptions.GatewayException:
            logging.critical('Exception talking to SIAM', exc_info=True, stack_info=True)
            raise
        return retval


    def get_authn_redirect(self, passive, callback_url, timeout=(3.05, 1)):
        """ Request an authn url from the IdP, either passive or not.

        :param passive: whether or not to request a passive URL :param timeout:
            How long to wait, in seconds, for the server to send data before
            giving up, as a float, or a (connect timeout, read timeout) tuple.
        :rtype: str
        :see: http://docs.python-requests.org/en/master/user/advanced/#timeouts
        :raise exceptions.GatewayRequestException: TODO --PvB
        """
        query_parameters = {
            'request': 'authenticate',
            'forced_logon': 'false',
            'app_id': self.app_id,
            'app_url': callback_url,
            'a-select-server': self.aselect_server,
            'shared_secret': self.shared_secret,
            'forced_passive': passive
        }
        response = self._request(query_parameters, timeout)
        expected_param_keys = {'result_code', 'as_url', 'a-select-server', 'rid'}
        result = {k: response[k][0] for k in expected_param_keys if k in response}
        if len(expected_param_keys) != len(result):
            raise exceptions.GatewayResponseException(
                'Missing required parameters in response: {}'.format(str(response))
            )
        passive_authn_link = '{}&a-select-server={}&rid={}'.format(
            result['as_url'],
            urllib.parse.quote(result['a-select-server']),
            urllib.parse.quote(result['rid'])
        )
        return passive_authn_link


    def get_user_attributes(self, aselect_credentials, rid, timeout=(3.05, 1)):
        """ Make a credential verification request to the IdP.

        This method also reports malformed responses from SIAM. A response is
        considered correct if it contains:

        1. a result_code other than 0000
        2. a result_code 0000, a uid and a tgt_exp_time that is larger than now
        
        No documentation about return type: this is a dict of strings, even
        though the tgt_exp_time is semantically a natural number. --PvB

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
        response = self._request(request_params, timeout)
        expected_param_keys = {'result_code', 'tgt_exp_time', 'uid'}
        result = {k: response[k][0] for k in expected_param_keys if k in response}
        if len(expected_param_keys) != len(result):
            raise exceptions.GatewayResponseException(
                'Missing required parameters in response: {}'.format(str(response))
            )
        if int(time.time()) >= int(result.get('tgt_exp_time', 0)):
            raise exceptions.GatewayResponseException('tgt_exp_time expired')
        return result
