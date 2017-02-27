Manual
======

Authentication
--------------

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

Web application flow
--------------------

Make authenticated requests through a 3rd party website.

.. NOTE::

   Only Amsterdam's identity provider (TMA) is currently supported. If you (or
   your users) do not a TMA account then you cannot make authenticated requests.
   Please contact `Datapunt support <mailto:datapunt.ois@amsterdam.nl>`_ if you
   want to know more.

1. Request users to TMA login screen
####################################

For details see the :ref:`REST API documentation <rest-siam-authenticate>`

.. code-block:: shell

    $ curl -D - 'https://api.data.amsterdam.nl/auth/siam/authenticate?active&callback=CALLBACK' 2> /dev/null | grep Location
    Location: https://tma.amsterdam.nl/aselectserver/server?request=login1&a-select-server=tma.amsterdam.nl&rid=R97C46FD4FA0C09341E5A45FD8692D6BB9FEA2717

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

For details see the :ref:`REST API documentation <rest-siam-token>`

.. code-block:: shell

    $ curl -H 'Accept: text/plain' 'https://api.data.amsterdam.nl/auth/siam/token?aselect_credentials=ASELECT_CREDENTIALS&rid=RID&a-select-server=A-SELECT-SERVER'
    eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.dCI6MTQ4NzA3NjOm51bGwsImlhg3NjgxMjE3fQQxNywiZXhwIjoxNDeyJzdWIi.VjLY8oQGs2ZM3_UWjpORLtHZW34wa71sgvWACYRwGfQ

3. Use the Refresh token to request an access token
###################################################

.. code-block:: shell

    $ token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOm51bGwsImlhdCI6MTQ4NzA3NjQxNywiZXhwIjoxNDg3NjgxMjE3fQ.VjLY8oQGs2ZM3_UW34wa71sgvWAWjpORLtHZCYRwGfQ'
    $ curl -H 'Accept: text/plain' -H "Authorization: Bearer $token" https://api.data.amsterdam.nl/auth/accesstoken
    eyJIUzI1NiJ9J0eXAiOiJKV1QiLCjdfgti.NjgxMjGwsImlhdCI6MTQ4NzA3NjQxNywiZXhwIjoxNE3fQeyJzdWIiOm51bDg3.QGs2ZM3_VjLY8oWjpORLtHZCYRwGfQUW34wa71sgvWA
