import os
import json
import urllib.request
import urllib.error
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.http import require_POST
from projects.models import Project
from tasks.models import Task
from companies.models import Company
from contacts.models import Contact
from notes.models import Note
from materials.models import Material
from parts.models import Part
from generator.models import Deal
from .models import AppSetting
from projects.utils import get_project_root_path


@login_required
def dashboard(request):
    context = {
        'project_count': Project.objects.filter(is_active=True).count(),
        'active_projects': Project.objects.filter(is_active=True, status='active').count(),
        'company_count': Company.objects.filter(is_active=True).count(),
        'contact_count': Contact.objects.filter(is_active=True).count(),
        'task_count': Task.objects.filter(is_active=True).count(),
        'recent_projects': Project.objects.filter(is_active=True).select_related('company').order_by('-created_at')[:6],
        'today_tasks': Task.objects.filter(is_active=True).select_related('project').order_by('-created_at'),
        'recent_notes': Note.objects.filter(is_active=True).select_related('project', 'company', 'contact').order_by('-created_at')[:5],
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def search_view(request):
    query = request.GET.get('q', '').strip()
    results = {}

    if query:
        results['projects'] = Project.objects.filter(is_active=True).filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(number__icontains=query)
        )[:10]

        results['contacts'] = Contact.objects.filter(is_active=True).filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query)
        )[:10]

        results['companies'] = Company.objects.filter(is_active=True).filter(
            Q(name__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query)
        )[:10]

        results['tasks'] = Task.objects.filter(is_active=True).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:10]

        results['notes'] = Note.objects.filter(is_active=True).filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )[:10]

        results['materials'] = Material.objects.filter(is_active=True).filter(
            Q(name__icontains=query)
        )[:10]

        results['parts'] = Part.objects.filter(is_active=True).filter(
            Q(number__icontains=query) | Q(size__icontains=query)
        )[:10]

        results['deals'] = Deal.objects.filter(is_active=True).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )[:10]

    return render(request, 'core/search_results.html', {
        'results': results,
        'query': query,
    })


@login_required
def settings_page(request):
    return render(request, 'core/settings.html')


@login_required
def save_setting(request):
    if request.method == 'POST':
        key = request.POST.get('key', '')
        value = request.POST.get('value', '')
        if key:
            AppSetting.set_value(key, value)
            return JsonResponse({'ok': True})
    return JsonResponse({'ok': False}, status=400)


@login_required
def get_setting(request, key):
    value = AppSetting.get_value(key, '')
    default = ''
    if not value and key == 'project_root_path':
        default = getattr(settings, 'PROJECT_ROOT_PATH', '')
    return JsonResponse({'key': key, 'value': value, 'default': default})


@login_required
def serve_project_file(request, file_path):
    if os.path.isabs(file_path):
        raise Http404("Invalid file path")

    root_path = get_project_root_path()
    if root_path:
        normalized_root = os.path.normpath(root_path)
        full_path = os.path.normpath(os.path.join(normalized_root, file_path))
        if full_path.startswith(normalized_root + os.sep) and os.path.exists(full_path):
            return FileResponse(open(full_path, 'rb'), filename=os.path.basename(full_path))

    media_root = os.path.normpath(str(settings.MEDIA_ROOT))
    media_path = os.path.normpath(os.path.join(media_root, file_path))
    if media_path.startswith(media_root + os.sep) and os.path.exists(media_path):
        return FileResponse(open(media_path, 'rb'), filename=os.path.basename(media_path))
    raise Http404("File not found")


@login_required
def help_page(request):
    return render(request, 'core/help.html')


PROVIDER_ENDPOINTS = {
    'anthropic': {
        'url': 'https://api.anthropic.com/v1/models',
        'headers': lambda key: {'x-api-key': key, 'anthropic-version': '2023-06-01'},
    },
    'openai': {
        'url': 'https://api.openai.com/v1/models',
        'headers': lambda key: {'Authorization': f'Bearer {key}'},
    },
    'google': {
        'url': f'https://generativelanguage.googleapis.com/v1beta/models?key=',
        'headers': lambda key: {},
        'key_in_url': True,
    },
    'mistral': {
        'url': 'https://api.mistral.ai/v1/models',
        'headers': lambda key: {'Authorization': f'Bearer {key}'},
    },
    'groq': {
        'url': 'https://api.groq.com/openai/v1/models',
        'headers': lambda key: {'Authorization': f'Bearer {key}'},
    },
    'deepseek': {
        'url': 'https://api.deepseek.com/models',
        'headers': lambda key: {'Authorization': f'Bearer {key}'},
    },
    'openrouter': {
        'url': 'https://openrouter.ai/api/v1/models',
        'headers': lambda key: {'Authorization': f'Bearer {key}'},
    },
}


def _normalize_models(provider, raw_data):
    models = []
    if provider == 'anthropic':
        for m in raw_data.get('data', []):
            models.append({'id': m.get('id', ''), 'name': m.get('display_name', m.get('id', ''))})
    elif provider == 'openai':
        for m in raw_data.get('data', []):
            models.append({'id': m.get('id', ''), 'name': m.get('id', '')})
    elif provider == 'google':
        for m in raw_data.get('models', []):
            full_name = m.get('name', '')
            model_id = full_name.replace('models/', '') if full_name.startswith('models/') else full_name
            models.append({'id': model_id, 'name': m.get('displayName', model_id)})
    elif provider == 'mistral':
        for m in raw_data.get('data', []):
            models.append({'id': m.get('id', ''), 'name': m.get('name', m.get('id', ''))})
    elif provider == 'groq':
        for m in raw_data.get('data', []):
            models.append({'id': m.get('id', ''), 'name': m.get('id', '')})
    elif provider == 'deepseek':
        for m in raw_data.get('data', []):
            models.append({'id': m.get('id', ''), 'name': m.get('id', '')})
    elif provider == 'openrouter':
        for m in raw_data.get('data', []):
            models.append({'id': m.get('id', ''), 'name': m.get('name', m.get('id', ''))})
    return models


@login_required
@require_POST
def ai_fetch_models(request):
    try:
        body = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON.'}, status=400)

    provider = body.get('provider', '')
    api_key = body.get('api_key', '')
    base_url = body.get('base_url', 'http://localhost:11434')

    if provider == 'ollama':
        url = f'{base_url}/api/tags'
        headers = {}
        req = urllib.request.Request(url, headers=headers, method='GET')
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = json.loads(resp.read().decode())
                models = []
                for m in raw.get('models', []):
                    models.append({'id': m.get('model', ''), 'name': m.get('name', m.get('model', ''))})
                return JsonResponse({'ok': True, 'models': models})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)})

    if provider not in PROVIDER_ENDPOINTS:
        return JsonResponse({'ok': False, 'error': f'Unknown provider: {provider}'}, status=400)

    if not api_key:
        return JsonResponse({'ok': False, 'error': 'API key is required.'}, status=400)

    endpoint = PROVIDER_ENDPOINTS[provider]
    url = endpoint['url']
    if endpoint.get('key_in_url'):
        url += api_key
    headers = endpoint['headers'](api_key)

    req = urllib.request.Request(url, headers=headers, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = json.loads(resp.read().decode())
            models = _normalize_models(provider, raw)
            return JsonResponse({'ok': True, 'models': models})
    except urllib.error.HTTPError as e:
        error_body = ''
        try:
            error_body = e.read().decode()[:500]
        except Exception:
            pass
        return JsonResponse({'ok': False, 'error': f'HTTP {e.code}: {error_body or e.reason}'})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})
