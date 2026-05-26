from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'project', 'assigned_to', 'due_date', 'is_active']
    list_filter = ['status', 'priority', 'is_active']
    search_fields = ['title']
