from django.urls import path
from . import views

app_name = 'visitors'

urlpatterns = [
    path('', views.visitor_list_view, name='visitor_list'),
    path('add/', views.visitor_create_view, name='visitor_create'),
    path('<int:pk>/checkout/', views.visitor_checkout_view, name='visitor_checkout'),
]
