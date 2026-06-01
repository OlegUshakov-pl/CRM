from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Material
from .forms import MaterialForm
from projects.models import Project
from core.models import log_activity


@login_required
def material_main(request):
    materials = Material.objects.filter(is_active=True).select_related('project').order_by('-created_at')
    query = request.GET.get('q', '')
    if query:
        materials = materials.filter(name__icontains=query)
    paginator = Paginator(materials, 20)
    page = request.GET.get('page', 1)
    materials_page = paginator.get_page(page)
    return render(request, 'materials/materials_main.html', {'materials': materials_page, 'query': query})


@login_required
def material_page(request, project_slug):
    project = get_object_or_404(Project.objects.prefetch_related('materials'), slug=project_slug)
    return render(request, 'materials/material_list.html', {'project': project})


@login_required
def material_create(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    form = MaterialForm()
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            material = form.save(commit=False)
            material.project = project
            material.created_by = request.user
            material.save()
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
    material = get_object_or_404(Material, slug=slug)
    project_slug = material.project.slug
    if request.method == 'POST':
        log_activity(request.user, 'deleted', f'Material "{material.name}"')
        material.delete()
        messages.success(request, 'Material deleted successfully.')
    return redirect('materials:main')


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
