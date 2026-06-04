from django.urls import path
from . import views

app_name = 'contacts'
urlpatterns = [
    path('', views.contact_list, name='contact_list'),
    path('latest/', views.contact_latest, name='contact_latest'),
    path('create/', views.contact_create, name='contact_create'),
    path('create/slide/', views.contact_create_slide, name='contact_create_slide'),
    path('<slug:slug>/', views.contact_detail, name='contact_detail'),
    path('<slug:slug>/edit/', views.contact_edit, name='contact_edit'),
    path('<slug:slug>/delete/', views.contact_delete, name='contact_delete'),
    path('<slug:slug>/edit/slide/', views.contact_edit_slide, name='contact_edit_slide'),
]
