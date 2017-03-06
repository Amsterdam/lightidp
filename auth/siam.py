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


class Client(_Client):
    """ Client bundles all runtime configuration parameters in it's constructor
    and provides methods for all four distinct requests supported by the
    service.

    "Parameters" doesn't feel quite right. "attributes"? --PvB

    :param base_url: base URL of the siam service.
    :param app_id: the app id of the calling application, as configured in the
        siam server.
    :param aselect_server: the aselect_server identifier.
    :param shared_secret: the siam shared secret.
    """

    RESULT_OK = '0000'
    RESULT_INVALID_CREDENTIALS = '0007'

    def _request(self, query_parameters, timeout):
        """ Convenience method to make a GET request to SIAM.

        Missing documentation: raise --PvB

        This documentation is not extracted by Sphinx --PvB

        :param query_parameters: GET query string parameters, as a dictionary
        :param timeout: How long to wait for the server to send data before
            giving up, as a float, or a (connect timeout, read timeout) tuple.
        :see: http://docs.python-requests.org/en/master/user/advanced/#timeouts
        :raise exceptions.GatewayTimeoutException: TODO --PvB
        :raise exceptions.GatewayRequestException: TODO --PvB
        :raise exceptions.GatewayConnectionException: TODO --PvB
        """
        url = '{}?{}'.format(self.base_url, urllib.parse.urlencode(query_parameters))
        try:
            r = requests.get(url, timeout=timeout)
        except requests.Timeout as e:
            raise exceptions.GatewayTimeoutException() from e
        except requests.RequestException as e:
            raise exceptions.GatewayRequestException() from e
        except requests.ConnectionError as e:
            raise exceptions.GatewayConnectionException() from e
        finally:
            # I'm not sure this will work. According to the docs, sys.exc_info
            # gives info about the latest exception caught in an except block.
            # This is a "finally" block. --PvB

            # Why not propagate this exception like above? --PvB
            if any(sys.exc_info()):  # an exception has been raised, lets log it
                logging.critical('Exception talking to SIAM', exc_info=True, stack_info=True)
        # This may fail because r is undefined: --PvB
        if r.status_code >= 400:
            logging.critical('HTTP {} response from SIAM'.format(r.status_code))
            raise exceptions.GatewayRequestException()
        return r

    def get_authn_redirect(self, passive, callback_url, timeout=(3.05, 1)):
        """ Request an authn url from the IdP, either passive or not.

        Missing documentation: :raise --PvB

        :param passive: whether or not to request a passive URL
        :param timeout: How long to wait for the server to send data before
            giving up, as a float, or a (connect timeout, read timeout) tuple.
            (What's the dimension of these floats? --PvB)
        :rtype: str
        :see: http://docs.python-requests.org/en/master/user/advanced/#timeouts
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
        r = self._request(query_parameters, timeout)
        # parse_qs excepts a query string, but you feed it a full URL. --PvB
        # By default, parse_qs assumes UTF-8 encoding, but we can't be sure
        # that's true. BINARY would be safer.
        response = urllib.parse.parse_qs(r.text)
        resultcode = response.get('result_code', ['no result code'])[0]
        if resultcode != self.RESULT_OK:
            logging.critical('Invalid SIAM response: {}'.format(r.text))
            raise exceptions.GatewayRequestException()
        # This can't work: putting unencoded data into a query string? --PvB
        # Should the fields below not be sanity checked as well, to prevent
        # KeyErrors? --PvB
        passive_authn_link = '{}&a-select-server={}&rid={}'.format(
            response['as_url'][0],
            response['a-select-server'][0],
            response['rid'][0])
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
        r = self._request(request_params, timeout)
        # parse_qs excepts a query string, but you feed it a full URL. --PvB
        # By default, parse_qs assumes UTF-8 encoding, but we can't be sure
        # that's true. BINARY would be safer.
        parsed = urllib.parse.parse_qs(r.text)
        expected_param_keys = {'result_code', 'tgt_exp_time', 'uid'}
        result = {k: parsed[k][0] for k in expected_param_keys if k in parsed}
        # Dangerous: assumes 0 is falsy. Better be explicit with != --PvB
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
