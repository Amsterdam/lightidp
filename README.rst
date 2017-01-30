Datapunt Authentication & Authorization service
===============================================

.. image:: https://img.shields.io/badge/python-3.4%2C%203.5%2C%203.6-blue.svg
    :target: https://www.python.org/

.. image:: https://img.shields.io/badge/license-MPLv2.0-blue.svg
    :target: https://www.mozilla.org/en-US/MPL/2.0/

---------------------

Features:

- Support for authentication with SIAM in `auth.blueprints.siam <auth/blueprints/siam.py>`_.
- Support for access tokens
- Support for Pipenv in the Makefile
- Pep8 compliant (without E501, lines <= 80)
- Fair test coverage (missing the blueprints)
- Support for setuptools, so it can run without needing test / dev dependencies (which it does; see ``Dockerfile`` and ``Jenkinsfile``)

Future work:

- CORS beyond simple requests?
- A better README?
- Support IP-based authentication
- Support access and refresh tokens
- Support claims / permission based authorization with a Postgres backend

Documentation
-------------

Pending a better README, an online version of the docs can be found `at readthedocs <http://datapunt-auth.readthedocs.io/en/latest/>`_.
Note that we haven't configured github to trigger documentation builds on readthedocs.
We may not use readthedocs (or Sphinx, for that matter) at all in the future. 

View the most recent docs locally with:

::

   $ make init docs
   $ open docs/_build/html/index.html
