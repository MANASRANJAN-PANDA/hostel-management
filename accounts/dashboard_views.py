import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal
from accounts.decorators import superadmin_required, warden_or_admin_required, student_required
from students.models import StudentProfile
from wardens.models import WardenProfile
from rooms.models import Room
from hostels.models import Hostel
from allocations.models import RoomAllocation
from fees.models import FeeRecord, Payment
from complaints.models import Complaint
from attendance.models import Attendance
from notices.models import Notice
from visitors.models import Visitor

@superadmin_required
def admin_dashboard_view(request):
    total_students = StudentProfile.objects.count()
    active_students = StudentProfile.objects.filter(account_status='ACTIVE').count()
    pending_registrations = StudentProfile.objects.filter(account_status='PENDING').count()

    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(room_status='FULL').count()
    partially_occupied_rooms = Room.objects.filter(room_status='PARTIALLY_OCCUPIED').count()
    available_rooms = Room.objects.filter(room_status='AVAILABLE').count()
    maintenance_rooms = Room.objects.filter(room_status='MAINTENANCE').count()

    total_capacity = sum(r.capacity for r in Room.objects.all()) or 1
    total_beds_occupied = RoomAllocation.objects.filter(status='ACTIVE').count()
    total_beds_available = max(0, total_capacity - total_beds_occupied)
    occupancy_pct = round((total_beds_occupied / total_capacity * 100), 1)

    total_wardens = WardenProfile.objects.count()
    total_fee_collection = Payment.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    pending_fee_payments = FeeRecord.objects.aggregate(total=Sum('remaining_amount'))['total'] or Decimal('0.00')
    pending_complaints = Complaint.objects.filter(status__in=['SUBMITTED', 'UNDER_REVIEW']).count()

    # Recent lists
    recent_students = StudentProfile.objects.select_related('user').order_by('-created_at')[:5]
    recent_complaints = Complaint.objects.select_related('student__user').order_by('-created_at')[:5]
    recent_payments = Payment.objects.select_related('fee_record__student__user', 'fee_record__category').order_by('-payment_date', '-created_at')[:5]

    # Chart 1: Occupancy Distribution
    occupancy_chart_data = {
        'labels': ['Occupied Beds', 'Available Beds'],
        'data': [total_beds_occupied, total_beds_available]
    }

    # Chart 2: Monthly Fee Collection (Past 6 months)
    monthly_collections = []
    month_labels = []
    now = timezone.now()
    for i in range(5, -1, -1):
        # Calculate year-month
        month_date = now - timezone.timedelta(days=i * 30)
        m_str = month_date.strftime('%Y-%m')
        m_label = month_date.strftime('%b %Y')
        month_labels.append(m_label)

        coll = Payment.objects.filter(payment_date__year=month_date.year, payment_date__month=month_date.month).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        monthly_collections.append(float(coll))

    chart_fee_data = {
        'labels': month_labels,
        'data': monthly_collections
    }

    context = {
        'total_students': total_students,
        'active_students': active_students,
        'pending_registrations': pending_registrations,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'partially_occupied_rooms': partially_occupied_rooms,
        'available_rooms': available_rooms,
        'maintenance_rooms': maintenance_rooms,
        'total_capacity': total_capacity,
        'total_beds_occupied': total_beds_occupied,
        'total_beds_available': total_beds_available,
        'occupancy_pct': occupancy_pct,
        'total_wardens': total_wardens,
        'total_fee_collection': total_fee_collection,
        'pending_fee_payments': pending_fee_payments,
        'pending_complaints': pending_complaints,
        'recent_students': recent_students,
        'recent_complaints': recent_complaints,
        'recent_payments': recent_payments,
        'occupancy_chart_json': json.dumps(occupancy_chart_data),
        'chart_fee_json': json.dumps(chart_fee_data),
    }
    return render(request, 'admin/dashboard.html', context)


