import pytest
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
        def get(username):
            return authzmap.get(username, authorization_levels.LEVEL_DEFAULT)
    monkeypatch.setattr(authorization, 'authz_mapper', authz_mapper)


@pytest.fixture(scope='session')
def config():
    return {
        'SIAM_BASE_URL': 'http://www.google.com',
        'SIAM_APP_ID': 'fake',
        'SIAM_ASELECT_SERVER': 'fake.siam',
        'SIAM_SHARED_SECRET': 'fake.secret',
        'JWT_SECRET': 'jwt secret',
        'JWT_LIFETIME': 300
    }


@pytest.fixture(scope='session')
def client(config):
    client = auth.siam.Client(
        base_url=config['SIAM_BASE_URL'],
        app_id=config['SIAM_APP_ID'],
        aselect_server=config['SIAM_ASELECT_SERVER'],
        shared_secret=config['SIAM_SHARED_SECRET']
    )
    return client
