from django.urls import path

from . import views

app_name = 'assistant'

urlpatterns = [
    path('chat/panel-state/', views.panel_state, name='panel_state'),
    path('chat/send/', views.chat, name='chat'),
    path('chat/clear/', views.clear_chat, name='clear_chat'),

    path('ai-files/', views.ai_files, name='ai_files'),
    path('ai-files/upload/', views.ai_file_upload, name='ai_file_upload'),
    path('ai-files/<uuid:file_id>/download/', views.ai_file_download, name='ai_file_download'),
    path('ai-files/<uuid:file_id>/delete/', views.ai_file_delete, name='ai_file_delete'),
    path('ai-files/bulk-delete/', views.ai_file_bulk_delete, name='ai_file_bulk_delete'),
    path('ai-files/cleanup/', views.ai_file_cleanup, name='ai_file_cleanup'),
    path('ai-files/<uuid:file_id>/attach/', views.ai_file_attach, name='ai_file_attach'),

    path('browser/preview/', views.browser_preview, name='browser_preview'),
]
