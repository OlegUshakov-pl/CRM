from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'company', 'is_active', 'created_at']
    list_filter = ['status', 'is_active']
    search_fields = ['name']
