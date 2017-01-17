'''
Created on 17 Jan 2017

@author: evert
'''
import jwt
import logging
from .client import Timeout, RequestException

logger = logging.getLogger(__name__)


def _siam_errors_to_50X(f):
    """ Decorator that translates SIAM exceptions into 50X server errors.
    """
    def wrapper(*args, **kwargs):
        try:
            resp = f(*args, **kwargs)
        except Timeout as e:
            logger.critical(e)
            resp = ('timeout while contacting the IdP', 504)
        except RequestException as e:
            logger.critical(e)
            resp = ('problem communicating with the IdP', 502)
        return resp
    return wrapper


def _jwt_errors_to_40X(f):
    """ Decorator that translates PyJWT exceptions into 40X client errors.
    """
    def wrapper(*args, **kwargs):
        try:
            resp = f(*args, **kwargs)
        except jwt.ExpiredSignatureError as e:
            logger.warn(e)
            resp = ('JWT token expired', 400)
        except jwt.exceptions.InvalidTokenError as e:
            logger.warn(e)
            resp = ('JWT token could not be decoded', 400)
        return resp
    return wrapper


class ResponseBuilder:

    def __init__(self, siamclient):
        self.client = siamclient

    @_siam_errors_to_50X
    def authn_link(self, passive):
        """ Redirect user to the IdP's authn page for (passive) authn.

        Responsecodes:
        * 307 Temporary Redirect if we received a URL from the IdP
        * 50X from _siam_50x_handler for siam errors out of our control

        :param passive: (truthy) create a link for passive authn
        """
        link = self.client.get_authn_link((passive and True) or False)
        return ('', 307, {'Location': link})

    @_siam_errors_to_50X
    def authn_verify(self, aselect_credentials, rid, secret_key):
        """ Verify the credentials and create a JWT token.

        Responsecodes:
        * 200 OK [JWT, expiry time] if the credentials are valid
        * 400 Bad Request if the credentials are invalid
        * 50X from _siam_50x_handler for siam errors out of our control

        :param aselect_credentials: The siam credentials provided by the client
        :param rid: The request identifier.
        :param secret_key: The secret key used for the JWT encryption
        """
        verification = self.client.verify_creds(aselect_credentials, rid)
        if verification['result_code'][0] != self.client.RESULT_CODE_OK:
            resp = ('verification of credentials failed', 400)
        else:
            encoded = jwt.encode({
                'exp': int(verification['tgt_exp_time'][0][:-3]),
                'ass': aselect_credentials,
                'rid': rid}, secret_key, algorithm='HS256')
            resp = (encoded, 200)
        return resp

    @_siam_errors_to_50X
    @_jwt_errors_to_40X
    def session_renew(self, encoded_jwt, secret_key):
        """ Renew the session and get a new expiry time.

        Responsecodes:
        * 200 OK Session is renewed
        * 400 Bad Request if SIAM tell us the credentials are invalid
        * 40X from _jwt_errors_to_40X if there was a problem with the JWT
        * 500 If we can't decode the encoded jwt token for some unknown reason
        * 50X from _siam_50x_handler for siam errors out of our control

        :param aselect_credentials: The siam credentials provided by the client
        """
        token = jwt.decode(encoded_jwt, key=secret_key)
        result = self.client.renew_session(token['ass'])['result_code'][0]
        if result == self.client.RESULT_CODE_INVALID_CREDENTIALS:
            resp = ('Credentials invalid', 400)
        elif result != self.client.RESULT_CODE_OK:
            resp = ('Renewal of credentials failed', 400)
        else:
            resp = self.authn_verify(token['ass'], token['rid'], secret_key)
        return resp

    @_siam_errors_to_50X
    @_jwt_errors_to_40X
    def session_end(self, encoded_jwt, secret_key):
        """ Invalidate the JWT and end the session with the IdP.

        Responsecodes:
        * 200 OK Session is ended
        * 40X from _jwt_errors_to_40X if there was a problem with the JWT
        * 50X from _siam_50x_handler for siam errors out of our control
        """
        token = jwt.decode(encoded_jwt, key=secret_key)
        self.client.end_session(token['ass'])
        return ('', 200)
