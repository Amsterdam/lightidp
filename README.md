# authenticatie_service

## Running the service

You can run the service in a virtual environment on your machine and you can run it in a docker. To do so you need to provide some environment variables.

### Environment variables

You _MUST_ provide:

    - `SECRET_KEY`: The key used to seed JWTs
    - `SIAM_URL`: The URL endpoint for SIAM
    - `SIAM_A_SELECT_SERVER`: The a-select server (whatever that is)
    - `SIAM_APP_ID`: Your application ID
    - `SIAM_SHARED_SECRET`: Your shared secret

    You _MAY_ also specify:

    - `DEBUG`: Run Flask in debug mode (default False)
    - `PREFERRED_URL_SCHEME`: http or https (default https)

The easiest way of doing this is by putting your settings in a file, for example `settings_test.env` (which is already in .gitignore).

To export all variables in the file:

```
$ set -a
$ source settings_test.env
$ set +a
```

### Running in Docker

```
$ docker-compose up -d
```

### Running locally

(You should use a virtual environment)

Install dependencies:

```
$ pip install -r -requirements.txt
```

Start it without uWSGI:

```
$ FLASK_APP=authn_authz/server.py python -m flask run -p 8102 --reload
```

... or start it with uWSGI:

```
$ uwsgi --ini ../uwsgi.ini
```
