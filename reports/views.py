import csv
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from decimal import Decimal
from accounts.decorators import warden_or_admin_required, superadmin_required
from students.models import StudentProfile
from rooms.models import Room
from hostels.models import Hostel
from fees.models import FeeRecord, Payment
from complaints.models import Complaint
from attendance.models import Attendance
from visitors.models import Visitor

@warden_or_admin_required
def reports_index_view(request):
    return render(request, 'admin/reports/index.html')


@warden_or_admin_required
def student_report_view(request):
    queryset = StudentProfile.objects.select_related('user').prefetch_related('allocations__room__hostel').all()

    course = request.GET.get('course', '').strip()
    status = request.GET.get('status', '').strip()

    if course:
        queryset = queryset.filter(course__icontains=course)
    if status:
        queryset = queryset.filter(account_status=status)

    export_csv = request.GET.get('export') == 'csv'
    if export_csv:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="students_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Reg Number', 'Full Name', 'Email', 'Phone', 'Gender', 'Course', 'Department', 'Year', 'Status', 'Room Allocated'])
        for s in queryset:
            room = s.current_room
            room_str = f"{room.hostel.code}-{room.room_number}" if room else "Not Allocated"
            writer.writerow([s.reg_number, s.user.get_display_name(), s.user.email, s.user.phone, s.get_gender_display(), s.course, s.department, s.academic_year, s.get_account_status_display(), room_str])
        return response

    context = {
        'students': queryset,
        'course': course,
        'status': status,
        'total_count': queryset.count(),
    }
    return render(request, 'admin/reports/student_report.html', context)


@warden_or_admin_required
def occupancy_report_view(request):
    hostels = Hostel.objects.prefetch_related('rooms__allocations').all()
    rooms = Room.objects.select_related('hostel', 'floor').all()

    hostel_id = request.GET.get('hostel')
    if hostel_id:
        rooms = rooms.filter(hostel_id=hostel_id)

    total_capacity = sum(r.capacity for r in rooms)
    total_occupied = sum(r.current_occupancy for r in rooms)
    total_available = sum(r.available_beds for r in rooms)
    occupancy_rate = round((total_occupied / total_capacity * 100), 1) if total_capacity > 0 else 0

    export_csv = request.GET.get('export') == 'csv'
    if export_csv:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="occupancy_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Hostel', 'Floor', 'Room Number', 'Type', 'Capacity', 'Occupied Beds', 'Available Beds', 'Status', 'Monthly Rent'])
        for r in rooms:
            writer.writerow([r.hostel.name, r.floor.floor_name, r.room_number, r.get_room_type_display(), r.capacity, r.current_occupancy, r.available_beds, r.get_room_status_display(), r.monthly_rent])
        return response

    context = {
        'rooms': rooms,
        'hostels': hostels,
        'total_capacity': total_capacity,
        'total_occupied': total_occupied,
        'total_available': total_available,
        'occupancy_rate': occupancy_rate,
        'selected_hostel': hostel_id,
    }
    return render(request, 'admin/reports/occupancy_report.html', context)


@warden_or_admin_required
def fee_collection_report_view(request):
    payments = Payment.objects.select_related('fee_record__student__user', 'fee_record__category', 'received_by').all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    method = request.GET.get('method')

    if start_date:
        payments = payments.filter(payment_date__gte=start_date)
    if end_date:
        payments = payments.filter(payment_date__lte=end_date)
    if method:
        payments = payments.filter(payment_method=method)

    total_collected = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    export_csv = request.GET.get('export') == 'csv'
    if export_csv:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="fee_collection_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Receipt No', 'Date', 'Student Reg No', 'Student Name', 'Category', 'Amount (₹)', 'Payment Method', 'Transaction Ref', 'Received By'])
        for p in payments:
            writer.writerow([
                p.receipt_number, p.payment_date, p.fee_record.student.reg_number,
                p.fee_record.student.user.get_display_name(), p.fee_record.category.name,
                p.amount, p.get_payment_method_display(), p.transaction_reference or '',
                p.received_by.get_display_name() if p.received_by else 'Admin'
            ])
        return response

    context = {
        'payments': payments,
        'total_collected': total_collected,
        'start_date': start_date,
        'end_date': end_date,
        'method': method,
    }
    return render(request, 'admin/reports/fee_collection_report.html', context)


