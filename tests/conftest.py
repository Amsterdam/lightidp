import os
import pytest
import auth.config
import auth.siam
import authorization
import authorization_levels


@pytest.fixture(autouse=True)
def no_database(monkeypatch):
    authzmap = {
        'employee': authorization_levels.LEVEL_EMPLOYEE,
        'employeeplus': authorization_levels.LEVEL_EMPLOYEE_PLUS,
    }

    def authz_mapper(*args, **kwargs):
        def get(sub):
            return authzmap.get(sub, authorization_levels.LEVEL_DEFAULT)
        return get
    monkeypatch.setattr(authorization, 'authz_mapper', authz_mapper)


@pytest.fixture(scope='session')
def config():
    return auth.config.load(configpath=os.getenv('CONFIG'))


@pytest.fixture()
def app(monkeypatch):
    """ Fixture for tests that need to import auth.server.app. Patches siam to
    not check whether the server is reachable.
    """

    def get_authn_redirect(*args, **kwargs):
        return 'http://redirect.url'

    def get_user_attributes(*args, **kwargs):
        return {
            'result_code': auth.siam.Client.RESULT_OK,
            'uid': 'testuser'
        }

    monkeypatch.setattr(auth.siam.Client, 'get_authn_redirect', get_authn_redirect)
    monkeypatch.setattr(auth.siam.Client, 'get_user_attributes', get_user_attributes)

    from auth import server
    server.app.config['TESTING'] = True
    return server.app


@pytest.fixture(scope='session')
def client(config):
    client = auth.siam.Client(
        base_url=config['siam']['base_url'],
        app_id=config['siam']['app_id'],
        aselect_server=config['siam']['aselect_server'],
        shared_secret=config['siam']['shared_secret'],
        allowed_callback_hosts=config['siam']['allowed_callback_hosts']
    )
    return client
