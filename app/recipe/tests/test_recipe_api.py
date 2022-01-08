import os.path
import tempfile

from PIL import Image
from core.models import Recipe, Tag, Ingredient
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializer import RecipeSerializer, RecipeDetailSerializer
from rest_framework import status
from rest_framework.test import APIClient

RECIPE_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """Return url for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_recipe(user, **params):
    """Create and retun a sample recipe"""
    default = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 200.00
    }
    default.update(params)
    return Recipe.objects.create(user=user, **default)


def sample_tag(user, name='Main Course'):
    """Create a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Roti'):
    """Create a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


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
        sample_recipe(user=self.user, title='AMAN')
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

    def test_view_recipe_detail(self):
        """Test viewing the recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredient.add(sample_ingredient(user=self.user))

        response = self.client.get(detail_url(recipe.id))

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(response.data, serializer.data)

    def test_create_basic_recipe(self):
        payload = {
            'title': 'chocolate',
            'time_minutes': 30,
            'price': 5.00
        }
        response = self.client.post(RECIPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        tag1 = sample_tag(user=self.user, name='Tdas')
        tag2 = sample_tag(user=self.user, name='Tdas123')
        payload = {
            'title': 'CHOLCO',
            'time_minutes': 30,
            'price': 30.00,
            'tags': [tag1.id, tag2.id]
        }

        response = self.client.post(RECIPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_recipe_with_ingredient(self):
        ingredient1 = sample_ingredient(user=self.user, name='XYZ')
        ingredient2 = sample_ingredient(user=self.user, name='XYZdasd')
        payload = {
            'title': "baskjfa",
            'time_minutes': 23,
            'price': 203.00,
            'ingredient': [ingredient1.id, ingredient2.id]
        }

        response = self.client.post(RECIPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        ingredients = recipe.ingredient.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient1, ingredients)

    def test_partial_update_recipe(self):
        """Test updating recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='HURRY')

        payload = {'title': 'Chicken Tikka', 'tags': [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.tags.count(), 1)
        self.assertIn(new_tag, recipe.tags.all())

    def test_full_update_recipe(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
            'title': 'akjda',
            'time_minutes': 23,
            'price': 23.00
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(recipe.tags.count(), 0)


class RecipeImageUploadTest(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('test@123.com', 'test@123')
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(self.user)

    def tearDown(self) -> None:
        self.recipe.image.delete()

    def test_upload_valid_image(self):
        """Test uplaod a recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            response = self.client.post(url, {'image': ntf}, format='multipart')
        self.recipe.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image', response.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Upload invalid image"""
        url = image_upload_url(self.recipe.id)
        response = self.client.post(url, {'image': 'test'}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
