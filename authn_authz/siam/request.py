"""
    Request handling
    ~~~~~~~~~~~~~~~~
"""
from flask import request, make_response
from .client import Client
from .response import ResponseBuilder


class RequestHandler:

    def __init__(self, base_url, app_id, aselect_server, shared_secret,
                 jwt_secret_key):
        self.client = Client(base_url, app_id, aselect_server, shared_secret)
        self.aselect_server = aselect_server
        self.jwt_secret_key = jwt_secret_key
        self.response_builder = ResponseBuilder(self.client)

    def authenticate(self):
        """ Route for authn requests
        """
        if 'callback' not in request.args:
            response = ('Must provide a callback URL', 400)
        elif 'active' in request.args:
            response = self.response_builder.authn_link(
                                            False,
                                            request.args['callback'])
        else:
            response = self.response_builder.authn_link(
                                            True,
                                            request.args['callback'])
        return make_response(response)

    def token(self):
        """ Route for token requests
        """
        if 'text/plain' not in request.accept_mimetypes:
            response = ('Can only serve tokens in plain text (set '
                        'your Accept header to support text/plain)', 406)
        elif request.method == 'POST':
            if 'Content-Type' not in request.headers or \
                    request.headers['Content-Type'][:10] != 'text/plain':
                response = ('Must use Content-Type plain/text', 415)
            elif len(request.data) == 0:
                response = ('POST request is empty', 400)
            elif 'renew' in request.args:
                response = self.response_builder.session_renew(
                                    request.data, self.jwt_secret_key)
            elif 'expire' in request.args:
                response = self.response_builder.session_end(
                                    request.data, self.jwt_secret_key)
            else:
                response = ('Unsupported operation (provide either '
                            '?renew or ?expire)', 400)
        else:  # GET
            creds = request.args.get('aselect_credentials') or None
            rid = request.args.get('rid') or None
            ass = request.args.get('a-select-server') or None
            if None in (creds, rid, ass):
                response = ('Must provide query parameters for '
                            'aselect_credentials, rid and a-select-server',
                            400)
            elif ass != self.aselect_server:
                response = ('Unsupported a-select-server', 400)
            else:
                response = self.response_builder.authn_verify(
                                    creds, rid, self.jwt_secret_key)
        r = make_response(response)
        r.mimetype = 'text/plain'
        return r
