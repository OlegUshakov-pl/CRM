from django.contrib import admin

from .models import AIFile, AILog, ChatMessage, ChatSession


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'last_message_at', 'is_active', 'created_at')
    list_filter = ('is_active', 'user')
    search_fields = ('title', 'user__username')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'kind', 'created_at')
    list_filter = ('role', 'kind')


@admin.register(AIFile)
class AIFileAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'owner', 'category', 'size', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('original_name', 'source_url', 'owner__username')


@admin.register(AILog)
class AILogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'status', 'description', 'duration_ms', 'created_at')
    list_filter = ('action', 'status')
    search_fields = ('description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
