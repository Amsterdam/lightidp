"""
    auth.tests.test_httputils
    ~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import types
import werkzeug.exceptions
import pytest

import auth.siam
from auth import httputils


@pytest.fixture()
def no_siam_check(monkeypatch):

    def get_authn_redirect(*args, **kwargs):
        pass

    monkeypatch.setattr(
        auth.siam.Client, 'get_authn_redirect', get_authn_redirect)


@pytest.mark.usefixtures('no_siam_check')
def test_assert_acceptable():
    @httputils.assert_acceptable('text/plain')
    def accept_text():
        pass

    from auth import server
    app = server.app
    # 1. Request without Accept header fails
    with app.test_request_context():
        with pytest.raises(werkzeug.exceptions.NotAcceptable):
            accept_text()
    # 2. Request with no matching Accept fails
    with app.test_request_context(headers={'Accept': 'application/json'}):
        with pytest.raises(werkzeug.exceptions.NotAcceptable):
            accept_text()
    # 3. Request with matching Accept succeeds
    with app.test_request_context(headers={
            'Accept': 'application/json; q=0.6, text/plain'}):
        accept_text()


@pytest.mark.usefixtures('no_siam_check')
def test_assert_mimetypes():
    @httputils.assert_mimetypes('text/plain', 'application/json')
    def accept_text_and_json():
        pass

    from auth import server
    app = server.app
    # 1. Request without Content-type fails
    with app.test_request_context():
        with pytest.raises(werkzeug.exceptions.UnsupportedMediaType):
            accept_text_and_json()
    # 2. Request with not matching Content-type fails
    with app.test_request_context(content_type='audio/*'):
        with pytest.raises(werkzeug.exceptions.UnsupportedMediaType):
            accept_text_and_json()
    # 3. Request with matching Content-type succeeds
    with app.test_request_context(content_type='application/json'):
        accept_text_and_json()


@pytest.mark.usefixtures('no_siam_check')
def test_assert_req_args():
    @httputils.assert_req_args('arg1', 'arg2')
    def accept_arg1_arg2():
        pass

    from auth import server
    app = server.app
    # 1. Request without params fails
    with app.test_request_context():
        with pytest.raises(werkzeug.exceptions.BadRequest):
            accept_arg1_arg2()
    # 2. Request with a subset of params fails
    with app.test_request_context(query_string={'arg1': 1, '2gra': 2}):
        with pytest.raises(werkzeug.exceptions.BadRequest):
            accept_arg1_arg2()
    # 3. Request including all params succeeds
    with app.test_request_context(query_string={'arg1': 1, 'arg2': 2}):
        accept_arg1_arg2()


@pytest.mark.usefixtures('no_siam_check')
def test_response_mimetype():

    @httputils.response_mimetype('application/json')
    def empty_mimetype():
        return types.SimpleNamespace()
    assert empty_mimetype().mimetype == 'application/json'

    @httputils.response_mimetype('application/json')
    def text_mimetype():
        r = types.SimpleNamespace()
        r.mimetype = 'text/plain'
        return r
    assert text_mimetype().mimetype == 'application/json'
