"""
    Configuration
    ~~~~~~~~~~~~~

    Required settings
    -----------------

    To run the service you must configure it for the IdPs you support.

    For SIAM you need the following:

    - ``SIAM_URL``: The URL endpoint for SIAM
    - ``SIAM_A_SELECT_SERVER``: The a-select server (whatever that is)
    - ``SIAM_APP_ID``: Your application ID
    - ``SIAM_SHARED_SECRET``: Your shared secret

    You'll also have to provide a shared key for access tokens:

    - ``JWT_SHARED_SECRET_KEY``: The seed for access tokens

    Optional settings
    -----------------

    Other settings you may (but don't need to) override:

    - ``DEBUG``: Run Flask in debug mode (default False)
    - ``JWT_ALGORITHM``: The algorithm to use for JWT encryption (default HS256)
    - ``JWT_SECRET_KEY``: The seed for refresh tokens (default JWT_SHARED_SECRET_KEY)
    - ``JWT_EXPIRATION_DELTA``: Expiration for access tokens (default 300 seconds)
    - ``JWT_REFRESH_EXPIRATION_DELTA``: Expiration for access tokens (default 1 week)

    How to configure the service
    ----------------------------

    The settings are `loaded using Flask
    <http://flask.pocoo.org/docs/0.12/config/>`_. Strictly speaking you have
    two ways of configuring the service:

    1. The way you should do it: *as environment variables*. You can define
       variables in a file and export them using set -a / set +a, ie ``set -a
       && source settings.env && set+a``. You should go this route if you
       intend to run the service in Docker.
    2. The way you probably shouldn't do it: point to a Flask config file in a
       ``AUTH_SETTINGS`` environment variable. This will also allow you to
       override `other Flask specific settings
       <http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values>`_.
"""
import os

# Flask config. See documentation at
# http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values
DEBUG = os.getenv('DEBUG', False) and True  # convert truthy / falsey to bool

# Application config
APP_ROOT = '/auth'
SKIP_CONF_CHECK = os.getenv('AUTH_SKIP_CONF_CHECK', False) and True

# SIAM config
SIAM_ROOT = '/siam'
SIAM_URL = os.getenv('SIAM_URL')
SIAM_A_SELECT_SERVER = os.getenv('SIAM_A_SELECT_SERVER')
SIAM_APP_ID = os.getenv('SIAM_APP_ID')
SIAM_SHARED_SECRET = os.getenv('SIAM_SHARED_SECRET')

# JWT config
JWT_ALGORITHM = 'HS256'
JWT_AT_SECRET = os.getenv('JWT_SECRET_KEY_ACCESS_TOKEN')
JWT_RT_SECRET = os.getenv('JWT_SECRET_KEY_REFRESH_TOKEN')
JWT_AT_LIFETIME = int(os.getenv('JWT_EXPIRATION_DELTA', 300))
JWT_RT_LIFETIME = int(os.getenv('JWT_REFRESH_EXPIRATION_DELTA', 3600 * 24 * 7))

# Postgres config
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_USER = os.getenv('PG_USER')
PG_PASS = os.getenv('PG_PASS')
PG_DB = os.getenv('PG_DB')
