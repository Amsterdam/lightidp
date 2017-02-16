import pytest
import auth.siam
import authorization
import authorization_levels

CONFIG = {
    'SIAM_URL': 'http://www.google.com',
    'SIAM_APP_ID': 'fake',
    'SIAM_A_SELECT_SERVER': 'fake.siam',
    'SIAM_SHARED_SECRET': 'fake.secret',
    'JWT_REFRESH_SECRET': 'refreshsecret',
    'JWT_ACCESS_SECRET': 'refreshsecret',
    'PG_HOST': 'localhost',
    'PG_PORT': 5432,
    'PG_USER': 'user',
    'PG_PASS': 'password',
    'PG_DB': 'database',
}


@pytest.fixture(autouse=True)
def settings(monkeypatch):
    for key in CONFIG:
        monkeypatch.setenv(key, CONFIG[key])


@pytest.fixture(autouse=True)
def no_database(monkeypatch):
    authzmap = {
        'employee': authorization_levels.LEVEL_EMPLOYEE,
        'employeeplus': authorization_levels.LEVEL_EMPLOYEE_PLUS,
    }

    def authz_mapper(*args, **kwargs):
        def get(username):
            return authzmap.get(username, authorization_levels.LEVEL_DEFAULT)
    monkeypatch.setattr(authorization, 'authz_mapper', authz_mapper)


@pytest.fixture(scope='session')
def config():
    return CONFIG


@pytest.fixture(scope='session')
def client(config):
    client = auth.siam.Client(
        base_url=config['SIAM_URL'],
        app_id=config['SIAM_APP_ID'],
        aselect_server=config['SIAM_A_SELECT_SERVER'],
        shared_secret=config['SIAM_SHARED_SECRET']
    )
    return client
