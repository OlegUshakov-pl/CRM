from django.contrib import admin
from .models import Project, Material


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'company', 'is_active', 'created_at']
    list_filter = ['status', 'is_active']
    search_fields = ['name']


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'quantity', 'unit']
    list_filter = ['unit']
    search_fields = ['name']
