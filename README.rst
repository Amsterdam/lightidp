Datapunt Authentication & Authorization service
===============================================

Features:

- Support for authentication with SIAM in :module:`auth.blueprints.siam`
- Support for Pipenv in the Makefile
- Pep8 compliant (without E501, lines <= 80)
- Fair test coverage (missing the blueprints)
- Support for setuptools, so it can run without needing test / dev dependencies (which it does; see ``Dockerfile`` and ``Jenkinsfile``)

Running the service
-------------------

Required settings
^^^^^^^^^^^^^^^^^

Refer to the documentation in :module:`auth.settings`.

The docs provide info on:

- Using the service, with a specification of the REST API
- Running the service, explaining how to configure it and run it in different modes
- The internal API

Create nice looking docs with:

::

   $ git clone https://github.com/DatapuntAmsterdam/auth.git
   $ cd auth
   $ make init docs
   $ open docs/_build/html/index.html

