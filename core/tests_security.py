from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory, override_settings

from .models import generate_unique_slug, Activity
from .context_processors import app_version


class GenerateUniqueSlugTest(TestCase):
    def test_basic_slug_generation(self):
        from projects.models import Project
        user = User.objects.create_user(username='slugtest', password='testpass')
        p = Project(name='My Test Project', created_by=user)
        p.save()
        self.assertEqual(p.slug, 'my-test-project')

    def test_slug_collision_increments_counter(self):
        from projects.models import Project
        user = User.objects.create_user(username='slugtest2', password='testpass')
        p1 = Project(name='Duplicate Name', created_by=user)
        p1.save()
        p2 = Project(name='Duplicate Name', created_by=user)
        p2.save()
        self.assertEqual(p1.slug, 'duplicate-name')
        self.assertEqual(p2.slug, 'duplicate-name-1')

    def test_empty_source_field_defaults_to_untitled(self):
        from projects.models import Project
        user = User.objects.create_user(username='slugtest3', password='testpass')
        p = Project(name='', created_by=user)
        p.save()
        self.assertEqual(p.slug, 'untitled')


class ActivityIndexTest(TestCase):
    def test_activity_has_composite_index(self):
        indexes = Activity._meta.indexes
        self.assertTrue(len(indexes) >= 1)
        fields = indexes[0].fields
        self.assertEqual(fields, ['content_type', 'object_id'])


class SSRFProtectionTest(TestCase):
    def test_is_private_ip_blocks_localhost(self):
        from assistant.services.browser import _is_private_ip
        self.assertTrue(_is_private_ip('http://127.0.0.1/'))

    def test_is_private_ip_blocks_10_x(self):
        from assistant.services.browser import _is_private_ip
        self.assertTrue(_is_private_ip('http://10.0.0.1/'))

    def test_is_private_ip_blocks_172_16(self):
        from assistant.services.browser import _is_private_ip
        self.assertTrue(_is_private_ip('http://172.16.0.1/'))

    def test_is_private_ip_blocks_192_168(self):
        from assistant.services.browser import _is_private_ip
        self.assertTrue(_is_private_ip('http://192.168.1.1/'))

    def test_is_private_ip_allows_public(self):
        from assistant.services.browser import _is_private_ip
        self.assertFalse(_is_private_ip('https://www.google.com'))

    def test_is_private_ip_blocks_empty_host(self):
        from assistant.services.browser import _is_private_ip
        self.assertTrue(_is_private_ip(''))


class OpenRedirectProtectionTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(ALLOWED_HOSTS=['localhost', 'localhost:8000'])
    def test_safe_redirect_blocks_external_referer(self):
        from projects.views import _safe_redirect
        request = self.factory.post('/projects/', HTTP_REFERER='https://evil.com/')
        request.META['HTTP_HOST'] = 'localhost:8000'
        response = _safe_redirect(request, '/fallback/')
        self.assertEqual(response.url, '/fallback/')

    @override_settings(ALLOWED_HOSTS=['localhost', 'localhost:8000'])
    def test_safe_redirect_allows_internal_referer(self):
        from projects.views import _safe_redirect
        request = self.factory.post('/projects/', HTTP_REFERER='http://localhost:8000/projects/edit/')
        request.META['HTTP_HOST'] = 'localhost:8000'
        response = _safe_redirect(request, '/fallback/')
        self.assertEqual(response.url, 'http://localhost:8000/projects/edit/')

    @override_settings(ALLOWED_HOSTS=['localhost', 'localhost:8000'])
    def test_safe_redirect_without_referer_goes_to_fallback(self):
        from projects.views import _safe_redirect
        request = self.factory.post('/projects/')
        request.META['HTTP_HOST'] = 'localhost:8000'
        response = _safe_redirect(request, '/fallback/')
        self.assertEqual(response.url, '/fallback/')


class CascadeToSetNullTest(TestCase):
    def test_material_project_set_null_on_delete(self):
        from projects.models import Project
        from materials.models import Material
        user = User.objects.create_user(username='cascade1', password='testpass')
        project = Project(name='Cascade Test', created_by=user)
        project.save()
        material = Material(name='Bolt', project=project, quantity=10)
        material.save()
        project.delete()
        material.refresh_from_db()
        self.assertIsNone(material.project)

    def test_part_project_set_null_on_delete(self):
        from projects.models import Project
        from parts.models import Part
        user = User.objects.create_user(username='cascade2', password='testpass')
        project = Project(name='Cascade Test 2', created_by=user)
        project.save()
        part = Part(number='P001', project=project)
        part.save()
        project.delete()
        part.refresh_from_db()
        self.assertIsNone(part.project)


class MinValueValidatorTest(TestCase):
    def test_material_quantity_rejects_negative(self):
        from materials.models import Material
        m = Material(name='Test', quantity=-1)
        with self.assertRaises(ValidationError):
            m.full_clean()

    def test_material_unit_price_rejects_negative(self):
        from materials.models import Material
        m = Material(name='Test', quantity=1, unit_price=-5)
        with self.assertRaises(ValidationError):
            m.full_clean()

    def test_project_budget_rejects_negative(self):
        from projects.models import Project
        user = User.objects.create_user(username='val1', password='testpass')
        p = Project(name='Test', budget=-100, created_by=user)
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_deal_value_rejects_negative(self):
        from generator.models import Deal
        user = User.objects.create_user(username='val2', password='testpass')
        d = Deal(name='Test', value=-50, created_by=user)
        with self.assertRaises(ValidationError):
            d.full_clean()


class SettingsSecurityTest(TestCase):
    @override_settings(DEBUG=False)
    def test_session_cookie_secure_when_not_debug(self):
        from django.conf import settings
        settings.SESSION_COOKIE_SECURE = True
        self.assertTrue(settings.SESSION_COOKIE_SECURE)

    def test_secret_key_reads_from_env(self):
        import os
        os.environ['DJANGO_SECRET_KEY'] = 'test-secret-key-12345'
        try:
            from importlib import reload
            import config.settings
            reload(config.settings)
            self.assertEqual(config.settings.SECRET_KEY, 'test-secret-key-12345')
        finally:
            os.environ.pop('DJANGO_SECRET_KEY', None)
            reload(config.settings)
