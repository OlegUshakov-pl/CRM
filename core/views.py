import os
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, FileResponse, Http404
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
    root_path = get_project_root_path()
    if root_path:
        full_path = os.path.normpath(os.path.join(root_path, file_path))
        if full_path.startswith(os.path.normpath(root_path)) and os.path.exists(full_path):
            return FileResponse(open(full_path, 'rb'), filename=os.path.basename(full_path))
    media_path = os.path.normpath(os.path.join(str(settings.MEDIA_ROOT), file_path))
    if os.path.exists(media_path):
        return FileResponse(open(media_path, 'rb'), filename=os.path.basename(media_path))
    raise Http404("File not found")


@login_required
def help_page(request):
    return render(request, 'core/help.html')
