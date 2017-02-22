.. _settings:

Configuration
~~~~~~~~~~~~~

Configuration is done using a ``yaml`` file that supports interpolation of
environment variables (with default values) and validation with JSON schema. You
can customize the provided ``config.yml`` file or provide environment variables.

See :ref:`the API docs on configuration <auth-config>` for details on
programmatic usage.

Interpolation
-------------

Interpolation provides string substitution as described in
`PEP 292 <https://www.python.org/dev/peps/pep-0292/>`_, using ``$`` instead of
``%``. In short:

- ``$$`` is an escape and replaced with a single ``$``
- ``$identifier`` names a substitution placeholder matching an environment
   variable named ``identifier``
- ``${identifier}`` is equivalent to ``$identifier``

Note that substituted values will be ``str`` or, if containing only digits,
``int``. Other types (floats, booleans) are not converted.

Default values
--------------

In addition to substitution you can provide default values for missing
environment variables using either ``:-`` (e.g. ``${VAR:-default}``) or ``-``
(e.g. ``${VAR-default}``).

Validation with JSON Schema
---------------------------

The config module validates the configuration against the `JSON Schema
<http://json-schema.org/>`_ in ``config_schema_v[VERSION].json``.
