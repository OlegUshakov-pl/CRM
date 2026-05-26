from django.urls import path
from . import views

app_name = 'projects'
urlpatterns = [
    path('', views.project_list, name='list'),
    path('<int:pk>/', views.project_detail, name='detail'),
    path('create/', views.project_create, name='create'),
    path('<int:pk>/edit/', views.project_edit, name='edit'),
    path('<int:pk>/delete/', views.project_delete, name='delete'),
    path('create/slide/', views.project_create_slide, name='create_slide'),
    path('<int:pk>/edit/slide/', views.project_edit_slide, name='edit_slide'),

    path('<int:project_pk>/materials/create/', views.material_create, name='material_create'),
    path('materials/<int:pk>/edit/', views.material_edit, name='material_edit'),
    path('materials/<int:pk>/delete/', views.material_delete, name='material_delete'),
    path('<int:project_pk>/materials/create/slide/', views.material_create_slide, name='material_create_slide'),
]
