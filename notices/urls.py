from django.urls import path
from . import views

app_name = 'notices'

urlpatterns = [
    path('', views.notice_student_board_view, name='student_board'),
    path('<int:pk>/', views.notice_detail_view, name='notice_detail'),
    path('manage/', views.notice_admin_list_view, name='admin_notice_list'),
    path('manage/add/', views.notice_create_view, name='notice_create'),
    path('manage/<int:pk>/edit/', views.notice_update_view, name='notice_update'),
    path('manage/<int:pk>/delete/', views.notice_delete_view, name='notice_delete'),
]
