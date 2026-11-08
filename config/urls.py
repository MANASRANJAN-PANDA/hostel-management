"""
URL configuration for Hostel Management System.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from accounts import dashboard_views

urlpatterns = [
    # Root redirects to dashboard dispatcher or login
    path('', lambda request: redirect('accounts:dashboard_redirect'), name='index'),

    # Direct dashboard routes
    path('admin-dashboard/', dashboard_views.admin_dashboard_view, name='admin_dashboard'),
    path('warden-dashboard/', dashboard_views.warden_dashboard_view, name='warden_dashboard'),
    path('student-dashboard/', dashboard_views.student_dashboard_view, name='student_dashboard'),

    # Student portal dedicated endpoints
    path('student/profile/', dashboard_views.student_profile_view, name='student_profile'),
    path('student/room/', dashboard_views.student_my_room_view, name='student_my_room'),
    path('student/fees/', dashboard_views.student_my_fees_view, name='student_my_fees'),

    # App URLs
    path('accounts/', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('wardens/', include('wardens.urls')),
    path('hostels/', include('hostels.urls')),
    path('rooms/', include('rooms.urls')),
    path('allocations/', include('allocations.urls')),
    path('fees/', include('fees.urls')),
    path('complaints/', include('complaints.urls')),
    path('attendance/', include('attendance.urls')),
    path('notices/', include('notices.urls')),
    path('visitors/', include('visitors.urls')),
    path('reports/', include('reports.urls')),

    # Django built-in admin
    path('django-admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
