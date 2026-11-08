from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q, Count
from accounts.decorators import warden_or_admin_required, student_required
from .models import Attendance
from .forms import SingleAttendanceForm
from students.models import StudentProfile
from hostels.models import Hostel
from allocations.models import RoomAllocation

@warden_or_admin_required
def attendance_list_view(request):
    selected_date_str = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
    hostel_id = request.GET.get('hostel', '').strip()
    status = request.GET.get('status', '').strip()
    q = request.GET.get('q', '').strip()

    try:
        selected_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        selected_date = timezone.now().date()
        selected_date_str = selected_date.strftime('%Y-%m-%d')

    queryset = Attendance.objects.filter(date=selected_date).select_related('student__user', 'recorded_by').prefetch_related('student__allocations__room__hostel')

    if hostel_id:
        queryset = queryset.filter(student__allocations__room__hostel_id=hostel_id, student__allocations__status='ACTIVE')

    if status:
        queryset = queryset.filter(status=status)

    if q:
        queryset = queryset.filter(
            Q(student__reg_number__icontains=q) |
            Q(student__user__first_name__icontains=q) |
            Q(student__user__last_name__icontains=q)
        )

    paginator = Paginator(queryset, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Date summary stats
    total_marked = Attendance.objects.filter(date=selected_date).count()
    present_marked = Attendance.objects.filter(date=selected_date, status='PRESENT').count()
    absent_marked = Attendance.objects.filter(date=selected_date, status='ABSENT').count()
    hostels = Hostel.objects.filter(is_active=True)

    context = {
        'attendances': page_obj,
        'page_obj': page_obj,
        'selected_date': selected_date_str,
        'hostel_id': hostel_id,
        'status': status,
        'q': q,
        'hostels': hostels,
        'total_marked': total_marked,
        'present_marked': present_marked,
        'absent_marked': absent_marked,
    }
    return render(request, 'admin/attendance/attendance_list.html', context)


@warden_or_admin_required
def attendance_mark_batch_view(request):
    selected_date_str = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
    hostel_id = request.GET.get('hostel', '').strip()

    try:
        selected_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        selected_date = timezone.now().date()
        selected_date_str = selected_date.strftime('%Y-%m-%d')

    # Get active students with room allocations
    students_query = StudentProfile.objects.filter(
        account_status='ACTIVE',
        allocations__status='ACTIVE'
    ).select_related('user').prefetch_related('allocations__room__hostel').order_by('allocations__room__room_number', 'reg_number')

    if hostel_id:
        students_query = students_query.filter(allocations__room__hostel_id=hostel_id)

    students = students_query.distinct()

    # Existing attendance for selected date
    existing_att = {
        att.student_id: att
        for att in Attendance.objects.filter(date=selected_date, student__in=students)
    }

    if request.method == 'POST':
        # Process batch attendance submission
        post_date_str = request.POST.get('attendance_date', selected_date_str)
        try:
            post_date = timezone.datetime.strptime(post_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            post_date = selected_date

        with transaction.atomic():
            for student in students:
                status_val = request.POST.get(f'status_{student.id}', 'PRESENT')
                remarks_val = request.POST.get(f'remarks_{student.id}', '').strip()

                Attendance.objects.update_or_create(
                    student=student,
                    date=post_date,
                    defaults={
                        'status': status_val,
                        'remarks': remarks_val,
                        'recorded_by': request.user,
                    }
                )

        messages.success(request, f"Attendance for {len(students)} students on {post_date} recorded successfully.")
        return redirect(f"{request.path}?date={post_date}&hostel={hostel_id}")

    student_records = []
    for s in students:
        att = existing_att.get(s.id)
        current_alloc = s.current_allocation
        room_label = f"{current_alloc.room.hostel.code}-{current_alloc.room.room_number}" if current_alloc else "N/A"
        student_records.append({
            'student': s,
            'room_label': room_label,
            'status': att.status if att else 'PRESENT',
            'remarks': att.remarks if att else '',
        })

    hostels = Hostel.objects.filter(is_active=True)

    context = {
        'student_records': student_records,
        'selected_date': selected_date_str,
        'hostel_id': hostel_id,
        'hostels': hostels,
        'total_count': len(student_records),
    }
    return render(request, 'admin/attendance/batch_attendance.html', context)


@warden_or_admin_required
def attendance_single_add_view(request):
    if request.method == 'POST':
        form = SingleAttendanceForm(request.POST)
        if form.is_valid():
            att = form.save(commit=False)
            att.recorded_by = request.user
            try:
                att.save()
                messages.success(request, f"Attendance for {att.student.reg_number} on {att.date} saved.")
                return redirect('attendance:attendance_list')
            except Exception as e:
                messages.error(request, f"Record for {att.student.reg_number} on {att.date} already exists or error: {str(e)}")
    else:
        form = SingleAttendanceForm()

    return render(request, 'admin/attendance/attendance_form.html', {'form': form, 'title': 'Mark Single Student Attendance'})


@student_required
def student_my_attendance_view(request):
    student = request.user.student_profile
    month_filter = request.GET.get('month', timezone.now().strftime('%Y-%m'))

    records = Attendance.objects.filter(
        student=student,
        date__startswith=month_filter
    ).order_by('-date')

    total_days = records.count()
    present_days = records.filter(status='PRESENT').count()
    absent_days = records.filter(status='ABSENT').count()
    pct = round((present_days / total_days * 100), 1) if total_days > 0 else 0

    all_time_total = Attendance.objects.filter(student=student).count()
    all_time_present = Attendance.objects.filter(student=student, status='PRESENT').count()
    all_time_pct = round((all_time_present / all_time_total * 100), 1) if all_time_total > 0 else 0

    context = {
        'records': records,
        'month_filter': month_filter,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'pct': pct,
        'all_time_total': all_time_total,
        'all_time_present': all_time_present,
        'all_time_pct': all_time_pct,
    }
    return render(request, 'student/my_attendance.html', context)
