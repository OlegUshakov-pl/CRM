from django.contrib import admin
from .models import Category, Material


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'number', 'category', 'project', 'quantity', 'unit', 'unit_price']
    search_fields = ['name', 'number', 'project__name', 'category__name']
