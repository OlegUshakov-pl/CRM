import mimetypes
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from projects.models import Project
from .models import Document
from .forms import DocumentForm, CommonDocumentForm


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


@login_required
def document_create_slide(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    form = DocumentForm()
    return render(request, 'documents/document_form.html', {
        'form': form, 'project': project, 'title': 'Add Document',
    })


@login_required
def document_edit_slide(request, pk):
    document = get_object_or_404(Document, pk=pk)
    form = DocumentForm(instance=document)
    return render(request, 'documents/document_form.html', {
        'form': form, 'document': document, 'project': document.project,
        'title': 'Edit Document',
    })


@login_required
def document_save(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    form = DocumentForm(request.POST, request.FILES)
    if form.is_valid():
        document = form.save(commit=False)
        document.project = project
        document.save()
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Refresh'] = 'true'
            return response
        messages.success(request, 'Document added successfully.')
        return redirect('documents:project', project_slug=project_slug)
    return render(request, 'documents/document_form.html', {
        'form': form, 'project': project, 'title': 'Add Document',
    })


@login_required
def document_common_create_slide(request):
    form = CommonDocumentForm()
    return render(request, 'documents/document_common_form.html', {
        'form': form, 'title': 'Add Document',
    })


@login_required
def document_common_save(request):
    form = CommonDocumentForm(request.POST, request.FILES)
    if form.is_valid():
        document = form.save(commit=False)
        document.save()
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Refresh'] = 'true'
            return response
        messages.success(request, 'Document added successfully.')
        return redirect('documents:list')
    return render(request, 'documents/document_common_form.html', {
        'form': form, 'title': 'Add Document',
    })


@login_required
def document_update(request, pk):
    document = get_object_or_404(Document, pk=pk)
    form = DocumentForm(request.POST, request.FILES, instance=document)
    if form.is_valid():
        form.save()
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Refresh'] = 'true'
            return response
        messages.success(request, 'Document updated successfully.')
        return redirect('documents:project', project_slug=document.project.slug)
    return render(request, 'documents/document_form.html', {
        'form': form, 'document': document, 'project': document.project,
        'title': 'Edit Document',
    })


@login_required
def document_show(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if not document.file:
        return HttpResponse('File not found', status=404)
    file_path = document.filepath
    if not os.path.exists(file_path):
        return HttpResponse('File not found', status=404)
    content_type, _ = mimetypes.guess_type(file_path)
    return FileResponse(open(file_path, 'rb'), content_type=content_type or 'application/octet-stream')


@login_required
def document_download(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if not document.file:
        return HttpResponse('File not found', status=404)
    file_path = document.filepath
    if not os.path.exists(file_path):
        return HttpResponse('File not found', status=404)
    content_type, _ = mimetypes.guess_type(file_path)
    response = FileResponse(open(file_path, 'rb'), content_type=content_type or 'application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{document.filename}"'
    return response


@login_required
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)
    project_slug = document.project.slug
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted.')
    return redirect('documents:project', project_slug=project_slug)
