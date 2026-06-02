from django.urls import path
from . import views

app_name = 'documents'
urlpatterns = [
    path('', views.document_list, name='list'),
    path('projects/', views.document_projects, name='projects'),
    path('<slug:project_slug>/', views.document_project, name='project'),
]
