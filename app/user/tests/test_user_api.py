from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITest(TestCase):
    """Test the user api public"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload success"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'test@1234',
            'name': 'Test'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertFalse(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        """Test the user already exists"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'test@1234',
            'name': 'Test'
        }

        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_to_short(self):
        """Test the password must be greather than 8 character"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'test',
            'name': 'Test'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """Test that token is created for the user"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'test',
            'name': 'Test'
        }
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_crediential(self):
        """Test that toeken is not created for invalid credential"""
        create_user(email='test@gmail.com', password='testpassword')
        payload = {
            'email': 'test@gmail.com',
            'password': 'test',
            'name': 'Test'
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test the token for user does not exist"""
        payload = {
            'email': 'test@gmail.com',
            'password': 'testpassword',
            'name': 'Test'
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test for email and password are required"""
        response = self.client.post(TOKEN_URL, {'email': 'test', 'password': ''})
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
