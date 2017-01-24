"""
    auth.http
    ~~~~~~~~~
"""
import functools
from flask import request
import werkzeug.exceptions


def assert_acceptable(*mimetypes):
    """ Decorator for the Accept header. Raises a 406 Not Acceptable if we
    can't comply.

    Usage:

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
            print(args)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def assert_mimetypes(*mimetypes):
    """ Decorator for the request Content-type header. Raises a 415 Unsupported
    Media Type if we can't comply.

    Usage:

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


def response_mimetype(mimetype):
    """ Decorator that sets the mimetype of the response to the one given.

    Usage:

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
