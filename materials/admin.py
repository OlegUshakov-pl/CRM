from django.contrib import admin
from .models import Material, CommonMaterial


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'quantity', 'unit', 'unit_price']
    search_fields = ['name', 'project__name']


@admin.register(CommonMaterial)
class CommonMaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'project_name', 'quantity', 'unit', 'unit_price']
    search_fields = ['name', 'project_name']
