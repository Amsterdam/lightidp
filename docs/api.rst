.. _api:

API Docs
========

.. module:: auth

HTTP utilities
--------------

.. autofunction:: auth.httputils.assert_acceptable
.. autofunction:: auth.httputils.assert_mimetypes
.. autofunction:: auth.httputils.assert_req_args
.. autofunction:: auth.httputils.response_mimetype

SIAM client
-----------

.. autoclass:: auth.siam.Client

.. autoexception:: auth.siam.Timeout
.. autoexception:: auth.siam.RequestException
.. autoexception:: auth.siam.ResponseException

