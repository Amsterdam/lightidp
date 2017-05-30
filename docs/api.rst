:tocdepth: 4

.. _api:

API Docs
========

Auditlog
--------

.. automodule:: auth.audit
   :members:

Blueprints (views)
------------------

:ref:`Flask blueprints <flask:blueprints>` for SIAM authentication and JWT
tokens.

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
   :private-members:
