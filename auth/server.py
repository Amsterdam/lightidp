"""
    Authentication service
    ~~~~~~~~~~~~~~~~~~~~~~
"""
import logging.config
import os

from authorization import AuthzMap
from flask import Flask

from . import token
from .config import load as config_load
from .blueprints import idpblueprint

# ====== 1. LOAD CONFIGURATION SETTINGS AND INITIALIZE LOGGING

config = config_load(configpath=os.getenv('CONFIG'))
logging.config.dictConfig(config['logging'])
_logger = logging.getLogger(__name__)

# ====== 2. CREATE AUTHZ FLOW

authz_map = AuthzMap(**config['postgres'])
tokenbuilder = token.TokenBuilder(**config['jwt'])

# ====== 3. RUN CONFIGURATION CHECKS

# Check whether we can generate refreshtokens
try:
    tokenbuilder.decode(tokenbuilder.create().encode())
except exceptions.JWTException:
    _logger.critical('Couldn\'t verify the refreshtoken config')
    raise
except Exception:
    _logger.critical('An unknown error occurred during startup')
    raise

# Check whether we can get authorization levels
try:
    authz_map.get('non-existing-user', None)
except:
    _logger.critical('Cannot check authorization levels in the database')
    raise

# ====== 4. CREATE FLASK WSGI APP AND BLUEPRINTS

app = Flask('authserver', static_url_path="{}/idp/static".format(config['app']['root']))
idp_bp = idpblueprint(tokenbuilder, config['callbacks'], authz_map)

# SimpleIdP
app.register_blueprint(idp_bp, url_prefix="{}/idp".format(config['app']['root']))
