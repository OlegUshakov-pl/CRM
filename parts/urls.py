from django.urls import path
from . import views

app_name = 'parts'
urlpatterns = [
    path('', views.part_list, name='list'),
    path('projects/', views.part_projects, name='projects'),
    path('model-projects/', views.model_projects, name='model_projects'),
    path('common/create/slide/', views.common_create_slide, name='common_create_slide'),
    path('common/save/', views.common_save, name='common_save'),
    path('common/<int:pk>/delete/', views.common_delete, name='common_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('category/create/slide/', views.category_create_slide, name='category_create_slide'),
    path('category/save/', views.category_save, name='category_save'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('<slug:project_slug>/page/', views.part_page, name='page'),
    path('<slug:project_slug>/create/', views.part_create, name='create'),
    path('<slug:project_slug>/create/slide/', views.part_create_slide, name='create_slide'),
    path('<int:pk>/edit/', views.part_edit, name='edit'),
    path('<int:pk>/edit/slide/', views.part_edit_slide, name='edit_slide'),
    path('<int:pk>/delete/', views.part_delete, name='delete'),
]
