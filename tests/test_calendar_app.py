from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


class CalendarViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_calendar_requires_login(self):
        response = self.client.get(reverse('calendar_app:view'))
        self.assertEqual(response.status_code, 302)

    def test_calendar_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('calendar_app:view'))
        self.assertEqual(response.status_code, 200)

    def test_calendar_with_year_month(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('calendar_app:view') + '?year=2026&month=7')
        self.assertEqual(response.status_code, 200)

    def test_calendar_invalid_year(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('calendar_app:view') + '?year=abc')
        self.assertEqual(response.status_code, 200)

    def test_calendar_invalid_month(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('calendar_app:view') + '?month=abc')
        self.assertEqual(response.status_code, 200)

    def test_calendar_month_clamped(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('calendar_app:view') + '?month=13')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('calendar_app:view') + '?month=0')
        self.assertEqual(response.status_code, 200)
