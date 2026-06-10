from django.contrib import admin
from .models import Category, Tag, LibraryItem, LibraryAttachment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'parent', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']


@admin.register(LibraryItem)
class LibraryItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'file_type', 'is_favorite', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_favorite', 'file_type', 'category']
    search_fields = ['title', 'description', 'content']


@admin.register(LibraryAttachment)
class LibraryAttachmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'item', 'uploaded_at']
