"""
    auth.tests.test_audit
    ~~~~~~~~~~~~~~~~~~~~~
"""
import pytest
from auth import audit


def test__mac_from_jwt_indexerror():
    with pytest.raises(IndexError):
        audit._mac_from_jwt('Ionlyhave.twoparts')


def test__mac_from_jwt_utf8():
    audit._mac_from_jwt('iam.utf.8')


def test__mac_from_jwt_bin():
    audit._mac_from_jwt(b'iam.bin.ary')


def test_log_token():
    audit.log_token('a.b.mac', sub='user')
    # Disable the assert, because the required library pytest-capturelog is EOL.
    # The I/O capturing has been incoorperated into newer versions of pytest.
    # TODO: update pytest (+dependencies) and refactor test code.
    #assert 'user' in caplog.text()
