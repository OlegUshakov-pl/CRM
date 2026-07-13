from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from library.models import LibraryItem, Category, Tag, LibraryAttachment


class LibraryItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_library_item(self):
        item = LibraryItem.objects.create(
            title='Test Article',
            content='<p>Hello World</p>',
            created_by=self.user,
        )
        self.assertEqual(item.title, 'Test Article')
        self.assertEqual(str(item), 'Test Article')
        self.assertIsNotNone(item.slug)

    def test_slug_auto_generated(self):
        item = LibraryItem.objects.create(title='My Article', created_by=self.user)
        self.assertEqual(item.slug, 'my-article')

    def test_slug_unique_collision(self):
        LibraryItem.objects.create(title='Same Title', created_by=self.user)
        i2 = LibraryItem.objects.create(title='Same Title', created_by=self.user)
        self.assertEqual(i2.slug, 'same-title-1')

    def test_detect_file_type_pdf(self):
        item = LibraryItem.objects.create(title='PDF', file='test.pdf', created_by=self.user)
        self.assertEqual(item.file_type, 'pdf')

    def test_detect_file_type_image(self):
        item = LibraryItem.objects.create(title='Image', file='photo.jpg', created_by=self.user)
        self.assertEqual(item.file_type, 'image')

    def test_is_favorite_default(self):
        item = LibraryItem.objects.create(title='Article', created_by=self.user)
        self.assertFalse(item.is_favorite)


class CategoryModelTest(TestCase):
    def test_create_category(self):
        category = Category.objects.create(name='Programming')
        self.assertEqual(str(category), 'Programming')

    def test_slug_auto_generated(self):
        category = Category.objects.create(name='Web Dev')
        self.assertIsNotNone(category.slug)


class TagModelTest(TestCase):
    def test_create_tag(self):
        tag = Tag.objects.create(name='python')
        self.assertEqual(str(tag), 'python')
        self.assertIsNotNone(tag.slug)

    def test_unique_name(self):
        Tag.objects.create(name='django')
        with self.assertRaises(Exception):
            Tag.objects.create(name='django')


class LibraryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.item = LibraryItem.objects.create(
            title='Test Article',
            content='<p>Test content</p>',
            created_by=self.user,
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('library:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('library:list'))
        self.assertEqual(response.status_code, 200)

    def test_detail_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('library:detail', kwargs={'slug': self.item.slug}))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('library:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_create_library_item(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('library:create'), {
            'title': 'New Article',
            'content': '<p>New content</p>',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(LibraryItem.objects.filter(title='New Article').exists())

    def test_edit_library_item(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('library:edit', kwargs={'slug': self.item.slug}), {
            'title': 'Updated Article',
            'content': '<p>Updated content</p>',
        })
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.title, 'Updated Article')

    def test_delete_library_item(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('library:delete', kwargs={'slug': self.item.slug}))
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertFalse(self.item.is_active)

    def test_toggle_favorite(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('library:favorite', kwargs={'slug': self.item.slug}))
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertTrue(self.item.is_favorite)

    def test_gallery_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('library:gallery'))
        self.assertEqual(response.status_code, 200)

    def test_files_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('library:files'))
        self.assertEqual(response.status_code, 200)

    def test_category_list_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('library:category_list'))
        self.assertEqual(response.status_code, 200)

    def test_category_create(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('library:category_create'), {
            'name': 'New Category',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='New Category').exists())

    def test_search_filter(self):
        self.client.login(username='testuser', password='testpass')
        LibraryItem.objects.create(title='Alpha Post', content='Content', created_by=self.user)
        LibraryItem.objects.create(title='Beta Post', content='Content', created_by=self.user)
        response = self.client.get(reverse('library:list') + '?q=Alpha')
        self.assertContains(response, 'Alpha Post')
        self.assertNotContains(response, 'Beta Post')

    def test_content_type_filter(self):
        self.client.login(username='testuser', password='testpass')
        LibraryItem.objects.create(title='File Only', file='test.pdf', created_by=self.user)
        response = self.client.get(reverse('library:list') + '?content_type=article')
        self.assertContains(response, 'Test Article')
        self.assertNotContains(response, 'File Only')
