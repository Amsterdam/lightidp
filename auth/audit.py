"""
    auth.audit
    ~~~~~~~~~~

    Wraps logging functions for JWT audit logging. Its goal is to provide
    enough information to track tokens.

    Usage:

    ::

        import auth.audit
        token = ...
        auth.audit.log_token(token, sub)
"""
import logging

_jwtlogger = logging.getLogger('auditlog.authserver')


def _mac_from_jwt(jwt):
    """ Extract the message authentication code (MAC) from the given JWT.

    :param jwt:
        For compatibility `jwt` may be either `bytes` (e.g. as created through
        `jwt.encode <jwt>` or `str` (e.g. as fetched from a header).
    :return: `str`
    """
    try:
        jwt_str = str(jwt, 'utf-8')
    except TypeError:
        jwt_str = jwt
    try:
        return jwt_str.split('.')[2]
    except IndexError:
        _jwtlogger.fatal('Not a valid JWT: {}'.format(jwt_str))
        raise

def log_token(token, sub):
    """ Logs a token

    :param token: The refreshtoken that was created
    :param sub: The subject associated with this refreshtoken
    """
    log_msg = 'Refreshtoken created: {} | sub={}'
    token_mac = _mac_from_jwt(token)
    _jwtlogger.info(log_msg.format(token_mac, sub))
