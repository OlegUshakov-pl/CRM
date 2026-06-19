import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from core.models import log_activity
from projects.utils import ensure_project_subfolder, sanitize_folder_name, cleanup_empty_dirs
from .models import Part, Category
from .forms import PartForm, CommonPartForm, CategoryForm


def _number_from_file(number, f):
    if not number and f:
        return os.path.splitext(f.name)[0]
    return number or ''


def _format_size(size_bytes):
    if not size_bytes:
        return ''
    size_bytes = int(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f'{size_bytes:.1f} {unit}' if unit != 'B' else f'{size_bytes} B'
        size_bytes /= 1024
    return f'{size_bytes:.1f} TB'


@login_required
def part_common_latest(request):
    from django.utils import timezone
    from datetime import timedelta
    parts = Part.objects.filter(is_active=True, created_at__gte=timezone.now() - timedelta(minutes=10)).select_related('category').order_by('-created_at')[:5]
    return render(request, 'parts/common_latest.html', {'parts': parts})


@login_required
def part_list(request):
    parts = Part.objects.select_related('category', 'project').all()
    parts, sort, order, sort_label = apply_part_sorting(parts, request)
    context = {
        'parts': parts,
        'sort_options': PART_SORT_OPTIONS, 'current_sort': sort, 'current_order': order,
        'current_sort_label': sort_label,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'parts/partials/part_list_content.html', context)
    return render(request, 'parts/part_list.html', context)


@login_required
def part_projects(request):
    from django.db.models import Q
    from projects.models import Project
    exclude_q = Q()
    for ext in Part.MODEL_EXTENSIONS + Part.DXF_EXTENSIONS:
        exclude_q |= Q(file__iendswith=ext)
    drawing_project_ids = Part.objects.exclude(exclude_q).values_list('project_id', flat=True).distinct()
    projects = Project.objects.filter(id__in=drawing_project_ids)
    return render(request, 'parts/part_projects.html', {'projects': projects})


PART_SORT_OPTIONS = [
    ('number', 'Number'),
    ('file_ext', 'Extension'),
    ('category__name', 'Category'),
    ('size', 'Size'),
    ('created', 'Date Created'),
    ('updated', 'Date Updated'),
]


def apply_part_sorting(queryset, request):
    sort_params = request.GET.getlist('sort')
    order_params = request.GET.getlist('order')
    sort = sort_params[-1] if sort_params else 'number'
    order = order_params[-1] if order_params else 'asc'
    valid_fields = [f[0] for f in PART_SORT_OPTIONS]
    if sort not in valid_fields:
        sort = 'number'
    if order not in ('asc', 'desc'):
        order = 'asc'
    sort_label = dict(PART_SORT_OPTIONS).get(sort, 'Sort')
    if sort == 'file_ext':
        items = list(queryset)
        items.sort(key=lambda p: p.file_ext or '', reverse=(order == 'desc'))
        return items, sort, order, sort_label
    if order == 'asc':
        queryset = queryset.order_by(sort)
    else:
        queryset = queryset.order_by(f'-{sort}')
    return queryset, sort, order, sort_label


@login_required
def part_page(request, project_slug):
    from django.db.models import Q
    from projects.models import Project
    project = get_object_or_404(Project, slug=project_slug)
    exclude_q = Q()
    for ext in Part.MODEL_EXTENSIONS + Part.DXF_EXTENSIONS:
        exclude_q |= Q(file__iendswith=ext)
    parts = Part.objects.filter(project=project).exclude(exclude_q).select_related('category')
    parts, sort, order, sort_label = apply_part_sorting(parts, request)
    context = {
        'project': project, 'parts': parts,
        'sort_options': PART_SORT_OPTIONS, 'current_sort': sort, 'current_order': order,
        'current_sort_label': sort_label,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'parts/partials/part_page_content.html', context)
    return render(request, 'parts/part_page.html', context)


@login_required
def part_create(request, project_slug):
    from projects.models import Project
    project = get_object_or_404(Project, slug=project_slug)
    form = PartForm(request.POST)
    if form.is_valid():
        if project.number:
            safe_number = sanitize_folder_name(project.number)
            up_files = request.FILES.getlist('file')
            has_model = False
            has_drawing = False
            if up_files:
                for f in up_files:
                    if f:
                        ext = os.path.splitext(f.name)[1].lower()
                        if ext in Part.MODEL_EXTENSIONS:
                            has_model = True
                        else:
                            has_drawing = True
            else:
                has_drawing = True
            if has_drawing:
                ensure_project_subfolder(project, f'{safe_number}_drawings')
            if has_model:
                ensure_project_subfolder(project, f'{safe_number}_models')
        up_files = request.FILES.getlist('file')
        if up_files:
            for f in up_files:
                if f:
                    Part.objects.create(project=project, number=_number_from_file(form.cleaned_data.get('number'), f), category=form.cleaned_data.get('category'), size=_format_size(f.size), rev=form.cleaned_data.get('rev'), created=form.cleaned_data.get('created'), updated=form.cleaned_data.get('updated'), file=f)
        else:
            part = form.save(commit=False)
            part.number = _number_from_file(form.cleaned_data.get('number'), None)
            part.project = project
            part.save()
        log_activity(request.user, 'created', 'Part created')
        if request.headers.get('HX-Request'):
            response = HttpResponse('<script>closeSlideOver()</script>')
            response['HX-Refresh'] = 'true'
            return response
        messages.success(request, 'Part added successfully.')
        return redirect('parts:page', project_slug=project.slug)
    return render(request, 'parts/part_form.html', {'form': form, 'project': project, 'title': 'Add Part'})


@login_required
def part_create_slide(request, project_slug):
    from projects.models import Project
    project = get_object_or_404(Project, slug=project_slug)
    form = PartForm()
    return render(request, 'parts/part_form.html', {'form': form, 'project': project, 'title': 'Add Part'})


@login_required
def part_edit(request, pk):
    part = get_object_or_404(Part, pk=pk)
    form = PartForm(request.POST, instance=part)
    if form.is_valid():
        part = form.save()
        log_activity(request.user, 'updated', f'Part {part.number} updated', part)
        if request.headers.get('HX-Request'):
            response = HttpResponse('<script>closeSlideOver()</script>')
            response['HX-Refresh'] = 'true'
            return response
        messages.success(request, 'Part updated successfully.')
        if part.project:
            return redirect('parts:page', project_slug=part.project.slug)
        return redirect('parts:list')
    return render(request, 'parts/part_form.html', {'form': form, 'part': part, 'project': part.project, 'title': 'Edit Part'})


@login_required
def part_edit_slide(request, pk):
    part = get_object_or_404(Part, pk=pk)
    form = PartForm(instance=part)
    return render(request, 'parts/part_form.html', {'form': form, 'part': part, 'project': part.project, 'title': 'Edit Part'})


@login_required
def part_delete(request, pk):
    part = get_object_or_404(Part, pk=pk)
    project_slug = part.project.slug if part.project else None
    log_activity(request.user, 'deleted', f'Part {part.number} deleted', part)
    if part.file:
        file_dir = os.path.dirname(part.file.path)
        part.file.delete(save=False)
        cleanup_empty_dirs(file_dir)
    part.delete()
    if request.headers.get('HX-Request'):
        response = HttpResponse('<script>closeSlideOver()</script>')
        response['HX-Refresh'] = 'true'
        return response
    messages.success(request, 'Part deleted.')
    next_url = request.POST.get('next') or request.GET.get('next') or ''
    if next_url.strip():
        return redirect(next_url)
    if project_slug:
        return redirect('parts:page', project_slug=project_slug)
    return redirect('parts:list')


@login_required
def common_create_slide(request):
    form = CommonPartForm()
    return render(request, 'parts/part_common_form.html', {'form': form, 'title': 'Add Part'})


@login_required
def common_save(request):
    form = CommonPartForm(request.POST)
    if form.is_valid():
        project = form.cleaned_data.get('project')
        if project and project.number:
            safe_number = sanitize_folder_name(project.number)
            up_files = request.FILES.getlist('file')
            has_model = False
            has_drawing = False
            if up_files:
                for f in up_files:
                    if f:
                        ext = os.path.splitext(f.name)[1].lower()
                        if ext in Part.MODEL_EXTENSIONS:
                            has_model = True
                        else:
                            has_drawing = True
            else:
                has_drawing = True
            if has_drawing:
                ensure_project_subfolder(project, f'{safe_number}_drawings')
            if has_model:
                ensure_project_subfolder(project, f'{safe_number}_models')
        up_files = request.FILES.getlist('file')
        if up_files:
            for f in up_files:
                if f:
                    Part.objects.create(number=_number_from_file(form.cleaned_data.get('number'), f), category=form.cleaned_data.get('category'), size=_format_size(f.size), rev=form.cleaned_data.get('rev'), created=form.cleaned_data.get('created'), updated=form.cleaned_data.get('updated'), file=f)
        else:
            part = form.save(commit=False)
            part.number = _number_from_file(form.cleaned_data.get('number'), None)
            part.save()
        log_activity(request.user, 'created', 'Part created')
        if request.headers.get('HX-Request'):
            return HttpResponse('<script>closeSlideOver(); refreshSection("parts")</script>')
        messages.success(request, 'Part added successfully.')
        return redirect('parts:list')
    return render(request, 'parts/part_common_form.html', {'form': form, 'title': 'Add Part'})


@login_required
def common_delete(request, pk):
    part = get_object_or_404(Part, pk=pk)
    log_activity(request.user, 'deleted', f'Part {part.number} deleted', part)
    if part.file:
        file_dir = os.path.dirname(part.file.path)
        part.file.delete(save=False)
        cleanup_empty_dirs(file_dir)
    part.delete()
    if request.headers.get('HX-Request'):
        response = HttpResponse('<script>closeSlideOver()</script>')
        response['HX-Refresh'] = 'true'
        return response
    messages.success(request, 'Part deleted.')
    return redirect('parts:list')


@login_required
def model_projects(request):
    from projects.models import Project
    projects = Project.objects.filter(parts__isnull=False, parts__file__isnull=False).distinct()
    return render(request, 'parts/model_projects.html', {'projects': projects})


@login_required
def model_page(request, project_slug):
    from django.db.models import Q
    from projects.models import Project
    project = get_object_or_404(Project, slug=project_slug)
    model_ext_q = Q()
    for ext in Part.MODEL_EXTENSIONS:
        model_ext_q |= Q(file__iendswith=ext)
    parts = Part.objects.filter(project=project).filter(model_ext_q).select_related('category')
    parts, sort, order, sort_label = apply_part_sorting(parts, request)
    context = {
        'project': project, 'parts': parts,
        'sort_options': PART_SORT_OPTIONS, 'current_sort': sort, 'current_order': order,
        'current_sort_label': sort_label,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'parts/partials/model_page_content.html', context)
    return render(request, 'parts/model_page.html', context)


@login_required
def dxf_page(request, project_slug):
    from django.db.models import Q
    from projects.models import Project
    project = get_object_or_404(Project, slug=project_slug)
    dxf_ext_q = Q()
    for ext in Part.DXF_EXTENSIONS:
        dxf_ext_q |= Q(file__iendswith=ext)
    parts = Part.objects.filter(project=project).filter(dxf_ext_q).select_related('category')
    parts, sort, order, sort_label = apply_part_sorting(parts, request)
    context = {
        'project': project, 'parts': parts,
        'sort_options': PART_SORT_OPTIONS, 'current_sort': sort, 'current_order': order,
        'current_sort_label': sort_label,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'parts/partials/dxf_page_content.html', context)
    return render(request, 'parts/dxf_page.html', context)


@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'parts/category_list.html', {'categories': categories})


@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    parts = Part.objects.filter(category=category).select_related('project')
    return render(request, 'parts/category_detail.html', {'category': category, 'parts': parts})


@login_required
def category_create_slide(request):
    form = CategoryForm()
    return render(request, 'parts/category_form.html', {'form': form, 'title': 'Add Category'})


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
        return redirect('parts:category_list')
    return render(request, 'parts/category_form.html', {'form': form, 'title': 'Add Category'})


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
    return redirect('parts:category_list')
