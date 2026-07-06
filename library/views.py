import json
import bleach
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.template.loader import render_to_string
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
    items = LibraryItem.objects.filter(is_active=True).select_related('category').prefetch_related('tags')

    query = request.GET.get('q', '')
    if query:
        items = items.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query) |
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

    tag_slug = request.GET.get('tag', '')
    if tag_slug:
        items = items.filter(tags__slug=tag_slug)

    date_filter = request.GET.get('date', '')
    if date_filter:
        now = timezone.now()
        if date_filter == 'today':
            items = items.filter(created_at__date=now.date())
        elif date_filter == 'week':
            items = items.filter(created_at__gte=now - timedelta(days=7))
        elif date_filter == 'month':
            items = items.filter(created_at__gte=now - timedelta(days=30))
        elif date_filter == 'year':
            items = items.filter(created_at__gte=now - timedelta(days=365))

    view_mode = request.GET.get('view', 'grid')
    paginator = Paginator(items, 24)
    page = request.GET.get('page', 1)
    items_page = paginator.get_page(page)

    categories = Category.objects.filter(is_active=True).annotate(item_count=Count('items'))
    file_types = LibraryItem.FILE_TYPE_CHOICES
    tags = Tag.objects.annotate(item_count=Count('items')).filter(item_count__gt=0).order_by('-item_count')[:20]

    if request.headers.get('HX-Request'):
        return render(request, 'library/list_partial.html', {
            'items': items_page,
            'query': query,
            'categories': categories,
            'file_types': file_types,
            'tags': tags,
            'current_category': category_slug,
            'current_type': file_type,
            'favorites_only': favorites_only,
            'view_mode': view_mode,
            'current_tag': tag_slug,
            'current_date': date_filter,
        })

    return render(request, 'library/list.html', {
        'items': items_page,
        'query': query,
        'categories': categories,
        'file_types': file_types,
        'tags': tags,
        'current_category': category_slug,
        'current_type': file_type,
        'favorites_only': favorites_only,
        'view_mode': view_mode,
        'current_tag': tag_slug,
        'current_date': date_filter,
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
                item.content = bleach.clean(item.content, tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'img', 'blockquote', 'pre', 'code', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'span', 'div'], attributes={'a': ['href', 'target'], 'img': ['src', 'alt', 'width', 'height'], 'span': ['style'], 'div': ['style']}, strip=True)
            item.created_by = request.user
            item.save()
            form._save_tags(item)
            for f in request.FILES.getlist('additional_files'):
                LibraryAttachment.objects.create(item=item, file=f)
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
        'active_tab': 'editor',
    })


