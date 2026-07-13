from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta

from generator.models import Deal
from companies.models import Company


class DealModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_deal(self):
        deal = Deal.objects.create(
            name='Big Deal',
            status='lead',
            priority='high',
            value=10000.00,
            created_by=self.user,
        )
        self.assertEqual(deal.name, 'Big Deal')
        self.assertEqual(str(deal), 'Big Deal')
        self.assertEqual(deal.status, 'lead')
        self.assertEqual(deal.priority, 'high')
        self.assertEqual(deal.value, 10000.00)
        self.assertIsNotNone(deal.slug)

    def test_slug_auto_generated(self):
        deal = Deal.objects.create(name='My Deal', created_by=self.user)
        self.assertEqual(deal.slug, 'my-deal')

    def test_slug_unique_collision(self):
        Deal.objects.create(name='Same Deal', created_by=self.user)
        d2 = Deal.objects.create(name='Same Deal', created_by=self.user)
        self.assertEqual(d2.slug, 'same-deal-1')

    def test_str_representation(self):
        deal = Deal.objects.create(name='Important Deal', created_by=self.user)
        self.assertEqual(str(deal), 'Important Deal')


class DealViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.deal = Deal.objects.create(
            name='Test Deal',
            status='proposal',
            priority='medium',
            value=5000.00,
            created_by=self.user,
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('generators:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('generators:list'))
        self.assertEqual(response.status_code, 200)

    def test_detail_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('generators:detail', kwargs={'slug': self.deal.slug}))
        self.assertEqual(response.status_code, 200)

    def test_create_deal(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('generators:create'), {
            'name': 'New Deal',
            'status': 'lead',
            'priority': 'low',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Deal.objects.filter(name='New Deal').exists())

    def test_edit_deal(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('generators:edit', kwargs={'slug': self.deal.slug}), {
            'name': 'Updated Deal',
            'status': 'won',
            'priority': 'high',
        })
        self.assertEqual(response.status_code, 302)
        self.deal.refresh_from_db()
        self.assertEqual(self.deal.name, 'Updated Deal')
        self.assertEqual(self.deal.status, 'won')

    def test_delete_deal(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('generators:delete', kwargs={'slug': self.deal.slug}))
        self.assertEqual(response.status_code, 302)
        self.deal.refresh_from_db()
        self.assertFalse(self.deal.is_active)

    def test_search_filter(self):
        self.client.login(username='testuser', password='testpass')
        Deal.objects.create(name='Alpha Deal', created_by=self.user)
        Deal.objects.create(name='Beta Deal', created_by=self.user)
        response = self.client.get(reverse('generators:list') + '?q=Alpha')
        self.assertContains(response, 'Alpha Deal')
        self.assertNotContains(response, 'Beta Deal')

    def test_status_filter(self):
        self.client.login(username='testuser', password='testpass')
        Deal.objects.create(name='Won Deal', status='won', created_by=self.user)
        response = self.client.get(reverse('generators:list') + '?status=proposal')
        self.assertContains(response, 'Test Deal')
        self.assertNotContains(response, 'Won Deal')

    def test_priority_filter(self):
        self.client.login(username='testuser', password='testpass')
        Deal.objects.create(name='Low Deal', priority='low', created_by=self.user)
        response = self.client.get(reverse('generators:list') + '?priority=medium')
        self.assertContains(response, 'Test Deal')
        self.assertNotContains(response, 'Low Deal')

    def test_create_slide_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('generators:create_slide'))
        self.assertEqual(response.status_code, 200)

    def test_edit_slide_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('generators:edit_slide', kwargs={'slug': self.deal.slug}))
        self.assertEqual(response.status_code, 200)
