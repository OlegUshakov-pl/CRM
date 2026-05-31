from django.contrib import admin
from .models import Deal


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'priority', 'value', 'company', 'assigned_to', 'due_date', 'is_active', 'created_at']
    list_filter = ['status', 'priority', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['status', 'priority']
    date_hierarchy = 'created_at'