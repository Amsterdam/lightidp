:tocdepth: 2

.. The api docs page main navigation isn't nice --PvB

.. _api:

.. toctree::
   :maxdepth: 0

API Docs
========

Auditlog
--------

.. automodule:: auth.audit
   :members:

Blueprints (views)
------------------

Flask `blueprints <http://flask.pocoo.org/docs/0.12/blueprints/>`_ for SIAM
authentication and JWT tokens.

.. autofunction:: auth.blueprints.siamblueprint
.. autofunction:: auth.blueprints.jwtblueprint

Configuration
-------------

.. automodule:: auth.config
   :members:

Decorators
----------

.. automodule:: auth.decorators
   :members:

Exceptions
----------

.. automodule:: auth.exceptions
   :members:

JSON Web Tokens
---------------

.. automodule:: auth.token
   :members:

SIAM (IdP) client
-----------------

The SIAM client handles all communication with the IdP.

.. autoclass:: auth.siam.Client
   :members: