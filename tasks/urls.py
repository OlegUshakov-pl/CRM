from django.urls import path
from . import views

app_name = 'tasks'
urlpatterns = [
    path('', views.task_list, name='list'),
    path('create/', views.task_create, name='create'),
    path('<int:pk>/edit/', views.task_edit, name='edit'),
    path('<int:pk>/delete/', views.task_delete, name='delete'),
    path('create/slide/', views.task_create_slide, name='create_slide'),
    path('<int:pk>/edit/slide/', views.task_edit_slide, name='edit_slide'),
]
