from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Note
from .forms import NoteForm
from core.models import log_activity


@login_required
def note_latest(request):
    from django.utils import timezone
    from datetime import timedelta
    notes = Note.objects.filter(is_active=True, created_at__gte=timezone.now() - timedelta(minutes=10)).order_by('-created_at')[:5]
    return render(request, 'notes/common_latest.html', {'notes': notes})


@login_required
def note_list(request):
    notes = Note.objects.filter(is_active=True).select_related('project', 'company', 'contact')
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'date_desc')
    if query:
        notes = notes.filter(title__icontains=query) | notes.filter(content__icontains=query)
    if sort == 'date_asc':
        notes = notes.order_by('created_at')
    elif sort == 'project':
        notes = notes.order_by('project__name', 'title')
    elif sort == 'contact':
        notes = notes.order_by('contact__first_name', 'contact__last_name', 'title')
    else:
        notes = notes.order_by('-created_at')
    paginator = Paginator(notes, 12)
    page = request.GET.get('page', 1)
    notes_page = paginator.get_page(page)
    return render(request, 'notes/note_list.html', {'notes': notes_page, 'query': query, 'sort': sort})


@login_required
def note_detail(request, slug):
    note = get_object_or_404(Note.objects.select_related('project', 'company', 'contact'), slug=slug)
    return render(request, 'notes/note_detail.html', {'note': note})


@login_required
def note_create(request):
    form = NoteForm()
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.created_by = request.user
            note.save()
            log_activity(request.user, 'created', f'Note "{note.title}"', note)
            messages.success(request, 'Note created successfully.')
            if request.headers.get('HX-Request'):
                return HttpResponse('<script>closeSlideOver(); refreshSection("notes")</script>')
            return redirect('notes:list')
    return render(request, 'notes/note_form.html', {'form': form, 'title': 'Add Note'})


@login_required
def note_edit(request, slug):
    note = get_object_or_404(Note, slug=slug)
    form = NoteForm(instance=note)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'updated', f'Note "{note.title}"', note)
            messages.success(request, 'Note updated successfully.')
            if request.headers.get('HX-Request'):
                return HttpResponse('<script>closeSlideOver(); refreshSection("notes")</script>')
            return redirect('notes:list')
    return render(request, 'notes/note_form.html', {'form': form, 'title': 'Edit Note', 'note': note})


@login_required
def note_delete(request, slug):
    note = get_object_or_404(Note, slug=slug)
    if request.method == 'POST':
        note.is_active = False
        note.save()
        log_activity(request.user, 'deleted', f'Note "{note.title}"')
        messages.success(request, 'Note deleted successfully.')
    if note.project:
        return redirect('projects:edit', slug=note.project.slug)
    return redirect('notes:list')


@login_required
def note_create_slide(request):
    form = NoteForm()
    return render(request, 'notes/note_form.html', {'form': form, 'title': 'Add Note'})


@login_required
def note_edit_slide(request, slug):
    note = get_object_or_404(Note, slug=slug)
    form = NoteForm(instance=note)
    return render(request, 'notes/note_form.html', {'form': form, 'title': 'Edit Note', 'note': note})
