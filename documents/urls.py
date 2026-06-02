from django.urls import path
from . import views

app_name = 'documents'
urlpatterns = [
    path('', views.document_list, name='list'),
    path('projects/', views.document_projects, name='projects'),
    path('<slug:project_slug>/', views.document_project, name='project'),
    path('<slug:project_slug>/create/slide/', views.document_create_slide, name='create_slide'),
    path('<slug:project_slug>/save/', views.document_save, name='save'),
    path('<int:pk>/edit/slide/', views.document_edit_slide, name='edit_slide'),
    path('<int:pk>/update/', views.document_update, name='update'),
    path('<int:pk>/delete/', views.document_delete, name='delete'),
]
