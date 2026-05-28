from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Project, Material, ProjectImage
from .forms import ProjectForm, MaterialForm
from core.models import log_activity


@login_required
def project_list(request):
    projects = Project.objects.filter(is_active=True).select_related('company').prefetch_related('contacts')
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    if query:
        projects = projects.filter(name__icontains=query)
    if status_filter:
        projects = projects.filter(status=status_filter)
    paginator = Paginator(projects, 12)
    page = request.GET.get('page', 1)
    projects_page = paginator.get_page(page)
    return render(request, 'projects/project_list.html', {
        'projects': projects_page,
        'query': query,
        'status_filter': status_filter,
    })


@login_required
def project_detail(request, slug):
    project = get_object_or_404(Project.objects.prefetch_related('materials', 'contacts', 'tasks', 'note_entries', 'images'), slug=slug)
    return render(request, 'projects/project_detail.html', {'project': project})


@login_required
def project_create(request):
    form = ProjectForm()
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            form.save_m2m()
            for f in request.FILES.getlist('images'):
                ProjectImage.objects.create(project=project, image=f)
            log_activity(request.user, 'created', f'Project "{project.name}"', project)
            messages.success(request, 'Project created successfully.')
            next_url = request.GET.get('next')
            if next_url == 'dashboard':
                return redirect('core:dashboard')
            return redirect('projects:list')
    return render(request, 'projects/project_create_page.html', {'form': form, 'title': 'Add Project', 'is_page': True})


@login_required
def project_edit(request, slug):
    project = get_object_or_404(Project, slug=slug)
    form = ProjectForm(instance=project)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            for f in request.FILES.getlist('images'):
                ProjectImage.objects.create(project=project, image=f)
            delete_ids = request.POST.getlist('delete_images')
            if delete_ids:
                ProjectImage.objects.filter(id__in=delete_ids, project=project).delete()
            log_activity(request.user, 'updated', f'Project "{project.name}"', project)
            messages.success(request, 'Project updated successfully.')
            return redirect('projects:detail', slug=project.slug)
    return render(request, 'projects/project_edit_page.html', {'form': form, 'title': 'Edit Project', 'project': project, 'is_page': True})


@login_required
def project_delete(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        project.is_active = False
        project.save()
        log_activity(request.user, 'deleted', f'Project "{project.name}"')
        messages.success(request, 'Project deleted successfully.')
    return redirect('projects:list')


@login_required
def project_create_slide(request):
    form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form, 'title': 'Add Project'})


@login_required
def project_edit_slide(request, slug):
    project = get_object_or_404(Project, slug=slug)
    form = ProjectForm(instance=project)
    return render(request, 'projects/project_form.html', {'form': form, 'title': 'Edit Project', 'project': project})


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
            messages.success(request, 'Material added successfully.')
            return redirect('projects:detail', slug=project_slug)
    return render(request, 'projects/material_form.html', {'form': form, 'project': project, 'title': 'Add Material'})


@login_required
def material_edit(request, slug):
    material = get_object_or_404(Material, slug=slug)
    form = MaterialForm(instance=material)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'updated', f'Material "{material.name}"')
            messages.success(request, 'Material updated successfully.')
            return redirect('projects:detail', slug=material.project.slug)
    return render(request, 'projects/material_form.html', {'form': form, 'project': material.project, 'title': 'Edit Material', 'material': material})


@login_required
def material_delete(request, slug):
    material = get_object_or_404(Material, slug=slug)
    project_slug = material.project.slug
    if request.method == 'POST':
        log_activity(request.user, 'deleted', f'Material "{material.name}"')
        material.delete()
        messages.success(request, 'Material deleted successfully.')
    return redirect('projects:detail', slug=project_slug)


@login_required
def material_create_slide(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    form = MaterialForm()
    return render(request, 'projects/material_form.html', {'form': form, 'project': project, 'title': 'Add Material'})
