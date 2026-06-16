import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme
from projects.models import Project
from projects.utils import ensure_project_subfolder, sanitize_folder_name, get_subfolder_name, get_project_root_path, cleanup_empty_dirs
from core.models import log_activity
from .models import Document, Category
from .forms import DocumentForm, CommonDocumentForm, CategoryForm


@login_required
def document_category_list(request):
    from django.db.models import Count
    type_counts = Document.objects.values('file_type').annotate(count=Count('id'))
    count_map = {c['file_type']: c['count'] for c in type_counts}
    categories = []
    for choice_value, choice_label in Document.FILE_TYPE_CHOICES:
        categories.append({'value': choice_value, 'label': choice_label, 'count': count_map.get(choice_value, 0)})
    custom_categories = Category.objects.all()
    return render(request, 'documents/documents_category.html', {'categories': categories, 'custom_categories': custom_categories})


@login_required
def document_category_detail(request, file_type):
    valid_values = [c[0] for c in Document.FILE_TYPE_CHOICES]
    if file_type not in valid_values:
        raise Http404("Invalid category")
    label = dict(Document.FILE_TYPE_CHOICES).get(file_type, file_type)
    documents = Document.objects.filter(file_type=file_type).select_related('project')
    return render(request, 'documents/documents_category_detail.html', {
        'documents': documents, 'category_label': label, 'category_value': file_type,
    })


@login_required
def document_list(request):
    documents = Document.objects.select_related('project').all()
    query = request.GET.get('q', '')
    type_filter = request.GET.get('type', '')
    sort = request.GET.get('sort', 'created_desc')
    if query:
        documents = documents.filter(number__icontains=query)
    if type_filter:
        documents = documents.filter(file_type=type_filter)
    if sort == 'type':
        documents = documents.order_by('file_type')
    elif sort == 'size':
        documents = documents.order_by('size')
    elif sort == 'size_desc':
        documents = documents.order_by('-size')
    elif sort == 'created':
        documents = documents.order_by('created_at')
    elif sort == 'project':
        documents = documents.order_by('project__name')
    else:
        documents = documents.order_by('-created_at')
    paginator = Paginator(documents, 20)
    page = request.GET.get('page', 1)
    documents_page = paginator.get_page(page)
    return render(request, 'documents/documents_list.html', {
        'documents': documents_page, 'query': query,
        'current_type': type_filter, 'current_sort': sort, 'total_count': paginator.count,
    })


