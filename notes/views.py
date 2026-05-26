from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Note
from .forms import NoteForm
from core.models import log_activity


@login_required
def note_list(request):
    notes = Note.objects.filter(is_active=True).select_related('project', 'company', 'contact')
    query = request.GET.get('q', '')
    if query:
        notes = notes.filter(title__icontains=query) | notes.filter(content__icontains=query)
    paginator = Paginator(notes, 12)
    page = request.GET.get('page', 1)
    notes_page = paginator.get_page(page)
    return render(request, 'notes/note_list.html', {'notes': notes_page, 'query': query})


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
            return redirect('notes:list')
    return render(request, 'notes/note_form.html', {'form': form, 'title': 'Add Note'})


@login_required
def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk)
    form = NoteForm(instance=note)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'updated', f'Note "{note.title}"', note)
            messages.success(request, 'Note updated successfully.')
            return redirect('notes:list')
    return render(request, 'notes/note_form.html', {'form': form, 'title': 'Edit Note', 'note': note})


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        note.is_active = False
        note.save()
        log_activity(request.user, 'deleted', f'Note "{note.title}"')
        messages.success(request, 'Note deleted successfully.')
    return redirect('notes:list')


@login_required
def note_create_slide(request):
    form = NoteForm()
    return render(request, 'notes/note_form.html', {'form': form, 'title': 'Add Note'})


@login_required
def note_edit_slide(request, pk):
    note = get_object_or_404(Note, pk=pk)
    form = NoteForm(instance=note)
    return render(request, 'notes/note_form.html', {'form': form, 'title': 'Edit Note', 'note': note})
