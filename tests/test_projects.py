from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta

from projects.models import Project
from companies.models import Company


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_project(self):
        project = Project.objects.create(
            name='Test Project',
            number='001',
            status='planning',
            created_by=self.user,
        )
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(str(project), 'Test Project')
        self.assertEqual(project.status, 'planning')
        self.assertIsNotNone(project.slug)

    def test_slug_auto_generated(self):
        project = Project.objects.create(name='My Project', created_by=self.user)
        self.assertEqual(project.slug, 'my-project')

    def test_slug_unique_collision(self):
        Project.objects.create(name='Same Name', created_by=self.user)
        p2 = Project.objects.create(name='Same Name', created_by=self.user)
        self.assertEqual(p2.slug, 'same-name-1')

    def test_str_representation(self):
        project = Project.objects.create(name='Important Project', created_by=self.user)
        self.assertEqual(str(project), 'Important Project')

    def test_status_choices(self):
        project = Project.objects.create(name='Active Project', status='active', created_by=self.user)
        self.assertEqual(project.status, 'active')


class ProjectViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.project = Project.objects.create(
            name='Test Project',
            number='001',
            status='planning',
            created_by=self.user,
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 200)

    def test_detail_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('projects:detail', kwargs={'slug': self.project.slug}))
        self.assertEqual(response.status_code, 200)

    def test_create_project(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('projects:create'), {
            'name': 'New Project',
            'number': '002',
            'status': 'active',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name='New Project').exists())

    def test_edit_project(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('projects:edit', kwargs={'slug': self.project.slug}), {
            'name': 'Updated Project',
            'number': '001',
            'status': 'active',
        })
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Updated Project')

    def test_delete_project(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('projects:delete', kwargs={'slug': self.project.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_create_slide_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('projects:create_slide'))
        self.assertEqual(response.status_code, 200)

    def test_edit_slide_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('projects:edit_slide', kwargs={'slug': self.project.slug}))
        self.assertEqual(response.status_code, 200)

    def test_import_page_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('projects:import_page'))
        self.assertEqual(response.status_code, 200)
