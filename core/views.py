from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from projects.models import Project
from tasks.models import Task
from contacts.models import Company, Contact
from notes.models import Note


@login_required
def dashboard(request):
    context = {
        'project_count': Project.objects.filter(is_active=True).count(),
        'active_projects': Project.objects.filter(is_active=True, status='active').count(),
        'company_count': Company.objects.filter(is_active=True).count(),
        'contact_count': Contact.objects.filter(is_active=True).count(),
        'task_count': Task.objects.filter(is_active=True).count(),
        'recent_projects': Project.objects.filter(is_active=True).select_related('company').order_by('-created_at')[:6],
        'today_tasks': Task.objects.filter(is_active=True, status__in=['todo', 'in_progress']).select_related('project').order_by('-created_at')[:8],
        'recent_notes': Note.objects.filter(is_active=True).select_related('project', 'company', 'contact').order_by('-created_at')[:5],
    }
    return render(request, 'core/dashboard.html', context)
