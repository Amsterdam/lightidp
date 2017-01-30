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

Initialize the project with Pipenv:

::

   $ make init

Make sure all :doc:`required settings </settings>` are available.

Now you can run the service either as a Flask application:

::

   $ make run-dev


Running tests
-------------

Run tests like this:

::

   $ make coverage

... or run tests in Docker:

::

   $ AUTH_SKIP_CONF_CHECK=1 docker-compose run auth make coverage
