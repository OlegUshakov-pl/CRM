import os
import shutil
from pathlib import Path

from django.http import FileResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Project, ProjectImage
from .forms import ProjectForm
from .services import ExportService, ImportService
from .utils import get_project_folder_path
from contacts.models import Contact
from companies.models import Company
from notes.forms import NoteForm
from materials.models import Material
from core.models import log_activity


def _safe_redirect(request, fallback_url):
    referer = request.META.get('HTTP_REFERER', '')
    if referer and url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}):
        return redirect(referer)
    return redirect(fallback_url)


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
    project = get_object_or_404(Project.objects.prefetch_related(Prefetch('materials', queryset=Material.objects.select_related('category')), 'contacts', 'tasks', 'note_entries', 'images'), slug=slug)
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
    project = get_object_or_404(Project.objects.prefetch_related('documents', 'materials__category', 'contacts', 'tasks', 'note_entries', 'images'), slug=slug)
    form = ProjectForm(instance=project)
    note_form = NoteForm()
    available_contacts = Contact.objects.filter(is_active=True).exclude(projects=project)
    available_companies = Company.objects.filter(is_active=True).exclude(pk=project.company_id) if project.company_id else Company.objects.filter(is_active=True)

    if request.method == 'POST':
        if 'note_submit' in request.POST:
            note_form = NoteForm(request.POST)
            if note_form.is_valid():
                note = note_form.save(commit=False)
                note.project = project
                note.created_by = request.user
                note.save()
                log_activity(request.user, 'created', f'Note "{note.title}" in "{project.name}"', note)
                messages.success(request, 'Note added successfully.')
                return redirect('projects:edit', slug=project.slug)
        else:
            form = ProjectForm(request.POST, request.FILES, instance=project)
            if form.is_valid():
                old_image = project.image if project.image else None
                form.save()
                if old_image and project.image and old_image.name != project.image.name:
                    old_image.delete(save=False)
                for f in request.FILES.getlist('images'):
                    ProjectImage.objects.create(project=project, image=f)
                delete_ids = request.POST.getlist('delete_images')
                if delete_ids:
                    for img in ProjectImage.objects.filter(id__in=delete_ids, project=project):
                        if img.image:
                            img.image.delete(save=False)
                        img.delete()
                log_activity(request.user, 'updated', f'Project "{project.name}"', project)
                messages.success(request, 'Project updated successfully.')
                return redirect('projects:detail', slug=project.slug)

    return render(request, 'projects/project_edit_page.html', {
        'form': form,
        'title': 'Edit Project',
        'project': project,
        'is_page': True,
        'note_form': note_form,
        'available_contacts': available_contacts,
        'available_companies': available_companies,
    })


@login_required
def remove_contact(request, slug, contact_id):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        contact = get_object_or_404(Contact, id=contact_id)
        project.contacts.remove(contact)
        log_activity(request.user, 'updated', f'Removed contact "{contact.get_full_name()}" from "{project.name}"', project)
        messages.success(request, 'Contact removed.')
    return _safe_redirect(request, reverse('projects:detail', kwargs={'slug': slug}))


@login_required
def add_contact(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        contact_id = request.POST.get('contact_id')
        if contact_id:
            contact = get_object_or_404(Contact, id=contact_id)
            project.contacts.add(contact)
            log_activity(request.user, 'updated', f'Added contact "{contact.get_full_name()}" to "{project.name}"', project)
            messages.success(request, 'Contact added.')
    return _safe_redirect(request, reverse('projects:edit', kwargs={'slug': slug}))


@login_required
def add_company(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        if company_id:
            from companies.models import Company
            company = get_object_or_404(Company, id=company_id)
            project.company = company
            project.save()
            log_activity(request.user, 'updated', f'Added company "{company.name}" to "{project.name}"', project)
            messages.success(request, 'Company added.')
    return _safe_redirect(request, reverse('projects:edit', kwargs={'slug': slug}))


@login_required
def remove_company(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        project.company = None
        project.save()
        log_activity(request.user, 'updated', f'Removed company from "{project.name}"', project)
        messages.success(request, 'Company removed.')
    return _safe_redirect(request, reverse('projects:detail', kwargs={'slug': slug}))


@login_required
def delete_image(request, pk):
    img = get_object_or_404(ProjectImage, pk=pk)
    if request.method == 'POST':
        if img.image:
            img.image.delete(save=False)
        img.delete()
        messages.success(request, 'Image deleted.')
    return redirect('projects:edit', slug=img.project.slug)


@login_required
def project_delete(request, slug):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        folder_path = get_project_folder_path(project)
        project.is_active = False
        project.save()
        if folder_path and os.path.exists(folder_path):
            shutil.rmtree(folder_path, ignore_errors=True)
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
def project_export(request, slug):
    project = get_object_or_404(Project, slug=slug)
    service = ExportService(project)
    try:
        zip_path = service.export()
        with open(str(zip_path), 'rb') as f:
            response = FileResponse(
                f.read(),
                content_type='application/zip',
                as_attachment=True,
                filename=f'{project.name}.zip',
            )
        return response
    except Exception as e:
        messages.error(request, f'Export failed: {e}')
        return redirect('projects:detail', slug=slug)
    finally:
        service.cleanup()


@login_required
def project_import_page(request):
    return render(request, 'projects/project_import.html')


@login_required
def project_import(request):
    if request.method != 'POST':
        return redirect('projects:import_page')

    zip_file = request.FILES.get('zip_file')
    if not zip_file:
        messages.error(request, 'Please select a ZIP file.')
        return redirect('projects:import_page')

    service = ImportService(zip_file)
    try:
        if not service.validate():
            for error in service.errors:
                messages.error(request, error)
            return redirect('projects:import_page')

        project = service.import_project()
        log_activity(request.user, 'created', f'Project "{project.name}" imported', project)
        messages.success(request, f'Project "{project.name}" imported successfully.')
        return redirect('projects:detail', slug=project.slug)
    except Exception as e:
        messages.error(request, f'Import failed: {e}')
        return redirect('projects:import_page')
    finally:
        service.cleanup()