@login_required
def document_project(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    documents = Document.objects.filter(project=project)
    sort = request.GET.get('sort', 'created_desc')
    if sort == 'type':
        documents = documents.order_by('file_type')
    elif sort == 'size':
        documents = documents.order_by('size')
    elif sort == 'size_desc':
        documents = documents.order_by('-size')
    elif sort == 'created':
        documents = documents.order_by('created_at')
    else:
        documents = documents.order_by('-created_at')
    return render(request, 'documents/documents_project.html', {
        'project': project, 'documents': documents, 'current_sort': sort,
    })


@login_required
def document_projects(request):
    projects = Project.objects.filter(is_active=True, documents__isnull=False).order_by('-created_at').distinct()
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
    projects = Project.objects.filter(is_active=True)
    return render(request, 'documents/document_form.html', {
        'form': form, 'document': document, 'project': document.project, 'projects': projects,
        'title': 'Edit Document',
    })


@login_required
def document_save(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    form = DocumentForm(request.POST, request.FILES)
    if form.is_valid():
        file_type = form.cleaned_data.get('file_type', 'other')
        up_files = request.FILES.getlist('file')
        if up_files and project.number:
            from documents.models import get_project_folder_name
            project_folder = get_project_folder_name(project)
            subfolder_map = {
                'drawings': get_subfolder_name(project.number, 'subfolder_drawings', 'drawings'),
                'models_3d': get_subfolder_name(project.number, 'subfolder_models', 'models'),
                'documents': get_subfolder_name(project.number, 'subfolder_documents', 'documents'),
                'photos': get_subfolder_name(project.number, 'subfolder_documents', 'documents'),
                'other': get_subfolder_name(project.number, 'subfolder_documents', 'documents'),
            }
            subfolder = subfolder_map.get(file_type, get_subfolder_name(project.number, 'subfolder_documents', 'documents'))
            root_path = get_project_root_path()
            if root_path:
                os.makedirs(os.path.join(root_path, project_folder, subfolder), exist_ok=True)
        if up_files:
            for f in up_files:
                if f:
                    Document.objects.create(project=project, number=form.cleaned_data.get('number', ''), file=f, file_type=file_type)
        else:
            Document.objects.create(project=project, number=form.cleaned_data.get('number', ''), file_type=file_type)
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Refresh'] = 'true'
            return response
        messages.success(request, 'Document(s) added successfully.')
        return redirect('documents:project', project_slug=project_slug)
    return render(request, 'documents/document_form.html', {'form': form, 'project': project, 'title': 'Add Document'})


@login_required
def document_common_create_slide(request):
    form = CommonDocumentForm()
    return render(request, 'documents/document_common_form.html', {'form': form, 'title': 'Add Document'})


@login_required
def document_common_save(request):
    form = CommonDocumentForm(request.POST, request.FILES)
    if form.is_valid():
        project = form.cleaned_data.get('project')
        file_type = form.cleaned_data.get('file_type', 'other')
        up_files = request.FILES.getlist('file')
        if up_files and project and project.number:
            from documents.models import get_project_folder_name
            project_folder = get_project_folder_name(project)
            subfolder_map = {
                'drawings': get_subfolder_name(project.number, 'subfolder_drawings', 'drawings'),
                'models_3d': get_subfolder_name(project.number, 'subfolder_models', 'models'),
                'documents': get_subfolder_name(project.number, 'subfolder_documents', 'documents'),
                'photos': get_subfolder_name(project.number, 'subfolder_documents', 'documents'),
                'other': get_subfolder_name(project.number, 'subfolder_documents', 'documents'),
            }
            subfolder = subfolder_map.get(file_type, get_subfolder_name(project.number, 'subfolder_documents', 'documents'))
            root_path = get_project_root_path()
            if root_path:
                os.makedirs(os.path.join(root_path, project_folder, subfolder), exist_ok=True)
        if up_files:
            for f in up_files:
                if f:
                    Document.objects.create(project=project, number=form.cleaned_data.get('number', ''), file=f, file_type=file_type)
        else:
            Document.objects.create(project=project, number=form.cleaned_data.get('number', ''), file_type=file_type)
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Refresh'] = 'true'
            return response
        messages.success(request, 'Document added successfully.')
        return redirect('documents:list')
    return render(request, 'documents/document_common_form.html', {'form': form, 'title': 'Add Document'})


@login_required
def document_update(request, pk):
    document = get_object_or_404(Document, pk=pk)
    old_file = document.file
    form = DocumentForm(request.POST, request.FILES, instance=document)
    if form.is_valid():
        doc = form.save(commit=False)
        up_files = request.FILES.getlist('file')
        if up_files:
            for f in up_files:
                if f:
                    doc.file = f
                    break
        if not doc.file and old_file:
            doc.file = old_file
        doc.save()
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Refresh'] = 'true'
            return response
        messages.success(request, 'Document updated successfully.')
        if doc.project:
            return redirect('documents:project', project_slug=doc.project.slug)
        return redirect('documents:list')
    return render(request, 'documents/document_form.html', {'form': form, 'document': document, 'project': document.project, 'title': 'Edit Document'})


@login_required
def document_show(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if not document.file:
        return HttpResponse('File not found', status=404)
    file_path = document.file.path
    if not os.path.exists(file_path):
        return HttpResponse('File not found', status=404)
    return FileResponse(open(file_path, 'rb'), filename=document.filename)


@login_required
def document_view(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if not document.file:
        return HttpResponse('File not found', status=404)
    file_path = document.file.path
    if not os.path.exists(file_path):
        return HttpResponse('File not found', status=404)
    ext = os.path.splitext(document.filename)[1].lower()
    is_image = ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg')
    is_pdf = ext == '.pdf'
    is_text = ext in ('.txt', '.md', '.csv', '.json', '.xml', '.yml', '.yaml', '.html', '.css', '.js', '.py', '.log', '.cfg', '.ini', '.conf')
    photos = []
    text_content = None
    if is_image:
        photos = Document.objects.filter(
            project=document.project, file_type='photos'
        ).exclude(pk=document.pk).order_by('-created_at')[:10]
    elif is_text:
        file_path = document.filepath
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                text_content = f.read()
        except Exception:
            text_content = None
    return render(request, 'documents/document_view.html', {
        'doc': document,
        'is_image': is_image,
        'is_pdf': is_pdf,
        'is_text': is_text,
        'photos': photos,
        'text_content': text_content,
        'file_url': reverse('documents:download', kwargs={'pk': document.pk}),
    })


@login_required
def document_download(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if not document.file:
        return HttpResponse('File not found', status=404)
    file_path = document.file.path
    if not os.path.exists(file_path):
        return HttpResponse('File not found', status=404)
    from urllib.parse import quote
    safe_filename = quote(document.filename)
    response = FileResponse(open(file_path, 'rb'), filename=document.filename)
    response['Content-Disposition'] = f"attachment; filename*=UTF-8''{safe_filename}"
    return response


@login_required
def document_common_latest(request):
    from django.utils import timezone
    from datetime import timedelta
    documents = Document.objects.filter(created_at__gte=timezone.now() - timedelta(minutes=10)).select_related('project').order_by('-created_at')[:5]
    return render(request, 'documents/common_latest.html', {'documents': documents})


@login_required
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        if document.file:
            file_dir = os.path.dirname(document.file.path)
            document.file.delete(save=False)
            cleanup_empty_dirs(file_dir)
        document.delete()
        messages.success(request, 'Document deleted.')
    referer = request.META.get('HTTP_REFERER', '')
    if referer and url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}):
        return redirect(referer)
    return redirect(reverse('documents:list'))


@login_required
def category_create_slide(request):
    form = CategoryForm()
    return render(request, 'documents/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def category_save(request):
    form = CategoryForm(request.POST)
    if form.is_valid():
        category = form.save()
        log_activity(request.user, 'created', f'Category {category.name} created', category)
        if request.headers.get('HX-Request'):
            response = HttpResponse('<script>closeSlideOver()</script>')
            response['HX-Refresh'] = 'true'
            return response
        messages.success(request, 'Category created.')
        return redirect('documents:category_list')
    return render(request, 'documents/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    log_activity(request.user, 'deleted', f'Category {category.name} deleted', category)
    category.delete()
    if request.headers.get('HX-Request'):
        response = HttpResponse('<script>closeSlideOver()</script>')
        response['HX-Refresh'] = 'true'
        return response
    messages.success(request, 'Category deleted.')
    return redirect('documents:category_list')
