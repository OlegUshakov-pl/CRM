from django.urls import path
from . import views

app_name = 'projects'
urlpatterns = [
    path('', views.project_list, name='list'),
    path('create/', views.project_create, name='create'),
    path('create/slide/', views.project_create_slide, name='create_slide'),
    path('import/', views.project_import_page, name='import_page'),
    path('import/do/', views.project_import, name='import'),

    path('<slug:slug>/', views.project_detail, name='detail'),
    path('<slug:slug>/edit/', views.project_edit, name='edit'),
    path('<slug:slug>/delete/', views.project_delete, name='delete'),
    path('<slug:slug>/export/', views.project_export, name='export'),
    path('<slug:slug>/edit/slide/', views.project_edit_slide, name='edit_slide'),
    path('image/<int:pk>/delete/', views.delete_image, name='delete_image'),
    path('<slug:slug>/contacts/<int:contact_id>/remove/', views.remove_contact, name='remove_contact'),
    path('<slug:slug>/contacts/add/', views.add_contact, name='add_contact'),
    path('<slug:slug>/company/add/', views.add_company, name='add_company'),
    path('<slug:slug>/company/remove/', views.remove_company, name='remove_company'),
]
