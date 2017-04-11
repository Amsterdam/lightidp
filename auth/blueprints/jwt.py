"""
    auth.blueprints.token
    ~~~~~~~~~~~~~~~~~~~~~
"""
from flask import Blueprint, make_response

from auth import audit, decorators
from authorization import levels


def blueprint(refreshtokenbuilder, accesstokenbuilder, authz_map):
    """ JWT-only resources.

    This function returns a blueprint with two routes configured:

    - GET /accesstoken: get an accesstoken

    :param token.RefreshTokenBuilder refreshtokenbuilder: JWT builder for refreshtokens
    :param token.AccessTokenBuilder accesstokenbuilder: JWT builder for accesstokens
    :param AuthzMap authzmap: map for user -> authz level
    :return: :class:`flask.Blueprint`
    """
    blueprint = Blueprint('jwt_app', __name__)

    @blueprint.route('/accesstoken', methods=('GET',))
    @decorators.assert_acceptable('text/plain')
    @decorators.response_mimetype('text/plain')
    @decorators.insert_jwt(refreshtokenbuilder)
    def accesstoken(tokendata, refreshjwt):
        """ Route for creating an access token based on a refresh token
        """
        authz_level = levels.LEVEL_EMPLOYEE \
            if tokendata['sub'] == 'Medewerker' \
            else authz_map.get(tokendata['sub'], levels.LEVEL_DEFAULT)
        accesstoken = accesstokenbuilder.create(authz=authz_level)
        accessjwt = accesstoken.encode()
        audit.log_accesstoken(refreshjwt, accessjwt)
        return make_response((accessjwt, 200))

    return blueprint
