from django.urls import path
from . import views

app_name = 'tasks'
urlpatterns = [
    path('', views.task_list, name='list'),
    path('latest/', views.task_latest, name='latest'),
    path('create/', views.task_create, name='create'),
    path('<slug:slug>/edit/', views.task_edit, name='edit'),
    path('<slug:slug>/delete/', views.task_delete, name='delete'),
    path('create/slide/', views.task_create_slide, name='create_slide'),
    path('<slug:slug>/edit/slide/', views.task_edit_slide, name='edit_slide'),
]
