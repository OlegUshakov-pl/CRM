from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Company, Contact
from .forms import CompanyForm, ContactForm
from core.models import log_activity


@login_required
def company_list(request):
    companies = Company.objects.filter(is_active=True).order_by('name')
    query = request.GET.get('q', '')
    if query:
        companies = companies.filter(name__icontains=query)
    paginator = Paginator(companies, 12)
    page = request.GET.get('page', 1)
    companies_page = paginator.get_page(page)
    return render(request, 'contacts/company_list.html', {'companies': companies_page, 'query': query})


@login_required
def company_detail(request, pk):
    company = get_object_or_404(Company.objects.prefetch_related('contacts'), pk=pk)
    return render(request, 'contacts/company_detail.html', {'company': company})


@login_required
def company_create(request):
    form = CompanyForm()
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            log_activity(request.user, 'created', f'Company "{company.name}"', company)
            messages.success(request, 'Company created successfully.')
            if request.headers.get('HX-Request'):
                response = HttpResponse('<script>closeSlideOver()</script>')
                response['HX-Refresh'] = 'true'
                return response
            return redirect('contacts:company_list')
    return render(request, 'contacts/company_form.html', {'form': form, 'title': 'Add Company'})


@login_required
def company_edit(request, pk):
    company = get_object_or_404(Company, pk=pk)
    form = CompanyForm(instance=company)
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'updated', f'Company "{company.name}"', company)
            messages.success(request, 'Company updated successfully.')
            if request.headers.get('HX-Request'):
                response = HttpResponse('<script>closeSlideOver()</script>')
                response['HX-Refresh'] = 'true'
                return response
            return redirect('contacts:company_list')
    return render(request, 'contacts/company_form.html', {'form': form, 'title': 'Edit Company', 'company': company})


@login_required
def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        company.is_active = False
        company.save()
        log_activity(request.user, 'deleted', f'Company "{company.name}"')
        messages.success(request, 'Company deleted successfully.')
    return redirect('contacts:company_list')


@login_required
def contact_list(request):
    contacts = Contact.objects.filter(is_active=True).select_related('company').order_by('first_name')
    query = request.GET.get('q', '')
    if query:
        contacts = contacts.filter(first_name__icontains=query) | contacts.filter(last_name__icontains=query)
    paginator = Paginator(contacts, 20)
    page = request.GET.get('page', 1)
    contacts_page = paginator.get_page(page)
    return render(request, 'contacts/contact_list.html', {'contacts': contacts_page, 'query': query})


@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(Contact.objects.select_related('company', 'created_by'), pk=pk)
    return render(request, 'contacts/contact_detail.html', {'contact': contact})


@login_required
def contact_create(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.created_by = request.user
            contact.save()
            log_activity(request.user, 'created', f'Contact "{contact.get_full_name()}"', contact)
            messages.success(request, 'Contact created successfully.')
            return redirect('contacts:contact_list')
    return render(request, 'contacts/contact_form.html', {'form': form, 'title': 'Add Contact'})


@login_required
def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    form = ContactForm(instance=contact)
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES, instance=contact)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'updated', f'Contact "{contact.get_full_name()}"', contact)
            messages.success(request, 'Contact updated successfully.')
            return redirect('contacts:contact_list')
    return render(request, 'contacts/contact_form.html', {'form': form, 'title': 'Edit Contact', 'contact': contact})


@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        contact.is_active = False
        contact.save()
        log_activity(request.user, 'deleted', f'Contact "{contact.get_full_name()}"')
        messages.success(request, 'Contact deleted successfully.')
    return redirect('contacts:contact_list')


@login_required
def company_create_slide(request):
    form = CompanyForm()
    return render(request, 'contacts/company_form.html', {'form': form, 'title': 'Add Company'})


@login_required
def company_edit_slide(request, pk):
    company = get_object_or_404(Company, pk=pk)
    form = CompanyForm(instance=company)
    return render(request, 'contacts/company_form.html', {'form': form, 'title': 'Edit Company', 'company': company})


@login_required
def contact_create_slide(request):
    form = ContactForm()
    return render(request, 'contacts/contact_form.html', {'form': form, 'title': 'Add Contact'})


@login_required
def contact_edit_slide(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    form = ContactForm(instance=contact)
    return render(request, 'contacts/contact_form.html', {'form': form, 'title': 'Edit Contact', 'contact': contact})
