"""
    auth.token
    ~~~~~~~~~~~

    This module maintains the base structure for our JWTs and wraps all jwt
    configuration.

    Usage:

    ::

        from auth import token

        # Create a builder that contains the config
        accesstokens = token.AccessTokenBuilder(**config)
        # Create accesstoken data
        data = accesstokens.create(authz.levels.LEVEL_EMPLOYEE)
        # data is a dict! add some property
        data['someprop'] = 'something the IdP gave us'
        # now create a JWT
        accesstoken_jwt = data.encode()

        # we can also decode the jwt the same way
        decoded = accesstokens.decode(accesstoken_jwt)
        # this is a dict again
        assert decoded['someprop'] == 'something the IdP gave us'
        # we could change something
        decoded['someprop'] = 'something else altogether'
        # and create a JWT again
        decoded.encode()
"""
import collections
import functools
import time
import types
import jwt

from . import exceptions

# Use a namedtuple to emphasize the immutability of the config
_TokenBuilder = collections.namedtuple(
    '_TokenBuilder', ('secret', 'lifetime', 'algorithm')
)


class _BaseBuilder(_TokenBuilder):
    """ Builder allows you to encode and decode JSON Web Tokens (JWTs).

    NOTE: needs Python >= 3.4

    The key-value datastucture in the tokens is a dictionary that provides an
    additional method ``encode()``. Under water, ``encode()`` will call
    :func:`jwt.encode` with all but the ``data`` argument passed in. It does
    so by using the convenient fact that :func:`jwt.encode` takes a `dict` as
    its first argument; it can use :func:`functools.partialmethod` to create a
    partial and then bind that method to a dynamically created ``dict``
    subclass. The result is a ``dict`` with an ``encode()`` method that, when
    called, will return a JWT based on ``self``.
    """

    @property
    def _tokendata(self):
        """ TokenData type as a property. This is a dynamically created class
        that wraps this namedtuple's instance data and the jwt.encode function
        """
        try:
            return self._td
        except AttributeError:
            pass
        # wrap the secret and algortihm in a partial
        encode = functools.partialmethod(
            jwt.encode, self.secret, algorithm=self.algorithm
        )
        # create the namespace structure
        td_ns = {'encode': encode}
        # create a class TokenData that bases dict & includes the encode method
        self._td = types.new_class(
            'TokenData', bases=(dict,), exec_body=lambda ns: ns.update(td_ns)
        )
        return self._td

    def decode(self, encoded_token):
        """ Decode a token into a dict. The resulting dict will be an
        instance of the dynamically created dict subclass that contains the
        ``encode()`` method.

        Usage:

        ::

            data = accesstokens.decode(accesstoken_jwt)
            assert data['myproperty'] == 42
            tokendata['myproperty'] += 1
            new_jwt = accesstokens.encode()

        """
        try:
            data = jwt.decode(encoded_token, key=self.secret)
        except jwt.exceptions.DecodeError as e:
            raise exceptions.JWTDecodeException() from e
        except jwt.exceptions.ExpiredSignatureError as e:
            raise exceptions.JWTExpiredSignatureException from e
        except jwt.exceptions.InvalidTokenError as e:
            raise exceptions.JWTException from e
        return self._tokendata(data)

    def create(self, *args, **kwargs):
        """ Create a new token. Subclasses should implement this method.
        """
        raise NotImplementedError()


class AccessTokenBuilder(_BaseBuilder):
    """ Token builder that creates access tokens.
    """

    def create(self, authz_level):
        """ Create a new accesstoken as a dict.

        Usage:

        ::

            accesstoken = tokenbuilder.create(auth.levels.LEVEL_DEFAULT)
            accesstoken['myproperty'] = 42
            jwt = accesstoken.encode()

        """
        now = int(time.time())
        data = {
            'iat': now,
            'exp': now + self.lifetime,
            'authz': authz_level
        }
        return self._tokendata(data)


class RefreshTokenBuilder(_BaseBuilder):
    """ Token builder that creates refresh tokens.
    """

    def create(self, sub=None):
        """ Create a new refreshtoken as a dict.

        :param sub: The subject claim (may be None)

        Usage:

        ::

            refreshtoken = tokenbuilder.create('I@Amsterdam.nl')
            jwt = refreshtoken.encode()

        """
        now = int(time.time())
        data = {
            'iat': now,
            'exp': now + self.lifetime,
            'sub': sub.lower(),
            'username': sub.lower(),  # temporary, will be removed
        }
        return self._tokendata(data)
