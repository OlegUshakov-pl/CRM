from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_open_redirect_external_url_blocked(self):
        response = self.client.post(
            reverse('accounts:login') + '?next=https://evil.com',
            {'username': 'testuser', 'password': 'testpass'},
        )
        self.assertRedirects(response, reverse('core:dashboard'))

    def test_open_redirect_external_post_next_blocked(self):
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'testuser', 'password': 'testpass', 'next': 'https://evil.com'},
        )
        self.assertRedirects(response, reverse('core:dashboard'))

    def test_internal_redirect_allowed(self):
        response = self.client.post(
            reverse('accounts:login') + '?next=/projects/',
            {'username': 'testuser', 'password': 'testpass'},
        )
        self.assertRedirects(response, '/projects/')

    def test_internal_post_redirect_allowed(self):
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'testuser', 'password': 'testpass', 'next': '/companies/'},
        )
        self.assertRedirects(response, '/companies/')
