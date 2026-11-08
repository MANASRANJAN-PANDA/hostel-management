from django.conf import settings
from notices.models import Notice
from complaints.models import Complaint

def hostel_context(request):
    context = {
        'SYSTEM_NAME': 'HostelPulse',
        'COLLEGE_NAME': 'College Hostel Management System',
        'unread_notices_count': 0,
        'pending_complaints_count': 0,
    }
    if request.user.is_authenticated:
        if request.user.is_student() and hasattr(request.user, 'student_profile'):
            student = request.user.student_profile
            context['current_student'] = student
            context['unread_notices_count'] = Notice.objects.filter(is_published=True).count()
            context['pending_complaints_count'] = Complaint.objects.filter(student=student, status__in=['SUBMITTED', 'UNDER_REVIEW', 'IN_PROGRESS']).count()
        elif request.user.is_warden() and hasattr(request.user, 'warden_profile'):
            context['current_warden'] = request.user.warden_profile
            context['pending_complaints_count'] = Complaint.objects.filter(status__in=['SUBMITTED', 'UNDER_REVIEW']).count()
        elif request.user.is_superadmin():
            context['pending_complaints_count'] = Complaint.objects.filter(status__in=['SUBMITTED', 'UNDER_REVIEW']).count()
    return context
