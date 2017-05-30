.. _running:

Starting, tests and coverage
============================

Auth is a `Flask <https://flask.readthedocs.io>`_ application, and so a `WSGI
<https://www.python.org/dev/peps/pep-3333/>`_ application.

If you want to run the service you should make sure you have :ref:`configured
<configuration>` it. However, you don't need to configure anything to run the
tests.

Starting the service
--------------------

Starting a database
^^^^^^^^^^^^^^^^^^^

Auth needs access to a Postgres instance for querying authorization information.

You can optionally start an instance using the provided ``docker-compose.yml``:

::

   # start the database
   $ docker-compose up -d database

   # give a user some permissions (optional)
   $ authz user some_user assign EMPLOYEE

Installing dependencies
^^^^^^^^^^^^^^^^^^^^^^^

Install the dev dependencies in your virtual environment:

::

    $ pip install -e .[dev]

Note: the ``[dev]`` refers to extra requirements for development and is
specified in ``setup.py``. You don't need to install them as the ``make test``
and ``make coverage`` targets work fine without having them in the virtualenv.
The only reason you might want to install them is so for example ``pytest`` and
``responses`` can be resolved in you IDE.

Starting the service
^^^^^^^^^^^^^^^^^^^^

Now you can run the service in development mode:

::

    $ make run-dev

Running tests / coverage
------------------------

For tests you don't need a virtual environment, you can just run:

::

   $ make test
   # or...
   $ make coverage

