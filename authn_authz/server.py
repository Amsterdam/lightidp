"""
    Authentication / authorization service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from flask import Flask

import siam

# create the WSGI application
app = Flask(__name__)
app.config.from_object('settings')
app.config.from_envvar('AUTHN_SIAM_SETTINGS', silent=True)

# load configuration
# TODO: we should parse and validate the config before using it!
siam_base_url = app.config['SIAM_URL']
siam_route_base = app.config['SIAM_ROUTE_BASE']
siam_app_id = app.config['SIAM_APP_ID']
siam_aselect_server = app.config['SIAM_A_SELECT_SERVER']
siam_shared_secret = app.config['SIAM_SHARED_SECRET']
jwt_secret = app.config['SECRET_KEY']

# Load the SIAM request handler
siam_requests = siam.RequestHandler(siam_base_url, siam_app_id,
                                    siam_aselect_server, siam_shared_secret,
                                    jwt_secret)

# Setup the SIAM routes
app.add_url_rule('{}/authenticate'.format(siam_route_base),
                 view_func=siam_requests.authenticate,
                 methods=('GET',))

app.add_url_rule('{}/token'.format(siam_route_base),
                 view_func=siam_requests.token,
                 methods=('GET', 'POST'))