@warden_or_admin_required
def warden_dashboard_view(request):
    warden = getattr(request.user, 'warden_profile', None)
    assigned_hostel = warden.assigned_hostel if warden else None

    rooms_qs = Room.objects.all()
    allocations_qs = RoomAllocation.objects.filter(status='ACTIVE')
    if assigned_hostel:
        rooms_qs = rooms_qs.filter(hostel=assigned_hostel)
        allocations_qs = allocations_qs.filter(room__hostel=assigned_hostel)

    total_rooms = rooms_qs.count()
    total_capacity = sum(r.capacity for r in rooms_qs)
    occupied_beds = allocations_qs.count()
    available_beds = max(0, total_capacity - occupied_beds)

    today = timezone.now().date()
    today_present = Attendance.objects.filter(date=today, status='PRESENT').count()
    today_absent = Attendance.objects.filter(date=today, status='ABSENT').count()

    pending_complaints = Complaint.objects.filter(status__in=['SUBMITTED', 'UNDER_REVIEW']).count()
    active_visitors = Visitor.objects.filter(exit_time__isnull=True).count()

    recent_complaints = Complaint.objects.select_related('student__user').order_by('-created_at')[:6]
    recent_notices = Notice.objects.filter(is_published=True).order_by('-published_date')[:5]

    context = {
        'warden': warden,
        'assigned_hostel': assigned_hostel,
        'total_rooms': total_rooms,
        'total_capacity': total_capacity,
        'occupied_beds': occupied_beds,
        'available_beds': available_beds,
        'today_present': today_present,
        'today_absent': today_absent,
        'pending_complaints': pending_complaints,
        'active_visitors': active_visitors,
        'recent_complaints': recent_complaints,
        'recent_notices': recent_notices,
    }
    return render(request, 'warden/dashboard.html', context)


@student_required
def student_dashboard_view(request):
    student = request.user.student_profile

    # Current room allocation & roommates
    current_allocation = student.current_allocation
    roommates = []
    if current_allocation:
        roommates = RoomAllocation.objects.filter(
            room=current_allocation.room,
            status='ACTIVE'
        ).exclude(student=student).select_related('student__user')

    # Fee summary
    unpaid_fees = FeeRecord.objects.filter(student=student, remaining_amount__gt=0).order_by('due_date')
    total_pending_fee = sum(f.remaining_amount for f in unpaid_fees)
    recent_payments = Payment.objects.filter(fee_record__student=student).select_related('fee_record__category').order_by('-payment_date')[:5]

    # Attendance summary
    total_attendance = Attendance.objects.filter(student=student).count()
    present_count = Attendance.objects.filter(student=student, status='PRESENT').count()
    attendance_rate = round((present_count / total_attendance * 100), 1) if total_attendance > 0 else 0

    # Recent complaints
    recent_complaints = Complaint.objects.filter(student=student).order_by('-created_at')[:5]

    # Notices
    recent_notices = Notice.objects.filter(is_published=True).exclude(target_audience='WARDENS_ONLY').order_by('-published_date')[:5]

    context = {
        'student': student,
        'current_allocation': current_allocation,
        'roommates': roommates,
        'unpaid_fees': unpaid_fees,
        'total_pending_fee': total_pending_fee,
        'recent_payments': recent_payments,
        'total_attendance': total_attendance,
        'present_count': present_count,
        'attendance_rate': attendance_rate,
        'recent_complaints': recent_complaints,
        'recent_notices': recent_notices,
    }
    return render(request, 'student/dashboard.html', context)


@student_required
def student_profile_view(request):
    student = request.user.student_profile
    return render(request, 'student/my_profile.html', {'student': student})


@student_required
def student_my_room_view(request):
    student = request.user.student_profile
    current_allocation = student.current_allocation
    roommates = []
    if current_allocation:
        roommates = RoomAllocation.objects.filter(
            room=current_allocation.room,
            status='ACTIVE'
        ).exclude(student=student).select_related('student__user')

    past_allocations = student.allocations.exclude(status='ACTIVE').select_related('room__hostel')

    context = {
        'student': student,
        'current_allocation': current_allocation,
        'roommates': roommates,
        'past_allocations': past_allocations,
    }
    return render(request, 'student/my_room.html', context)


@student_required
def student_my_fees_view(request):
    student = request.user.student_profile
    fee_records = FeeRecord.objects.filter(student=student).select_related('category').prefetch_related('payments').order_by('-due_date')
    payments = Payment.objects.filter(fee_record__student=student).select_related('fee_record__category').order_by('-payment_date')

    total_invoiced = sum(f.total_amount for f in fee_records)
    total_paid = sum(f.paid_amount for f in fee_records)
    total_remaining = sum(f.remaining_amount for f in fee_records)

    context = {
        'student': student,
        'fee_records': fee_records,
        'payments': payments,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'total_remaining': total_remaining,
    }
    return render(request, 'student/my_fees.html', context)
