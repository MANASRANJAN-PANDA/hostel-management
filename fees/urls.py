from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.fee_list_view, name='fee_list'),
    path('add/', views.fee_create_view, name='fee_create'),
    path('batch-generate/', views.fee_batch_generate_view, name='fee_batch_generate'),
    path('<int:fee_id>/pay/', views.payment_record_view, name='payment_record'),
    path('payments/', views.payment_list_view, name='payment_list'),
    path('receipt/<str:receipt_number>/', views.receipt_detail_view, name='receipt_detail'),
    path('categories/', views.category_list_view, name='category_list'),
]
