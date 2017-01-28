"""
    auth.blueprints.siam
    ~~~~~~~~~~~~~~~~~~~~
"""
import werkzeug.exceptions
from flask import Blueprint, request, make_response, redirect
from auth import httputils


def blueprint(client, tokenbuilder):
    """ Wrapper for a SIAM request handler.

    This function generates a SIAM request handler for the given config.

    :param base_url: The base url of the SIAM server
    :param app_id: The application ID of our app
    :param aselectserver: The aselect server ID
    :param secret: The shared secret for authn with SIAM
    :param jwt_secret: The JWT seed
    :param jwt_lt: The JWT lifetime
    :return: RequestHandler
    """

    # Create the Flask blueprint
    blueprint = Blueprint('siam_app', __name__)

    @blueprint.route('/authenticate', methods=('GET',))
    @httputils.assert_req_args('callback')
    @httputils.assert_gateway
    def authenticate():
        """ Route for authn requests
        """
        response = client.get_authn_link(
            'active' not in request.args, request.args['callback']
        )
        return redirect(response, code=307)

    @blueprint.route('/token', methods=('GET',))
    @httputils.assert_acceptable('text/plain')
    @httputils.assert_req_args('aselect_credentials', 'rid', 'a-select-server')
    @httputils.assert_gateway
    @httputils.response_mimetype('text/plain')
    def token():
        """ Route for getting a new token
        """
        creds = request.args.get('aselect_credentials') or None
        rid = request.args.get('rid') or None
        ass = request.args.get('a-select-server') or None
        if ass != ass:
            raise werkzeug.exceptions.BadRequest('Unsupported a-select-server')
        verification = client.verify_creds(creds, rid)
        if verification['result_code'] != client.RESULT_OK:
            raise werkzeug.exceptions.BadRequest("Couldn't verify credentials")
        # all checks done, now create and return the JWT
        basetoken = tokenbuilder.accesstoken_for(verification['uid'])
        basetoken['orig_iat'] = basetoken['iat']
        basetoken['aselect_credentials'] = creds
        basetoken['rid'] = rid
        return make_response((basetoken.encode(), 200))

    return blueprint
