"""
    auth.decorators
    ~~~~~~~~~~~~~~~

    This module provides several decorators that help with common HTTP
    protocol related tasks, such as checking, parsing or setting headers.
"""
import functools

from flask import request
import werkzeug.exceptions


def assert_req_args(*required):
    """ Decorator to check the presence of required request arguments. Raises a
    400 if the request is not valid.

    Usage:

    ::

        @app.route('/')
        @decorators.assert_req_args('uid', 'callback')
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
