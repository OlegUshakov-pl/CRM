import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


class ServeProjectFileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_path_traversal_absolute_path_blocked(self):
        response = self.client.get(
            reverse('core:serve_project_file', kwargs={'file_path': 'C:\\Windows\\win.ini'})
        )
        self.assertEqual(response.status_code, 404)

    def test_path_traversal_dotdot_blocked(self):
        response = self.client.get(
            reverse('core:serve_project_file', kwargs={'file_path': '../../../../etc/passwd'})
        )
        self.assertEqual(response.status_code, 404)

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_path_traversal_encoded_dotdot_blocked(self):
        response = self.client.get(
            reverse('core:serve_project_file', kwargs={'file_path': '..%2f..%2f..%2fetc%2fpasswd'})
        )
        self.assertEqual(response.status_code, 404)

    def test_legitimate_file_in_media_404(self):
        response = self.client.get(
            reverse('core:serve_project_file', kwargs={'file_path': 'nonexistent.txt'})
        )
        self.assertEqual(response.status_code, 404)
