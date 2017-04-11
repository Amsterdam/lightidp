"""
    auth.blueprints.idp
    ~~~~~~~~~~~~~~~~~~~

    Temporary identity provider.
"""
import base64
import urllib

import werkzeug
from flask import Blueprint, make_response, redirect, render_template, request

from auth import audit, decorators, url


def blueprint(refreshtokenbuilder, allowed_callback_hosts, authz_map):
    blueprint = Blueprint('idp_app', __name__)

    def _valid_callback_bytes(callback_url):
        """ Takes a string, validates it against all allowed hosts and (if all is
        well) returns a bytestring.
        """
        parsed_callback = url.parse_url(callback_url)
        host = parsed_callback.host
        scheme = parsed_callback.scheme
        for allowed_host, schemes in allowed_callback_hosts.items():
            if (host == allowed_host or host.endswith('.' + allowed_host)) and scheme in schemes:
                break
        else:
            raise werkzeug.exceptions.BadRequest(
                'Bad callback URL "{}"'.format(callback_url)
            )
        try:
            return callback_url  # .encode('ascii')
        except UnicodeEncodeError:
            raise werkzeug.exceptions.BadRequest(
                'Callback parameter may only include ascii characters'
            )

    @blueprint.route('/login', methods=('GET',))
    @decorators.assert_req_args('callback')
    def show_form():
        """ Route for creating an access token based on a refresh token
        """
        callback = _valid_callback_bytes(request.args.get('callback'))
        return render_template(
            'login.html', query_string=urllib.parse.urlencode({'callback': callback})
        )

    @blueprint.route('/login', methods=('POST',))
    @decorators.assert_req_args('callback')
    def handle_login():
        """ Route for creating an access token based on a refresh token.

        Is this still an accurate docstring? —PvB
        """
        callback = _valid_callback_bytes(request.args.get('callback'))
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        as_employee = request.form.get('as_employee', '') == 'yes'
        if as_employee:
            email = 'Medewerker'
        elif not authz_map.verify_password(email, password):
            return render_template(
                'login.html', query_string=urllib.parse.urlencode({'callback': callback})
            )
        jwt = refreshtokenbuilder.create(sub=email).encode()
        audit.log_refreshtoken(jwt, email)
        response_params = urllib.parse.urlencode({
            'aselect_credentials': jwt,
            'rid': 0,
            'a-select-server': 0
        })
        return redirect('{}?{}'.format(callback, response_params), code=302)

    @blueprint.route('/token', methods=('GET',))
    @decorators.assert_acceptable('text/plain')
    @decorators.assert_req_args('aselect_credentials', 'rid', 'a-select-server')
    @decorators.response_mimetype('text/plain')
    def token():
        return make_response((request.args['aselect_credentials'], 200))

    return blueprint
