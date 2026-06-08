"""
Concrete command handlers for the 10 CRM commands in v1.

Each handler:
- Receives a CommandContext with parsed params.
- For write actions that are critical -> returns needs_confirmation=True.
- Logs into Activity with description prefixed by 'AI Chat' (per spec 1.1).
- Marks the result as undoable when possible (per spec 1.2).
"""
import logging
import os
import re
import uuid
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from .commands import CommandContext, CommandResult
from .i18n import detect_lang, t

logger = logging.getLogger(__name__)


AI_TAG = 'AI Chat'


def _find_project(name: str, lang: str = 'en'):
    from projects.models import Project
    if not name:
        return None
    return (
        Project.objects.filter(is_active=True)
        .filter(Q(name__icontains=name) | Q(number__iexact=name) | Q(slug__iexact=slugify(name)))
        .first()
    )


def _find_contact(name: str, lang: str = 'en'):
    from contacts.models import Contact
    if not name:
        return None
    parts = name.split()
    qs = Contact.objects.filter(is_active=True)
    for p in parts:
        qs = qs.filter(Q(first_name__icontains=p) | Q(last_name__icontains=p) | Q(email__icontains=p))
    return qs.first()


def _log_activity(user, action: str, description: str, obj: Any = None):
    try:
        from core.models import log_activity
        log_activity(user, action, f'{AI_TAG}: {description}', obj)
    except Exception as e:  # noqa: BLE001
        logger.warning('Activity log failed: %s', e)


def _undo_token() -> str:
    return uuid.uuid4().hex


def _confirm_create_project(ctx: CommandContext) -> CommandResult:
    lang = detect_lang(ctx.text)
    name = ctx.params.get('name') or ctx.params.get('project_name') or ''
    number = ctx.params.get('number') or ctx.params.get('project_number') or ''
    start = ctx.params.get('date') or ctx.params.get('start_date') or date.today().isoformat()
    if not name:
        return CommandResult(ok=False, error=t('project_missing_name', lang))

    full = (f'{number}, {name}' if number else name)
    text = t('project_confirm', lang, full=full, date=start)
    return CommandResult(
        ok=True,
        needs_confirmation=True,
        confirmation_text=text,
        message=text,
        payload={'intent': 'create_project', 'number': number, 'name': name, 'start_date': start, 'lang': lang},
    )