@login_required
def library_import_url(request):
    if request.method == 'POST':
        url = request.POST.get('url', '').strip()
        if not url:
            messages.error(request, 'Please provide a URL.')
            return render(request, 'library/import_url.html', {'url': url})

        try:
            import urllib.request
            from html.parser import HTMLParser

            class ContentParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.title = ''
                    self.in_title = False
                    self.content = []
                    self.in_body = False
                    self.current_tag = None
                    self.images = []

                def handle_starttag(self, tag, attrs):
                    if tag == 'title':
                        self.in_title = True
                    elif tag == 'body':
                        self.in_body = True
                    elif tag == 'img' and self.in_body:
                        attrs_dict = dict(attrs)
                        if 'src' in attrs_dict:
                            self.images.append(attrs_dict['src'])
                    if tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote']:
                        self.current_tag = tag
                    if self.in_body and tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'div']:
                        self.content.append(f'<{tag}>')

                def handle_endtag(self, tag):
                    if tag == 'title':
                        self.in_title = False
                    elif tag == 'body':
                        self.in_body = False
                    if self.in_body and tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'div']:
                        self.content.append(f'</{tag}>')

                def handle_data(self, data):
                    if self.in_title:
                        self.title += data.strip()
                    elif self.in_body and data.strip():
                        self.content.append(data.strip())

            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                html_content = response.read().decode('utf-8', errors='ignore')

            parser = ContentParser()
            parser.feed(html_content)

            title = parser.title or url.split('/')[-1].replace('-', ' ').replace('_', ' ')
            content = ' '.join(parser.content)
            summary = content[:300] + '...' if len(content) > 300 else content

            item = LibraryItem(
                title=title,
                content=bleach.clean(content, tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'img', 'blockquote', 'pre', 'code', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'span', 'div'], attributes={'a': ['href', 'target'], 'img': ['src', 'alt', 'width', 'height'], 'span': ['style'], 'div': ['style']}, strip=True),
                summary=summary,
                source_url=url,
                created_by=request.user,
            )
            item.save()

            tags_input = request.POST.get('tags_input', '')
            if tags_input:
                tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
                for name in tag_names:
                    tag, _ = Tag.objects.get_or_create(name=name)
                    item.tags.add(tag)

            category_id = request.POST.get('category')
            if category_id:
                try:
                    item.category = Category.objects.get(id=category_id, is_active=True)
                    item.save()
                except Category.DoesNotExist:
                    pass

            log_activity(request.user, 'created', f'Library item "{item.title}" (imported from URL)', item)
            messages.success(request, f'Document imported successfully from URL.')
            return redirect('library:detail', slug=item.slug)

        except Exception as e:
            messages.error(request, f'Failed to import URL: {str(e)}')
            return render(request, 'library/import_url.html', {'url': url})

    categories = Category.objects.filter(is_active=True)
    return render(request, 'library/import_url.html', {
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
                item.content = bleach.clean(item.content, tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'a', 'img', 'blockquote', 'pre', 'code', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'span', 'div'], attributes={'a': ['href', 'target'], 'img': ['src', 'alt', 'width', 'height'], 'span': ['style'], 'div': ['style']}, strip=True)
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
        'active_tab': 'editor',
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
def library_delete_htmx(request, slug):
    if request.method == 'DELETE':
        item = get_object_or_404(LibraryItem, slug=slug, is_active=True)
        item.is_active = False
        item.save()
        log_activity(request.user, 'deleted', f'Library item "{item.title}"')
        return HttpResponse('')
    return HttpResponse(status=405)


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
def library_gallery(request):
    image_filter = Q(file_type='image') | Q(attachments__file__icontains='.jpg') | Q(attachments__file__icontains='.jpeg') | Q(attachments__file__icontains='.png') | Q(attachments__file__icontains='.webp')
    items = LibraryItem.objects.filter(
        is_active=True,
    ).filter(
        image_filter
    ).select_related('category').distinct()

    paginator = Paginator(items, 36)
    page = request.GET.get('page', 1)
    items_page = paginator.get_page(page)

    if request.headers.get('HX-Request'):
        return render(request, 'library/gallery_partial.html', {'items': items_page})

    return render(request, 'library/gallery.html', {'items': items_page})


@login_required
def library_files(request):
    items = LibraryItem.objects.filter(
        is_active=True
    ).exclude(
        file_type='image'
    ).select_related('category').order_by('-created_at')

    query = request.GET.get('q', '')
    if query:
        items = items.filter(
            Q(title__icontains=query) |
            Q(file__icontains=query)
        )

    file_type = request.GET.get('type', '')
    if file_type:
        items = items.filter(file_type=file_type)

    paginator = Paginator(items, 20)
    page = request.GET.get('page', 1)
    items_page = paginator.get_page(page)

    file_types = LibraryItem.FILE_TYPE_CHOICES

    if request.headers.get('HX-Request'):
        return render(request, 'library/files_partial.html', {
            'items': items_page,
            'query': query,
            'current_type': file_type,
            'file_types': file_types,
        })

    return render(request, 'library/files.html', {
        'items': items_page,
        'query': query,
        'current_type': file_type,
        'file_types': file_types,
    })


@login_required
def category_list(request):
    categories = Category.objects.filter(is_active=True).annotate(item_count=Count('items')).order_by('name')

    if request.headers.get('HX-Request'):
        return render(request, 'library/category_list_partial.html', {'categories': categories})

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
            if request.headers.get('HX-Request'):
                categories = Category.objects.filter(is_active=True).annotate(item_count=Count('items')).order_by('name')
                return render(request, 'library/category_list_partial.html', {'categories': categories})
            return redirect('library:category_list')
    else:
        form = CategoryForm()

    if request.headers.get('HX-Request'):
        return render(request, 'library/category_form_inline.html', {'form': form, 'title': 'Create Category'})

    return render(request, 'library/category_form.html', {'form': form, 'title': 'Create Category'})


@login_required
def category_edit(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated.')
            if request.headers.get('HX-Request'):
                categories = Category.objects.filter(is_active=True).annotate(item_count=Count('items')).order_by('name')
                return render(request, 'library/category_list_partial.html', {'categories': categories})
            return redirect('library:category_list')
    else:
        form = CategoryForm(instance=category)

    if request.headers.get('HX-Request'):
        return render(request, 'library/category_form_inline.html', {'form': form, 'title': 'Edit Category', 'category': category})

    return render(request, 'library/category_form.html', {'form': form, 'title': 'Edit Category', 'category': category})


@login_required
def category_delete(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    if request.method == 'POST':
        category.is_active = False
        category.save()
        messages.success(request, f'Category "{category.name}" deleted.')
        if request.headers.get('HX-Request'):
            return HttpResponse('')
        return redirect('library:category_list')
    return render(request, 'library/category_confirm_delete.html', {'category': category})


@login_required
def category_create_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            if not name:
                return JsonResponse({'error': 'Name is required'}, status=400)

            category = Category.objects.create(
                name=name,
                color=data.get('color', '#8B5CF6'),
                created_by=request.user,
            )
            return JsonResponse({'id': category.pk, 'name': category.name, 'slug': category.slug})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'POST required'}, status=400)


@login_required
def library_search_external(request):
    query = request.GET.get('q', '')
    engine = request.GET.get('engine', 'google')

    if not query:
        return JsonResponse({'error': 'Query required'}, status=400)

    if engine == 'google':
        url = f'https://www.google.com/search?q={query}'
    elif engine == 'duckduckgo':
        url = f'https://duckduckgo.com/?q={query}'
    else:
        url = f'https://www.google.com/search?q={query}'

    return JsonResponse({'url': url})
