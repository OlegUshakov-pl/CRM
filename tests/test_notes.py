from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from datetime import date

from notes.models import Note
from projects.models import Project
from companies.models import Company


class NoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_note(self):
        note = Note.objects.create(title='Test Note', content='Some content', created_by=self.user)
        self.assertEqual(note.title, 'Test Note')
        self.assertEqual(note.content, 'Some content')
        self.assertEqual(str(note), 'Test Note')
        self.assertIsNotNone(note.slug)

    def test_slug_auto_generated(self):
        note = Note.objects.create(title='My Note', content='Content', created_by=self.user)
        self.assertEqual(note.slug, 'my-note')

    def test_slug_unique_collision(self):
        Note.objects.create(title='Same Note', content='Content', created_by=self.user)
        n2 = Note.objects.create(title='Same Note', content='Content', created_by=self.user)
        self.assertEqual(n2.slug, 'same-note-1')

    def test_active_manager_filters(self):
        Note.objects.create(title='Active Note', content='Content', created_by=self.user)
        n2 = Note.objects.create(title='Inactive Note', content='Content', created_by=self.user)
        n2.is_active = False
        n2.save()
        self.assertEqual(Note.objects.count(), 1)

    def test_str_representation(self):
        note = Note.objects.create(title='Important Note', content='Content', created_by=self.user)
        self.assertEqual(str(note), 'Important Note')


class NoteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.note = Note.objects.create(
            title='Test Note',
            content='Test content',
            date=date.today(),
            created_by=self.user,
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notes:list'))
        self.assertEqual(response.status_code, 200)

    def test_detail_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notes:detail', kwargs={'slug': self.note.slug}))
        self.assertEqual(response.status_code, 200)

    def test_create_note(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('notes:create'), {
            'title': 'New Note',
            'content': 'New content',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Note.objects.filter(title='New Note').exists())

    def test_edit_note(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('notes:edit', kwargs={'slug': self.note.slug}), {
            'title': 'Updated Note',
            'content': 'Updated content',
        })
        self.assertEqual(response.status_code, 302)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated Note')

    def test_delete_note(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('notes:delete', kwargs={'slug': self.note.slug}))
        self.assertEqual(response.status_code, 302)
        self.note.refresh_from_db()
        self.assertFalse(self.note.is_active)

    def test_search_filter(self):
        self.client.login(username='testuser', password='testpass')
        Note.objects.create(title='Meeting notes', content='Discussed project', created_by=self.user)
        Note.objects.create(title='Ideas', content='Brainstorm', created_by=self.user)
        response = self.client.get(reverse('notes:list') + '?q=Meeting')
        self.assertContains(response, 'Meeting notes')
        self.assertNotContains(response, 'Ideas')

    def test_sort_by_date_asc(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notes:list') + '?sort=date_asc')
        self.assertEqual(response.status_code, 200)

    def test_sort_by_project(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notes:list') + '?sort=project')
        self.assertEqual(response.status_code, 200)

    def test_create_slide_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notes:create_slide'))
        self.assertEqual(response.status_code, 200)

    def test_edit_slide_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notes:edit_slide', kwargs={'slug': self.note.slug}))
        self.assertEqual(response.status_code, 200)
