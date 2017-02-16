"""
    Authentication & authorization service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import logging
import os

import authorization
from flask import Flask

from . import config, exceptions, siam, token
from .blueprints import siamblueprint, jwtblueprint

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

# ====== 1. LOAD CONFIGURATION SETTINGS

settings = config.load(configpath=os.getenv('CONFIG'))

# ====== 2. CREATE SIAM CLIENT, TOKENBUILDERS AND AUTHZ FLOW

authz_flow = authorization.authz_mapper(**settings['postgres'])
refreshtokenbuilder = token.RefreshTokenBuilder(**settings['jwt']['refreshtokens'])
accesstokenbuilder = token.AccessTokenBuilder(**settings['jwt']['accesstokens'])
siamclient = siam.Client(**settings['siam'])

# ====== 3. RUN CONFIGURATION CHECKS

# 3.1 Check whether we can get a authn link from SIAM
try:
    siamclient.get_authn_redirect(False, 'http://test')
except exceptions.AuthException:
    _logger.critical('Couldn\'t verify the SIAM config')
    raise
except Exception:
    _logger.critical('An unknown error occurred during startup')
    raise

# 3.2 Check whether we can generate accesstokens
try:
    refreshtokenbuilder.decode(refreshtokenbuilder.create('sub').encode())
except exceptions.JWTException:
    _logger.critical('Couldn\'t verify the refreshtoken config')
    raise
except Exception:
    _logger.critical('An unknown error occurred during startup')
    raise

# 3.3 Check whether we can generate accesstokens
try:
    accesstokenbuilder.decode(accesstokenbuilder.create(0).encode())
except exceptions.JWTException:
    _logger.critical('Couldn\'t verify the accesstoken config')
    raise
except Exception:
    _logger.critical('An unknown error occurred during startup')
    raise


# ====== 4. CREATE FLASK WSGI APP AND BLUEPRINTS

app = Flask(__name__)
jwt_bp = jwtblueprint(refreshtokenbuilder, accesstokenbuilder, authz_flow)
siam_bp = siamblueprint(siamclient, refreshtokenbuilder, authz_flow)

# JWT
app.register_blueprint(jwt_bp, url_prefix="{}".format(settings['app']['root']))

# SIAM
app.register_blueprint(siam_bp, url_prefix="{}/siam".format(settings['app']['root']))
