"""
    Authentication service
    ~~~~~~~~~~~~~~~~~~~~~~
"""
import logging.config
import os

from dpuser import Users
from flask import Flask

from . import token
from .config import load as config_load
from .blueprints import idpblueprint

# ====== 1. LOAD CONFIGURATION SETTINGS AND INITIALIZE LOGGING

config = config_load(configpath=os.getenv('CONFIG'))
logging.config.dictConfig(config['logging'])
_logger = logging.getLogger(__name__)

# ====== 2. CREATE AUTHZ FLOW
dsn = 'postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
    **config['postgres']
)
users = Users(dsn)
tokenbuilder = token.TokenBuilder(**config['jwt'])

# ====== 3. RUN CONFIGURATION CHECKS

# Check whether we can generate refreshtokens
try:
    tokenbuilder.decode(tokenbuilder.create().encode())
except:
    _logger.critical('Cannot startup: invalid config')
    raise

# ====== 4. CREATE FLASK WSGI APP AND BLUEPRINTS

app = Flask('authserver', static_url_path="{}/idp/static".format(config['app']['root']))
idp_bp = idpblueprint(tokenbuilder, config['callbacks'], users)

# SimpleIdP
app.register_blueprint(idp_bp, url_prefix="{}/idp".format(config['app']['root']))
