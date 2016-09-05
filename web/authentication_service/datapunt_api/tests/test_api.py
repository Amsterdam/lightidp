from django.conf import settings
from rest_framework.test import APITestCase

TEST_USER = 'testuser'
PASSWORD = settings.TEST_USER_PASSWORD


class AuthenticationServiceTest(APITestCase):

    def test_standard_jwt_method(self):
        response = self.client.post('/api-token-auth/', {'username': TEST_USER, 'password': PASSWORD})
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_authenticatie_method_for_datapunt_apis(self):
        response = self.client.post('/authenticatie/token', {'username': TEST_USER, 'password': PASSWORD, 'grant_type': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)


    def test_without_credentials(self):
        response = self.client.get('/authenticatie/token')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([], response.data)
        self.assertNotIn('token', response.data)
