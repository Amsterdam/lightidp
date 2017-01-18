"""
    Authn / authz settings
    ~~~~~~~~~~~~~~~~~~~~~~

    See below all available settings. Override by creating a new file and point
    to it in an env variable AUTHN_SIAM_SETTINGS. You should override at least
    all params you received from SIAM:

    SIAM_URL: The URL endpoint for SIAM
    SIAM_A_SELECT_SERVER: The a-select server (whatever that is)
    SIAM_APP_ID: Your application ID
    SIAM_SHARED_SECRET: Your shared secret
"""
import os

# Flask config. See documentation at
# http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values
DEBUG = False
PREFERRED_URL_SCHEME = 'https'
SECRET_KEY = os.getenv('SECRET_KEY')

# SIAM config
SIAM_ROUTE_BASE = '/siam'
SIAM_URL = '[siam url]'
SIAM_A_SELECT_SERVER = '[aselect server]'
SIAM_APP_ID = '[app_id]'
SIAM_SHARED_SECRET = '[secret]'
