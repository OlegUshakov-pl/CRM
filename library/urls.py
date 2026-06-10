from django.urls import path
from . import views

app_name = 'library'
urlpatterns = [
    path('', views.library_list, name='list'),
    path('dashboard/', views.library_dashboard, name='dashboard'),
    path('create/', views.library_create, name='create'),
    path('<slug:slug>/', views.library_detail, name='detail'),
    path('<slug:slug>/edit/', views.library_edit, name='edit'),
    path('<slug:slug>/delete/', views.library_delete, name='delete'),
    path('<slug:slug>/favorite/', views.library_toggle_favorite, name='favorite'),
    path('<slug:slug>/upload-attachment/', views.library_upload_attachment, name='upload_attachment'),
]
