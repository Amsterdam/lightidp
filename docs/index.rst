.. Datapunt Authentication & Authorization documentation master file, created by
   sphinx-quickstart on Fri Jan 27 20:42:04 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Datapunt: Authentication & Authorization service
================================================

Congratulations, you found the documentation for the authentication and
authorization (AA) service at the heart of the city of Amsterdam's `open data
services <https://api.datapunt.amsterdam.nl/api/>`_.

The AA service authenticates users through external identity providers (IdP's),
manages user permissions and creates access and refresh tokens in the form of
`JSON Web Tokens <https://tools.ietf.org/html/rfc7519>`_ (JWTs).

Using the service
-----------------

.. toctree::
   :maxdepth: 2

   usage

Running the service
-------------------

.. toctree::
  :maxdepth: 2

  settings
  running

API Documentation
-----------------

If you are looking for information on a specific function, class, or method,
this part of the documentation is for you.

.. toctree::
  :maxdepth: 2

  api
