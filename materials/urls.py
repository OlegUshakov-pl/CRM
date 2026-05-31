from django.urls import path
from . import views

app_name = 'materials'
urlpatterns = [
    path('<slug:project_slug>/create/', views.material_create, name='create'),
    path('<slug:slug>/edit/', views.material_edit, name='edit'),
    path('<slug:slug>/delete/', views.material_delete, name='delete'),
    path('<slug:project_slug>/create/slide/', views.material_create_slide, name='create_slide'),
]
