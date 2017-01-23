"""
    Authentication & authorization service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from flask import Flask

from . import siam

# create the WSGI application
app = Flask(__name__)
app.config.from_object('auth.settings')
app.config.from_envvar('AUTHN_SIAM_SETTINGS', silent=True)

# load configuration
siam_base_url = app.config['SIAM_URL']
siam_route_base = app.config['SIAM_ROUTE_BASE']
siam_app_id = app.config['SIAM_APP_ID']
siam_aselect_server = app.config['SIAM_A_SELECT_SERVER']
siam_shared_secret = app.config['SIAM_SHARED_SECRET']
jwt_secret = app.config['JWT_SECRET']
jwt_lifetime = app.config['JWT_LIFETIME']

# Load the SIAM request handler
siam_handler = siam.request_handler(siam_base_url, siam_app_id,
                                    siam_aselect_server, siam_shared_secret,
                                    jwt_secret, jwt_lifetime)

# Fail fast if SIAM config is incorrect
try:
    siam_handler.confcheck()
except Exception as e:
    app.logger.critical("Could not verify that the SIAM config is correct")
    raise e

# Register the request handler blueprint
app.register_blueprint(siam_handler.app, url_prefix=siam_route_base)
