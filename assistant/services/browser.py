"""
Browser service: headless fetch + screenshot.

In v1 we use stdlib + Pillow for screenshots (no chromium dependency required).
For real screenshots we'd plug in playwright/selenium; here we use a placeholder
SVG screenshot so the UX works end-to-end without external binaries.
"""
import hashlib
import logging
import os
import re
import socket
import ssl
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class FetchResult:
    ok: bool
    content: bytes = b''
    content_type: str = ''
    file_name: str = ''
    size: int = 0
    error: str = ''
    final_url: str = ''

    @property
    def is_html(self) -> bool:
        return 'html' in self.content_type.lower()

    @property
    def is_image(self) -> bool:
        ct = self.content_type.lower()
        return ct.startswith('image/')

    @property
    def is_pdf(self) -> bool:
        return 'pdf' in self.content_type.lower()


def _ensure_scheme(url: str) -> str:
    if not re.match(r'^https?://', url, re.IGNORECASE):
        return 'http://' + url
    return url


def _is_blacklisted(url: str) -> bool:
    host = urllib.parse.urlparse(url).hostname or ''
    for blocked in getattr(settings, 'AI_BROWSER_BLACKLIST', []):
        if blocked and blocked.lower() in host.lower():
            return True
    return False


class BrowserService:
    ALLOWED_DOWNLOAD_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',
                            '.pdf', '.docx', '.xlsx', '.dwg'}

    def __init__(self, timeout: Optional[int] = None):
        self.timeout = timeout or getattr(settings, 'AI_BROWSER_TIMEOUT', 20)
        self._ctx = ssl.create_default_context()
        self._ctx.check_hostname = False
        self._ctx.verify_mode = ssl.CERT_NONE

    def fetch(self, url: str) -> FetchResult:
        url = _ensure_scheme(url.strip())
        if _is_blacklisted(url):
            return FetchResult(ok=False, error='Сайт в чёрном списке.')
        try:
            socket.setdefaulttimeout(self.timeout)
            req = urllib.request.Request(url, headers={'User-Agent': 'CRM-Assistant/1.0'})
            with urllib.request.urlopen(req, timeout=self.timeout, context=self._ctx) as resp:
                content = resp.read()
                ct = resp.headers.get_content_type()
                final = resp.geturl()
        except Exception as e:  # noqa: BLE001
            logger.warning('Fetch failed for %s: %s', url, e)
            return FetchResult(ok=False, error=f'Не удалось открыть сайт: {e}')

        if len(content) > getattr(settings, 'AI_FILES_MAX_SIZE', 50 * 1024 * 1024):
            return FetchResult(ok=False, error='Файл больше 50 МБ.')

        path = urllib.parse.urlparse(final).path
        name = os.path.basename(path) or 'file'
        if '.' not in name:
            ext = {
                'text/html': '.html',
                'application/pdf': '.pdf',
                'image/png': '.png',
                'image/jpeg': '.jpg',
                'image/gif': '.gif',
                'image/webp': '.webp',
            }.get(ct, '')
            name = (name or 'file') + ext

        return FetchResult(
            ok=True,
            content=content,
            content_type=ct,
            file_name=name,
            size=len(content),
            final_url=final,
        )

    def extract_pdf_links(self, html: str, base_url: str) -> list:
        hrefs = re.findall(r'href=["\']([^"\']+\.pdf[^"\']*)["\']', html, re.IGNORECASE)
        out = []
        for h in hrefs:
            out.append(urllib.parse.urljoin(base_url, h))
        return out

    def extract_titles(self, html: str, limit: int = 5) -> list:
        titles = re.findall(r'<h[1-3][^>]*>(.*?)</h[1-3]>', html, re.IGNORECASE | re.DOTALL)
        clean = []
        for t in titles:
            t = re.sub(r'<[^>]+>', '', t).strip()
            if t:
                clean.append(t)
            if len(clean) >= limit:
                break
        if not clean:
            clean = re.findall(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        return clean[:limit]

    def screenshot(self, url: str) -> bytes:
        """
        Generate a placeholder PNG screenshot. The file is the rendered page hash
        plus a small SVG of the URL. When a real headless browser is available,
        replace this with a real screenshot.
        """
        import io
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            return self._placeholder_bytes(url)

        img = Image.new('RGB', (1280, 800), color=(245, 245, 250))
        draw = ImageDraw.Draw(img)
        draw.text((40, 40), f'CRM Browser Preview\n{url}', fill=(80, 80, 120))
        draw.rectangle((20, 20, 1260, 780), outline=(200, 200, 220), width=2)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    def _placeholder_bytes(self, url: str) -> bytes:
        # 1x1 transparent PNG fallback if Pillow is unavailable
        return (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xff'
            b'\xff?\x00\x05\xfe\x02\xfe\xa3\xee\x9c\xee\x00\x00\x00\x00IEND\xaeB`\x82'
        )

    def search_web(self, query: str, max_results: int = 8) -> list:
        """Search DuckDuckGo and return list of {title, url, snippet}."""
        import urllib.parse
        encoded = urllib.parse.quote(query)
        search_url = f'https://html.duckduckgo.com/html/?q={encoded}'
        result = self.fetch(search_url)
        if not result.ok:
            return []
        try:
            html = result.content.decode('utf-8', errors='ignore')
        except Exception:
            html = result.content.decode('utf-8', errors='ignore')

        items = []
        # Parse result blocks: <a class="result__a" href="...">title</a>
        # followed by <a class="result__snippet" ...>snippet</a>
        blocks = re.split(r'<div[^>]*class="[^"]*result[^"]*"[^>]*>', html)
        for block in blocks[1:]:
            if len(items) >= max_results:
                break
            title_match = re.search(r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]*)"[^>]*>(.*?)</a>', block, re.DOTALL)
            snippet_match = re.search(r'<a[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>', block, re.DOTALL)
            if not title_match:
                continue
            url_raw = title_match.group(1)
            title = re.sub(r'<[^>]+>', '', title_match.group(2)).strip()
            snippet = ''
            if snippet_match:
                snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()
            # DuckDuckGo wraps redirect URLs
            if url_raw.startswith('//'):
                url_raw = 'https:' + url_raw
            elif url_raw.startswith('/'):
                url_raw = 'https://duckduckgo.com' + url_raw
            # Decode redirect URL if present
            parsed = urllib.parse.urlparse(url_raw)
            if parsed.hostname and 'duckduckgo' in parsed.hostname:
                qs = urllib.parse.parse_qs(parsed.query)
                actual = qs.get('uddg', [None])[0] or qs.get('ru', [None])[0] or url_raw
            else:
                actual = url_raw
            items.append({'title': title, 'url': actual, 'snippet': snippet})
        return items

    def screenshot_path(self, url: str) -> str:
        from django.conf import settings
        h = hashlib.md5(url.encode('utf-8')).hexdigest()[:10]
        rel = os.path.join('browser', f'{h}.png')
        root = os.path.join(settings.MEDIA_ROOT, 'ai_browser')
        os.makedirs(root, exist_ok=True)
        full = os.path.join(root, f'{h}.png')
        if not os.path.exists(full) or (time.time() - os.path.getmtime(full)) > 300:
            with open(full, 'wb') as f:
                f.write(self.screenshot(url))
        return os.path.join('ai_browser', f'{h}.png')
