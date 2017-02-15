"""
    auth.audit
    ~~~~~~~~~~
"""
import logging

jwtlogger = logging.getLogger('JWTlog')


def _mac_from_jwt(jwt):
    # jwt may be bytes or string, depending on whether it comes from an Accept
    # header or from jwt.encode
    dot = (isinstance(jwt, bytes) and b'.') or '.'
    return jwt.split(dot)[2]


def log_accesstoken(refreshjwt, accessjwt):
    log_msg = 'Refreshtoken {} -> Accesstoken {}'
    refresh_mac = _mac_from_jwt(refreshjwt)
    access_mac = _mac_from_jwt(accessjwt)
    jwtlogger.info(log_msg.format(refresh_mac, access_mac))


def log_refreshtoken(refreshjwt):
    log_msg = 'Refreshtoken created: {}'
    refresh_mac = _mac_from_jwt(refreshjwt)
    jwtlogger.info(log_msg.format(refresh_mac))
