"""
    auth.blueprints.siam
    ~~~~~~~~~~~~~~~~~~~~
"""
import werkzeug.exceptions
from flask import Blueprint, request, make_response, redirect

from auth import audit, decorators, exceptions


def blueprint(client, refreshtokenbuilder):
    """ SIAM IdP related resources.

    This function returns a blueprint with two routes configured:

    - GET /authenticate: get a SIAM authn URL
    - GET /token: get a JWT after a succesful authentication

    :param siam.Client client: The client for the SIAM server
    :param token.RefreshTokenBuilder refreshtokenbuilder: The JWT builder for refresh tokens
    :return: :class:`flask.Blueprint`
    """

    # Create the Flask blueprint
    blueprint = Blueprint('siam_app', __name__)

    @blueprint.route('/authenticate', methods=('GET',))
    @decorators.assert_req_args('callback')
    @decorators.assert_gateway
    def authenticate():
        """ Route for authn requests
        """
        response = client.get_authn_redirect(
            'active' not in request.args, request.args['callback']
        )
        return redirect(response, code=307)

    @blueprint.route('/token', methods=('GET',))
    @decorators.assert_acceptable('text/plain')
    @decorators.assert_req_args('aselect_credentials', 'rid', 'a-select-server')
    @decorators.assert_gateway
    @decorators.response_mimetype('text/plain')
    def token():
        """ Route for getting a new token
        """
        creds = request.args.get('aselect_credentials') or None
        rid = request.args.get('rid') or None
        ass = request.args.get('a-select-server') or None
        if ass != client.aselect_server:
            raise werkzeug.exceptions.BadRequest('Unsupported a-select-server')
        try:
            user_attrs = client.get_user_attributes(creds, rid)
        except exceptions.GatewayBadCredentialsException:
            raise werkzeug.exceptions.BadRequest("Couldn't verify credentials")
        # all checks done, now create, log and return the JWT
        jwt = refreshtokenbuilder.create(sub=user_attrs['uid']).encode()
        audit.log_refreshtoken(jwt, sub=user_attrs['uid'])
        return make_response((jwt, 200))

    return blueprint
