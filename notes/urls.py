from django.urls import path
from . import views

app_name = 'notes'
urlpatterns = [
    path('', views.note_list, name='list'),
    path('create/', views.note_create, name='create'),
    path('create/slide/', views.note_create_slide, name='create_slide'),
    path('<slug:slug>/', views.note_detail, name='detail'),
    path('<slug:slug>/edit/', views.note_edit, name='edit'),
    path('<slug:slug>/delete/', views.note_delete, name='delete'),
    path('<slug:slug>/edit/slide/', views.note_edit_slide, name='edit_slide'),
]
