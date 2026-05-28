from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Task
from .forms import TaskForm
from core.models import log_activity


@login_required
def task_list(request):
    tasks = Task.objects.filter(is_active=True).select_related('project', 'assigned_to')
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    if query:
        tasks = tasks.filter(title__icontains=query)
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    paginator = Paginator(tasks, 20)
    page = request.GET.get('page', 1)
    tasks_page = paginator.get_page(page)
    return render(request, 'tasks/task_list.html', {
        'tasks': tasks_page,
        'query': query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    })


@login_required
def task_create(request):
    form = TaskForm()
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            form.save_m2m()
            log_activity(request.user, 'created', f'Task "{task.title}"', task)
            messages.success(request, 'Task created successfully.')
            return redirect('tasks:list')
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Add Task'})


@login_required
def task_edit(request, slug):
    task = get_object_or_404(Task, slug=slug)
    form = TaskForm(instance=task)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'updated', f'Task "{task.title}"', task)
            messages.success(request, 'Task updated successfully.')
            return redirect('tasks:list')
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Edit Task', 'task': task})


@login_required
def task_delete(request, slug):
    task = get_object_or_404(Task, slug=slug)
    if request.method == 'POST':
        task.is_active = False
        task.save()
        log_activity(request.user, 'deleted', f'Task "{task.title}"')
        messages.success(request, 'Task deleted successfully.')
    return redirect('tasks:list')


@login_required
def task_create_slide(request):
    form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Add Task'})


@login_required
def task_edit_slide(request, slug):
    task = get_object_or_404(Task, slug=slug)
    form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Edit Task', 'task': task})
