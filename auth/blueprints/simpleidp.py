"""
    auth.blueprints.idp
    ~~~~~~~~~~~~~~~~~~~

    Temporary identity provider.
"""
import urllib

import werkzeug
from flask import Blueprint, make_response, redirect, render_template, request

from auth import audit, decorators, url


def blueprint(refreshtokenbuilder, allowed_callback_hosts, authz_map):
    blueprint = Blueprint('idp_app', __name__)

    def _validate_callback_url(callback_url):
        """ Takes a string, validates it.

        - The host must be allowed
        - the URL must contain a fragment identifier (or at least end with a hash "#"

        :raise werkzeug.exceptions.BadRequest: if the callback is invalid.
        :return: None

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
        if parsed_callback.fragment is None:
            raise werkzeug.exceptions.BadRequest(
                'Missing required fragment identifier in URL "{}"'.format(callback_url)
            )

    def _whitelisted(request):
        return 'X-Auth-Whitelist' in request.headers

    @blueprint.route('/login', methods=('GET',))
    @decorators.assert_req_args('callback')
    def show_form():
        """ Route for creating an access token based on a refresh token
        """
        callback = request.args.get('callback')
        _validate_callback_url(callback)
        return render_template(
            'login.html',
            query_string=urllib.parse.urlencode({'callback': callback}),
            whitelisted=_whitelisted(request)
        )

    @blueprint.route('/login', methods=('POST',))
    @decorators.assert_req_args('callback')
    def handle_login():
        """ Route for creating an access token based on a refresh token.

        Is this still an accurate docstring? —PvB
        """
        callback = request.args.get('callback')
        _validate_callback_url(callback)
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        as_employee = request.form.get('type', '') == 'employee'
        if as_employee:
            if _whitelisted(request):
                email = 'Medewerker'
            else:
                return render_template(
                    'login.html',
                    query_string=urllib.parse.urlencode({'callback': callback}),
                    error_html='Uw komt niet meer vanaf een vertrouwd internetadres.',
                    whitelisted=False
                )
        elif not authz_map.verify_password(email, password):
            return render_template(
                'login.html',
                query_string=urllib.parse.urlencode({'callback': callback}),
                error_html='De combinatie gebruikersnaam en wachtwoord wordt niet herkend.',
                whitelisted=_whitelisted(request)
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
