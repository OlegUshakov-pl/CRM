from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('search/', views.search_view, name='search'),
    path('help/', views.help_page, name='help'),
    path('settings/', views.settings_page, name='settings_page'),
    path('settings/save/', views.save_setting, name='save_setting'),
    path('settings/<str:key>/', views.get_setting, name='get_setting'),
    path('project-files/<path:file_path>', views.serve_project_file, name='serve_project_file'),
]
