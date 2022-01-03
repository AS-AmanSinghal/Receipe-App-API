from django.contrib.auth import get_user_model
from django.test import TestCase


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        '''Test create a new user with email is successful'''
        email = "test@gmail.com"
        password = "Test@123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalised(self):
        '''Test the email for a new user is normalized'''

        email = 'test@AMAN.COM'
        user = get_user_model().objects.create_user(email, 'test123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        '''Test creating user with no email address raise error'''
        with self.assertRaises(ValueError):
            email = ''
            user = get_user_model().objects.create_user(email, 'test123')

    def test_create_new_super_user(self):
        '''Test creating a new super user'''
        user = get_user_model().objects.create_superuser('test@aman.com', 'Test123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
