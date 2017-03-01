Datapunt Authentication & Authorization service
===============================================

.. image:: https://img.shields.io/badge/python-3.4%2C%203.5%2C%203.6-blue.svg
    :target: https://www.python.org/

.. image:: https://img.shields.io/badge/license-MPLv2.0-blue.svg
    :target: https://www.mozilla.org/en-US/MPL/2.0/

---------------------

Have a look at the `documentation on ReadTheDocs <https://datapunt-auth.readthedocs.io/>`_.

Future work:

- Move to an async framework; apart from encoding/decoding tokens (HMAC +
  SHA256) this service does nothing significant, it may as well do I/O async so
  it can handle more incoming connections. A possible stack could be (asyncio
  uvloop aiohttp) | tornado + asyncpg + requests-futures.

Contributing
------------

1. Install the dev dependencies in your virtual environment
###########################################################

::

    $ pip install -e .[dev]

Note: the ``[dev]`` refers to extra requirements for development and is
specified in ``setup.py``. You don't need to install them as the ``make test``
and ``make coverage`` targets work fine without having them in the virtualenv.
The only reason you might want to install them is so for example ``pytest`` and
``responses`` can be resolved in you IDE.

2. Create a configuration or environment file
#############################################

In ``config.yml`` you can see an example configuration. You can either:

- make a copy of ``config.yml``, adjust it to your needs and point to it using
  export CONFIG=`pwd`/my_config.yml
- or export values for the environment variables referenced in ``config.yml``.

3. Make sure you have a database running and that the tables exist
##################################################################

If you have docker installed then you can start a Postgres instance with:

::

 	$ docker-compose up -d database

You can use the authorization CLI to set up a user. Note that this will also
silently create the needed tables, if they don't exist.

::

 	$ authz user [username] assign [DEFAULT | EMPLOYEE | EMPLOYEE_PLUS]

Now you can develop, run and test code!

