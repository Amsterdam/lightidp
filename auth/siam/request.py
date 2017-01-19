"""
    Request handling
    ~~~~~~~~~~~~~~~~
"""
import collections
from flask import request, make_response
from .client import Client
from .response import ResponseBuilder

_RequestHandler = collections.namedtuple('_RequestHandler', 'client rb ass')


def request_handler(base_url, app_id, ass, secret, jwt_secret, jwt_lt):
    # Create the SIAM client
    siam_client = Client(base_url, app_id, ass, secret)
    # Create the SIAM response builder
    siam_response_builder = ResponseBuilder(siam_client, jwt_secret, jwt_lt)
    # Load the SIAM request handler
    return RequestHandler(siam_client, siam_response_builder, ass)


class RequestHandler(_RequestHandler):

    def authenticate(self):
        """ Route for authn requests
        """
        if 'callback' not in request.args:
            response = ('Must provide a callback URL', 400)
        elif 'active' in request.args:
            response = self.rb.authn_link(False, request.args['callback'])
        else:
            response = self.rb.authn_link(True, request.args['callback'])
        return make_response(response)

    def token(self):
        """ Route for token requests
        """
        if 'text/plain' not in request.accept_mimetypes:
            response = ('Can only serve tokens in plain text (set your Accept '
                        'header to support text/plain)', 406)
        elif request.method == 'POST':
            if request.mimetype != 'text/plain':
                response = ('Mime-type not text/plain', 415)
            elif len(request.data) == 0:
                response = ('POST request is empty', 400)
            else:
                response = self.rb.session_renew(request.data)
        else:  # GET
            creds = request.args.get('aselect_credentials') or None
            rid = request.args.get('rid') or None
            ass = request.args.get('a-select-server') or None
            if None in (creds, rid, ass):
                response = (
                    'Must provide query parameters for aselect_credentials, '
                    'rid and a-select-server', 400
                )
            elif ass != self.ass:
                response = ('Unsupported a-select-server', 400)
            else:
                response = self.rb.authn_verify(creds, rid)
        r = make_response(response)
        r.mimetype = 'text/plain'
        return r
