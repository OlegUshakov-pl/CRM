from django.contrib import admin
from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'quantity', 'unit', 'unit_price']
    search_fields = ['name', 'project__name']
