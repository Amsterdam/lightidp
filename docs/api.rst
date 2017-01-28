.. _api:

API Docs
========

.. module:: auth

The auth service exports its HTTP endpoints through Flask blueprints.

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

