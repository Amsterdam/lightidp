"""
    Authentication & authorization service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from flask import Flask

from .web import siamrequesthandler
from . import jwtutils, siamclient


# ====== 0. CREATE FLASK WSGI APP AND LOAD SETTINGS

app = Flask(__name__)
app.config.from_object('auth.settings')
app.config.from_envvar('AUTHN_SIAM_SETTINGS', silent=True)


# ====== 1. PARSE SETTINGS (todo: validate semantics somewhere else)

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


# ====== 2. CREATE FLASK BLUEPRINTS AND SUPPORTING OBJECTS

# Create the JWT token builder
tokenbuilder = jwtutils.TokenBuilder(jwt_rt_secret, jwt_at_secret, jwt_rt_lifetime, jwt_at_lifetime, jwt_algorithm)
# Create a siam client
siamclient = siamclient.Client(siam_base_url, siam_app_id, siam_aselect_server, siam_shared_secret)
# Create the SIAM blueprint
siam_bp = siamrequesthandler.blueprint(siamclient, tokenbuilder)


# ====== 3. RUN CONFIGURATION CHECKS

# Do SIAM configuration checks ONLY if we're not in debug mode
if not app.debug:
    # Check whether we can get a authn link from SIAM
    try:
        siamclient.get_authn_link(False, 'http://test')
    except (siamclient.RequestException, siamclient.ResponseException):
        app.logger.critical('Couldn\'t verify that the SIAM config is correct')
        raise
    except Exception:
        app.logger.critical('An unknown error occurred during startup')
        raise

# Check whether we can generate a JWT
try:
    tokenbuilder.accesstoken_for('test').encode()
except (jwtutils.InvalidKeyError, jwtutils.InvalidTokenError):
    app.logger.critical('Couldn\'t verify that the JWT config is correct')
    raise
except Exception:
    app.logger.critical('An unknown error occurred during startup')
    raise


# ====== 4. REGISTER FLASK BLUEPRINTS

# SIAM
app.register_blueprint(siam_bp, url_prefix="{}{}".format(app_root, siam_root))
