"""
    auth.token
    ~~~~~~~~~~

    This module maintains the base structure for our JWTs and wraps all jwt
    configuration.

    Usage:

    ::

        from auth import token

        # Create a builder that contains the config
        tokenbuilder = token.builder(**jwtconfig)
        # Create accesstoken data
        data = tokenbuilder.accesstoken_for('some subject')
        # data is a dict! add some property
        data['someprop'] = 'something the IdP gave us'
        # now create a JWT
        jwt = data.encode()

        # we can also decode the jwt the same way
        decoded = tokenbuilder.decode_accesstoken(jwt)
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

from auth import exceptions

# Use a namedtuple to emphasize the immutability of the config
_TokenBuilder = collections.namedtuple('_TokenBuilder', (
    'rt_secret', 'at_secret', 'rt_lifetime', 'at_lifetime', 'algorithm'
))


class Builder(_TokenBuilder):
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
            jwt.encode, self.at_secret, algorithm=self.algorithm
        )
        # create the namespace structure
        td_ns = {'encode': encode}
        # create a class TokenData that bases dict & includes the encode method
        self._td = types.new_class(
            'TokenData', bases=(dict,), exec_body=lambda ns: ns.update(td_ns)
        )
        return self._td

    def accesstoken_for(self, sub):
        """ Create a new accesstoken as a dict.

        Usage:

        ::

            accesstoken = tokenbuilder.accesstoken_for('userID')
            accesstoken['myproperty'] = 42
            jwt = accesstoken.encode()

        """
        now = int(time.time())
        data = {
            'iat': now,
            'exp': now + self.at_lifetime,
            'sub': sub
        }
        return self._tokendata(data)

    def decode_accesstoken(self, encoded_token):
        """ Decode an accesstoken into a dict. The resulting dict will be an
        instance of the dynamically created dict subclass that contains the
        ``encode()`` method.

        Usage:

        ::

            tokendata = tokenbuilder.decode_accesstoken(accesstoken)
            assert tokendata['myproperty'] == 42
            tokendata['myproperty'] += 1
            jwt = tokendata.encode()

        """
        try:
            data = jwt.decode(encoded_token, key=self.at_secret)
        except jwt.exceptions.DecodeError as e:
            raise exceptions.JWTDecodeException() from e
        except jwt.exceptions.ExpiredSignatureError as e:
            raise exceptions.JWTExpiredSignatureException from e
        except jwt.exceptions.InvalidTokenError as e:
            raise exceptions.JWTException from e
        return self._tokendata(data)
