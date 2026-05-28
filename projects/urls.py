from django.urls import path
from . import views

app_name = 'projects'
urlpatterns = [
    path('', views.project_list, name='list'),
    path('<slug:slug>/', views.project_detail, name='detail'),
    path('create/', views.project_create, name='create'),
    path('<slug:slug>/edit/', views.project_edit, name='edit'),
    path('<slug:slug>/delete/', views.project_delete, name='delete'),
    path('create/slide/', views.project_create_slide, name='create_slide'),
    path('<slug:slug>/edit/slide/', views.project_edit_slide, name='edit_slide'),

    path('<slug:project_slug>/materials/create/', views.material_create, name='material_create'),
    path('materials/<slug:slug>/edit/', views.material_edit, name='material_edit'),
    path('materials/<slug:slug>/delete/', views.material_delete, name='material_delete'),
    path('<slug:project_slug>/materials/create/slide/', views.material_create_slide, name='material_create_slide'),
]
