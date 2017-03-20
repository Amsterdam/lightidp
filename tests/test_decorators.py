"""
    auth.tests.test_decorators
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import types
import werkzeug.exceptions
import pytest

from auth import exceptions, decorators, token


@pytest.mark.usefixtures('app')
def test_assert_acceptable(app):
    @decorators.assert_acceptable('text/plain')
    def accept_text():
        pass

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
    # 4. Request with catch-all Accept succeeds
    with app.test_request_context(headers={
            'Accept': '*/*'}):
        accept_text()
    # 5. Request with wildcard Accept succeeds
    with app.test_request_context(headers={
            'Accept': 'text/*'}):
        accept_text()
    # 6. Request with wildcard Accept among multiple succeeds
    with app.test_request_context(headers={
            'Accept': 'application/*; q=0.6, text/*'}):
        accept_text()


@pytest.mark.usefixtures('app')
def test_assert_mimetypes(app):
    @decorators.assert_mimetypes('text/plain', 'application/json')
    def accept_text_and_json():
        return 'correct'

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
        assert accept_text_and_json() == 'correct'


@pytest.mark.usefixtures('app')
def test_assert_req_args(app):
    @decorators.assert_req_args('arg1', 'arg2')
    def accept_arg1_arg2():
        pass

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


def test_assert_gateway():
    wz = werkzeug.exceptions
    for expected, thrown in (
        (wz.GatewayTimeout, (exceptions.GatewayTimeoutException,)),
        (wz.BadGateway, (exceptions.GatewayRequestException, exceptions.GatewayResponseException, exceptions.GatewayConnectionException)),
        (wz.BadRequest, (exceptions.CallbackException,))
    ):
        for e in thrown:
            @decorators.assert_gateway
            def gatewaytimeout():
                raise e
            with pytest.raises(expected):
                gatewaytimeout()


def test_response_mimetype():

    @decorators.response_mimetype('application/json')
    def empty_mimetype():
        return types.SimpleNamespace()
    assert empty_mimetype().mimetype == 'application/json'

    @decorators.response_mimetype('application/json')
    def text_mimetype():
        r = types.SimpleNamespace()
        r.mimetype = 'text/plain'
        return r
    assert text_mimetype().mimetype == 'application/json'


@pytest.mark.usefixtures('app')
def test_insert_jwt(app):
    tokenbuilder = token.RefreshTokenBuilder('secret', 300, 'HS256')
    tokendata = tokenbuilder.create(sub='tester')
    valid_jwt = str(tokendata.encode(), 'utf-8')

    @decorators.insert_jwt(tokenbuilder)
    def get_jwt(data, jwt):
        assert jwt == valid_jwt
        assert data == tokendata

    # 1. Request without token header fails
    with app.test_request_context():
        response = get_jwt()
        assert response.status_code == 401
    # 2. Request with wrong Authz prefix fails
    with app.test_request_context(headers={'Authorization': 'JWT a.b.c'}):
        response = get_jwt()
        assert response.status_code == 401
    # 3. Request with wrong Authz format fails
    with app.test_request_context(headers={'Authorization': 'JWT a.b.c def'}):
        response = get_jwt()
        assert response.status_code == 401
    # 4. Request with wrong Authz format fails
    with app.test_request_context(headers={'Authorization': 'Bearer ' + valid_jwt}):
        get_jwt()
