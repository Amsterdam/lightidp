"""
    auth.authz
    ~~~~~~~~~~
"""


class UserAuthzMap():
    """ Class that maps users to their authorizations.

    Note that this map may look a little like a `dict` or a
    :class:`collections.abc.Mapping` because it allows bracket notation, but
    that is where the likeliness stops. This class does not support any
    other collection or mapping methods. Neither will it ever raise a
    :class:`KeyError` - if no explicit authorization level is found it will
    return the default level.

    Authorizations are backed by Postgresql. This class wraps a
    :class:`psycopg2.pool.SimpleConnectionPool`.

    Typical usage:

    ::

        ua_map = UserAuthzMap(connpool)

        # be friendly
        authz = ua_map['username']

        # NONE of the below will work, by design
        'username' in ua_map

        authz.get('username', 'not authorized')

        for user in ua_map:
            print(ua_map(user))

        del ua_map['username']
    """

    def __init__(self, connpool):
        self.connpool = connpool

    def __getitem__(self, key):
        """ Implements :meth:`collections.abc.Mapping.__getitem__`
        """
        return 'unauthorized'
