:tocdepth: 3

Manual
======

Authentication for web applications
-----------------------------------

Make authenticated requests through a 3rd party website.

.. NOTE::

   Only Amsterdam's identity provider (TMA) is currently supported. If you (or
   your users) do not a TMA account then you cannot make authenticated requests.
   Please contact `Datapunt support <mailto:datapunt.ois@amsterdam.nl>`_ if you
   want to know more.

1. Redirect users to TMA login screen
#####################################

GET ``/auth/siam/authenticate``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Description
+++++++++++

Gets SIAM authentication redirect.
Required query param callback specifies the URL the user should be redirected to by the IdP after succesful authentication.
Optional query param active determines whether we want the user to see a login screen if she is not authenticated.

Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        callback | query | Yes | string |  |  | IdP will redirect to this URL after authentication
        active | query | No | boolean |  |  | If present, ask IdP to show user a login screen if she is not authenticated.

Responses
+++++++++

- **307**: Redirect to generated authentication url
- **400**: Query param callback is not present
- **502**: Problem communicating with the SIAM server
- **504**: Communication with SIAM server timed out

2. TMA redirects back to your site
##################################

If the user successfully authenticates, then TMA will redirect the user back to
the ``callback`` url provided in the previous step, with three parameters:
``aselect_credentials``, ``rid`` and ``a-select-server``. You can exchange these
for a **refresh token**.

.. NOTE::

   Refresh tokens are long lived, and they can be used to create access tokens.
   Make sure you keep them safe. If you expect abuse, plase contact `Datapunt
   support <mailto:datapunt.ois@amsterdam.nl>`_

GET ``/auth/siam/token``
~~~~~~~~~~~~~~~~~~~~~~~~

Description
+++++++++++

Gets JSON Web Token for the current user.

Parameters
++++++++++

.. csv-table::
    :delim: |
    :header: "Name", "Located in", "Required", "Type", "Format", "Properties", "Description"
    :widths: 20, 15, 10, 10, 10, 20, 30

        aselect_credentials | query | Yes | string |  |  | The credentials as provided by SIAM
        rid | query | Yes | string |  |  | The request ID associated with this authentication attempt, provided by SIAM
        a-select-server | query | Yes | string |  |  | The a-select-server used for this authentication attempt, as provided by SIAM

Request headers
+++++++++++++++

- ``Accept: text/plain``

Responses
+++++++++

- **200**: Success
   - ``Content-type: text/plain``

- **400**: Required query param is not present
- **406**: Requested content-type (Accept header) cannot be produced (only ``text/plain`` is supported)
- **502**: Problem communicating with the SIAM server
- **504**: Communication with SIAM server timed out


3. Use the Refresh token to request an access token
###################################################

GET ``/auth/accesstoken``
~~~~~~~~~~~~~~~~~~~~~~~~~

Description
+++++++++++

Gets an accesstoken.

Request headers
+++++++++++++++

- ``Accept: text/plain``
- ``Authorization: Bearer [JWT]`` where ``JWT`` is a valid refresh token

Responses
+++++++++

- **200**: Success
   - ``Content-type: text/plain``

- **401**: Refreshtoken is missing or invalid
   - ``WWW-Authenticate: Bearer realm="datapunt"[, error="invalid_token", error_description="[DESC]"]`` where ``DESC`` is a human readable description

- **406**: Requested content-type (Accept header) cannot be produced (only ``text/plain`` is supported)

Making authenticated requests
-----------------------------

You can currently only authenticate using an accesstoken. Requests that require
an authenticated user will respond with a ``401 Authentication Required`` and
contain a ``WWW-Authenticate`` header.

.. code-block:: shell

    $ curl -H "Authorization: Bearer [ACCESS_TOKEN]" https://api.data.amsterdam.nl

Authentication errors
#####################

If an ``Authorization`` header is malformed or the accesstoken is invalid, the
``WWW-Authenticate`` header may include an ``error`` property and an
``error_description`` property, that may help you resolve the problem.