def _do_create_project(user, payload: Dict[str, Any]) -> CommandResult:
    from projects.models import Project

    lang = payload.get('lang') or 'en'
    name = payload.get('name') or 'Untitled'
    number = payload.get('number') or ''
    start = payload.get('start_date') or None

    p = Project(name=name, number=number or None, status='planning', created_by=user)
    if start:
        try:
            p.start_date = datetime.strptime(start, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            pass
    p.save()
    _log_activity(user, 'created', f'Project "{p.name}"', p)

    return CommandResult(
        ok=True,
        message=t('project_done', lang, name=p.name),
        undoable=True,
        undo_token=_undo_token(),
        payload={
            'object': 'project',
            'id': p.id,
            'name': p.name,
            'number': p.number,
            'slug': p.slug,
        },
        actions=[
            {'type': 'open_url', 'label': t('project_open', lang), 'url': f'/projects/{p.slug}/'},
        ],
    )


def _confirm_create_task(ctx: CommandContext) -> CommandResult:
    lang = detect_lang(ctx.text)
    title = ctx.params.get('title') or ctx.params.get('text') or ctx.params.get('task') or ''
    due = ctx.params.get('date') or ctx.params.get('due_date') or ''
    project_name = ctx.params.get('project') or ctx.params.get('project_name') or ''

    if not title:
        return CommandResult(ok=False, error=t('task_missing_title', lang))

    project = _find_project(project_name) if project_name else None
    if not due:
        due = date.today().isoformat()
    project_part = t('task_project_part', lang, name=project.name) if project else ''

    text = t('task_confirm', lang, title=title, date=due, project_part=project_part)
    return CommandResult(
        ok=True,
        needs_confirmation=True,
        confirmation_text=text,
        message=text,
        payload={
            'intent': 'create_task',
            'title': title,
            'due_date': due,
            'project_id': project.id if project else None,
            'lang': lang,
        },
    )


def _do_create_task(user, payload: Dict[str, Any]) -> CommandResult:
    from tasks.models import Task

    lang = payload.get('lang') or 'en'
    title = payload.get('title') or 'Untitled'
    due_raw = payload.get('due_date')
    project_id = payload.get('project_id')

    due = None
    if due_raw:
        try:
            due = datetime.strptime(due_raw, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            due = None

    t_obj = Task(title=title, status='todo', priority='medium', due_date=due, created_by=user)
    if project_id:
        t_obj.project_id = project_id
    t_obj.save()
    _log_activity(user, 'created', f'Task "{t_obj.title}"', t_obj)

    return CommandResult(
        ok=True,
        message=t('task_done', lang, title=t_obj.title, due=str(t_obj.due_date) if t_obj.due_date else '—'),
        undoable=True,
        undo_token=_undo_token(),
        payload={'object': 'task', 'id': t_obj.id, 'title': t_obj.title},
        actions=[{'type': 'open_url', 'label': t('task_open', lang), 'url': '/tasks/'}],
    )


def _handle_find_contact(ctx: CommandContext) -> CommandResult:
    lang = detect_lang(ctx.text)
    name = (ctx.params.get('name') or ctx.params.get('contact_name') or '').strip()
    if not name:
        return CommandResult(ok=False, error=t('contact_missing_name', lang))

    contact = _find_contact(name)
    if not contact:
        return CommandResult(ok=False, message=t('contact_not_found', lang, name=name), error='not_found')

    return CommandResult(
        ok=True,
        message=t('contact_found', lang, name=contact.get_full_name()),
        payload={
            'object': 'contact',
            'id': contact.id,
            'name': contact.get_full_name(),
            'phone': contact.phone or '—',
            'email': contact.email or '—',
            'position': contact.position or '—',
            'company': contact.company.name if contact.company else '—',
        },
        actions=[
            {'type': 'open_url', 'label': t('project_open', lang), 'url': f'/contacts/{contact.id}/'},
        ],
    )


def _confirm_add_material(ctx: CommandContext) -> CommandResult:
    lang = detect_lang(ctx.text)
    name = ctx.params.get('name') or ctx.params.get('material_name') or ''
    qty = ctx.params.get('quantity') or ctx.params.get('qty') or 1
    project_name = ctx.params.get('project') or ctx.params.get('project_name') or ''
    unit = ctx.params.get('unit') or 'pcs'

    if not name:
        return CommandResult(ok=False, error=t('material_missing_name', lang))
    project = _find_project(project_name)
    if not project:
        return CommandResult(ok=False, error=t('project_not_found', lang, name=project_name))

    text = t('material_confirm', lang, name=name, qty=qty, unit=unit, project=project.name)
    return CommandResult(
        ok=True,
        needs_confirmation=True,
        confirmation_text=text,
        message=text,
        payload={
            'intent': 'create_material',
            'name': name,
            'quantity': qty,
            'unit': unit,
            'project_id': project.id,
            'lang': lang,
        },
    )


def _do_create_material(user, payload: Dict[str, Any]) -> CommandResult:
    from materials.models import Material

    lang = payload.get('lang') or 'en'
    m = Material(
        project_id=payload.get('project_id'),
        name=payload.get('name') or 'Untitled',
        quantity=payload.get('quantity') or 1,
        unit=payload.get('unit') or 'pcs',
        created_by=user,
    )
    m.save()
    _log_activity(user, 'created', f'Material "{m.name}"', m)

    return CommandResult(
        ok=True,
        message=t('material_done', lang, name=m.name),
        undoable=True,
        undo_token=_undo_token(),
        payload={'object': 'material', 'id': m.id, 'name': m.name},
    )


def _confirm_upload_document(ctx: CommandContext) -> CommandResult:
    lang = detect_lang(ctx.text)
    file_name = ctx.params.get('file_name') or ctx.params.get('filename') or ''
    project_name = ctx.params.get('project') or ctx.params.get('project_name') or ''
    project = _find_project(project_name)
    if not project:
        return CommandResult(ok=False, error=t('project_not_found', lang, name=project_name))

    text = t('doc_confirm', lang, file=file_name or '(file not selected)', project=project.name)
    return CommandResult(
        ok=True,
        needs_confirmation=True,
        confirmation_text=text,
        message=text,
        payload={
            'intent': 'upload_document',
            'file_name': file_name,
            'project_id': project.id,
            'project_slug': project.slug,
            'lang': lang,
        },
    )


def _handle_show_drawings(ctx: CommandContext) -> CommandResult:
    lang = detect_lang(ctx.text)
    project_name = ctx.params.get('project') or ctx.params.get('project_name') or ''
    project = _find_project(project_name)
    if not project:
        return CommandResult(ok=False, error=t('project_not_found', lang, name=project_name))

    from parts.models import Part
    parts = project.parts.filter(is_active=True).order_by('number')
    if not parts.exists():
        return CommandResult(ok=True, message=t('drawings_none', lang, name=project.name))

    items = [
        {
            'number': p.number,
            'category': p.category.name if p.category else '',
            'size': p.size or '',
            'rev': p.rev or '',
            'file_url': p.file.url if p.file else None,
        }
        for p in parts
    ]
    return CommandResult(
        ok=True,
        message=t('drawings_list', lang, name=project.name, count=len(items)),
        payload={'drawings': items, 'project_slug': project.slug, 'project_name': project.name},
        actions=[{'type': 'open_url', 'label': t('drawings_open_project', lang),
                  'url': f'/projects/{project.slug}/'}],
    )


def _handle_show_company(ctx: CommandContext) -> CommandResult:
    lang = detect_lang(ctx.text)
    project_name = ctx.params.get('project') or ctx.params.get('project_name') or ''
    project = _find_project(project_name)
    if not project:
        return CommandResult(ok=False, error=t('project_not_found', lang, name=project_name))
    if not project.company:
        return CommandResult(ok=True, message=t('company_missing', lang, name=project.name))

    c = project.company
    return CommandResult(
        ok=True,
        message=t('company_found', lang, project=project.name, company=c.name),
        payload={
            'object': 'company',
            'id': c.id,
            'name': c.name,
            'phone': c.phone or '—',
            'email': c.email or '—',
            'website': c.website or '—',
        },
        actions=[{'type': 'open_url', 'label': t('company_open', lang), 'url': f'/companies/{c.id}/'}],
    )


def _confirm_create_note(ctx: CommandContext) -> CommandResult:
    lang = detect_lang(ctx.text)
    title = ctx.params.get('title') or ctx.params.get('text') or ctx.params.get('content') or ''
    project_name = ctx.params.get('project') or ctx.params.get('project_name') or ''
    project = _find_project(project_name) if project_name else None

    if not title:
        return CommandResult(ok=False, error=t('note_missing_title', lang))

    project_part = t('note_project_part', lang, name=project.name) if project else ''
    text = t('note_confirm', lang, title=title, project_part=project_part)
    return CommandResult(
        ok=True,
        needs_confirmation=True,
        confirmation_text=text,
        message=text,
        payload={
            'intent': 'create_note',
            'title': title,
            'project_id': project.id if project else None,
            'lang': lang,
        },
    )


def _do_create_note(user, payload: Dict[str, Any]) -> CommandResult:
    from notes.models import Note

    lang = payload.get('lang') or 'en'
    n = Note(
        title=payload.get('title') or 'Untitled',
        content=payload.get('title') or '',
        date=date.today(),
        project_id=payload.get('project_id') or None,
        created_by=user,
    )
    n.save()
    _log_activity(user, 'created', f'Note "{n.title}"', n)
    return CommandResult(
        ok=True,
        message=t('note_done', lang),
        undoable=True,
        undo_token=_undo_token(),
        payload={'object': 'note', 'id': n.id, 'title': n.title},
    )


# === Browser / AI Files handlers (Modules 3-4) ===

def _handle_open_browser(ctx: CommandContext) -> CommandResult:
    lang = detect_lang(ctx.text)
    url = ctx.params.get('url') or ''
    if not url:
        return CommandResult(ok=False, error=t('browser_missing_url', lang))

    from .browser import BrowserService, _ensure_scheme
    bs = BrowserService()
    try:
        fetch = bs.fetch(url)
    except Exception as e:  # noqa: BLE001
        return CommandResult(ok=False, error=t('browser_fetch_error', lang, err=e))
    if not fetch.ok:
        return CommandResult(ok=False, error=fetch.error or t('browser_open_error', lang))

    titles: list = []
    if fetch.is_html:
        try:
            html = fetch.content.decode(fetch.content_type.split('charset=')[-1] if 'charset=' in fetch.content_type else 'utf-8', errors='ignore')
        except Exception:
            html = fetch.content.decode('utf-8', errors='ignore')
        titles = bs.extract_titles(html, limit=5)
        pdfs = bs.extract_pdf_links(html, fetch.final_url)
    else:
        pdfs = []

    safe_url = _ensure_scheme(url)
    rel = bs.screenshot_path(url)
    pdf_part = t('browser_pdf_part', lang, n=len(pdfs)) if pdfs else ''

    return CommandResult(
        ok=True,
        message=t('browser_done', lang, url=safe_url, titles=len(titles), pdfs=pdf_part),
        payload={
            'object': 'browser',
            'url': safe_url,
            'final_url': fetch.final_url,
            'titles': titles,
            'pdf_links': pdfs,
            'image_url': settings.MEDIA_URL + rel,
        },
        actions=[{'type': 'open_url', 'label': t('browser_open_new_tab', lang), 'url': safe_url}],
    )


def _handle_download_file(ctx: CommandContext) -> CommandResult:
    lang = detect_lang(ctx.text)
    from .browser import BrowserService
    from .files import AIFileService

    url = ctx.params.get('url') or ''
    if not url:
        return CommandResult(ok=False, error=t('download_missing_url', lang))
    try:
        bs = BrowserService()
        result = bs.fetch(url)
    except Exception as e:  # noqa: BLE001
        return CommandResult(ok=False, error=t('download_error', lang, err=e))

    if not result.ok:
        return CommandResult(ok=False, error=result.error or t('download_failed', lang))

    fs = AIFileService(ctx.user)
    saved = fs.save_downloaded(result)
    if not saved:
        return CommandResult(ok=False, error=t('download_blocked', lang))

    return CommandResult(
        ok=True,
        message=t('download_done', lang, name=saved.original_name, size=saved.size),
        payload={
            'object': 'ai_file',
            'id': str(saved.id),
            'name': saved.original_name,
            'size': saved.size,
            'category': saved.category,
            'source_url': saved.source_url,
        },
        actions=[
            {'type': 'attach_to_project', 'label': t('download_attach_action', lang), 'file_id': str(saved.id)},
        ],
    )


def _handle_web_search(ctx: CommandContext) -> CommandResult:
    lang = detect_lang(ctx.text)
    from .browser import BrowserService

    query = ctx.params.get('query') or ctx.params.get('q') or ''
    if not query:
        return CommandResult(ok=False, error=t('search_missing_query', lang))

    bs = BrowserService()
    try:
        results = bs.search_web(query)
    except Exception as e:  # noqa: BLE001
        logger.warning('Web search failed: %s', e)
        return CommandResult(ok=False, error=t('search_failed', lang, err=e))

    if not results:
        return CommandResult(ok=True, message=t('search_no_results', lang, query=query))

    msg = t('search_done', lang, query=query, count=len(results))
    actions = []
    for r in results[:5]:
        actions.append({'type': 'open_url', 'label': r['title'][:60], 'url': r['url']})

    return CommandResult(
        ok=True,
        message=msg,
        payload={
            'object': 'search',
            'query': query,
            'results': results,
        },
        actions=actions,
    )


def _handle_find_on_site(ctx: CommandContext) -> CommandResult:
    from .browser import BrowserService
    lang = detect_lang(ctx.text)

    file_type = (ctx.params.get('type') or '').lower()
    site_url = ctx.params.get('site') or ctx.params.get('url') or ''
    name_filter = (ctx.params.get('name') or '').lower()

    if not file_type or not site_url:
        return CommandResult(ok=False, error=t('find_on_site_missing_params', lang))

    file_type = 'pdf' if file_type in ('pdf',) else 'image' if file_type in ('picture', 'image', 'photo', 'pic') else 'other'

    bs = BrowserService()
    try:
        result = bs.fetch(site_url)
    except Exception as e:
        return CommandResult(ok=False, error=t('find_on_site_fetch_error', lang, err=e))

    if not result.ok or not result.is_html:
        return CommandResult(ok=False, error=t('find_on_site_not_html', lang))

    try:
        html = result.content.decode('utf-8', errors='ignore')
    except Exception:
        html = result.content.decode('utf-8', errors='ignore')

    import urllib.parse

    if file_type == 'pdf':
        all_links = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)
        matches = []
        for href in all_links:
            if '.pdf' not in href.lower():
                continue
            full_url = urllib.parse.urljoin(result.final_url, href)
            fname = urllib.parse.urlparse(full_url).path.split('/')[-1] or full_url
            if name_filter and name_filter not in fname.lower() and name_filter not in full_url.lower():
                continue
            matches.append({'title': fname, 'url': full_url})
    else:
        all_links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>.*?</a>', html, re.DOTALL)
        img_tags = re.findall(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', html, re.IGNORECASE)
        all_srcs = []
        for src in img_tags:
            full_url = urllib.parse.urljoin(result.final_url, src)
            fname = urllib.parse.urlparse(full_url).path.split('/')[-1] or full_url
            if name_filter and name_filter not in fname.lower() and name_filter not in full_url.lower():
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'):
                all_srcs.append({'title': fname, 'url': full_url})
        matches = all_srcs[:20]

    if not matches:
        return CommandResult(ok=True, message=t('find_on_site_none', lang, type=file_type, site=site_url))

    type_label = 'PDF' if file_type == 'pdf' else 'images'
    msg = t('find_on_site_done', lang, type=type_label, site=site_url, count=len(matches))
    actions = []
    for m in matches[:10]:
        label = m['title'][:60]
        actions.append({'type': 'open_url', 'label': label, 'url': m['url']})

    return CommandResult(
        ok=True,
        message=msg,
        payload={
            'object': 'site_files',
            'type': file_type,
            'site': site_url,
            'results': matches[:20],
        },
        actions=actions,
    )


def _handle_create_file(ctx: CommandContext) -> CommandResult:
    lang = detect_lang(ctx.text)
    from .files import AIFileService

    filename = ctx.params.get('filename') or ctx.params.get('name') or ''
    content = ctx.params.get('content') or ''
    description = ctx.params.get('description') or ''

    if not filename:
        return CommandResult(ok=False, error=t('file_create_missing_name', lang))

    if not content and description:
        try:
            import urllib.request
            import json
            base = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
            model = ctx.model or ''
            if model:
                payload = {
                    'model': model,
                    'messages': [{'role': 'user', 'content': f'Generate content for {description}. Return only the raw content, no explanations.'}],
                    'stream': False,
                }
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(
                    f'{base}/api/chat', data=data,
                    headers={'Content-Type': 'application/json'}, method='POST',
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    result = json.loads(resp.read().decode())
                    content = result.get('message', {}).get('content', '')
        except Exception as e:
            logger.warning('Ollama generation failed: %s', e)
            return CommandResult(ok=False, error=t('file_create_generation_failed', lang, err=e))

    if not content:
        return CommandResult(ok=False, error=t('file_create_missing_content', lang))

    fs = AIFileService(ctx.user)
    saved = fs.save_content(filename, content)
    if not saved:
        return CommandResult(ok=False, error=t('file_create_rejected', lang))

    return CommandResult(
        ok=True,
        message=t('file_create_done', lang, name=filename, size=saved.size),
        payload={
            'object': 'ai_file',
            'id': str(saved.id),
            'name': saved.original_name,
            'size': saved.size,
            'category': saved.category,
        },
        actions=[
            {'type': 'attach_to_project', 'label': t('download_attach_action', lang), 'file_id': str(saved.id)},
        ],
    )


# === Patterns (English only) ===

PROJECT_CREATE_PATTERNS = [
    r'create\s+project\s+(?P<number>[A-Za-z0-9_\-]+)[\s,]+(?P<name>.+?)(?:\s+(?:on|by|for)\s+(?P<date>\S+))?$',
    r'create\s+project\s+(?P<name>.+?)(?:\s+(?:on|by|for)\s+(?P<date>\S+))?$',
    r'new\s+project[\s:]+(?P<name>.+?)(?:\s+(?:number|#)\s*(?P<number>[A-Za-z0-9_\-]+))?(?:\s+(?:on|for)\s+(?P<date>\S+))?$',
]

TASK_CREATE_PATTERNS = [
    r'add\s+task\s+(?P<title>.+?)\s+(?:on|by|for)\s+(?P<date>\S+)$',
    r'add\s+task\s+(?P<title>.+?)$',
    r'new\s+task[\s:]+(?P<title>.+?)(?:\s+(?:on|by|for)\s+(?P<date>\S+))?$',
    r'create\s+task\s+(?P<title>.+?)(?:\s+(?:on|by|for)\s+(?P<date>\S+))?$',
]

CONTACT_FIND_PATTERNS = [
    r'find\s+contact\s+(?P<name>.+?)$',
    r'search\s+contact\s+(?P<name>.+?)$',
    r'show\s+contact\s+(?P<name>.+?)$',
]

MATERIAL_ADD_PATTERNS = [
    r'add\s+material\s+(?P<name>.+?)\s+(?P<quantity>\d+(?:[.,]\d+)?)\s*(?P<unit>pcs|kg|m|m2|m3|l|set)?\s+to\s+(?:project\s+)?(?P<project>.+?)$',
]

DOCUMENT_UPLOAD_PATTERNS = [
    r'upload\s+(?P<file_name>[\w\.\-]+)\s+to\s+(?:project\s+)?(?P<project>.+?)$',
]

DRAWINGS_SHOW_PATTERNS = [
    r'show\s+(?:all\s+)?drawings\s+(?:of|for|by)\s+(?:project\s+)?(?P<project>.+?)$',
    r'list\s+drawings\s+(?:of|for)\s+(?:project\s+)?(?P<project>.+?)$',
]

COMPANY_SHOW_PATTERNS = [
    r'who\s+is\s+(?:the\s+)?company\s+(?:of|for)\s+(?:project\s+)?(?P<project>.+?)$',
    r"what(?:'s|\s+is)\s+(?:the\s+)?company\s+(?:of|for)\s+(?:project\s+)?(?P<project>.+?)$",
    r'show\s+company\s+(?:of|for)\s+(?:project\s+)?(?P<project>.+?)$',
]

NOTE_CREATE_PATTERNS = [
    r'create\s+note\s+(?P<title>.+?)\s+(?:to|for)\s+(?:project\s+)?(?P<project>.+?)$',
    r'create\s+note\s+(?P<title>.+?)$',
    r'add\s+note\s+(?P<title>.+?)(?:\s+(?:to|for)\s+(?:project\s+)?(?P<project>.+?))?$',
]

BROWSER_OPEN_PATTERNS = [
    r'open\s+(?P<url>(?:https?://)?[\w\.\-]+\.[a-z]{2,}[^\s]*)',
    r'show\s+(?:me\s+)?(?:website|site)\s+(?P<url>(?:https?://)?[\w\.\-]+\.[a-z]{2,}[^\s]*)',
]

DOWNLOAD_FILE_PATTERNS = [
    r'download\s+(?:file|image|pdf|document)\s+from\s+(?P<url>(?:https?://)?[\S]+)',
    r'get\s+(?:file|image|pdf)\s+from\s+(?P<url>(?:https?://)?[\S]+)',
]

FILE_CREATE_PATTERNS = [
    r'create\s+file\s+(?P<filename>\S+)\s+with\s+content\s+(?P<content>.+?)$',
    r'make\s+file\s+(?P<filename>\S+)\s+with\s+content\s+(?P<content>.+?)$',
    r'generate\s+(?:file\s+)?(?P<filename>\S+)\s+(?:with\s+content\s+)?(?P<content>.+?)$',
    r'create\s+file\s+(?P<filename>\S+?)(?:\s+for\s+(?P<description>.+?))?$',
    r'make\s+file\s+(?P<filename>\S+?)(?:\s+for\s+(?P<description>.+?))?$',
    r'create\s+(?P<filename>\S+\.\w+)(?:\s+with\s+content\s+(?P<content>.+?))?$',
    r'write\s+file\s+(?P<filename>\S+)(?:\s+with\s+content\s+(?P<content>.+?))?$',
]

WEB_SEARCH_PATTERNS = [
    r'search\s+(?:for\s+)?(?P<query>.+?)$',
    r'search\s+internet\s+(?:for\s+)?(?P<query>.+?)$',
    r'find\s+(?:information\s+)?(?:about\s+)?(?P<query>.+?)\s+on\s+the\s+internet$',
    r'find\s+(?:information\s+)?(?:about\s+)?(?P<query>.+?)$',
    r'look\s+up\s+(?P<query>.+?)$',
    r'what\s+is\s+(?P<query>.+?)\?*$',
    r'who\s+is\s+(?P<query>.+?)\?*$',
]

FIND_ON_SITE_PATTERNS = [
    r'find\s+(?P<type>pdf|picture|image|photo|pic)\s+on\s+(?:site|website)\s+(?P<site>\S+)$',
    r'find\s+(?P<type>pdf|picture|image|photo|pic)\s+with\s+name\s+(?P<name>\S+)\s+on\s+(?:site|website)\s+(?P<site>\S+)$',
    r'find\s+(?P<type>pdf|picture|image|photo|pic)\s+(?P<name>\S+)\s+on\s+(?:site|website)\s+(?P<site>\S+)$',
    r'find\s+(?P<type>pdf|picture|image|photo|pic)s?\s+on\s+(?:site|website)\s+(?P<site>\S+)$',
]


def register_all(registry):
    registry.register('create_project', PROJECT_CREATE_PATTERNS, _confirm_create_project,
                      description='Create a project')
    registry.register('create_task', TASK_CREATE_PATTERNS, _confirm_create_task,
                      description='Add a task')
    registry.register('find_contact', CONTACT_FIND_PATTERNS, _handle_find_contact,
                      description='Find a contact')
    registry.register('create_material', MATERIAL_ADD_PATTERNS, _confirm_add_material,
                      description='Add a material')
    registry.register('upload_document', DOCUMENT_UPLOAD_PATTERNS, _confirm_upload_document,
                      description='Upload a document')
    registry.register('show_drawings', DRAWINGS_SHOW_PATTERNS, _handle_show_drawings,
                      description='Show project drawings')
    registry.register('show_company', COMPANY_SHOW_PATTERNS, _handle_show_company,
                      description='Show project company')
    registry.register('create_note', NOTE_CREATE_PATTERNS, _confirm_create_note,
                      description='Create a note')
    registry.register('browser_open', BROWSER_OPEN_PATTERNS, _handle_open_browser,
                      description='Open a website')
    registry.register('download_file', DOWNLOAD_FILE_PATTERNS, _handle_download_file,
                      description='Download a file from the internet')
    registry.register('create_file', FILE_CREATE_PATTERNS, _handle_create_file,
                      description='Create a file with content')
    registry.register('web_search', WEB_SEARCH_PATTERNS, _handle_web_search,
                      description='Search the internet')
    registry.register('find_on_site', FIND_ON_SITE_PATTERNS, _handle_find_on_site,
                      description='Find PDFs or images on a website')


CONFIRMATION_HANDLERS = {
    'create_project': _do_create_project,
    'create_task': _do_create_task,
    'create_material': _do_create_material,
    'create_note': _do_create_note,
    'browser_open': _handle_open_browser,
}


def perform_confirmed(intent: str, user, payload: Dict[str, Any]) -> CommandResult:
    handler = CONFIRMATION_HANDLERS.get(intent)
    if handler is None:
        lang = payload.get('lang') or 'en'
        return CommandResult(ok=False, error=t('no_executor', lang, intent=intent))
    return handler(user, payload)
