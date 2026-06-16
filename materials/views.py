import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Category, Material, MaterialFile
from .forms import CategoryForm, MaterialForm, CommonMaterialForm, MaterialFileForm, ALLOWED_MATERIAL_EXTENSIONS
from projects.models import Project
from projects.utils import get_project_root_path, sanitize_folder_name
from documents.models import get_project_folder_name
from core.models import log_activity


@login_required
def material_common_latest(request):
    from django.utils import timezone
    from datetime import timedelta
    materials = Material.objects.filter(is_active=True, created_at__gte=timezone.now() - timedelta(minutes=10)).select_related('category').order_by('-created_at')[:5]
    return render(request, 'materials/common_latest.html', {'materials': materials})


@login_required
def material_main(request):
    projects = Project.objects.filter(is_active=True, materials__isnull=False).distinct().order_by('-created_at')
    query = request.GET.get('q', '')
    if query:
        projects = projects.filter(name__icontains=query)
    paginator = Paginator(projects, 12)
    page = request.GET.get('page', 1)
    projects_page = paginator.get_page(page)
    return render(request, 'materials/materials_main.html', {'projects': projects_page, 'query': query})


SORT_OPTIONS = [
    ('name', 'Name'),
    ('category__name', 'Category'),
    ('quantity', 'Qty'),
    ('unit_price', 'Price'),
    ('created_at', 'Date Created'),
]


def apply_sorting(queryset, request):
    sort_params = request.GET.getlist('sort')
    order_params = request.GET.getlist('order')
    sort = sort_params[-1] if sort_params else 'created_at'
    order = order_params[-1] if order_params else 'desc'
    valid_fields = [f[0] for f in SORT_OPTIONS]
    if sort not in valid_fields:
        sort = 'created_at'
    if order not in ('asc', 'desc'):
        order = 'desc'
    sort_label = dict(SORT_OPTIONS).get(sort, 'Sort')
    if order == 'asc':
        queryset = queryset.order_by(sort)
    else:
        queryset = queryset.order_by(f'-{sort}')
    return queryset, sort, order, sort_label


@login_required
def material_common(request):
    materials = Material.objects.filter(is_active=True).select_related('project', 'category')
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    if query:
        materials = materials.filter(name__icontains=query)
    if category_filter:
        materials = materials.filter(category_id=category_filter)
    materials, sort, order, sort_label = apply_sorting(materials, request)
    categories = Category.objects.all()
    paginator = Paginator(materials, 20)
    page = request.GET.get('page', 1)
    materials_page = paginator.get_page(page)
    context = {
        'materials': materials_page, 'query': query, 'total_count': paginator.count,
        'sort_options': SORT_OPTIONS, 'current_sort': sort, 'current_order': order,
        'current_sort_label': sort_label, 'current_page': page,
        'categories': categories, 'current_category': category_filter,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'materials/partials/material_list_content.html', context)
    return render(request, 'materials/materials_common.html', context)