@warden_or_admin_required
def pending_fee_report_view(request):
    fee_records = FeeRecord.objects.filter(remaining_amount__gt=0).select_related('student__user', 'category')

    month = request.GET.get('month')
    if month:
        fee_records = fee_records.filter(billing_month=month)

    total_pending = fee_records.aggregate(total=Sum('remaining_amount'))['total'] or Decimal('0.00')

    export_csv = request.GET.get('export') == 'csv'
    if export_csv:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="pending_fee_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Student Reg No', 'Student Name', 'Fee Title', 'Category', 'Billing Month', 'Total Amount', 'Paid Amount', 'Remaining Amount', 'Due Date', 'Status'])
        for f in fee_records:
            writer.writerow([
                f.student.reg_number, f.student.user.get_display_name(), f.title,
                f.category.name, f.billing_month, f.total_amount, f.paid_amount,
                f.remaining_amount, f.due_date, f.get_status_display()
            ])
        return response

    context = {
        'fee_records': fee_records,
        'total_pending': total_pending,
        'month': month,
    }
    return render(request, 'admin/reports/pending_fee_report.html', context)


@warden_or_admin_required
def complaint_report_view(request):
    complaints = Complaint.objects.select_related('student__user', 'assigned_warden__user').all()

    category = request.GET.get('category')
    status = request.GET.get('status')
    if category:
        complaints = complaints.filter(category=category)
    if status:
        complaints = complaints.filter(status=status)

    export_csv = request.GET.get('export') == 'csv'
    if export_csv:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="complaint_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Date', 'Student Reg No', 'Student Name', 'Category', 'Title', 'Status', 'Assigned Warden', 'Resolved At'])
        for c in complaints:
            writer.writerow([
                c.id, c.created_at.strftime('%Y-%m-%d %H:%M'), c.student.reg_number,
                c.student.user.get_display_name(), c.get_category_display(), c.title,
                c.get_status_display(), c.assigned_warden.user.get_display_name() if c.assigned_warden else 'Unassigned',
                c.resolved_at.strftime('%Y-%m-%d %H:%M') if c.resolved_at else ''
            ])
        return response

    context = {
        'complaints': complaints,
        'total_count': complaints.count(),
        'category': category,
        'status': status,
    }
    return render(request, 'admin/reports/complaint_report.html', context)


@warden_or_admin_required
def attendance_report_view(request):
    records = Attendance.objects.select_related('student__user').all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        records = records.filter(date__gte=start_date)
    if end_date:
        records = records.filter(date__lte=end_date)

    total_records = records.count()
    present_count = records.filter(status='PRESENT').count()
    absent_count = records.filter(status='ABSENT').count()
    overall_pct = round((present_count / total_records * 100), 1) if total_records > 0 else 0

    export_csv = request.GET.get('export') == 'csv'
    if export_csv:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Date', 'Student Reg No', 'Student Name', 'Status', 'Remarks', 'Recorded By'])
        for a in records:
            writer.writerow([
                a.date, a.student.reg_number, a.student.user.get_display_name(),
                a.get_status_display(), a.remarks or '', a.recorded_by.get_display_name() if a.recorded_by else ''
            ])
        return response

    context = {
        'records': records[:100],
        'total_records': total_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'overall_pct': overall_pct,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'admin/reports/attendance_report.html', context)


@warden_or_admin_required
def visitor_report_view(request):
    visitors = Visitor.objects.select_related('student__user', 'recorded_by').all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date:
        visitors = visitors.filter(entry_time__date__gte=start_date)
    if end_date:
        visitors = visitors.filter(entry_time__date__lte=end_date)

    export_csv = request.GET.get('export') == 'csv'
    if export_csv:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="visitor_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Visitor Name', 'Phone', 'Student Reg No', 'Student Name', 'Relationship', 'Purpose', 'Entry Time', 'Exit Time'])
        for v in visitors:
            writer.writerow([
                v.visitor_name, v.phone_number, v.student.reg_number,
                v.student.user.get_display_name(), v.relationship, v.purpose,
                v.entry_time.strftime('%Y-%m-%d %H:%M'),
                v.exit_time.strftime('%Y-%m-%d %H:%M') if v.exit_time else 'Still Inside'
            ])
        return response

    context = {
        'visitors': visitors,
        'total_count': visitors.count(),
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'admin/reports/visitor_report.html', context)
