from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    path('', views.complaint_list_view, name='complaint_list'),
    path('<int:pk>/', views.complaint_detail_view, name='complaint_detail'),
    path('submit/', views.student_complaint_submit_view, name='student_complaint_submit'),
    path('my/', views.student_my_complaints_view, name='my_complaints'),
]
