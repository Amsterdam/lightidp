# Authn & authz service

## Running the service

You can run the service in a virtual environment on your machine and you can run it in a docker. To do so you need to provide some environment variables.

### Environment variables

You _MUST_ override:

- __SIAM_URL__: The URL endpoint for SIAM
- __SIAM_A_SELECT_SERVER__: The a-select server (whatever that is)
- __SIAM_APP_ID__: Your application ID
- __SIAM_SHARED_SECRET__: Your shared secret
- __JWT_SHARED_SECRET_KEY__: The seed for access tokens

You _MAY_ override:

- __DEBUG__: Run Flask in debug mode (default False)
- __JWT_ALGORITHM__: The algorithm to use for JWT encryption (default HS256)
- __JWT_SECRET_KEY__: The seed for refresh tokens (default JWT_SHARED_SECRET_KEY)
- __JWT_EXPIRATION_DELTA__: Expiration for access tokens (default 300 seconds)
- __JWT_REFRESH_EXPIRATION_DELTA__: Expiration for access tokens (default 1 week)

See the sections below on how to set the variables in different scenario's.

### Running locally

During development, the easiest way to provide settings is by creating a `settings.py` file and pointing to it in a `AUTHN_SIAM_SETTINGS` environment variable.

For example, `settings.py`:

```
DEBUG = True
SIAM_URL = "https://some_url"
SIAM_A_SELECT_SERVER = "some_server"
SIAM_APP_ID = "some_app_id"
SIAM_SHARED_SECRET = "siam_key"
JWT_SHARED_SECRET_KEY = "jwt_key"
```

and then export `AUTHN_SIAM_SETTINGS`:

```
$ export AUTHN_SIAM_SETTINGS=`pwd`/settings.py
```

Now you're ready to install dependencies:

```
$ make init
```

And run the app:

```
$ make run
 ...
 [lots of output]
 ...
 * Serving Flask app "auth.server"
 * Running on http://127.0.0.1:8109/ (Press CTRL+C to quit)
 * Restarting with stat

```

You can also run the service using uwsgi, if you like:

```
$ uwsgi --ini uwsgi.ini
```


### Running in Docker

The `docker-compose.yml` will read all settings from your environment. You can store your settings in, for example, `settings.env`:

```
DEBUG=True
SIAM_URL=https://some_url
SIAM_A_SELECT_SERVER=some_server
SIAM_APP_ID=some_app_id
SIAM_SHARED_SECRET=siam_key
JWT_SHARED_SECRET_KEY=jwt_key
```

And then export the settings like this:

```
$ set -a && . settings_test.env && set +a
```

Now you can run docker-compose to start the container:

```
$ docker-compose up -d
```
