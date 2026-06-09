import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import FileResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import AIFile, AILog, ChatMessage, ChatSession
from .services import AIFileService, BrowserService, LLMService
from .services.i18n import detect_lang, t

logger = logging.getLogger(__name__)


def _get_or_create_session(user) -> ChatSession:
    session = (
        ChatSession.objects
        .filter(user=user, is_active=True)
        .order_by('-last_message_at')
        .first()
    )
    if not session:
        session = ChatSession.objects.create(user=user, title='', is_active=True)
    return session


def _save_message(session: ChatSession, role: str, content: str,
                  kind: str = 'text', payload: Dict[str, Any] = None) -> ChatMessage:
    msg = ChatMessage.objects.create(
        session=session, role=role, kind=kind, content=content, payload=payload or {},
    )
    session.last_message_at = timezone.now()
    session.save(update_fields=['last_message_at'])
    return msg


def _log(user, action: str, status: str, description: str, *,
         request_text: str = '', response_text: str = '', payload: Dict[str, Any] = None,
         duration_ms: int = 0, session: ChatSession = None):
    try:
        AILog.objects.create(
            user=user, session=session, action=action, status=status,
            description=description[:500], request_text=request_text[:4000],
            response_text=response_text[:4000], payload=payload or {}, duration_ms=duration_ms,
        )
    except Exception as e:  # noqa: BLE001
        logger.warning('Failed to write AILog: %s', e)


def _ollama_chat(text: str, model: str, user) -> Dict[str, Any]:
    """Send a message to Ollama and return the response."""
    import urllib.request
    import urllib.error
    base = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
    if not model:
        return {'ok': False, 'message': 'No model selected. Choose a model from the dropdown.'}
    payload = {
        'model': model,
        'messages': [{'role': 'user', 'content': text}],
        'stream': False,
    }
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f'{base}/api/chat',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode())
            msg = result.get('message', {}).get('content', '')
            if not msg:
                msg = 'Empty response from model.'
            return {'ok': True, 'message': msg}
    except urllib.error.URLError as e:
        return {'ok': False, 'message': f'Cannot connect to Ollama: {e}'}
    except Exception as e:
        return {'ok': False, 'message': f'Ollama error: {e}'}


@login_required
@require_GET
def panel_state(request):
    """Return current state of the chat panel (history) for the active session."""
    session = _get_or_create_session(request.user)
    msgs = session.messages.all()[:200]
    return JsonResponse({
        'session_id': session.id,
        'messages': [
            {
                'id': m.id,
                'role': m.role,
                'kind': m.kind,
                'content': m.content,
                'payload': m.payload,
                'created_at': m.created_at.isoformat(),
            } for m in msgs
        ],
        'storage_used': AIFileService(request.user).total_size(),
        'storage_quota': settings.AI_FILES_TOTAL_QUOTA,
    })


