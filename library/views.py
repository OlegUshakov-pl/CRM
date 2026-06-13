import json
import bleach
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import LibraryItem, Category, Tag, LibraryAttachment
from .forms import LibraryItemForm, CategoryForm
from core.models import log_activity


@login_required
def library_dashboard(request):
    recent = LibraryItem.objects.filter(is_active=True).order_by('-created_at')[:10]
    favorites = LibraryItem.objects.filter(is_active=True, is_favorite=True).order_by('-updated_at')[:10]
    categories = Category.objects.filter(is_active=True).annotate(item_count=Count('items')).filter(item_count__gt=0)
    return render(request, 'library/dashboard.html', {
        'recent': recent,
        'favorites': favorites,
        'categories': categories,
    })


@login_required
def library_list(request):
    items = LibraryItem.objects.filter(is_active=True).select_related('category')

    query = request.GET.get('q', '')
    if query:
        items = items.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    category_slug = request.GET.get('category', '')
    if category_slug:
        items = items.filter(category__slug=category_slug)

    file_type = request.GET.get('type', '')
    if file_type:
        items = items.filter(file_type=file_type)

    favorites_only = request.GET.get('favorites', '')
    if favorites_only:
        items = items.filter(is_favorite=True)

    view_mode = request.GET.get('view', 'list')
    paginator = Paginator(items, 24)
    page = request.GET.get('page', 1)
    items_page = paginator.get_page(page)

    categories = Category.objects.filter(is_active=True)
    file_types = LibraryItem.FILE_TYPE_CHOICES

    return render(request, 'library/list.html', {
        'items': items_page,
        'query': query,
        'categories': categories,
        'file_types': file_types,
        'current_category': category_slug,
        'current_type': file_type,
        'favorites_only': favorites_only,
        'view_mode': view_mode,
    })


@login_required
def library_detail(request, slug):
    item = get_object_or_404(LibraryItem.objects.select_related('category').prefetch_related('tags', 'attachments'), slug=slug, is_active=True)
    return render(request, 'library/detail.html', {'item': item})


@login_required
def library_create(request):
    if request.method == 'POST':
        form = LibraryItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            if item.content:
                item.content = bleach.clean(item.content, tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'img', 'blockquote', 'pre', 'code', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'span', 'div'], attributes={'a': ['href', 'target'], 'img': ['src', 'alt', 'width', 'height'], 'span': ['style'], 'div': ['style']}, styles=['color', 'background-color', 'font-size', 'font-weight', 'text-align', 'padding', 'margin'], strip=True)
            item.created_by = request.user
            item.save()
            form._save_tags(item)
            log_activity(request.user, 'created', f'Library item "{item.title}"', item)
            messages.success(request, 'Document created successfully.')
            return redirect('library:detail', slug=item.slug)
    else:
        form = LibraryItemForm()
    categories = Category.objects.filter(is_active=True)
    return render(request, 'library/form.html', {
        'form': form,
        'title': 'Create Document',
        'categories': categories,
    })


@login_required
def library_edit(request, slug):
    item = get_object_or_404(LibraryItem, slug=slug, is_active=True)
    if request.method == 'POST':
        form = LibraryItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            if item.content:
                item.content = bleach.clean(item.content, tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'img', 'blockquote', 'pre', 'code', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'span', 'div'], attributes={'a': ['href', 'target'], 'img': ['src', 'alt', 'width', 'height'], 'span': ['style'], 'div': ['style']}, styles=['color', 'background-color', 'font-size', 'font-weight', 'text-align', 'padding', 'margin'], strip=True)
            item.save()
            log_activity(request.user, 'updated', f'Library item "{item.title}"', item)
            messages.success(request, 'Document updated successfully.')
            return redirect('library:detail', slug=item.slug)
    else:
        form = LibraryItemForm(instance=item)
    categories = Category.objects.filter(is_active=True)
    return render(request, 'library/form.html', {
        'form': form,
        'title': 'Edit Document',
        'item': item,
        'categories': categories,
    })


@login_required
def library_delete(request, slug):
    item = get_object_or_404(LibraryItem, slug=slug, is_active=True)
    if request.method == 'POST':
        item.is_active = False
        item.save()
        log_activity(request.user, 'deleted', f'Library item "{item.title}"')
        messages.success(request, 'Document deleted successfully.')
        return redirect('library:list')
    return render(request, 'library/confirm_delete.html', {'item': item})


@login_required
def library_toggle_favorite(request, slug):
    item = get_object_or_404(LibraryItem, slug=slug, is_active=True)
    item.is_favorite = not item.is_favorite
    item.save()
    return JsonResponse({'is_favorite': item.is_favorite})


@login_required
def library_upload_attachment(request, slug):
    item = get_object_or_404(LibraryItem, slug=slug, is_active=True)
    if request.method == 'POST' and request.FILES.get('file'):
        attachment = LibraryAttachment.objects.create(
            item=item,
            file=request.FILES['file'],
        )
        return JsonResponse({'id': attachment.pk, 'name': attachment.name})
    return JsonResponse({'error': 'No file provided'}, status=400)


@login_required
def category_list(request):
    categories = Category.objects.filter(is_active=True).annotate(item_count=Count('items')).order_by('name')
    return render(request, 'library/category_list.html', {'categories': categories})


@login_required
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    items = LibraryItem.objects.filter(is_active=True, category=category).order_by('-created_at')
    paginator = Paginator(items, 24)
    page = request.GET.get('page', 1)
    items_page = paginator.get_page(page)
    return render(request, 'library/category_detail.html', {
        'category': category,
        'items': items_page,
    })


@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.save()
            messages.success(request, f'Category "{category.name}" created.')
            return redirect('library:category_list')
    else:
        form = CategoryForm()
    return render(request, 'library/category_form.html', {'form': form, 'title': 'Create Category'})


@login_required
def category_edit(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated.')
            return redirect('library:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'library/category_form.html', {'form': form, 'title': 'Edit Category', 'category': category})


@login_required
def category_delete(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    if request.method == 'POST':
        category.is_active = False
        category.save()
        messages.success(request, f'Category "{category.name}" deleted.')
        return redirect('library:category_list')
    return render(request, 'library/category_confirm_delete.html', {'category': category})
