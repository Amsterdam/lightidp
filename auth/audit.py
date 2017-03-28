"""
    auth.audit
    ~~~~~~~~~~

    Wraps logging functions for JWT audit logging. Its goal is to provide
    enough information to track access tokens back to refreshtokens, and track
    refreshtokens back to subjects.

    Usage:

    ::

        import auth.audit
        refreshtoken = ...
        auth.audit.log_refreshtoken(refreshtoken, sub)
        accesstoken = ...
        auth.audit.log_accesshtoken(refreshtoken, accesstoken)
"""
import logging

_jwtlogger = logging.getLogger('auditlog.authserver')


def _mac_from_jwt(jwt):
    """ Extract the message authentication code (MAC) from the given JWT.

    :param jwt:
        For compatibility `jwt` may be either `bytes` (e.g. as created through
        :func:`jwt.encode`) or `str` (e.g. as fetched from a header).
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


def log_accesstoken(refreshjwt, accessjwt):
    """ Logs an accesstoken request as “Refreshtoken [MAC] -> Accesstoken [MAC]”

    :param refreshjwt: The refreshtoken that was used for creating this accesstoken.
    :param accessjwt: The accesstoken that was created
    """
    log_msg = 'Refreshtoken {} -> Accesstoken {}'
    refresh_mac = _mac_from_jwt(refreshjwt)
    access_mac = _mac_from_jwt(accessjwt)
    _jwtlogger.info(log_msg.format(refresh_mac, access_mac))


def log_refreshtoken(refreshjwt, sub):
    """ Logs a refreshtoken request as “Refreshtoken created: [MAC]”

    :param refreshjwt: The refreshtoken that was created
    :param sub: The subject associated with this refreshtoken
    """
    log_msg = 'Refreshtoken created: {} | sub={}'
    refresh_mac = _mac_from_jwt(refreshjwt)
    _jwtlogger.info(log_msg.format(refresh_mac, sub))
