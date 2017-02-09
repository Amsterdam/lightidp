"""
    Authentication & authorization service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import authorization
from flask import Flask

from .blueprints import siamblueprint
from . import exceptions, siam, token
import authorization_levels


# ====== 0. CREATE FLASK WSGI APP AND LOAD SETTINGS

app = Flask(__name__)
app.config.from_object('auth.settings')
app.config.from_envvar('AUTH_SETTINGS', silent=True)


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
accesstokenbuilder_settings = {
    'secret': app.config['JWT_AT_SECRET'],
    'lifetime': app.config['JWT_AT_LIFETIME'],
    'algorithm': app.config['JWT_ALGORITHM']
}
refreshtokenbuilder_settings = {
    'secret': app.config['JWT_RT_SECRET'],
    'lifetime': app.config['JWT_RT_LIFETIME'],
    'algorithm': app.config['JWT_ALGORITHM']
}
postgres_settings = {
    'host': app.config['PG_HOST'],
    'port': app.config['PG_PORT'],
    'dbname': app.config['PG_DB'],
    'user': app.config['PG_USER'],
    'password': app.config['PG_PASS'],
}


# ====== 2. CREATE FLASK BLUEPRINTS AND SUPPORTING OBJECTS

# Create the authz flow
authz_flow = authorization.authz_mapper(**postgres_settings)
# Create the JWT token builder
tokenbuilder = token.AccessTokenBuilder(**accesstokenbuilder_settings)
# Create a siam client
siamclient = siam.Client(**siamclient_settings)
# Create the SIAM blueprint
siam_bp = siamblueprint(siamclient, tokenbuilder, authz_flow)


# ====== 3. RUN CONFIGURATION CHECKS

if not skip_conf_check:
    # 3.1 Check whether we can get a authn link from SIAM
    try:
        siamclient.get_authn_link(False, 'http://test')
    except exceptions.AuthException:
        app.logger.critical('Couldn\'t verify that the SIAM config is correct')
        raise
    except Exception:
        app.logger.critical('An unknown error occurred during startup')
        raise

    # 3.2 Check whether we can generate a JWT
    try:
        tokenbuilder.decode(tokenbuilder.create(authorization_levels.LEVEL_DEFAULT).encode())
    except exceptions.JWTException:
        app.logger.critical('Couldn\'t verify that the JWT config is correct')
        raise
    except Exception:
        app.logger.critical('An unknown error occurred during startup')
        raise


# ====== 4. REGISTER FLASK BLUEPRINTS

# SIAM
app.register_blueprint(siam_bp, url_prefix="{}{}".format(app_root, siam_root))


# ====== 5. ENABLE SIMPLE CORS

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
