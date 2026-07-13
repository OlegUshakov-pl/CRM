from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta

from tasks.models import Task
from projects.models import Project


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_task(self):
        task = Task.objects.create(title='Test Task', created_by=self.user)
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(str(task), 'Test Task')
        self.assertEqual(task.status, 'todo')
        self.assertEqual(task.priority, 'medium')
        self.assertIsNotNone(task.slug)

    def test_slug_auto_generated(self):
        task = Task.objects.create(title='My Task', created_by=self.user)
        self.assertEqual(task.slug, 'my-task')

    def test_slug_unique_collision(self):
        Task.objects.create(title='Same Task', created_by=self.user)
        t2 = Task.objects.create(title='Same Task', created_by=self.user)
        self.assertEqual(t2.slug, 'same-task-1')

    def test_active_manager_filters(self):
        Task.objects.create(title='Active Task', created_by=self.user)
        t2 = Task.objects.create(title='Inactive Task', created_by=self.user)
        t2.is_active = False
        t2.save()
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.all_tasks.count(), 2)

    def test_str_representation(self):
        task = Task.objects.create(title='Important Task', created_by=self.user)
        self.assertEqual(str(task), 'Important Task')


class TaskViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.task = Task.objects.create(
            title='Test Task',
            description='Test description',
            status='todo',
            priority='high',
            due_date=date.today() + timedelta(days=7),
            created_by=self.user,
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)

    def test_create_task(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('tasks:create'), {
            'title': 'New Task',
            'status': 'todo',
            'priority': 'medium',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='New Task').exists())

    def test_edit_task(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('tasks:edit', kwargs={'slug': self.task.slug}), {
            'title': 'Updated Task',
            'status': 'done',
            'priority': 'low',
        })
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
        self.assertEqual(self.task.status, 'done')

    def test_delete_task(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('tasks:delete', kwargs={'slug': self.task.slug}))
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertFalse(self.task.is_active)

    def test_search_filter(self):
        self.client.login(username='testuser', password='testpass')
        Task.objects.create(title='Buy groceries', created_by=self.user)
        Task.objects.create(title='Write code', created_by=self.user)
        response = self.client.get(reverse('tasks:list') + '?q=groceries')
        self.assertContains(response, 'Buy groceries')
        self.assertNotContains(response, 'Write code')

    def test_status_filter(self):
        self.client.login(username='testuser', password='testpass')
        Task.objects.create(title='Done task', status='done', created_by=self.user)
        response = self.client.get(reverse('tasks:list') + '?status=todo')
        self.assertContains(response, 'Test Task')
        self.assertNotContains(response, 'Done task')

    def test_priority_filter(self):
        self.client.login(username='testuser', password='testpass')
        Task.objects.create(title='Low task', priority='low', created_by=self.user)
        response = self.client.get(reverse('tasks:list') + '?priority=high')
        self.assertContains(response, 'Test Task')
        self.assertNotContains(response, 'Low task')

    def test_create_slide_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('tasks:create_slide'))
        self.assertEqual(response.status_code, 200)

    def test_edit_slide_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('tasks:edit_slide', kwargs={'slug': self.task.slug}))
        self.assertEqual(response.status_code, 200)
