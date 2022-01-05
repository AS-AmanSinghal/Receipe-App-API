from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe
from recipe.serializer import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """Create and retun a sample recipe"""
    default = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 200.00
    }
    default.update(params)
    return Recipe.objects.create(user=user, **default)


class PublicRecipeApiTest(TestCase):
    """Test Unauthenticated Recipe Api access"""

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """Test the authentication required"""
        response = self.client.get(RECIPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Test Authenticated API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('test@gmal.com', 'test@123')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        """Test to retrieve the recipe"""
        sample_recipe(self.user)
        sample_recipe(user=self.user,title='AMAN')
        response = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrive_limited_user_recipe(self):
        user2 = get_user_model().objects.create_user('test123@gmail.com', 'hdsad')
        sample_recipe(user2)
        sample_recipe(self.user)
        response = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)
