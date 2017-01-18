import pytest
import auth.siam.client

SIAM_BASE_URL = 'http://fake.siam'
SIAM_APP_ID = 'fake'
SIAM_ASELECT_SERVER = 'fake.siam'
SIAM_SHARED_SECRET = 'fake.secret'


@pytest.fixture(scope="module")
def siamclient():
    client = siam.client.Client(
        base_url=SIAM_BASE_URL,
        app_id=SIAM_APP_ID,
        aselect_server=SIAM_ASELECT_SERVER,
        shared_secret=SIAM_SHARED_SECRET
    )
    return client
