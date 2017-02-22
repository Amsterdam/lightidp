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
            if not capable & acceptable:
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


def insert_jwt(f):
    """ Decorator that provides the JWT that must be present in the
    Authorization header. Will return a 401 if the JWT is missing or the
    Authorization header is malformed.

    This function will include a ``WWW-Authenticate`` in the response detailing
    the error code as specified in section 3 of the `OAuht2 Bearer Token Usage spec
    <http://self-issued.info/docs/draft-ietf-oauth-v2-bearer.html#authn-header>`_.

    Usage:

    ::

        @app.route('/')
        @httputils.insert_jwt
        def handle(jwt):
            # jwt contains the JWT
    """
    header_bearer = 'Bearer realm="datapunt"'
    header_bearer_error = header_bearer + ', error="invalid_token", error_description="{}"'

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if 'Authorization' not in request.headers:
            return make_response(('', 401, {'WWW-Authenticate': header_bearer}))

        try:
            prefix, jwt = request.headers['Authorization'].split()
        except ValueError:
            error_msg = 'Authorization header must have format: Bearer [JWT]'
            return make_response(
                ('', 401, {
                    'WWW-Authenticate': header_bearer_error.format(error_msg)
                })
            )

        if prefix != 'Bearer':
            error_msg = 'Authorization header prefix must be Bearer'
            return make_response(
                ('', 401, {
                    'WWW-Authenticate': header_bearer_error.format(error_msg)
                })
            )

        return f(jwt, *args, **kwargs)
    return wrapper
