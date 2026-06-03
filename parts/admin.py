from django.contrib import admin
from .models import Category, Part


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ['number', 'category', 'project', 'size', 'rev', 'created', 'updated']
    search_fields = ['number', 'project__name', 'category__name']
