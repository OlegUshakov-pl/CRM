from django.urls import path
from . import views

app_name = 'materials'
urlpatterns = [
    path('', views.material_main, name='main'),
    path('common/', views.material_common, name='common'),
    path('common/create/slide/', views.common_create_slide, name='common_create_slide'),
    path('common/save/', views.common_save, name='common_save'),
    path('common/<slug:slug>/delete/', views.common_delete, name='common_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('category/create/slide/', views.category_create_slide, name='category_create_slide'),
    path('category/save/', views.category_save, name='category_save'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('<slug:project_slug>/page/', views.material_page, name='page'),
    path('<slug:project_slug>/create/', views.material_create, name='create'),
    path('<slug:slug>/edit/', views.material_edit, name='edit'),
    path('<slug:slug>/delete/', views.material_delete, name='delete'),
    path('<slug:project_slug>/create/slide/', views.material_create_slide, name='create_slide'),
    path('<slug:slug>/edit/slide/', views.material_edit_slide, name='edit_slide'),
]
