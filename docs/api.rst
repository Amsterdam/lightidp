.. _api:

.. toctree::
   :maxdepth: 1

API Docs
========

.. module:: auth

Flask blueprints (views)
------------------------

.. autofunction:: auth.blueprints.siam.blueprint

HTTP utilities
--------------

.. autofunction:: auth.httputils.assert_acceptable
.. autofunction:: auth.httputils.assert_mimetypes
.. autofunction:: auth.httputils.assert_req_args
.. autofunction:: auth.httputils.assert_gateway
.. autofunction:: auth.httputils.response_mimetype

SIAM client
-----------

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

