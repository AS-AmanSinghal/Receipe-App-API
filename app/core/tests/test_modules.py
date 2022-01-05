from core.models import Tag, Ingredient, Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase


def sample_user(email='test@gmail.com', password='test@123'):
    """Create sample user"""
    return get_user_model().objects.create_user(email, password)


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

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = Tag.objects.create(user=sample_user(), name='Vegan')
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = Ingredient.objects.create(user=sample_user(), name='CUCUmber')
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = Recipe.objects.create(
            user=sample_user(),
            title='Mashroom',
            time_minutes=5,
            price=10.00,
        )

        self.assertEqual(str(recipe), recipe.title)
