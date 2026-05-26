from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'company', 'contact', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title', 'content']
