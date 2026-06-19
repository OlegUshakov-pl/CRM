from django.urls import path
from . import views

app_name = 'documents'
urlpatterns = [
    path('', views.document_list, name='list'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/create/slide/', views.category_create_slide, name='category_create_slide'),
    path('categories/save/', views.category_save, name='category_save'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('projects/', views.document_projects, name='projects'),
    path('common/latest/', views.document_common_latest, name='common_latest'),
    path('common/create/slide/', views.document_common_create_slide, name='common_create_slide'),
    path('common/save/', views.document_common_save, name='common_save'),
    path('<slug:project_slug>/', views.document_project, name='project'),
    path('<slug:project_slug>/create/slide/', views.document_create_slide, name='create_slide'),
    path('<slug:project_slug>/save/', views.document_save, name='save'),
    path('<int:pk>/edit/slide/', views.document_edit_slide, name='edit_slide'),
    path('<int:pk>/update/', views.document_update, name='update'),
    path('<int:pk>/delete/', views.document_delete, name='delete'),
    path('<int:pk>/show/', views.document_show, name='show'),
    path('<int:pk>/view/', views.document_view, name='view'),
    path('<int:pk>/download/', views.document_download, name='download'),
]
