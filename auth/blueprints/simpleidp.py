"""
    auth.blueprints.idp
    ~~~~~~~~~~~~~~~~~~~

    Temporary identity provider.
"""
import urllib

import werkzeug
from flask import Blueprint, redirect, render_template, request

from auth import audit, decorators


def blueprint(tokenbuilder, allowed_callbacks, users):
    blueprint = Blueprint('idp_app', __name__)

    def _validate_callback_url(callback_url):
        """ Takes a string, validates it.

        :raise werkzeug.exceptions.BadRequest: if the callback is invalid.
        :return: None

        """
        if not any(callback_url.startswith(cb) for cb in allowed_callbacks):
            raise werkzeug.exceptions.BadRequest(
                'Bad callback URL "{}"'.format(callback_url)
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
                    error_html='U komt niet meer vanaf een vertrouwd internetadres.',
                    whitelisted=False
                )
        elif not users.verify_password(email, password):
            return render_template(
                'login.html',
                query_string=urllib.parse.urlencode({'callback': callback}),
                error_html='De combinatie gebruikersnaam en wachtwoord wordt niet herkend.',
                whitelisted=_whitelisted(request)
            )
        jwt = tokenbuilder.create(sub=email).encode()
        audit.log_token(jwt, email)
        # Put credential in callback query
        scheme, netloc, path, query, fragment = urllib.parse.urlsplit(callback)
        query = {k: v[0] for k, v in urllib.parse.parse_qs(query).items()}
        query['credentials'] = jwt
        query = urllib.parse.urlencode(query)
        result = urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))
        return redirect(result, code=303)

    return blueprint
