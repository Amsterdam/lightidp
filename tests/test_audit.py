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


def test_log_refreshtoken_anon(caplog):
    audit.log_refreshtoken('a.b.mac')
    assert 'mac' in caplog.text()
    assert 'anonymous' in caplog.text()


def test_log_refreshtoken_user(caplog):
    audit.log_refreshtoken('a.b.mac', user='user')
    assert 'user' in caplog.text()


def test_log_accesstoken(caplog):
    audit.log_accesstoken('refre.shtoken.rmac', 'acce.sstoken.amac')
    assert 'rmac' in caplog.text()
    assert 'amac' in caplog.text()
