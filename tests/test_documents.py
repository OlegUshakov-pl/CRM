from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from io import BytesIO

from documents.models import Document, Category
from projects.models import Project


class DocumentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.project = Project.objects.create(name='Test Project', number='001', created_by=self.user)

    def test_create_document(self):
        doc = Document.objects.create(
            project=self.project,
            number='DOC-001',
            document_type='document',
        )
        self.assertEqual(doc.number, 'DOC-001')
        self.assertEqual(doc.document_type, 'document')
        self.assertIsNotNone(doc.created_at)

    def test_str_representation_no_project(self):
        doc = Document.objects.create(number='DOC-002')
        self.assertIn('DOC-002', str(doc))

    def test_str_representation_with_project(self):
        doc = Document.objects.create(project=self.project, number='DOC-003')
        self.assertIn('Test Project', str(doc))

    def test_is_pdf_property(self):
        doc = Document.objects.create(number='test.pdf')
        doc.file.name = 'test.pdf'
        self.assertTrue(doc.is_pdf)

    def test_is_image_property(self):
        doc = Document.objects.create(number='test.jpg')
        doc.file.name = 'test.jpg'
        self.assertTrue(doc.is_image)


class CategoryModelTest(TestCase):
    def test_create_category(self):
        category = Category.objects.create(name='Technical Docs')
        self.assertEqual(str(category), 'Technical Docs')

    def test_unique_name(self):
        Category.objects.create(name='Manuals')
        with self.assertRaises(Exception):
            Category.objects.create(name='Manuals')


class DocumentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.project = Project.objects.create(name='Test Project', number='001', created_by=self.user)
        self.doc = Document.objects.create(
            project=self.project,
            number='DOC-001',
            document_type='document',
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('documents:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('documents:list'))
        self.assertEqual(response.status_code, 200)

    def test_projects_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('documents:projects'))
        self.assertEqual(response.status_code, 200)

    def test_project_documents_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('documents:project', kwargs={'project_slug': self.project.slug}))
        self.assertEqual(response.status_code, 200)

    def test_category_list_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('documents:category_list'))
        self.assertEqual(response.status_code, 200)

    def test_search_filter(self):
        self.client.login(username='testuser', password='testpass')
        Document.objects.create(project=self.project, number='ALPHA-001')
        Document.objects.create(project=self.project, number='BETA-001')
        response = self.client.get(reverse('documents:list') + '?q=ALPHA')
        self.assertContains(response, 'ALPHA-001')
        self.assertNotContains(response, 'BETA-001')
