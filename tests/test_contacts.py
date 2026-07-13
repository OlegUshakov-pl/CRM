from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from contacts.models import Contact
from companies.models import Company


class ContactModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_contact(self):
        contact = Contact.objects.create(first_name='John', last_name='Doe', created_by=self.user)
        self.assertEqual(contact.first_name, 'John')
        self.assertEqual(contact.last_name, 'Doe')
        self.assertEqual(str(contact), 'John Doe')
        self.assertEqual(contact.get_full_name(), 'John Doe')
        self.assertIsNotNone(contact.slug)

    def test_slug_auto_generated(self):
        contact = Contact.objects.create(first_name='Jane', last_name='Smith', created_by=self.user)
        self.assertEqual(contact.slug, 'jane-smith')

    def test_slug_unique_collision(self):
        Contact.objects.create(first_name='John', last_name='Doe', created_by=self.user)
        c2 = Contact.objects.create(first_name='John', last_name='Doe', created_by=self.user)
        self.assertEqual(c2.slug, 'john-doe-1')

    def test_str_representation(self):
        contact = Contact.objects.create(first_name='Alice', last_name='Wonder', created_by=self.user)
        self.assertEqual(str(contact), 'Alice Wonder')

    def test_get_full_name(self):
        contact = Contact.objects.create(first_name='Bob', last_name='Builder', created_by=self.user)
        self.assertEqual(contact.get_full_name(), 'Bob Builder')


class ContactViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.contact = Contact.objects.create(
            first_name='John', last_name='Doe',
            email='john@test.com', phone='+1234567890'
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('contacts:contact_list'))
        self.assertEqual(response.status_code, 302)

    def test_list_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('contacts:contact_list'))
        self.assertEqual(response.status_code, 200)

    def test_detail_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('contacts:contact_detail', kwargs={'slug': self.contact.slug}))
        self.assertEqual(response.status_code, 200)

    def test_create_contact(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('contacts:contact_create'), {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@test.com',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Contact.objects.filter(first_name='Jane', last_name='Smith').exists())

    def test_edit_contact(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('contacts:contact_edit', kwargs={'slug': self.contact.slug}), {
            'first_name': 'Updated',
            'last_name': 'Name',
        })
        self.assertEqual(response.status_code, 302)
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.first_name, 'Updated')

    def test_delete_contact(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('contacts:contact_delete', kwargs={'slug': self.contact.slug}))
        self.assertEqual(response.status_code, 302)
        self.contact.refresh_from_db()
        self.assertFalse(self.contact.is_active)

    def test_search_filter(self):
        self.client.login(username='testuser', password='testpass')
        Contact.objects.create(first_name='Alice', last_name='Wonder')
        Contact.objects.create(first_name='Bob', last_name='Builder')
        response = self.client.get(reverse('contacts:contact_list') + '?q=Alice')
        self.assertContains(response, 'Alice')
        self.assertNotContains(response, 'Builder')

    def test_create_slide_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('contacts:contact_create_slide'))
        self.assertEqual(response.status_code, 200)

    def test_edit_slide_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('contacts:contact_edit_slide', kwargs={'slug': self.contact.slug}))
        self.assertEqual(response.status_code, 200)