@login_required
@require_POST
def chat(request):
    """
    Single API endpoint per spec 6.2: POST {message, confirm_token?, confirm?, mode?, model?}.
    Handles: Q&A, commands, confirmations, undo, Ollama chat.
    """
    start = time.time()
    try:
        body = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON.'}, status=400)

    text = (body.get('message') or '').strip()
    confirm = bool(body.get('confirm'))
    confirm_token = body.get('confirm_token') or ''
    undo_token = body.get('undo_token') or ''
    mode = body.get('mode') or 'chat'
    model = body.get('model') or ''
    lang = detect_lang(text) if text else 'en'

    session = _get_or_create_session(request.user)
    duration_ms = 0

    if undo_token:
        ok, msg_text, lang_u = _undo_action(request.user, undo_token, lang)
        _save_message(session, 'assistant', msg_text, kind='undo')
        return JsonResponse({'ok': ok, 'message': msg_text, 'messages': _session_payload(session)})

    if not text:
        return JsonResponse({'ok': False, 'error': t('empty_message', lang)}, status=400)

    # Check for file creation intent in chat mode
    if mode == 'chat' and not confirm:
        _save_message(session, 'user', text, kind='text')
        from .services.handlers import FILE_CREATE_PATTERNS, WEB_SEARCH_PATTERNS, FIND_ON_SITE_PATTERNS, NEWS_SEARCH_PATTERNS
        import re as _re
        _is_file_create = False
        _is_search = False
        _is_find_on_site = False
        _is_news_search = False
        for _pat in FILE_CREATE_PATTERNS:
            if _re.search(_pat, text, _re.IGNORECASE | _re.UNICODE):
                _is_file_create = True
                break
        if not _is_file_create:
            for _pat in WEB_SEARCH_PATTERNS:
                if _re.search(_pat, text, _re.IGNORECASE | _re.UNICODE):
                    _is_search = True
                    break
        if not _is_file_create and not _is_search:
            for _pat in FIND_ON_SITE_PATTERNS:
                if _re.search(_pat, text, _re.IGNORECASE | _re.UNICODE):
                    _is_find_on_site = True
                    break
        if not _is_file_create and not _is_search and not _is_find_on_site:
            for _pat in NEWS_SEARCH_PATTERNS:
                if _re.search(_pat, text, _re.IGNORECASE | _re.UNICODE):
                    _is_news_search = True
                    break
        if _is_file_create or _is_search or _is_find_on_site or _is_news_search:
            llm = LLMService()
            result = llm.process(text, request.user, session=session, model=model)
            duration_ms = int((time.time() - start) * 1000)
            msg_text = result.get('message') or result.get('confirmation_text') or ''
            m = _save_message(session, 'assistant', msg_text,
                              kind='result', payload={
                                  'intent': result.get('intent'),
                                  'actions': result.get('actions', []),
                                  'payload': result.get('payload', {}),
                                  'model': model, 'mode': 'chat',
                              })
            _log(request.user, 'chat', 'ok', f'Intent via chat: {result.get("intent")}',
                 request_text=text, response_text=msg_text,
                 payload={'intent': result.get('intent')},
                 duration_ms=duration_ms, session=session)
            return JsonResponse({
                'ok': result.get('ok', True),
                'message': msg_text,
                'actions': result.get('actions', []),
                'payload': {**result.get('payload', {}), 'model': model, 'mode': 'chat'},
                'message_id': m.id,
            })

        ollama_result = _ollama_chat(text, model, request.user)
        duration_ms = int((time.time() - start) * 1000)
        m = _save_message(session, 'assistant', ollama_result['message'], kind='result',
                          payload={'model': model, 'mode': 'chat'})
        _log(request.user, 'chat', 'ok' if ollama_result['ok'] else 'error',
             f'Ollama chat ({model})',
             request_text=text, response_text=ollama_result['message'],
             payload={'model': model}, duration_ms=duration_ms, session=session)
        return JsonResponse({
            'ok': ollama_result['ok'],
            'message': ollama_result['message'],
            'actions': [],
            'payload': {'model': model, 'mode': 'chat'},
            'message_id': m.id,
        })

    # Commands mode or confirmations
    llm = LLMService()

    if not confirm:
        result = llm.process(text, request.user, session=session, model=model)
        duration_ms = int((time.time() - start) * 1000)
        kind = result.get('kind', 'text')
        _save_message(session, 'user', text, kind='text')
        msg_text = result.get('message') or result.get('confirmation_text') or ''
        m = _save_message(session, 'assistant', msg_text,
                          kind='confirmation' if result.get('needs_confirmation') else 'result',
                          payload={
                              'intent': result.get('intent'),
                              'actions': result.get('actions', []),
                              'needs_confirmation': result.get('needs_confirmation', False),
                              'confirmation_text': result.get('confirmation_text', ''),
                              'payload': result.get('payload', {}),
                              'undoable': result.get('undoable', False),
                              'undo_token': result.get('undo_token'),
                              'lang': result.get('lang', lang),
                          })
        _log(request.user, 'chat', 'ok', f'Intent: {result.get("intent") or kind}',
             request_text=text, response_text=msg_text,
             payload={'intent': result.get('intent')},
             duration_ms=duration_ms, session=session)
        return JsonResponse({
            'ok': result.get('ok', True),
            'message': msg_text,
            'needs_confirmation': result.get('needs_confirmation', False),
            'confirmation_text': result.get('confirmation_text', ''),
            'actions': result.get('actions', []),
            'payload': result.get('payload', {}),
            'undoable': result.get('undoable', False),
            'undo_token': result.get('undo_token'),
            'message_id': m.id,
        })

    # Confirmation path
    from .services import handlers as _handlers
    last = session.messages.filter(role='assistant', kind='confirmation').order_by('-created_at').first()
    if not last or not last.payload:
        return JsonResponse({'ok': False, 'error': t('no_pending', lang)})
    intent = last.payload.get('intent')
    payload = last.payload.get('payload', {})
    payload['lang'] = payload.get('lang') or last.payload.get('lang') or lang
    if not intent:
        return JsonResponse({'ok': False, 'error': t('no_intent', lang)})

    result = _handlers.perform_confirmed(intent, request.user, payload)
    duration_ms = int((time.time() - start) * 1000)
    done_lang = payload.get('lang') or lang
    if result.ok:
        msg_text = result.message or t('success', done_lang)
    else:
        msg_text = result.error or t('error_generic', done_lang, err='?')
    m = _save_message(session, 'assistant', msg_text,
                      kind='result',
                      payload={
                          'actions': result.actions,
                          'undoable': result.undoable,
                          'undo_token': result.undo_token,
                          'payload': result.payload,
                          'lang': done_lang,
                      })
    _log(request.user, 'action', 'ok' if result.ok else 'error',
         f'{intent} confirmed',
         request_text=text, response_text=msg_text,
         payload={'intent': intent, 'payload': payload, 'result': result.payload},
         duration_ms=duration_ms, session=session)
    return JsonResponse({
        'ok': result.ok,
        'message': msg_text,
        'actions': result.actions,
        'undoable': result.undoable,
        'undo_token': result.undo_token,
        'payload': result.payload,
        'message_id': m.id,
    })


