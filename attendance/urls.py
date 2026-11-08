from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list_view, name='attendance_list'),
    path('batch/', views.attendance_mark_batch_view, name='attendance_mark_batch'),
    path('mark-single/', views.attendance_single_add_view, name='attendance_single_add'),
    path('my/', views.student_my_attendance_view, name='my_attendance'),
]
