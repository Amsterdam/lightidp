from datetime import datetime
import time

from rest_framework.test import APITestCase
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User

TEST_USER = 'testuser'
PASSWORD = 'just_a_password'


class AuthenticationServiceTest(APITestCase):
    def test_header_in_code(self):
        response = self.client.get('/authenticatie/echo', {}, **{'HTTP_X_SAML_ATTRIBUTE_TOKEN1':'xxxx'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('saml', response.data)
        self.assertEqual('xxxx', response.data['saml'])






    # def test_refresh(self):
    #     response = self.client.post('/authenticatie/token', {'username': TEST_USER, 'password': PASSWORD})
    #     now = datetime.utcnow()
    #     time.sleep(2)
    #     token = response.data['token']
    #     response = self.client.post('/authenticatie/refresh', {'token': token})
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('token', response.data)
    #     self.assertNotEqual(token, response.data['token'])
    #
    #     jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
    #     decoded = jwt_decode_handler(response.data['token'])
    #
    #     expiry = datetime.fromtimestamp(int(decoded['exp']))
    #     timediff = expiry - now
    #     self.assertGreater(timediff.total_seconds(), 300)
    #
    #     original_expiry = datetime.fromtimestamp(int(decoded['orig_iat']))
    #     self.assertLess(original_expiry, expiry)
    #
    # def test_get_token(self):
    #     response = self.client.get('/authenticatie/token')
    #     self.assertEqual(response.status_code, 405)
    #
    # def test_without_credentials(self):
    #     response = self.client.post('/authenticatie/token')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn('non_field_errors', response.data)
    #     self.assertEqual("Unable to login with provided credentials.",
    #                      response.data['non_field_errors'][0])
    #
    # def test_get_status_health(self):
    #     response=self.client.get('/status/health')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('Connectivity OK', str(response.content))
    #