def _session_payload(session: ChatSession):
    return [
        {
            'id': m.id,
            'role': m.role,
            'kind': m.kind,
            'content': m.content,
            'payload': m.payload,
            'created_at': m.created_at.isoformat(),
        }
        for m in session.messages.all()[:200]
    ]


def _undo_action(user, token: str, lang: str = 'en'):
    from .services.handlers import CONFIRMATION_HANDLERS
    if not token:
        return False, t('undo_token_missing', lang), lang
    from .models import AILog
    log = AILog.objects.filter(user=user, payload__undo_token=token).order_by('-created_at').first()
    if not log:
        return False, t('undo_not_found', lang), lang
    if (timezone.now() - log.created_at).total_seconds() > 10:
        return False, t('undo_expired', lang), lang
    payload = log.payload or {}
    intent = payload.get('intent')
    obj = payload.get('payload', {})
    target = obj.get('object')
    target_id = obj.get('id')
    deleted = False
    try:
        if target == 'project' and target_id:
            from projects.models import Project
            p = Project.objects.filter(id=target_id).first()
            if p:
                p.is_active = False
                p.save()
                deleted = True
        elif target == 'task' and target_id:
            from tasks.models import Task
            t = Task.objects.filter(id=target_id).first()
            if t:
                t.is_active = False
                t.save()
                deleted = True
        elif target == 'material' and target_id:
            from materials.models import Material
            Material.objects.filter(id=target_id).delete()
            deleted = True
        elif target == 'note' and target_id:
            from notes.models import Note
            Note.objects.filter(id=target_id).delete()
            deleted = True
    except Exception as e:  # noqa: BLE001
        return False, t('undo_error', lang, err=e), lang
    AILog.objects.create(
        user=user, action='undo', status='ok' if deleted else 'error',
        description=f'Undo {intent} #{target_id}',
        payload={'undo_token': token},
    )
    msg = t('undo_done', lang) if deleted else t('undo_failed', lang)
    return deleted, msg, lang


@login_required
@require_POST
def clear_chat(request):
    sessions = ChatSession.objects.filter(user=request.user, is_active=True)
    sessions.update(is_active=False)
    return JsonResponse({'ok': True})


@login_required
@require_GET
def ai_files(request):
    qs = AIFile.objects.filter(owner=request.user, is_active=True)
    cat = request.GET.get('category', 'all')
    if cat in ('image', 'pdf', 'document', 'other'):
        qs = qs.filter(category=cat)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(original_name__icontains=q) | Q(source_url__icontains=q))

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    used = AIFileService(request.user).total_size()
    quota = settings.AI_FILES_TOTAL_QUOTA
    from projects.models import Project
    all_projects = Project.objects.filter(is_active=True).order_by('name')
    return render(request, 'assistant/ai_files.html', {
        'page_obj': page,
        'files': page.object_list,
        'category': cat,
        'q': q,
        'storage_used': used,
        'storage_quota': quota,
        'storage_pct': int(used / quota * 100) if quota else 0,
        'all_projects': all_projects,
    })


