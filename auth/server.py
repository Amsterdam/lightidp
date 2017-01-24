"""
    Authentication & authorization service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from flask import Flask

from .web import siamrequesthandler
from . import jwtutils

# create the WSGI application
app = Flask(__name__)
app.config.from_object('auth.settings')
app.config.from_envvar('AUTHN_SIAM_SETTINGS', silent=True)

# load configuration
app_root = app.config['APP_ROOT']
siam_base_url = app.config['SIAM_URL']
siam_root = app.config['SIAM_ROOT']
siam_app_id = app.config['SIAM_APP_ID']
siam_aselect_server = app.config['SIAM_A_SELECT_SERVER']
siam_shared_secret = app.config['SIAM_SHARED_SECRET']
jwt_algorithm = app.config['JWT_ALGORITHM']
jwt_at_secret = app.config['JWT_AT_SECRET']
jwt_rt_secret = app.config['JWT_RT_SECRET']
jwt_at_lifetime = app.config['JWT_AT_LIFETIME']
jwt_rt_lifetime = app.config['JWT_RT_LIFETIME']

# Create the JWT token builder
tokenbuilder = jwtutils.TokenBuilder(
    jwt_rt_secret, jwt_at_secret, jwt_rt_lifetime, jwt_at_lifetime, jwt_algorithm
)

# Create the SIAM blueprint
siam_bp = siamrequesthandler.blueprint(siam_base_url, siam_app_id,
                                       siam_aselect_server, siam_shared_secret,
                                       tokenbuilder)

# Register the blueprint
app.register_blueprint(siam_bp, url_prefix="{}{}".format(app_root, siam_root))
