from django.urls import path
from . import views

app_name = 'allocations'

urlpatterns = [
    path('', views.allocation_list_view, name='allocation_list'),
    path('add/', views.allocation_create_view, name='allocation_create'),
    path('<int:pk>/transfer/', views.allocation_transfer_view, name='allocation_transfer'),
    path('<int:pk>/vacate/', views.allocation_vacate_view, name='allocation_vacate'),
]
