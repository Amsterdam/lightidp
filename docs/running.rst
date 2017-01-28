Starting the service
====================

Auth is a `Flask <https://flask.readthedocs.io>`_ application, and so a `WSGI <https://www.python.org/dev/peps/pep-3333/>`_ application. You can run it in your current shell or in a Docker container.

Running it in a Docker container
--------------------------------

The service comes with a ``Dockerfile`` and a ``docker-compose.yml`` file. To run the service in Docker you must have at least :doc:`all required settings </settings>` available **as environment variables**

If you have all settings in your environment and a running Docker daemon, then you should be able to start it with docker-compose:

::

   # start the service
   $ docker-compose up -d

   # see what it's up to
   $ docker-compose logs -f
   # ^C to stop watching the logs

   # kill the service
   $ docker-compose down

Running it in your shell
------------------------

This mode is useful during development. You should always run *in a virtualenv*.

First make sure you have all requirements installed:

::

   # this will install all requirements in your virtualenv
   $ make init

Make sure all :doc:`required settings </settings>` are available.

Now you can run the service either as a Flask application:

::

   $ make run

... or you can run it using uwsgi:

::

   $ make run-uwsgi

Running tests
-------------

Auth comes with a testsuite. If you set ``AUTH_SKIP_CONF_CHECK`` in your shell you don't need to provide any of the settings to run the tests.

You can run tests in your shell (assuming you have all dependencies installed in your virtualenv):

::

   $ AUTH_SKIP_CONF_CHECK=1 make test

... or you can run it in Docker:

::

   $ AUTH_SKIP_CONF_CHECK=1 docker-compose run auth make -C /app test
