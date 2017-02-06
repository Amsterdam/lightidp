"""
    auth.blueprints.siam
    ~~~~~~~~~~~~~~~~~~~~
"""
import werkzeug.exceptions
from flask import Blueprint, request, make_response, redirect
from auth import httputils


def blueprint(client, tokenbuilder, authz_flow):
    """ `Flask blueprint <http://flask.pocoo.org/docs/0.12/blueprints/>`_ for
    SIAM IdP related requests.

    This function returns a blueprint with two routes configured:

    - GET /authenticate: get a SIAM authn URL
    - GET /token: get a JWT after a succesful authentication

    :param siam.Client client: The client for the SIAM server
    :param token.Builder tokenbuilder: The JWT builder
    :return: :class:`flask.Blueprint`
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
        if ass != client.aselect_server:
            raise werkzeug.exceptions.BadRequest('Unsupported a-select-server')
        verification = client.verify_creds(creds, rid)
        if verification['result_code'] != client.RESULT_OK:
            raise werkzeug.exceptions.BadRequest("Couldn't verify credentials")
        # all checks done, now create and return the JWT
        basetoken = tokenbuilder.accesstoken_for(verification['uid'])
        basetoken['orig_iat'] = basetoken['iat']
        basetoken['authz'] = authz_flow(verification['uid'])
        basetoken['uid'] = verification['uid']
        return make_response((basetoken.encode(), 200))

    return blueprint
