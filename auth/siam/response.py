"""
    Response generation
    ~~~~~~~~~~~~~~~~~~~
"""
import collections
import jwt
import logging
import time
from .client import Timeout, RequestException

logger = logging.getLogger(__name__)

_ResponseBuilder = collections.namedtuple(
    '_ResponseBuilder', 'client jwt_secret jwt_lt'
)


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


class ResponseBuilder(_ResponseBuilder):

    @_siam_errors_to_50X
    def authn_link(self, passive, cb_url):
        """ Redirect user to the IdP's authn page for (passive) authn.

        Responsecodes:
        * 307 Temporary Redirect if we received a URL from the IdP
        * 50X from _siam_50x_handler for siam errors out of our control

        :param passive: (truthy) create a link for passive authn
        :param cb_url: (str) the callback URL to redirect to after
            authentication (must be urlencoded)
        """
        link = self.client.get_authn_link((passive and True) or False, cb_url)
        return ('', 307, {'Location': link})

    @_siam_errors_to_50X
    def authn_verify(self, aselect_credentials, rid):
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
        now = int(time.time())
        if len({'result_code', 'tgt_exp_time', 'uid'} - verification.keys()):
            logger.critical('SIAM sent a bad response on rid={}'.format(rid))
            resp = ('malformed response from SIAM', 502)
        elif verification['result_code'][0] != self.client.RESULT_OK:
            resp = ('verification of credentials failed', 400)
        elif now > int(verification['tgt_exp_time'][0][:-3] or 0):
            exp = verification['tgt_exp_time'][0][:-3]
            logger.critical('Exp time mismatch with SIAM (received={}, '
                            'local={})'.format(exp, now))
            resp = ('problem between auth server and SIAM', 502)
        else:
            encoded = jwt.encode({
                'exp': now,
                'orig_iat': now + self.jwt_lt,
                'username': verification['uid'][0],
                'ass': aselect_credentials,
                'rid': rid}, self.jwt_secret, algorithm='HS256')
            resp = (encoded, 200)
        return resp

    @_jwt_errors_to_40X
    def session_renew(self, encoded_jwt):
        """ Renew the session and get a new expiry time.

        Responsecodes:
        * 200 OK Session is renewed
        * 40X from _jwt_errors_to_40X if there was a problem with the JWT

        :param aselect_credentials: The siam credentials provided by the client
        """
        token = jwt.decode(encoded_jwt, key=self.jwt_secret)
        token['exp'] = int(time.time()) + self.jwt_lt
        return (jwt.encode(token, self.jwt_secret, algorithm='HS256'), 200)
