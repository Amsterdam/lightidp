import os
import pytest
import auth.config
import authorization


@pytest.fixture(autouse=True)
def no_database(monkeypatch):
    authzmap = {
        'employee': authorization.levels.LEVEL_EMPLOYEE,
        'employeeplus': authorization.levels.LEVEL_EMPLOYEE_PLUS,
    }

    def AuthzMap(*args, **kwargs):
        return authzmap
    monkeypatch.setattr(authorization, 'AuthzMap', AuthzMap)


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
