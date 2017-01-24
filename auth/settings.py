"""
    Authn / authz settings
    ~~~~~~~~~~~~~~~~~~~~~~

    See below all available settings. Override by setting the corresponsing
    environment variables. Optionally you can override these parameters in a
    separate settings file, and point to that in env var `AUTHN_SIAM_SETTINGS`.
    This may be useful during development.

    You _MUST_ override:

    - `SIAM_URL`: The URL endpoint for SIAM
    - `SIAM_A_SELECT_SERVER`: The a-select server (whatever that is)
    - `SIAM_APP_ID`: Your application ID
    - `SIAM_SHARED_SECRET`: Your shared secret
    - `JWT_SHARED_SECRET_KEY`: The seed for access tokens

    You _MAY_ override:

    - `DEBUG`: Run Flask in debug mode (default False)
    - `JWT_ALGORITHM`: The algorithm to use for JWT encryption (default HS256)
    - `JWT_SECRET_KEY`: The seed for refresh tokens (default JWT_SHARED_SECRET_KEY)
    - `JWT_EXPIRATION_DELTA`: Expiration for access tokens (default 300 seconds)
    - `JWT_REFRESH_EXPIRATION_DELTA`: Expiration for access tokens (default 1 week)

    If you use a separate configuration file with `AUTHN_SIAM_SETTINGS`, you
    can also override other Flask configuration parameters. See
    http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values for
    an overview.
"""
import os

# Flask config. See documentation at
# http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values
DEBUG = os.getenv('DEBUG', False) and True  # convert truthy / falsey to bool

# Application config
APP_ROOT = '/auth'

# SIAM config
SIAM_ROOT = '/siam'
SIAM_URL = os.getenv('SIAM_URL')
SIAM_A_SELECT_SERVER = os.getenv('SIAM_A_SELECT_SERVER')
SIAM_APP_ID = os.getenv('SIAM_APP_ID')
SIAM_SHARED_SECRET = os.getenv('SIAM_SHARED_SECRET')

# JWT config
JWT_ALGORITHM = 'HS256'
JWT_AT_SECRET = os.getenv('JWT_SHARED_SECRET_KEY')
JWT_RT_SECRET = os.getenv('JWT_SECRET_KEY', JWT_AT_SECRET)
JWT_AT_LIFETIME = int(os.getenv('JWT_EXPIRATION_DELTA', 300))
JWT_RT_LIFETIME = int(os.getenv('JWT_REFRESH_EXPIRATION_DELTA', 3600*24*7))
