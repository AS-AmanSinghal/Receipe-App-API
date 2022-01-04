from core.models import Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializer import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient

TAG_URL = reverse('receipe:tag-list')


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
        self.user = get_user_model().objects.create_user('test@gmail.com', 'test@123')
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
        tag=Tag.objects.create(user=self.user, name='AMSNAasdaasdass')
        response = self.client.get(TAG_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], tag.name)
