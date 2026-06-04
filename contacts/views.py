from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Contact
from .forms import ContactForm
from core.models import log_activity


@login_required
def contact_latest(request):
    from django.utils import timezone
    from datetime import timedelta
    contacts = Contact.objects.filter(is_active=True, created_at__gte=timezone.now() - timedelta(minutes=10)).order_by('-created_at')[:5]
    return render(request, 'contacts/common_latest.html', {'contacts': contacts})


@login_required
def contact_list(request):
    contacts = Contact.objects.filter(is_active=True).select_related('company').prefetch_related('projects').order_by('first_name')
    query = request.GET.get('q', '')
    if query:
        contacts = contacts.filter(first_name__icontains=query) | contacts.filter(last_name__icontains=query)
    paginator = Paginator(contacts, 20)
    page = request.GET.get('page', 1)
    contacts_page = paginator.get_page(page)
    return render(request, 'contacts/contact_list.html', {'contacts': contacts_page, 'query': query})


@login_required
def contact_detail(request, slug):
    contact = get_object_or_404(Contact.objects.select_related('company', 'created_by'), slug=slug)
    return render(request, 'contacts/contact_detail.html', {'contact': contact})


@login_required
def contact_create(request):
    form = ContactForm()
    project_slug = request.POST.get('project') or request.GET.get('project')
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.created_by = request.user
            contact.save()
            if project_slug:
                from projects.models import Project
                project = Project.objects.filter(slug=project_slug).first()
                if project:
                    project.contacts.add(contact)
            log_activity(request.user, 'created', f'Contact "{contact.get_full_name()}"', contact)
            messages.success(request, 'Contact created successfully.')
            if request.headers.get('HX-Request'):
                response = HttpResponse('<script>closeSlideOver()</script>')
                response['HX-Trigger'] = 'refresh-contacts'
                return response
            return redirect('contacts:contact_list')
    return render(request, 'contacts/contact_form.html', {'form': form, 'title': 'Add Contact', 'project_slug': project_slug})


@login_required
def contact_edit(request, slug):
    contact = get_object_or_404(Contact, slug=slug)
    form = ContactForm(instance=contact)
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES, instance=contact)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'updated', f'Contact "{contact.get_full_name()}"', contact)
            messages.success(request, 'Contact updated successfully.')
            if request.headers.get('HX-Request'):
                response = HttpResponse('<script>closeSlideOver()</script>')
                response['HX-Refresh'] = 'true'
                return response
            return redirect('contacts:contact_list')
    return render(request, 'contacts/contact_form.html', {'form': form, 'title': 'Edit Contact', 'contact': contact})


@login_required
def contact_delete(request, slug):
    contact = get_object_or_404(Contact, slug=slug)
    if request.method == 'POST':
        contact.is_active = False
        contact.save()
        log_activity(request.user, 'deleted', f'Contact "{contact.get_full_name()}"')
        messages.success(request, 'Contact deleted successfully.')
    return redirect('contacts:contact_list')


@login_required
def contact_create_slide(request):
    form = ContactForm()
    project_slug = request.GET.get('project')
    return render(request, 'contacts/contact_form.html', {'form': form, 'title': 'Add Contact', 'project_slug': project_slug})


@login_required
def contact_edit_slide(request, slug):
    contact = get_object_or_404(Contact, slug=slug)
    form = ContactForm(instance=contact)
    return render(request, 'contacts/contact_form.html', {'form': form, 'title': 'Edit Contact', 'contact': contact})
