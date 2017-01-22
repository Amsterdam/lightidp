import pytest
import auth.siam.client


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
def siamclient(config):
    client = auth.siam.client.Client(
        base_url=config['SIAM_BASE_URL'],
        app_id=config['SIAM_APP_ID'],
        aselect_server=config['SIAM_ASELECT_SERVER'],
        shared_secret=config['SIAM_SHARED_SECRET']
    )
    return client
