"""
    auth.blueprints.token
    ~~~~~~~~~~~~~~~~~~~~~
"""
from flask import Blueprint, make_response
import werkzeug.exceptions

from auth import audit, httputils, exceptions


def blueprint(refreshtokenbuilder, accesstokenbuilder, authz_flow):
    # Create the Flask blueprint
    blueprint = Blueprint('jwt_app', __name__)

    @blueprint.route('/accesstoken', methods=('GET',))
    @httputils.assert_acceptable('text/plain')
    @httputils.response_mimetype('text/plain')
    @httputils.insert_jwt
    def accesstoken(refreshjwt):
        """ Route for creating an access token based on a refresh token
        """
        try:
            refreshtoken = refreshtokenbuilder.decode(refreshjwt)
        except exceptions.JWTException as e:
            raise werkzeug.exceptions.BadRequest('Refreshtoken invalid') from e
        authz_level = authz_flow(refreshtoken['sub'])
        accesstoken = accesstokenbuilder.create(authz=authz_level)
        accessjwt = accesstoken.encode()
        audit.log_accesstoken(refreshjwt, accessjwt)
        return make_response((accessjwt, 200))

    @blueprint.route('/refreshtoken', methods=('GET',))
    @httputils.assert_acceptable('text/plain')
    @httputils.response_mimetype('text/plain')
    def refreshtoken():
        """ Route for creating an anonymous refreshtoken
        """
        refreshtoken = refreshtokenbuilder.create(sub=None)
        refreshjwt = refreshtoken.encode()
        audit.log_refreshtoken(refreshjwt)
        return make_response((refreshjwt, 200))

    return blueprint
