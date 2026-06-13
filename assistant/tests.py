from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from .services.commands import CommandContext, command_registry
from .services.handlers import _find_contact, _find_project, register_all


class HandlersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        register_all(command_registry)

    def test_find_contact_empty_returns_none(self):
        result = _find_contact('')
        self.assertIsNone(result)

    def test_find_contact_whitespace_returns_none(self):
        result = _find_contact('   ')
        self.assertIsNone(result)

    def test_find_project_empty_returns_none(self):
        result = _find_project('')
        self.assertIsNone(result)

    def test_confirm_create_task_invalid_date_defaults_to_today(self):
        ctx = CommandContext(
            user=self.user,
            text='add task test task on invalid-date',
            intent='create_task',
            params={'title': 'test task', 'date': 'not-a-date'},
        )
        result = command_registry.handle('create_task', ctx)
        self.assertTrue(result.ok)
        self.assertTrue(result.needs_confirmation)
        payload = result.payload
        self.assertEqual(payload['title'], 'test task')
        self.assertEqual(payload['due_date'], date.today().isoformat())

    def test_confirm_create_task_empty_date_defaults_to_today(self):
        ctx = CommandContext(
            user=self.user,
            text='add task test task',
            intent='create_task',
            params={'title': 'test task', 'date': ''},
        )
        result = command_registry.handle('create_task', ctx)
        self.assertTrue(result.ok)
        self.assertTrue(result.needs_confirmation)
        self.assertEqual(result.payload['due_date'], date.today().isoformat())

    def test_confirm_create_note_contains_content_in_payload(self):
        ctx = CommandContext(
            user=self.user,
            text='create note test title with content hello world',
            intent='create_note',
            params={'title': 'test title', 'content': 'hello world'},
        )
        result = command_registry.handle('create_note', ctx)
        self.assertTrue(result.ok)
        self.assertEqual(result.payload.get('content'), 'hello world')
