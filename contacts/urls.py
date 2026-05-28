from django.urls import path
from . import views

app_name = 'contacts'
urlpatterns = [
    path('companies/', views.company_list, name='company_list'),
    path('companies/<int:pk>/', views.company_detail, name='company_detail'),
    path('companies/create/', views.company_create, name='company_create'),
    path('companies/<int:pk>/edit/', views.company_edit, name='company_edit'),
    path('companies/<int:pk>/delete/', views.company_delete, name='company_delete'),
    path('companies/create/slide/', views.company_create_slide, name='company_create_slide'),
    path('companies/<int:pk>/edit/slide/', views.company_edit_slide, name='company_edit_slide'),

    path('', views.contact_list, name='contact_list'),
    path('<int:pk>/', views.contact_detail, name='contact_detail'),
    path('create/', views.contact_create, name='contact_create'),
    path('<int:pk>/edit/', views.contact_edit, name='contact_edit'),
    path('<int:pk>/delete/', views.contact_delete, name='contact_delete'),
    path('create/slide/', views.contact_create_slide, name='contact_create_slide'),
    path('<int:pk>/edit/slide/', views.contact_edit_slide, name='contact_edit_slide'),
]
