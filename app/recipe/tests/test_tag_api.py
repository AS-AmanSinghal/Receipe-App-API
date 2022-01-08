from core.models import Tag, Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializer import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient

TAG_URL = reverse('recipe:tag-list')


class PublicTagApiTest(TestCase):
    """Test the public available tags api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """test the login required for retrive tags"""
        response = self.client.get(TAG_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('test123@gmail.com', '@m@NN892310')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_test(self):
        """Test retrieve tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Desset')

        response = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_authenticate_user(self):
        """test the tag limited to authenticated user"""
        user2 = get_user_model().objects.create_user('other@gmail.com', 'test@123')
        Tag.objects.create(user=user2, name='AMSNA')
        Tag.objects.create(user=user2, name='AMSNAasdas')
        tag = Tag.objects.create(user=self.user, name='AMSNAasdaasdass')
        response = self.client.get(TAG_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_create_tags_successful(self):
        """Test creating a new tag"""
        payload = {'name': "AMANS"}
        response = self.client.post(TAG_URL, payload)
        exists = Tag.objects.filter(user=self.user, name=payload['name']).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        payload = {
            'name': ""
        }
        response = self.client.post(TAG_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipe(self):
        """Test filtered tags by those assigned to recipes"""
        tag1 = Tag.objects.create(user=self.user, name='Breakefast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            title='NEw',
            time_minutes=10,
            price=2.43,
            user=self.user
        )
        recipe.tags.add(tag1)

        response = self.client.get(TAG_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(user=self.user, name='Test')
        Tag.objects.create(user=self.user, name='LUNCH')

        recipe1 = Recipe.objects.create(
            title='XYA',
            time_minutes=2,
            price=23.3,
            user=self.user
        )
        recipe1.tags.add(tag)

        recipe2 = Recipe.objects.create(
            title='XYAAS',
            time_minutes=2,
            price=23.3,
            user=self.user
        )
        recipe2.tags.add(tag)

        response = self.client.get(TAG_URL, {'assigned_only': 1})

        self.assertEqual(len(response.data), 1)
