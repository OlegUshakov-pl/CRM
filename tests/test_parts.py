from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from parts.models import Part, Category
from projects.models import Project


class PartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.project = Project.objects.create(name='Test Project', number='001', created_by=self.user)

    def test_create_part(self):
        part = Part.objects.create(
            project=self.project,
            number='PART-001',
            size='100x50x20',
            rev='A',
        )
        self.assertEqual(part.number, 'PART-001')
        self.assertEqual(part.size, '100x50x20')
        self.assertEqual(part.rev, 'A')
        self.assertEqual(str(part), 'PART-001')

    def test_is_model_property(self):
        part = Part.objects.create(number='model.stp')
        part.file.name = 'model.stp'
        self.assertTrue(part.is_model)

    def test_is_dxf_property(self):
        part = Part.objects.create(number='drawing.dxf')
        part.file.name = 'drawing.dxf'
        self.assertTrue(part.is_dxf)

    def test_file_ext_property(self):
        part = Part.objects.create(number='test.iam')
        part.file.name = 'test.iam'
        self.assertEqual(part.file_ext, '.iam')


class CategoryModelTest(TestCase):
    def test_create_category(self):
        category = Category.objects.create(name='Mechanical')
        self.assertEqual(str(category), 'Mechanical')


class PartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.project = Project.objects.create(name='Test Project', number='001', created_by=self.user)
        self.part = Part.objects.create(
            project=self.project,
            number='PART-001',
            size='100x50x20',
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('parts:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('parts:list'))
        self.assertEqual(response.status_code, 200)

    def test_projects_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('parts:projects'))
        self.assertEqual(response.status_code, 200)

    def test_category_list_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('parts:category_list'))
        self.assertEqual(response.status_code, 200)

    def test_page_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('parts:page', kwargs={'project_slug': self.project.slug}))
        self.assertEqual(response.status_code, 200)

    def test_model_page_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('parts:model_page', kwargs={'project_slug': self.project.slug}))
        self.assertEqual(response.status_code, 200)

    def test_dxf_page_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('parts:dxf_page', kwargs={'project_slug': self.project.slug}))
        self.assertEqual(response.status_code, 200)
