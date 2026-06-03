from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Prefetch
from .models import Project, ProjectImage
from .forms import ProjectForm
from contacts.models import Contact
from notes.forms import NoteForm
from materials.models import Material
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
                form.save()
                for f in request.FILES.getlist('images'):
                    ProjectImage.objects.create(project=project, image=f)
                delete_ids = request.POST.getlist('delete_images')
                if delete_ids:
                    ProjectImage.objects.filter(id__in=delete_ids, project=project).delete()
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
    })


@login_required
def remove_contact(request, slug, contact_id):
    project = get_object_or_404(Project, slug=slug)
    if request.method == 'POST':
        contact = get_object_or_404(Contact, id=contact_id)
        project.contacts.remove(contact)
        log_activity(request.user, 'updated', f'Removed contact "{contact.get_full_name()}" from "{project.name}"', project)
        messages.success(request, 'Contact removed.')
    return redirect(request.META.get('HTTP_REFERER') or reverse('projects:detail', kwargs={'slug': slug}))


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
    return redirect(request.META.get('HTTP_REFERER') or reverse('projects:edit', kwargs={'slug': slug}))


@login_required
def delete_image(request, pk):
    img = get_object_or_404(ProjectImage, pk=pk)
    if request.method == 'POST':
        img.delete()
        messages.success(request, 'Image deleted.')
    return redirect('projects:edit', slug=img.project.slug)


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
