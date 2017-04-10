# """
#     auth.tests.web.test_siamrequesthandler
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# """
# import urllib
# 
# import pytest
# 
# 
# def siam_authenticate(app, data={}, headers={}):
#     client = app.test_client()
#     qs = urllib.parse.urlencode(data)
#     return client.get('/auth/siam/authenticate', query_string=qs, headers=headers, follow_redirects=False)
# 
# 
# def siam_token(app, data={}, headers={}):
#     client = app.test_client()
#     qs = urllib.parse.urlencode(data)
#     return client.get('/auth/siam/token', query_string=qs, headers=headers)
# 
# 
# @pytest.mark.usefixtures('app')
# def test_siam_authenticate(app):
#     # 1. No callback param in query
#     response = siam_authenticate(app)
#     assert response.status_code == 400
#     # 2. Callback param in query
#     response = siam_authenticate(app, data={'callback': 'http://cb'})
#     assert response.status_code == 307
# 
# 
# @pytest.mark.usefixtures('app', 'config')
# def test_siam_token(app, config):
#     valid_data = {
#         'aselect_credentials': 'credentials',
#         'rid': 1,
#         'a-select-server': config['siam']['aselect_server']
#     }
#     invalid_data_1 = {
#         'aselect_credentials': 'credentials',
#         'a-select-server': config['siam']['aselect_server']
#     }
#     invalid_data_2 = {
#         'aselect_credentials': 'credentials',
#         'rid': 1,
#         'a-select-server': 'arris'
#     }
#     # 1. no Accept header
#     response = siam_token(app, data=valid_data)
#     assert response.status_code == 406
#     # 2. Accept header, no params
#     response = siam_token(app, headers={'Accept': 'text/plain'})
#     assert response.status_code == 400
#     # 3. Params in query, Accept header
#     response = siam_token(app, data=valid_data, headers={'Accept': 'text/plain'})
#     assert response.status_code == 200
#     # 3. Params in query, Accept header
#     response = siam_token(app, data=invalid_data_1, headers={'Accept': 'text/plain'})
#     assert response.status_code == 400
#     # 3. Params in query, Accept header
#     response = siam_token(app, data=invalid_data_2, headers={'Accept': 'text/plain'})
#     assert response.status_code == 400
