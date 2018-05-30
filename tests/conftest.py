import os
import pytest
import auth.config


@pytest.fixture(scope='session')
def config():
    return auth.config.load(configpath=os.getenv('CONFIG'))


@pytest.fixture()
def app():
    """ Fixture for tests that need to import auth.server.app. Patches siam to
    not check whether the server is reachable.
    """
    import auth.server
    auth.server.app.config['TESTING'] = True
    return auth.server.app
