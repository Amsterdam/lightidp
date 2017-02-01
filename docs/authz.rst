Authorization
=============

All users of Datapunt have a distinct authorization level assigned. Currently the authorization levels make use of the nested set model; each ‘higher’ level includes all ‘lower’ ones.

Levels
------

1. Public: can view all public data
2. Restricted: can view all public data and some (but not all) restricted data
3. Restricted+: can view everything

Assignment
----------

Levels are assigned based on two user attributes that are set during authentication:

* IP address
* Username

The below flow describes how authorization levels are assigned:

.. image:: _static/authzflow.png

Internal usage
--------------

Every user will have a **refresh token** that is assigned during authentication. Note that even if a user doesn't login, an implicit authentication flow is completed that will result in a refresh token. Refresh tokens always contain the IP address and username properties for the current user. Refresh tokens are long lived and contain the user attributes.

To access services the user needs an **access token**. Access tokens are given to any user with a valid refresh token. Access tokens are short lived, so that whenever a user requests a new token we can check changes in the user's authorization levels. Access tokens contain the user's authorization level.

