from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser('test@aman.com','test@123')
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(email='test123@gmail.com',password='Test@123',name='Test')


    def test_user_listed(self):
        '''Test the users are listed on user page'''
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        self.assertContains(response,self.user.email)
        self.assertContains(response, self.user.name)

    def test_user_change_page(self):
        '''Test the user edit page'''
        url = reverse('admin:core_user_change',args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)

    def test_user_create_page(self):
        '''Test the user create page'''
        url = reverse('admin:core_user_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)

