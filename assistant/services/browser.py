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


def _is_private_ip(url: str) -> bool:
    """Check if URL resolves to a private/reserved IP address (SSRF protection)."""
    host = urllib.parse.urlparse(url).hostname or ''
    if not host:
        return True
    try:
        addr = socket.getaddrinfo(host, None)
        for family, _, _, _, sockaddr in addr:
            ip = sockaddr[0]
            parts = ip.split('.')
            if len(parts) == 4:
                a, b = int(parts[0]), int(parts[1])
                if a == 10:
                    return True
                if a == 172 and 16 <= b <= 31:
                    return True
                if a == 192 and b == 168:
                    return True
                if a == 127:
                    return True
                if a == 0:
                    return True
                if a == 169 and b == 254:
                    return True
    except (socket.gaierror, ValueError):
        return True
    return False


class BrowserService:
    ALLOWED_DOWNLOAD_EXT = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',
                            '.pdf', '.docx', '.xlsx', '.dwg'}

    def __init__(self, timeout: Optional[int] = None):
        self.timeout = timeout or getattr(settings, 'AI_BROWSER_TIMEOUT', 20)
        self._ctx = ssl.create_default_context()

    def fetch(self, url: str) -> FetchResult:
        url = _ensure_scheme(url.strip())
        if _is_blacklisted(url):
            return FetchResult(ok=False, error='Сайт в чёрном списке.')
        if _is_private_ip(url):
            return FetchResult(ok=False, error='Доступ к внутренним ресурсам запрещён.')
        try:
            socket.setdefaulttimeout(self.timeout)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'})
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
        from html.parser import HTMLParser

        class PDFLinkFinder(HTMLParser):
            def __init__(self):
                super().__init__()
                self.links = []

            def handle_starttag(self, tag, attrs):
                if tag != 'a':
                    return
                attrs_dict = dict(attrs)
                href = attrs_dict.get('href', '')
                if '.pdf' in href.lower():
                    self.links.append(href)

        parser = PDFLinkFinder()
        parser.feed(html)
        return [urllib.parse.urljoin(base_url, h) for h in parser.links]

    def extract_titles(self, html: str, limit: int = 5) -> list:
        from html.parser import HTMLParser

        class TitleFinder(HTMLParser):
            def __init__(self, limit):
                super().__init__()
                self.limit = limit
                self.titles = []
                self._in_title_tag = False
                self._in_heading = False
                self._current_text = []
                self._heading_tags = {'h1', 'h2', 'h3'}
                self._tag_stack = []

            def handle_starttag(self, tag, attrs):
                self._tag_stack.append(tag)
                if tag == 'title':
                    self._in_title_tag = True
                    self._current_text = []
                elif tag in self._heading_tags:
                    self._in_heading = True
                    self._current_text = []

            def handle_endtag(self, tag):
                if self._tag_stack and self._tag_stack[-1] == tag:
                    self._tag_stack.pop()
                if tag == 'title' and self._in_title_tag:
                    self._in_title_tag = False
                    text = ''.join(self._current_text).strip()
                    if text and not self.titles:
                        self.titles.append(text)
                elif tag in self._heading_tags and self._in_heading:
                    self._in_heading = False
                    text = ''.join(self._current_text).strip()
                    if text and len(self.titles) < self.limit:
                        self.titles.append(text)

            def handle_data(self, data):
                if self._in_title_tag or self._in_heading:
                    self._current_text.append(data)

        parser = TitleFinder(limit)
        parser.feed(html)
        return parser.titles[:limit]

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

    def _parse_ddg_results(self, html: str, max_results: int) -> list:
        from html.parser import HTMLParser

        class DDGResultParser(HTMLParser):
            def __init__(self, max_results):
                super().__init__()
                self.max_results = max_results
                self.items = []
                self._current = None
                self._in_result = False
                self._in_title = False
                self._in_snippet = False
                self._skip_link = False
                self._text_parts = []

            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs)
                cls = attrs_dict.get('class', '')
                if 'result' in cls.split():
                    if self._in_result and self._current:
                        self._finish_item()
                    if len(self.items) >= self.max_results:
                        return
                    self._in_result = True
                    self._current = {'title': '', 'url': '', 'snippet': ''}
                if not self._in_result:
                    return
                if tag == 'a' and 'result__a' in cls.split():
                    self._in_title = True
                    self._text_parts = []
                    self._current['url'] = attrs_dict.get('href', '')
                if tag == 'a' and 'result__snippet' in cls.split():
                    self._in_snippet = True
                    self._text_parts = []

            def handle_endtag(self, tag):
                if not self._in_result:
                    return
                if self._in_title and tag == 'a':
                    self._in_title = False
                    self._current['title'] = ''.join(self._text_parts).strip()
                if self._in_snippet and tag == 'a':
                    self._in_snippet = False
                    self._current['snippet'] = ''.join(self._text_parts).strip()

            def handle_data(self, data):
                if self._in_title or self._in_snippet:
                    self._text_parts.append(data)

            def _finish_item(self):
                if self._current and self._current['url']:
                    url = self._current['url']
                    if url.startswith('//'):
                        url = 'https:' + url
                    elif url.startswith('/'):
                        url = 'https://duckduckgo.com' + url
                    parsed = urllib.parse.urlparse(url)
                    if parsed.hostname and 'duckduckgo' in parsed.hostname:
                        qs = urllib.parse.parse_qs(parsed.query)
                        actual = qs.get('uddg', [None])[0] or qs.get('ru', [None])[0] or url
                    else:
                        actual = url
                    self._current['url'] = actual
                    self.items.append(self._current)
                self._current = None

        parser = DDGResultParser(max_results)
        parser.feed(html)
        if parser._in_result and parser._current:
            parser._finish_item()
        return parser.items[:max_results]

    def search_web(self, query: str, max_results: int = 8) -> list:
        """Search DuckDuckGo and return list of {title, url, snippet}."""
        try:
            from duckduckgo_search import DDGS
            ddgs = DDGS()
            raw = list(ddgs.text(query, max_results=max_results))
            return [{'title': r.get('title', ''), 'url': r.get('href', ''), 'snippet': r.get('body', '')} for r in raw]
        except Exception as exc:
            logger.warning('DDGS text search failed, falling back to HTML: %s', exc)
        import urllib.parse as _up
        encoded = _up.quote(query)
        search_url = f'https://html.duckduckgo.com/html/?q={encoded}'
        result = self.fetch(search_url)
        if not result.ok:
            return []
        try:
            html = result.content.decode('utf-8', errors='ignore')
        except Exception:
            html = result.content.decode('utf-8', errors='ignore')
        return self._parse_ddg_results(html, max_results)

    def search_news(self, query: str, max_results: int = 8, site: str = '') -> list:
        """Search DuckDuckGo news and return list of {title, url, snippet}."""
        q = f'{query} site:{site}' if site else query
        try:
            from duckduckgo_search import DDGS
            ddgs = DDGS()
            raw = list(ddgs.news(q, max_results=max_results))
            key = 'url' if 'url' in (raw[0] if raw else {}) else 'link'
            return [{'title': r.get('title', ''), 'url': r.get(key, ''), 'snippet': r.get('body', '')} for r in raw]
        except Exception as exc:
            logger.warning('DDGS news search failed, falling back to HTML: %s', exc)
        import urllib.parse as _up
        encoded = _up.quote(q)
        search_url = f'https://html.duckduckgo.com/html/?q={encoded}&iar=news'
        result = self.fetch(search_url)
        if not result.ok:
            return []
        try:
            html = result.content.decode('utf-8', errors='ignore')
        except Exception:
            html = result.content.decode('utf-8', errors='ignore')
        return self._parse_ddg_results(html, max_results)

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
