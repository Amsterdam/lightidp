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


def test_log_token(caplog):
    audit.log_token('a.b.mac', sub='user')
    assert 'user' in caplog.text()
