"""
    Authentication & authorization service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from flask import Flask

from .web import siamrequesthandler
from . import jwtutils, siam


# ====== 0. CREATE FLASK WSGI APP AND LOAD SETTINGS

app = Flask(__name__)
app.config.from_object('auth.settings')
app.config.from_envvar('AUTHN_SIAM_SETTINGS', silent=True)


# ====== 1. PARSE SETTINGS (todo: validate semantics somewhere else)

skip_conf_check = app.config['SKIP_CONF_CHECK']
app_root = app.config['APP_ROOT']
siam_root = app.config['SIAM_ROOT']
siamclient_settings = {
    'base_url': app.config['SIAM_URL'],
    'app_id': app.config['SIAM_APP_ID'],
    'aselect_server': app.config['SIAM_A_SELECT_SERVER'],
    'shared_secret': app.config['SIAM_SHARED_SECRET']
}
tokenbuilder_settings = {
    'rt_secret': app.config['JWT_RT_SECRET'],
    'at_secret': app.config['JWT_AT_SECRET'],
    'rt_lifetime': app.config['JWT_RT_LIFETIME'],
    'at_lifetime': app.config['JWT_AT_LIFETIME'],
    'algorithm': app.config['JWT_ALGORITHM']
}


# ====== 2. CREATE FLASK BLUEPRINTS AND SUPPORTING OBJECTS

# Create the JWT token builder
tokenbuilder = jwtutils.TokenBuilder(**tokenbuilder_settings)
# Create a siam client
siamclient = siam.Client(**siamclient_settings)
# Create the SIAM blueprint
siam_bp = siamrequesthandler.blueprint(siamclient, tokenbuilder)


# ====== 3. RUN CONFIGURATION CHECKS

if not skip_conf_check:
    # 3.1 Check whether we can get a authn link from SIAM
    try:
        siamclient.get_authn_link(False, 'http://test')
    except (siam.RequestException, siam.ResponseException):
        app.logger.critical('Couldn\'t verify that the SIAM config is correct')
        raise
    except Exception:
        app.logger.critical('An unknown error occurred during startup')
        raise

    # 3.2 Check whether we can generate a JWT
    try:
        tokenbuilder.accesstoken_for('test').encode()
    except (NotImplementedError, jwtutils.InvalidTokenError):
        app.logger.critical('Couldn\'t verify that the JWT config is correct')
        raise
    except Exception:
        app.logger.critical('An unknown error occurred during startup')
        raise


# ====== 4. REGISTER FLASK BLUEPRINTS

# SIAM
app.register_blueprint(siam_bp, url_prefix="{}{}".format(app_root, siam_root))
