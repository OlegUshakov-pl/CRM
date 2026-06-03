from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from core.models import log_activity
from .models import Part, Category
from .forms import PartForm, CommonPartForm, CategoryForm


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
        part = form.save(commit=False)
        part.project = project
        part.save()
        log_activity(request.user, 'created', part, f'Part {part.number} created')
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
        part = form.save()
        log_activity(request.user, 'created', part, f'Part {part.number} created')
        if request.headers.get('HX-Request'):
            response = HttpResponse('<script>closeSlideOver()</script>')
            response['HX-Refresh'] = 'true'
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
