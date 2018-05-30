import os
import pytest
import auth.config
import dpuser

@pytest.fixture(autouse=True)
def no_database(monkeypatch):
    def Users(*args, **kwargs):
        return object()
    monkeypatch.setattr(dpuser, 'Users', Users)


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
