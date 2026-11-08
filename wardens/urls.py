from django.urls import path
from . import views

app_name = 'wardens'

urlpatterns = [
    path('', views.warden_list_view, name='warden_list'),
    path('add/', views.warden_create_view, name='warden_create'),
    path('<int:pk>/edit/', views.warden_update_view, name='warden_update'),
    path('<int:pk>/delete/', views.warden_delete_view, name='warden_delete'),
    path('<int:pk>/toggle-status/', views.warden_toggle_status_view, name='warden_toggle_status'),
]
