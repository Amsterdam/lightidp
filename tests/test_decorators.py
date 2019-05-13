"""
    auth.tests.test_decorators
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
# import werkzeug.exceptions
# import pytest

# from auth import decorators

# @pytest.mark.usefixtures('app')
# def test_assert_req_args(app):
#     @decorators.assert_req_args('arg1', 'arg2')
#     def accept_arg1_arg2():
#         pass

#     # 1. Request without params fails
#     with app.test_request_context():
#         with pytest.raises(werkzeug.exceptions.BadRequest):
#             accept_arg1_arg2()
#     # 2. Request with a subset of params fails
#     with app.test_request_context(query_string={'arg1': 1, '2gra': 2}):
#         with pytest.raises(werkzeug.exceptions.BadRequest):
#             accept_arg1_arg2()
#     # 3. Request including all params succeeds
#     with app.test_request_context(query_string={'arg1': 1, 'arg2': 2}):
#         accept_arg1_arg2()