@login_required
@require_POST
def ai_file_upload(request):
    f = request.FILES.get('file')
    svc = AIFileService(request.user)
    saved = svc.save_uploaded(f)
    if not saved:
        return JsonResponse({'ok': False, 'error': t('file_rejected', 'en')}, status=400)
    return JsonResponse({'ok': True, 'id': str(saved.id), 'name': saved.original_name})


@login_required
def ai_file_download(request, file_id):
    f = get_object_or_404(AIFile, id=file_id, owner=request.user)
    if not f.file or not os.path.exists(f.file.path):
        messages.error(request, t('file_not_found', 'en'))
        return redirect('assistant:ai_files')
    return FileResponse(open(f.file.path, 'rb'), as_attachment=True, filename=f.original_name)


@login_required
@require_POST
def ai_file_delete(request, file_id):
    f = get_object_or_404(AIFile, id=file_id, owner=request.user)
    try:
        if f.file and os.path.exists(f.file.path):
            os.remove(f.file.path)
    except OSError:
        pass
    f.is_active = False
    f.save()
    return JsonResponse({'ok': True})


@login_required
@require_POST
def ai_file_bulk_delete(request):
    ids = request.POST.getlist('ids')
    if not ids:
        return JsonResponse({'ok': False, 'error': t('no_files_selected', 'en')})
    qs = AIFile.objects.filter(id__in=ids, owner=request.user, is_active=True)
    n = 0
    for f in list(qs):
        try:
            if f.file and os.path.exists(f.file.path):
                os.remove(f.file.path)
        except OSError:
            pass
        f.is_active = False
        f.save()
        n += 1
    return JsonResponse({'ok': True, 'deleted': n})


@login_required
@require_POST
def ai_file_cleanup(request):
    days = int(request.POST.get('days', 30))
    n = AIFileService(request.user).cleanup_older_than(days)
    return JsonResponse({'ok': True, 'deleted': n})


@login_required
@require_POST
def ai_file_attach(request, file_id):
    """Attach AI File to a project document."""
    project_id = request.POST.get('project_id')
    if not project_id:
        return JsonResponse({'ok': False, 'error': t('project_id_missing', 'en')}, status=400)
    from projects.models import Project
    project = get_object_or_404(Project, id=project_id, is_active=True)
    svc = AIFileService(request.user)
    doc = svc.attach_to_project(file_id, project)
    if not doc:
        return JsonResponse({'ok': False, 'error': t('attach_failed', 'en')}, status=400)
    _log(request.user, 'file', 'ok', f'AI File {file_id} → project {project.name}',
         payload={'file_id': file_id, 'project_id': project.id})
    return JsonResponse({'ok': True, 'document_id': doc.id})


@login_required
@require_GET
def browser_preview(request, url):
    svc = BrowserService()
    if not url:
        return HttpResponseBadRequest('No url')
    rel = svc.screenshot_path(url)
    return JsonResponse({'ok': True, 'image_url': settings.MEDIA_URL + rel, 'url': url})


@login_required
@require_GET
def ollama_models(request):
    import urllib.request
    import urllib.error
    base = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
    try:
        req = urllib.request.Request(f'{base}/api/tags', method='GET')
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            models = [m.get('name', '') for m in data.get('models', [])]
    except (urllib.error.URLError, OSError, json.JSONDecodeError):
        models = []
    current = request.session.get('ollama_model', getattr(settings, 'OLLAMA_DEFAULT_MODEL', ''))
    return JsonResponse({'ok': True, 'models': models, 'current': current})


@login_required
@require_POST
def ollama_set_model(request):
    try:
        body = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON.'}, status=400)
    model = (body.get('model') or '').strip()
    if not model:
        return JsonResponse({'ok': False, 'error': 'No model specified.'}, status=400)
    request.session['ollama_model'] = model
    return JsonResponse({'ok': True, 'model': model})
