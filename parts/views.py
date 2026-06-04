import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from core.models import log_activity
from projects.utils import ensure_project_subfolder, sanitize_folder_name
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
    parts = Part.objects.select_related('category').order_by('-created')[:5]
    return render(request, 'parts/common_latest.html', {'parts': parts})


@login_required
def part_list(request):
    parts = Part.objects.select_related('category', 'project').all()
    return render(request, 'parts/part_list.html', {'parts': parts})


@login_required
def part_projects(request):
    projects = Part.objects.values('project__name', 'project__slug').distinct()
    return render(request, 'parts/part_projects.html', {'projects': projects})


@login_required
def part_page(request, project_slug):
    from projects.models import Project
    project = get_object_or_404(Project, slug=project_slug)
    parts = Part.objects.filter(project=project).select_related('category')
    return render(request, 'parts/part_page.html', {'project': project, 'parts': parts})


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
        log_activity(request.user, 'created', None, 'Part created')
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
        log_activity(request.user, 'updated', part, f'Part {part.number} updated')
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
    log_activity(request.user, 'deleted', part, f'Part {part.number} deleted')
    part.delete()
    if request.headers.get('HX-Request'):
        response = HttpResponse('<script>closeSlideOver()</script>')
        response['HX-Refresh'] = 'true'
        return response
    messages.success(request, 'Part deleted.')
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
        log_activity(request.user, 'created', None, 'Part created')
        if request.headers.get('HX-Request'):
            response = HttpResponse('<script>closeSlideOver()</script>')
            response['HX-Trigger'] = 'refresh-parts'
            return response
        messages.success(request, 'Part added successfully.')
        return redirect('parts:list')
    return render(request, 'parts/part_common_form.html', {'form': form, 'title': 'Add Part'})


@login_required
def common_delete(request, pk):
    part = get_object_or_404(Part, pk=pk)
    log_activity(request.user, 'deleted', part, f'Part {part.number} deleted')
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
        log_activity(request.user, 'created', category, f'Category {category.name} created')
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
    log_activity(request.user, 'deleted', category, f'Category {category.name} deleted')
    category.delete()
    if request.headers.get('HX-Request'):
        response = HttpResponse('<script>closeSlideOver()</script>')
        response['HX-Refresh'] = 'true'
        return response
    messages.success(request, 'Category deleted.')
    return redirect('parts:category_list')
