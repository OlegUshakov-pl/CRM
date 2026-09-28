import urllib.error
import urllib.request

from django.test import TestCase

from assistant.services.browser import _is_private_ip
from core.url_guard import (
    UnsafeURLError,
    _ValidatingRedirectHandler,
    validate_public_url,
    validate_service_url,
)

PUBLIC_IPV4 = 'http://93.184.216.34/'
PUBLIC_IPV6 = 'http://[2606:4700:4700::1111]/'


class ValidatePublicUrlTest(TestCase):
    def test_rejects_non_http_schemes(self):
        for url in (
            'file:///C:/Windows/win.ini',
            'file:///etc/passwd',
            'ftp://example.com/x',
            'gopher://x/',
            'data:text/html,hi',
            '',
        ):
            with self.subTest(url=url), self.assertRaises(UnsafeURLError):
                validate_public_url(url)

    def test_rejects_internal_ip_literals(self):
        for url in (
            'http://127.0.0.1/db.sqlite3',
            'http://0.0.0.0/',
            'https://192.168.1.10/',
            'http://10.0.0.5/',
            'http://172.16.0.1/',
            'http://169.254.169.254/latest/meta-data/',
            'http://[::1]/',
            'http://[fe80::1]/',
            'http://[fd00:ec2::254]/',
        ):
            with self.subTest(url=url), self.assertRaises(UnsafeURLError):
                validate_public_url(url)

    def test_rejects_hostname_resolving_to_loopback(self):
        with self.assertRaises(UnsafeURLError):
            validate_public_url('http://localhost:8000/')

    def test_allows_public_ip_literals(self):
        self.assertEqual(validate_public_url(PUBLIC_IPV4), PUBLIC_IPV4)
        self.assertEqual(validate_public_url(PUBLIC_IPV6), PUBLIC_IPV6)

    def test_requires_host(self):
        with self.assertRaises(UnsafeURLError):
            validate_public_url('http:///path-only')


class ValidateServiceUrlTest(TestCase):
    def test_allows_local_services(self):
        validate_service_url('http://localhost:11434/api/tags')
        validate_service_url('http://127.0.0.1:11434/')
        validate_service_url('http://[::1]:11434/')
        validate_service_url('http://192.168.1.20:11434/')
        validate_service_url('https://api.openai.com/v1/models')

    def test_blocks_link_local_metadata(self):
        for url in (
            'http://169.254.169.254/latest/meta-data/',
            'http://[fe80::1]/',
        ):
            with self.subTest(url=url), self.assertRaises(UnsafeURLError):
                validate_service_url(url)

    def test_blocks_non_http_schemes(self):
        with self.assertRaises(UnsafeURLError):
            validate_service_url('file:///etc/passwd')


class RedirectValidationTest(TestCase):
    def setUp(self):
        self.handler = _ValidatingRedirectHandler(validate_public_url)
        self.req = urllib.request.Request('http://example.com/page')

    def _redirect(self, newurl):
        return self.handler.redirect_request(
            self.req, None, 302, 'Found', {}, newurl
        )

    def test_blocks_file_redirect(self):
        with self.assertRaises(urllib.error.HTTPError):
            self._redirect('file:///etc/passwd')

    def test_blocks_internal_redirect(self):
        with self.assertRaises(urllib.error.HTTPError):
            self._redirect('http://127.0.0.1/secret')

    def test_allows_public_redirect(self):
        new_req = self._redirect('https://93.184.216.34/next')
        self.assertEqual(new_req.full_url, 'https://93.184.216.34/next')


class BrowserGuardTest(TestCase):
    def test_blocks_file_urls(self):
        self.assertTrue(_is_private_ip('file:///etc/passwd'))

    def test_blocks_ipv6_loopback(self):
        self.assertTrue(_is_private_ip('http://[::1]/'))

    def test_blocks_ipv4_loopback(self):
        self.assertTrue(_is_private_ip('http://127.0.0.1/'))

    def test_allows_public_host(self):
        self.assertFalse(_is_private_ip(PUBLIC_IPV4))
