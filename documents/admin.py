from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['number', 'project', 'file_type', 'size', 'filename', 'created_at']
    list_filter = ['file_type', 'project']
    search_fields = ['number', 'project__name']
