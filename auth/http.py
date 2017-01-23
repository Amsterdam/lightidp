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
        @auth.http.assert_acceptable('text/plain', 'application/json')
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
        @auth.http.assert_mimetypes('text/plain', 'application/json')
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
