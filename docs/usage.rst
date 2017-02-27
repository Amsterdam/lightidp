REST API
========

.. toctree::
   :maxdepth: 3


.. _rest-siam-authenticate:

GET ``/auth/siam/authenticate``
-------------------------------

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


.. _rest-siam-token:

GET ``/auth/siam/token``
------------------------

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


GET ``/auth/refreshtoken``
--------------------------

Description
+++++++++++

Gets an anonymous refreshtoken.

Request headers
+++++++++++++++

- ``Accept: text/plain``

Responses
+++++++++

- **200**: Success
   - ``Content-type: text/plain``

- **406**: Requested content-type (Accept header) cannot be produced (only ``text/plain`` is supported)


.. _rest-accesstoken:

GET ``/auth/accesstoken``
-------------------------

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
