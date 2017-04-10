"""
    Authentication & authorization service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import logging.config
import os

import authorization
from flask import Flask

from . import exceptions, token
from .config import load as config_load
from .blueprints import jwtblueprint, idpblueprint

# ====== 1. LOAD CONFIGURATION SETTINGS AND INITIALIZE LOGGING

config = config_load(configpath=os.getenv('CONFIG'))
logging.config.dictConfig(config['logging'])
_logger = logging.getLogger(__name__)

# ====== 2. CREATE SIAM CLIENT, TOKENBUILDERS AND AUTHZ FLOW

authz_level_for, password_validator = authorization.authz_mapper(**config['postgres'])
refreshtokenbuilder = token.RefreshTokenBuilder(**config['jwt']['refreshtokens'])
accesstokenbuilder = token.AccessTokenBuilder(**config['jwt']['accesstokens'])
# siamclient = siam.Client(**config['siam'])

# ====== 3. RUN CONFIGURATION CHECKS

# 3.1 Check whether we can get an authn redirect from SIAM
# try:
#     siamclient.get_authn_redirect(False, 'http://localhost')
# except exceptions.AuthException:
#     _logger.critical('Couldn\'t verify the SIAM config')
#     raise
# except Exception:
#     _logger.critical('An unknown error occurred during startup')
#     raise

# 3.2 Check whether we can generate refreshtokens
try:
    refreshtokenbuilder.decode(refreshtokenbuilder.create(sub='sub').encode())
except exceptions.JWTException:
    _logger.critical('Couldn\'t verify the refreshtoken config')
    raise
except Exception:
    _logger.critical('An unknown error occurred during startup')
    raise

# 3.3 Check whether we can generate accesstokens
try:
    accesstokenbuilder.decode(accesstokenbuilder.create(authz=0).encode())
except exceptions.JWTException:
    _logger.critical('Couldn\'t verify the accesstoken config')
    raise
except Exception:
    _logger.critical('An unknown error occurred during startup')
    raise

# 3.4 Check whether we can get authorization levels
try:
    authz_level_for('user')
except:
    _logger.critical('Cannot check authorization levels in the database')
    raise

# ====== 4. CREATE FLASK WSGI APP AND BLUEPRINTS

app = Flask('authserver')
# siam_bp = siamblueprint(siamclient, refreshtokenbuilder, config['allowed_callback_hosts'])
jwt_bp = jwtblueprint(refreshtokenbuilder, accesstokenbuilder, authz_level_for)
idp_bp = idpblueprint(refreshtokenbuilder, config['allowed_callback_hosts'], password_validator)

# JWT
app.register_blueprint(jwt_bp, url_prefix="{}".format(config['app']['root']))

# SIAM
# app.register_blueprint(siam_bp, url_prefix="{}/siam".format(config['app']['root']))

# SimpleIdP
app.register_blueprint(idp_bp, url_prefix="{}/idp".format(config['app']['root']))
