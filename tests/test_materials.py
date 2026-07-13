from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from materials.models import Material, Category, MaterialFile
from projects.models import Project


class MaterialModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.project = Project.objects.create(name='Test Project', number='001', created_by=self.user)

    def test_create_material(self):
        material = Material.objects.create(
            name='Bolt M10',
            project=self.project,
            quantity=100,
            unit='pcs',
            unit_price=5.50,
            created_by=self.user,
        )
        self.assertEqual(material.name, 'Bolt M10')
        self.assertEqual(str(material), 'Bolt M10')
        self.assertEqual(material.quantity, 100)
        self.assertEqual(material.total_price(), 550.00)
        self.assertIsNotNone(material.slug)

    def test_slug_auto_generated(self):
        material = Material.objects.create(name='Steel Pipe', project=self.project, created_by=self.user)
        self.assertEqual(material.slug, 'steel-pipe')

    def test_slug_unique_collision(self):
        Material.objects.create(name='Same Name', project=self.project, created_by=self.user)
        m2 = Material.objects.create(name='Same Name', project=self.project, created_by=self.user)
        self.assertEqual(m2.slug, 'same-name-1')

    def test_total_price(self):
        material = Material.objects.create(
            name='Item', quantity=10, unit_price=25.00,
            project=self.project, created_by=self.user,
        )
        self.assertEqual(material.total_price(), 250.00)

    def test_total_price_no_unit_price(self):
        material = Material.objects.create(
            name='Item', quantity=10, unit_price=None,
            project=self.project, created_by=self.user,
        )
        self.assertEqual(material.total_price(), 0)

    def test_str_representation(self):
        material = Material.objects.create(name='Cable', project=self.project, created_by=self.user)
        self.assertEqual(str(material), 'Cable')


class CategoryModelTest(TestCase):
    def test_create_category(self):
        category = Category.objects.create(name='Fasteners')
        self.assertEqual(str(category), 'Fasteners')

    def test_unique_name(self):
        Category.objects.create(name='Metal')
        with self.assertRaises(Exception):
            Category.objects.create(name='Metal')


class MaterialViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.project = Project.objects.create(name='Test Project', number='001', created_by=self.user)
        self.material = Material.objects.create(
            name='Test Material',
            project=self.project,
            quantity=50,
            unit='pcs',
            created_by=self.user,
        )

    def test_main_requires_login(self):
        response = self.client.get(reverse('materials:main'))
        self.assertEqual(response.status_code, 302)

    def test_main_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('materials:main'))
        self.assertEqual(response.status_code, 200)

    def test_common_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('materials:common'))
        self.assertEqual(response.status_code, 200)

    def test_page_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('materials:page', kwargs={'project_slug': self.project.slug}))
        self.assertEqual(response.status_code, 200)

    def test_create_material(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('materials:create', kwargs={'project_slug': self.project.slug}), {
            'name': 'New Material',
            'quantity': 10,
            'unit': 'kg',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Material.objects.filter(name='New Material').exists())

    def test_edit_material(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('materials:edit', kwargs={'slug': self.material.slug}), {
            'name': 'Updated Material',
            'quantity': 100,
            'unit': 'pcs',
            'project': self.project.pk,
        })
        self.assertEqual(response.status_code, 302)
        self.material.refresh_from_db()
        self.assertEqual(self.material.name, 'Updated Material')

    def test_delete_material(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('materials:delete', kwargs={'slug': self.material.slug}))
        self.assertEqual(response.status_code, 302)
        self.material.refresh_from_db()
        self.assertFalse(self.material.is_active)

    def test_category_list_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('materials:category_list'))
        self.assertEqual(response.status_code, 200)

    def test_category_create(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('materials:category_list'), {'name': 'New Category'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='New Category').exists())

    def test_search_filter(self):
        self.client.login(username='testuser', password='testpass')
        Material.objects.create(name='Alpha Part', project=self.project, created_by=self.user)
        Material.objects.create(name='Beta Part', project=self.project, created_by=self.user)
        response = self.client.get(reverse('materials:common') + '?q=Alpha')
        self.assertContains(response, 'Alpha Part')
        self.assertNotContains(response, 'Beta Part')
