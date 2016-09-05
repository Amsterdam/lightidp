from rest_framework.test import APITestCase
from django.contrib.auth.models import User

TEST_USER = 'testuser'
PASSWORD = 'just_a_password'


class AuthenticationServiceTest(APITestCase):

    def setUp(self):
        test_user = User.objects.create(username=TEST_USER)
        test_user.set_password(PASSWORD)
        test_user.save()

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
