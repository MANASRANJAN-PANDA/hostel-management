from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_index_view, name='reports_index'),
    path('students/', views.student_report_view, name='student_report'),
    path('occupancy/', views.occupancy_report_view, name='occupancy_report'),
    path('fee-collection/', views.fee_collection_report_view, name='fee_collection_report'),
    path('pending-fees/', views.pending_fee_report_view, name='pending_fee_report'),
    path('complaints/', views.complaint_report_view, name='complaint_report'),
    path('attendance/', views.attendance_report_view, name='attendance_report'),
    path('visitors/', views.visitor_report_view, name='visitor_report'),
]
