from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Company
from .forms import CompanyForm
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
    return render(request, 'companies/company_list.html', {'companies': companies_page, 'query': query})


@login_required
def company_detail(request, slug):
    company = get_object_or_404(Company.objects.prefetch_related('contacts'), slug=slug)
    linked_projects = company.projects.filter(is_active=True)
    return render(request, 'companies/company_detail.html', {'company': company, 'linked_projects': linked_projects})


@login_required
def company_create(request):
    form = CompanyForm()
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            project = form.cleaned_data.get('project')
            if project:
                project.company = company
                project.save()
            log_activity(request.user, 'created', f'Company "{company.name}"', company)
            messages.success(request, 'Company created successfully.')
            if request.headers.get('HX-Request'):
                response = HttpResponse('<script>closeSlideOver()</script>')
                response['HX-Refresh'] = 'true'
                return response
            return redirect('companies:company_list')
    return render(request, 'companies/company_form.html', {'form': form, 'title': 'Add Company'})


@login_required
def company_edit(request, slug):
    company = get_object_or_404(Company, slug=slug)
    form = CompanyForm(instance=company, company=company)
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company, company=company)
        if form.is_valid():
            form.save()
            project = form.cleaned_data.get('project')
            from projects.models import Project
            if project:
                project.company = company
                project.save()
            else:
                Project.objects.filter(company=company).update(company=None)
            log_activity(request.user, 'updated', f'Company "{company.name}"', company)
            messages.success(request, 'Company updated successfully.')
            if request.headers.get('HX-Request'):
                response = HttpResponse('<script>closeSlideOver()</script>')
                response['HX-Refresh'] = 'true'
                return response
            return redirect('companies:company_list')
    return render(request, 'companies/company_form.html', {'form': form, 'title': 'Edit Company', 'company': company})


@login_required
def company_delete(request, slug):
    company = get_object_or_404(Company, slug=slug)
    if request.method == 'POST':
        company.is_active = False
        company.save()
        log_activity(request.user, 'deleted', f'Company "{company.name}"')
        messages.success(request, 'Company deleted successfully.')
    return redirect('companies:company_list')


@login_required
def company_create_slide(request):
    form = CompanyForm()
    return render(request, 'companies/company_form.html', {'form': form, 'title': 'Add Company'})


@login_required
def company_edit_slide(request, slug):
    company = get_object_or_404(Company, slug=slug)
    form = CompanyForm(instance=company, company=company)
    return render(request, 'companies/company_form.html', {
        'form': form,
        'title': 'Edit Company',
        'company': company,
    })
