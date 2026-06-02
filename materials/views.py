from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Category, Material
from .forms import CategoryForm, MaterialForm, CommonMaterialForm
from projects.models import Project
from core.models import log_activity


@login_required
def material_main(request):
    projects = Project.objects.filter(is_active=True, materials__isnull=False).distinct().order_by('-created_at')
    query = request.GET.get('q', '')
    if query:
        projects = projects.filter(name__icontains=query)
    paginator = Paginator(projects, 12)
    page = request.GET.get('page', 1)
    projects_page = paginator.get_page(page)
    return render(request, 'materials/materials_main.html', {'projects': projects_page, 'query': query})


SORT_OPTIONS = [
    ('name', 'Name'),
    ('category__name', 'Category'),
    ('quantity', 'Qty'),
    ('unit_price', 'Price'),
    ('created_at', 'Date Created'),
]


def apply_sorting(queryset, request):
    sort_params = request.GET.getlist('sort')
    order_params = request.GET.getlist('order')
    sort = sort_params[-1] if sort_params else 'created_at'
    order = order_params[-1] if order_params else 'desc'
    valid_fields = [f[0] for f in SORT_OPTIONS]
    if sort not in valid_fields:
        sort = 'created_at'
    if order not in ('asc', 'desc'):
        order = 'desc'
    sort_label = dict(SORT_OPTIONS).get(sort, 'Sort')
    if order == 'asc':
        queryset = queryset.order_by(sort)
    else:
        queryset = queryset.order_by(f'-{sort}')
    return queryset, sort, order, sort_label


@login_required
def material_common(request):
    materials = Material.objects.filter(is_active=True).select_related('project', 'category')
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    if query:
        materials = materials.filter(name__icontains=query)
    if category_filter:
        materials = materials.filter(category_id=category_filter)
    materials, sort, order, sort_label = apply_sorting(materials, request)
    categories = Category.objects.all()
    paginator = Paginator(materials, 20)
    page = request.GET.get('page', 1)
    materials_page = paginator.get_page(page)
    return render(request, 'materials/materials_common.html', {
        'materials': materials_page, 'query': query, 'total_count': paginator.count,
        'sort_options': SORT_OPTIONS, 'current_sort': sort, 'current_order': order,
        'current_sort_label': sort_label, 'current_page': page,
        'categories': categories, 'current_category': category_filter,
    })


@login_required
def material_page(request, project_slug):
    project = get_object_or_404(Project, slug=project_slug)
    materials = Material.objects.filter(project=project, is_active=True).select_related('category')
    materials, sort, order, sort_label = apply_sorting(materials, request)
    return render(request, 'materials/material_list.html', {
        'project': project, 'materials': materials,
        'sort_options': SORT_OPTIONS, 'current_sort': sort, 'current_order': order,
        'current_sort_label': sort_label,
    })


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
    return redirect('projects:detail', slug=project_slug)


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


@login_required
def category_create_slide(request):
    form = CategoryForm()
    return render(request, 'materials/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def category_save(request):
    form = CategoryForm(request.POST)
    if form.is_valid():
        form.save()
        response = HttpResponse()
        response['HX-Refresh'] = 'true'
        return response
    return render(request, 'materials/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def common_create_slide(request):
    form = CommonMaterialForm()
    return render(request, 'materials/common_material_form.html', {'form': form, 'title': 'Add Material'})


@login_required
def common_save(request):
    form = CommonMaterialForm(request.POST)
    if form.is_valid():
        material = form.save(commit=False)
        material.created_by = request.user
        material.save()
        response = HttpResponse()
        response['HX-Refresh'] = 'true'
        return response
    return render(request, 'materials/common_material_form.html', {'form': form, 'title': 'Add Material'})


@login_required
def common_delete(request, slug):
    material = get_object_or_404(Material, slug=slug)
    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Material deleted.')
    return redirect('materials:common')


@login_required
def category_list(request):
    categories = Category.objects.all()
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('materials:category_list')
    return render(request, 'materials/category_list.html', {'categories': categories, 'form': form})


@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    materials = Material.objects.filter(category=category, is_active=True).select_related('project')
    return render(request, 'materials/category_detail.html', {'category': category, 'materials': materials})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Category "{category.name}" deleted.')
    return redirect('materials:category_list')
