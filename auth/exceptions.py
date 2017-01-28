"""
auth.exceptions
~~~~~~~~~~~~~~~~~~~

This module defines the set of Exceptions that can be thrown throughout auth.
"""


class AuthException(Exception):

    def __init__(self, *args, **kwargs):
        super(AuthException, self).__init__(*args, **kwargs)


class GatewayConnectionException(AuthException):
    ...


class GatewayTimeoutException(AuthException):
    ...


class GatewayRequestException(AuthException):
    ...


class GatewayResponseException(AuthException):
    ...


class JWTException(AuthException):
    ...


class JWTDecodeException(JWTException):
    ...


class JWTExpiredSignatureException(JWTException):
    ...
