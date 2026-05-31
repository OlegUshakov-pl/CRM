from django.urls import path
from . import views

app_name = 'projects'
urlpatterns = [
    path('', views.project_list, name='list'),
    path('create/', views.project_create, name='create'),
    path('create/slide/', views.project_create_slide, name='create_slide'),

    path('<slug:slug>/', views.project_detail, name='detail'),
    path('<slug:slug>/edit/', views.project_edit, name='edit'),
    path('<slug:slug>/delete/', views.project_delete, name='delete'),
    path('<slug:slug>/edit/slide/', views.project_edit_slide, name='edit_slide'),
]
