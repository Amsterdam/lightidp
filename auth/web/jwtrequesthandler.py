"""
    auth.jwt.requesthandler
    ~~~~~~~~~~~~~~~~~~~~~~~~
"""
from flask import Blueprint, request, make_response
import jwt
import werkzeug.exceptions
from auth import httputils


def assert_valid_jwt(f):
    """ Decorator that translates PyJWT exceptions into 40X client errors.
    """
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            raise werkzeug.exceptions.BadRequest('JWT token expired')
        except jwt.InvalidTokenError:
            raise werkzeug.exceptions.BadRequest('JWT could not be decoded')
    return wrapper


def blueprint(tokenbuilder):
    # Create the Flask blueprint
    app = Blueprint('jwt_app', __name__)

    @app.route('/token', methods=('POST',))
    @httputils.assert_acceptable('text/plain')
    @httputils.assert_mimetypes('text/plain')
    @assert_valid_jwt
    @httputils.response_mimetype('text/plain')
    def token_renew():
        """ Route for renewing a token
        """
        token = tokenbuilder.decode_accesstoken(request.data)
        new_token = tokenbuilder.basetoken_for(token['uid'])
        token.update(new_token)
        if token['exp'] > token['orig_iat'] + tokenbuilder.rt_lifetime:
            raise werkzeug.exceptions.BadRequest('Max token refresh expired')
        return make_response(token.encode(), 200)

    return app
