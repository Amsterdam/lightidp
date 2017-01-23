"""
    auth.siam.request
    ~~~~~~~~~~~~~~~~~
"""
import collections
import functools
import werkzeug.exceptions
from flask import Blueprint, request, make_response
from auth import http
from .client import Client
from .response import ResponseBuilder

RequestHandler = collections.namedtuple('RequestHandler', 'app confcheck')


def handler(base_url, app_id, aselectserver, secret, jwt_secret, jwt_lt):
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
    app = Blueprint('siam_app', __name__)
    # Create the SIAM client
    client = Client(base_url, app_id, aselectserver, secret)
    # Create the SIAM response builder
    rb = ResponseBuilder(client, jwt_secret, jwt_lt)

    @app.route('/authenticate', methods=('GET',))
    def authenticate():
        """ Route for authn requests
        """
        if 'callback' not in request.args:
            raise werkzeug.exceptions.BadRequest('Must provide a callback URL')
        if 'active' in request.args:
            response = rb.authn_link(False, request.args['callback'])
        else:
            response = rb.authn_link(True, request.args['callback'])
        return make_response(response)

    @app.route('/token', methods=('GET',))
    @http.assert_acceptable('text/plain')
    def token():
        """ Route for getting a new token
        """
        creds = request.args.get('aselect_credentials') or None
        rid = request.args.get('rid') or None
        ass = request.args.get('a-select-server') or None
        if None in (creds, rid, ass):
            raise werkzeug.exceptions.BadRequest(
                'Must provide query parameters: aselect_credentials, rid and '
                'a-select-server')
        if ass != aselectserver:
            raise werkzeug.exceptions.BadRequest('Unsupported a-select-server')
        r = make_response(rb.authn_verify(creds, rid))
        r.mimetype = 'text/plain'
        return r

    @app.route('/token', methods=('POST',))
    @http.assert_acceptable('text/plain')
    @http.assert_mimetypes('text/plain')
    def token_renew():
        """ Route for renewing a token
        """
        response = rb.session_renew(request.data)
        r = make_response(response)
        r.mimetype = 'text/plain'
        return r

    # This partial should be a good enough check on the siam config
    confcheck = functools.partial(client.get_authn_link, False, 'http://test')

    return RequestHandler(app, confcheck)
