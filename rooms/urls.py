from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.room_list_view, name='room_list'),
    path('add/', views.room_create_view, name='room_create'),
    path('<int:pk>/', views.room_detail_view, name='room_detail'),
    path('<int:pk>/edit/', views.room_update_view, name='room_update'),
    path('<int:pk>/delete/', views.room_delete_view, name='room_delete'),
    path('ajax/load-floors/', views.ajax_load_floors, name='ajax_load_floors'),
]
