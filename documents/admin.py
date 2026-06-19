from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['number', 'project', 'size', 'filename', 'created_at']
    list_filter = ['project']
    search_fields = ['number', 'project__name']
