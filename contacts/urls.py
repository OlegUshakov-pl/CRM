from django.urls import path
from . import views

app_name = 'contacts'
urlpatterns = [
    path('companies/', views.company_list, name='company_list'),
    path('companies/create/', views.company_create, name='company_create'),
    path('companies/create/slide/', views.company_create_slide, name='company_create_slide'),
    path('companies/<slug:slug>/', views.company_detail, name='company_detail'),
    path('companies/<slug:slug>/edit/', views.company_edit, name='company_edit'),
    path('companies/<slug:slug>/delete/', views.company_delete, name='company_delete'),
    path('companies/<slug:slug>/edit/slide/', views.company_edit_slide, name='company_edit_slide'),

    path('', views.contact_list, name='contact_list'),
    path('create/', views.contact_create, name='contact_create'),
    path('create/slide/', views.contact_create_slide, name='contact_create_slide'),
    path('<slug:slug>/', views.contact_detail, name='contact_detail'),
    path('<slug:slug>/edit/', views.contact_edit, name='contact_edit'),
    path('<slug:slug>/delete/', views.contact_delete, name='contact_delete'),
    path('<slug:slug>/edit/slide/', views.contact_edit_slide, name='contact_edit_slide'),
]
