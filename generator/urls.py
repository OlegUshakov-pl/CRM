from django.urls import path
from . import views

app_name = 'generators'
urlpatterns = [
    path('', views.deal_list, name='list'),
    path('create/', views.deal_create, name='create'),
    path('create/slide/', views.deal_create_slide, name='create_slide'),
    path('<slug:slug>/', views.deal_detail, name='detail'),
    path('<slug:slug>/edit/', views.deal_edit, name='edit'),
    path('<slug:slug>/delete/', views.deal_delete, name='delete'),
    path('<slug:slug>/edit/slide/', views.deal_edit_slide, name='edit_slide'),
]