from core.models import Ingredient
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializer import IngredientSerializer
from rest_framework import status
from rest_framework.test import APIClient

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTest(TestCase):
    """Test the publicly ingredients api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test the login to require to endpoint"""
        response = self.client.get(INGREDIENT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    """Test the private ingredient api means get authuroied"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('test@123.com', 'test@123')
        self.client.force_authenticate(self.user)

    def test_retrive_ingredient_list(self):
        """test retriece ingredient list"""

        Ingredient.objects.create(user=self.user, name='XYA')
        Ingredient.objects.create(user=self.user, name='XYAdasdas')

        response = self.client.get(INGREDIENT_URL)
        ingredient = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredient, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test the ingreident for the authenticated user return"""

        user2 = get_user_model().objects.create_user('xyz@gmail.com', 'AMAN')
        Ingredient.objects.create(user=user2, name='XYA')
        Ingredient.objects.create(user=user2, name='XYA')
        ingredient = Ingredient.objects.create(user=self.user, name='XYA')
        response = self.client.get(INGREDIENT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test create a new ingredient"""
        payload = {
            'name': "AMAN"
        }
        self.client.post(INGREDIENT_URL, payload)
        exists = Ingredient.objects.filter(user=self.user,name=payload['name']).exists()
        self.assertTrue(exists)


    def test_create_ingredient_invalid(self):
        """Test create the invalid ingredient"""
        payload = {
            'name':""
        }
        response = self.client.post(INGREDIENT_URL,payload)
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
