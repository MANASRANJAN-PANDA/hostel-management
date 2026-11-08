from django.urls import path
from . import views

app_name = 'hostels'

urlpatterns = [
    path('', views.hostel_list_view, name='hostel_list'),
    path('add/', views.hostel_create_view, name='hostel_create'),
    path('<int:pk>/edit/', views.hostel_update_view, name='hostel_update'),
    path('floor/add/', views.floor_create_view, name='floor_create'),
    path('<int:hostel_id>/floor/add/', views.floor_create_view, name='floor_create_for_hostel'),
]
