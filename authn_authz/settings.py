'''
Default settings. Override by creating a new file and pointing to it in
AUTHN_SIAM_SETTINGS
'''
import os

# Flask config. See documentation at
# http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values
DEBUG = os.getenv('SECRET_KEY') is None
PREFERRED_URL_SCHEME = 'http'
SECRET_KEY = os.getenv('SECRET_KEY', 'make me more secret')

# SIAM config
SIAM_ROUTE_BASE = '/siam'
SIAM_URL = 'https://siam1.test.anoigo.nl/aselectserver/server'
SIAM_A_SELECT_SERVER = 'siam1.test.anoigo.nl'
SIAM_APP_ID = 'amsterdam1'
SIAM_SHARED_SECRET = '553G-11FJ-VBNC-QQWD-99CV-LJHA-HGPPIK-94FD'
