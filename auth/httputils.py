"""
    auth.httputils
    ~~~~~~~~~~~~~~

    This module provides several decorators that help with common HTTP
    protocol related tasks, such as checking, parsing or setting headers.
"""
import functools
from flask import make_response, request
import werkzeug.exceptions
from auth import exceptions


def assert_acceptable(*mimetypes):
    """ Decorator for the Accept header. Raises a 406 Not Acceptable if we
    can't comply.

    Usage:

    ::

        @app.route('/')
        @httputils.assert_acceptable('text/plain', 'application/json')
        def handle():
            data = ... # create some response data
            best_mimetype = request.accept_mimetypes.best_match(
                ('text/plain', 'application/json')
            )
            if best_mimetype == 'text/plain':
                # return text/plain
            else:
                # return json

    :param mimetypes: sequence of mimetypes
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            capable = set(mimetypes)
            acceptable = {r[0] for r in request.accept_mimetypes}
            if not (capable & acceptable or '*/*' in acceptable):
                # No literal / catchall match, lets take this apart
                for acc in acceptable:
                    try:
                        (first, second) = acc.split('/')
                    except ValueError:
                        continue
                    if second == '*':
                        first = '{}/'.format(first)
                        if {cap for cap in capable if first in cap}:
                            break
                else:
                    raise werkzeug.exceptions.NotAcceptable(
                        'Resource can only serve: {}'.format(capable)
                    )
            return f(*args, **kwargs)
        return wrapper
    return decorator


def assert_mimetypes(*mimetypes):
    """ Decorator for the request Content-type header. Raises a 415 Unsupported
    Media Type if we can't comply.

    Usage:

    ::

        @app.route('/')
        @httputils.assert_mimetypes('text/plain', 'application/json')
        def handle():
            if request.mimetype == 'text/plain':
                # read text/plain
            else:
                # read json

    :param mimetypes: sequence of mimetypes
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            acceptable = set(mimetypes)
            sent = request.mimetype
            if sent not in acceptable:
                raise werkzeug.exceptions.UnsupportedMediaType(
                    'Resouce only accepts: {}'.format(acceptable)
                )
            return f(*args, **kwargs)
        return wrapper
    return decorator


def assert_req_args(*required):
    """ Decorator to check the presence of required request arguments. Raises a
    400 if the request is not valid.

    Usage:

    ::

        @app.route('/')
        @httputils.assert_req_args('uid', 'callback')
        def handle():
            # these are now guaranteed to be present
            uid = request.args.get('uid')
            callback = request.args.get('callback')

    :param required_args: sequence of strings
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            missing = tuple(a for a in required if a not in request.args)
            if missing:
                raise werkzeug.exceptions.BadRequest(
                    'Resouce requires query parameters: {}'.format(required)
                )
            return f(*args, **kwargs)
        return wrapper
    return decorator


def assert_gateway(f):
    """ Decorator that translates gateway exceptions into 502/504 server errors.

    Usage:

    ::

        @app.route('/')
        @httputils.assert_gateway
        def handle():
            # this may raise a gateway error that will be translated into a 50X
            siamclient.renew_session(...)

    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except exceptions.GatewayTimeoutException as e:
            raise werkzeug.exceptions.GatewayTimeout() from e
        except (exceptions.GatewayRequestException,
                exceptions.GatewayResponseException,
                exceptions.GatewayConnectionException) as e:
            raise werkzeug.exceptions.BadGateway() from e
    return wrapper


def response_mimetype(mimetype):
    """ Decorator that sets the mimetype of the response to the one given.

    Usage:

    ::

        @app.route('/')
        @httputils.response_mimetype('application/json')
        def handle():
            make_response({"msg": "hello world"})

    :param mimetype: A mimetype string
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            response = f(*args, **kwargs)
            response.mimetype = mimetype
            return response
        return wrapper
    return decorator


def _invalid_token_401(errmsg=None):
    """ Helper to return a 401 Unauthorized.

    This function will include a ``WWW-Authenticate`` in the response detailing
    the error code as specified in section 3 of the `OAuht2 Bearer Token Usage spec
    <http://self-issued.info/docs/draft-ietf-oauth-v2-bearer.html#authn-header>`_.

    If no ``errmsg`` is given then WWW-Authenticate will not include an error at
    all. If given, then ``error`` will be "invalid_token" and
    ``error_description`` will be ``errmsg``.

    :param str errmsg: The message to be included in error_description
    """
    header_value = 'Bearer realm="datapunt"'
    if (errmsg):
        header_value += ', error="invalid_token", error_description="{}"'.format(errmsg)
    return make_response(('', 401, {'WWW-Authenticate': header_value}))


def insert_jwt(refreshtokenbuilder):
    """ Decorator that provides the JWT that must be present in the
    Authorization header. Will return a 401 if the JWT is missing or the
    Authorization header is malformed.

    Usage:

    ::

        @app.route('/')
        @httputils.insert_jwt
        def handle(jwt):
            # jwt contains the JWT
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if 'Authorization' not in request.headers:
                return _invalid_token_401()

            try:
                prefix, jwt = request.headers['Authorization'].split()
            except ValueError:
                error_msg = 'Authorization header must have format: Bearer [JWT]'
                return _invalid_token_401(errmsg=error_msg)

            if prefix != 'Bearer':
                error_msg = 'Authorization header prefix must be Bearer'
                return _invalid_token_401(errmsg=error_msg)

            try:
                tokendata = refreshtokenbuilder.decode(jwt)
            except exceptions.JWTException:
                return _invalid_token_401(errmsg='Refreshtoken invalid')

            return f(tokendata, jwt, *args, **kwargs)
        return wrapper
    return decorator
