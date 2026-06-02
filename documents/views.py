from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from projects.models import Project
from .models import Document


@login_required
def document_list(request):
    documents = Document.objects.select_related('project').all()
    query = request.GET.get('q', '')
    type_filter = request.GET.get('type', '')
    if query:
        documents = documents.filter(number__icontains=query)
    if type_filter:
        documents = documents.filter(file_type=type_filter)
    paginator = Paginator(documents, 20)
    page = request.GET.get('page', 1)
    documents_page = paginator.get_page(page)
    return render(request, 'documents/documents_list.html', {
        'documents': documents_page, 'query': query,
        'current_type': type_filter, 'total_count': paginator.count,
    })


@login_required
def document_project(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    documents = Document.objects.filter(project=project)
    return render(request, 'documents/documents_project.html', {
        'project': project, 'documents': documents,
    })


@login_required
def document_projects(request):
    projects = Project.objects.filter(is_active=True).order_by('-created_at')
    query = request.GET.get('q', '')
    if query:
        projects = projects.filter(name__icontains=query)
    paginator = Paginator(projects, 12)
    page = request.GET.get('page', 1)
    projects_page = paginator.get_page(page)
    return render(request, 'documents/documents_projects.html', {
        'projects': projects_page, 'query': query,
    })
