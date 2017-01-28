"""
    auth.jwt.requesthandler
    ~~~~~~~~~~~~~~~~~~~~~~~~
"""
from flask import Blueprint, request, make_response
import werkzeug.exceptions
from auth import httputils, exceptions


def blueprint(tokenbuilder):
    # Create the Flask blueprint
    blueprint = Blueprint('jwt_app', __name__)

    @blueprint.route('/token', methods=('POST',))
    @httputils.assert_acceptable('text/plain')
    @httputils.assert_mimetypes('text/plain')
    @httputils.response_mimetype('text/plain')
    def token_renew():
        """ Route for renewing a token
        """
        try:
            token = tokenbuilder.decode_accesstoken(request.data)
        except exceptions.JWTException as e:
            raise werkzeug.exceptions.BadRequest('Invalid JWT') from e
        new_token = tokenbuilder.basetoken_for(token['uid'])
        token.update(new_token)
        if token['exp'] > token['orig_iat'] + tokenbuilder.rt_lifetime:
            raise werkzeug.exceptions.BadRequest('Max token refresh expired')
        return make_response(token.encode(), 200)

    return blueprint
