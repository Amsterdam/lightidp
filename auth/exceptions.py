"""
auth.exceptions
~~~~~~~~~~~~~~~~~~~

This module defines the set of Exceptions that can be thrown throughout auth.
"""


class AuthException(Exception):
    """ Base exception for all other exceptions defined in auth.
    """

    def __init__(self, *args, **kwargs):
        super(AuthException, self).__init__(*args, **kwargs)


class CallbackException(AuthException):
    """ Base class for all exceptions related to upstream problems with the IdP.
    """


class GatewayException(AuthException):
    """ Base class for all exceptions related to upstream problems with the IdP.
    """


class GatewayConnectionException(GatewayException):
    """ Will be raised in the event of a network problem (e.g. DNS failure,
    refused connection, etc) while talking to an IdP.
    """


class GatewayTimeoutException(GatewayException):
    """ Will be raised when either a connection or a request to an IdP times out.
    """


class GatewayRequestException(GatewayException):
    """ Will be raised when the IdP can't handle our request.
    """


class GatewayResponseException(GatewayException):
    """ Will be raised when the response from an IdP is not one we understand.
    """


class GatewayBadCredentialsException(GatewayException):
    """ Will be raised by siam.get_user_attributes
    """


class JWTException(AuthException):
    """ Base exception for all JWT errors.

    Catching this exception will also catch :class:`JWTDecodeException` and
    :class:`JWTExpiredSignatureException`.
    """


class JWTDecodeException(JWTException):
    """ Will be raised when a given JWT cannot be decoded, for whatever reason.
    """


class JWTExpiredSignatureException(JWTException):
    """ Will be raised when the signature on a given JWT has expired (the
    ``exp`` claim).
    """
