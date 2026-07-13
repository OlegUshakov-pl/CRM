from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from companies.models import Company
from projects.models import Project


class CompanyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_company(self):
        company = Company.objects.create(name='TestCorp', created_by=self.user)
        self.assertEqual(company.name, 'TestCorp')
        self.assertEqual(str(company), 'TestCorp')
        self.assertIsNotNone(company.slug)

    def test_slug_auto_generated(self):
        company = Company.objects.create(name='My Company', created_by=self.user)
        self.assertEqual(company.slug, 'my-company')

    def test_slug_unique_collision(self):
        Company.objects.create(name='Same Name', created_by=self.user)
        c2 = Company.objects.create(name='Same Name', created_by=self.user)
        self.assertEqual(c2.slug, 'same-name-1')

    def test_str_representation(self):
        company = Company.objects.create(name='Acme Inc', created_by=self.user)
        self.assertEqual(str(company), 'Acme Inc')


class CompanyViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.company = Company.objects.create(name='TestCorp', email='info@test.com', phone='+1234567890')

    def test_list_requires_login(self):
        response = self.client.get(reverse('companies:company_list'))
        self.assertEqual(response.status_code, 302)

    def test_list_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('companies:company_list'))
        self.assertEqual(response.status_code, 200)

    def test_detail_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('companies:company_detail', kwargs={'slug': self.company.slug}))
        self.assertEqual(response.status_code, 200)

    def test_create_company(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('companies:company_create'), {
            'name': 'NewCorp',
            'email': 'info@newcorp.com',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Company.objects.filter(name='NewCorp').exists())

    def test_edit_company(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('companies:company_edit', kwargs={'slug': self.company.slug}), {
            'name': 'Updated Corp',
            'email': 'updated@test.com',
        })
        self.assertEqual(response.status_code, 302)
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, 'Updated Corp')

    def test_delete_company(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('companies:company_delete', kwargs={'slug': self.company.slug}))
        self.assertEqual(response.status_code, 302)
        self.company.refresh_from_db()
        self.assertFalse(self.company.is_active)

    def test_create_slide_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('companies:company_create_slide'))
        self.assertEqual(response.status_code, 200)

    def test_edit_slide_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('companies:company_edit_slide', kwargs={'slug': self.company.slug}))
        self.assertEqual(response.status_code, 200)

    def test_search_filter(self):
        self.client.login(username='testuser', password='testpass')
        Company.objects.create(name='Alpha Corp')
        Company.objects.create(name='Beta Inc')
        response = self.client.get(reverse('companies:company_list') + '?q=Alpha')
        self.assertContains(response, 'Alpha Corp')
        self.assertNotContains(response, 'Beta Inc')
