.. _api:

.. toctree::
   :maxdepth: 0

API Docs
========

.. module:: auth

Blueprints (resources / views)
------------------------------

Flask `blueprints <http://flask.pocoo.org/docs/0.12/blueprints/>`_ for SIAM
authentication and JWT tokens.

.. autofunction:: auth.blueprints.siamblueprint
.. autofunction:: auth.blueprints.jwtblueprint

HTTP utilities
--------------

.. automodule:: auth.httputils
   :members:

SIAM (IdP) client
-----------------

The SIAM client handles all communication with the IdP.

.. autoclass:: auth.siam.Client
   :members:

JSON Web Tokens
---------------

.. automodule:: auth.token
   :members:

Exceptions
----------

.. automodule:: auth.exceptions
   :members:
