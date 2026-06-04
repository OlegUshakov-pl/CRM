from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('search/', views.search_view, name='search'),
    path('settings/save/', views.save_setting, name='save_setting'),
    path('settings/<str:key>/', views.get_setting, name='get_setting'),
]
