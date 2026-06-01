from django.urls import path
from . import views

app_name = 'materials'
urlpatterns = [
    path('', views.material_main, name='main'),
    path('common/', views.material_common, name='common'),
    path('<slug:project_slug>/page/', views.material_page, name='page'),
    path('<slug:project_slug>/create/', views.material_create, name='create'),
    path('<slug:slug>/edit/', views.material_edit, name='edit'),
    path('<slug:slug>/delete/', views.material_delete, name='delete'),
    path('<slug:project_slug>/create/slide/', views.material_create_slide, name='create_slide'),
    path('<slug:slug>/edit/slide/', views.material_edit_slide, name='edit_slide'),
]