@login_required
def material_page(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    materials = Material.objects.filter(project=project, is_active=True).select_related('category')
    materials, sort, order, sort_label = apply_sorting(materials, request)
    return render(request, 'materials/material_list.html', {
        'project': project, 'materials': materials,
        'sort_options': SORT_OPTIONS, 'current_sort': sort, 'current_order': order,
        'current_sort_label': sort_label,
    })


@login_required
def material_create(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    form = MaterialForm()
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        up_files = request.FILES.getlist('files')
        if form.is_valid():
            material = form.save(commit=False)
            material.project = project
            material.created_by = request.user
            if not material.name and up_files:
                material.name = os.path.splitext(up_files[0].name)[0]
            material.save()
            _handle_material_files(material, up_files)
            log_activity(request.user, 'created', f'Material "{material.name}" in "{project.name}"', material)
            if request.headers.get('HX-Request'):
                response = HttpResponse('<script>closeSlideOver()</script>')
                response['HX-Refresh'] = 'true'
                return response
            messages.success(request, 'Material added successfully.')
            return redirect('materials:page', project_slug=project_slug)
    return render(request, 'materials/material_form.html', {'form': form, 'project': project, 'title': 'Add Material'})


@login_required
def material_edit(request, slug):
    material = get_object_or_404(Material, slug=slug)
    form = MaterialForm(instance=material)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            _handle_material_files(material, request.FILES.getlist('files'))
            log_activity(request.user, 'updated', f'Material "{material.name}"')
            if request.headers.get('HX-Request'):
                response = HttpResponse('<script>closeSlideOver()</script>')
                response['HX-Refresh'] = 'true'
                return response
            messages.success(request, 'Material updated successfully.')
            return redirect('materials:page', project_slug=material.project.slug)
    return render(request, 'materials/material_form.html', {'form': form, 'project': material.project, 'title': 'Edit Material', 'material': material})


@login_required
def material_delete(request, slug):
    material = get_object_or_404(Material.objects.select_related('project').filter(is_active=True), slug=slug)
    project_slug = material.project.slug
    if request.method == 'POST':
        material.is_active = False
        material.save()
        log_activity(request.user, 'deleted', f'Material "{material.name}"')
        messages.success(request, 'Material deleted successfully.')
    return redirect('projects:detail', slug=project_slug)


@login_required
def material_create_slide(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    form = MaterialForm()
    return render(request, 'materials/material_form.html', {'form': form, 'project': project, 'title': 'Add Material'})


@login_required
def material_edit_slide(request, slug):
    material = get_object_or_404(Material, slug=slug)
    form = MaterialForm(instance=material)
    return render(request, 'materials/material_form.html', {'form': form, 'project': material.project, 'title': 'Edit Material', 'material': material})


@login_required
def category_create_slide(request):
    form = CategoryForm()
    return render(request, 'materials/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def category_save(request):
    form = CategoryForm(request.POST)
    if form.is_valid():
        form.save()
        response = HttpResponse()
        response['HX-Refresh'] = 'true'
        return response
    return render(request, 'materials/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def common_create_slide(request):
    form = CommonMaterialForm()
    projects = Project.objects.filter(is_active=True)
    return render(request, 'materials/common_material_form.html', {'form': form, 'projects': projects, 'title': 'Add Material'})


@login_required
def common_save(request):
    form = CommonMaterialForm(request.POST)
    if form.is_valid():
        material = form.save(commit=False)
        material.created_by = request.user
        project_id = request.POST.get('project')
        if project_id:
            material.project = get_object_or_404(Project, id=project_id)
        material.save()
        return HttpResponse('<script>closeSlideOver(); refreshSection("materials")</script>')
    projects = Project.objects.filter(is_active=True)
    return render(request, 'materials/common_material_form.html', {'form': form, 'projects': projects, 'title': 'Add Material'})


@login_required
def common_delete(request, slug):
    material = get_object_or_404(Material.objects.filter(is_active=True), slug=slug)
    if request.method == 'POST':
        material.is_active = False
        material.save()
        log_activity(request.user, 'deleted', f'Material "{material.name}"')
        messages.success(request, 'Material deleted.')
    return redirect('materials:common')


@login_required
def category_list(request):
    categories = Category.objects.all()
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('materials:category_list')
    return render(request, 'materials/category_list.html', {'categories': categories, 'form': form})


@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    materials = Material.objects.filter(category=category, is_active=True).select_related('project')
    sort = request.GET.get('sort', 'name')
    if sort == 'category':
        materials = materials.order_by('category__name')
    elif sort == 'qty':
        materials = materials.order_by('quantity')
    elif sort == 'price':
        materials = materials.order_by('unit_price')
    elif sort == 'created':
        materials = materials.order_by('-created_at')
    else:
        materials = materials.order_by('name')
    return render(request, 'materials/category_detail.html', {'category': category, 'materials': materials, 'current_sort': sort})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Category "{category.name}" deleted.')
    return redirect('materials:category_list')


def _handle_material_files(material, files):
    if not files:
        return
    for f in files:
        if f:
            ext = os.path.splitext(f.name)[1].lower()
            if ext in ALLOWED_MATERIAL_EXTENSIONS:
                MaterialFile.objects.create(material=material, file=f)


@login_required
def material_file_upload_slide(request, material_slug):
    material = get_object_or_404(Material, slug=material_slug)
    form = MaterialFileForm()
    files = material.files.all()
    return render(request, 'materials/material_file_form.html', {
        'form': form, 'material': material, 'files': files, 'title': 'Upload Files',
    })


@login_required
def material_file_save(request, material_slug):
    material = get_object_or_404(Material, slug=material_slug)
    form = MaterialFileForm(request.POST, request.FILES)
    if form.is_valid():
        up_files = request.FILES.getlist('file')
        _handle_material_files(material, up_files)
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Refresh'] = 'true'
            return response
        messages.success(request, 'File(s) uploaded successfully.')
    else:
        if request.headers.get('HX-Request'):
            return render(request, 'materials/material_file_form.html', {
                'form': form, 'material': material, 'files': material.files.all(), 'title': 'Upload Files',
            })
    return redirect('materials:page', project_slug=material.project.slug)


@login_required
def material_file_delete(request, pk):
    material_file = get_object_or_404(MaterialFile, pk=pk)
    material_slug = material_file.material.slug
    project_slug = material_file.material.project.slug if material_file.material.project else None
    if request.method == 'POST':
        if material_file.file:
            material_file.file.delete(save=False)
        material_file.delete()
        messages.success(request, 'File deleted.')
    if request.headers.get('HX-Request'):
        response = HttpResponse()
        response['HX-Refresh'] = 'true'
        return response
    if project_slug:
        return redirect('materials:page', project_slug=project_slug)
    return redirect('materials:common')


@login_required
def material_file_download(request, pk):
    material_file = get_object_or_404(MaterialFile, pk=pk)
    if not material_file.file:
        return HttpResponse('File not found', status=404)
    file_path = material_file.file.path
    if not os.path.exists(file_path):
        return HttpResponse('File not found', status=404)
    from urllib.parse import quote
    safe_filename = quote(material_file.original_name or material_file.filename)
    response = FileResponse(open(file_path, 'rb'), filename=material_file.original_name or material_file.filename)
    response['Content-Disposition'] = f"attachment; filename*=UTF-8''{safe_filename}"
    return response


@login_required
def material_file_view(request, pk):
    material_file = get_object_or_404(MaterialFile, pk=pk)
    if not material_file.file:
        return HttpResponse('File not found', status=404)
    file_path = material_file.file.path
    if not os.path.exists(file_path):
        return HttpResponse('File not found', status=404)
    ext = os.path.splitext(material_file.original_name or material_file.filename)[1].lower()
    is_image = ext in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg')
    is_pdf = ext == '.pdf'
    is_text = ext in ('.txt', '.md', '.csv', '.json', '.xml', '.yml', '.yaml', '.html', '.css', '.js', '.py', '.log', '.cfg', '.ini', '.conf')
    text_content = None
    if is_text:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                text_content = f.read()
        except Exception:
            text_content = None
    return render(request, 'materials/material_file_view.html', {
        'material_file': material_file,
        'material': material_file.material,
        'is_image': is_image,
        'is_pdf': is_pdf,
        'is_text': is_text,
        'text_content': text_content,
        'file_url': material_file.file.url,
    })
