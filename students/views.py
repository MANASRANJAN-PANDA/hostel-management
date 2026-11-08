from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from accounts.decorators import warden_or_admin_required, superadmin_required
from .models import StudentProfile
from .forms import StudentAdminForm
from hostels.models import Hostel
from allocations.models import RoomAllocation

@warden_or_admin_required
def student_list_view(request):
    queryset = StudentProfile.objects.select_related('user').prefetch_related('allocations__room__hostel').all()

    # Search query
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__email__icontains=q) |
            Q(reg_number__icontains=q) |
            Q(roll_number__icontains=q) |
            Q(user__phone__icontains=q)
        )

    # Filter by course
    course = request.GET.get('course', '').strip()
    if course:
        queryset = queryset.filter(course__icontains=course)

    # Filter by department
    department = request.GET.get('department', '').strip()
    if department:
        queryset = queryset.filter(department__icontains=department)

    # Filter by academic year
    year = request.GET.get('year', '').strip()
    if year:
        queryset = queryset.filter(academic_year=year)

    # Filter by status
    status = request.GET.get('status', '').strip()
    if status:
        queryset = queryset.filter(account_status=status)

    # Filter by hostel
    hostel_id = request.GET.get('hostel', '').strip()
    if hostel_id:
        queryset = queryset.filter(allocations__room__hostel_id=hostel_id, allocations__status='ACTIVE')

    # Sorting
    sort = request.GET.get('sort', '-created_at')
    queryset = queryset.order_by(sort)

    # Pagination
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Stats for quick badges
    total_count = StudentProfile.objects.count()
    pending_count = StudentProfile.objects.filter(account_status='PENDING').count()
    active_count = StudentProfile.objects.filter(account_status='ACTIVE').count()
    hostels = Hostel.objects.filter(is_active=True)

    context = {
        'students': page_obj,
        'page_obj': page_obj,
        'q': q,
        'course': course,
        'department': department,
        'year': year,
        'status': status,
        'hostel_id': hostel_id,
        'hostels': hostels,
        'total_count': total_count,
        'pending_count': pending_count,
        'active_count': active_count,
    }
    return render(request, 'admin/students/student_list.html', context)


@warden_or_admin_required
def student_detail_view(request, pk):
    student = get_object_or_404(
        StudentProfile.objects.select_related('user').prefetch_related(
            'allocations__room__hostel',
            'fee_records__category',
            'fee_records__payments',
            'complaints',
            'attendances'
        ),
        pk=pk
    )

    # Current room and roommates
    current_allocation = student.current_allocation
    roommates = []
    if current_allocation:
        roommates = RoomAllocation.objects.filter(
            room=current_allocation.room,
            status='ACTIVE'
        ).exclude(student=student).select_related('student__user')

    # Fee summary
    fee_records = student.fee_records.all()[:10]
    total_fee = sum(f.total_amount for f in fee_records)
    total_paid = sum(f.paid_amount for f in fee_records)
    total_pending = sum(f.remaining_amount for f in fee_records)

    # Attendance stats
    attendances = student.attendances.order_by('-date')[:15]
    total_att = student.attendances.count()
    present_att = student.attendances.filter(status='PRESENT').count()
    attendance_rate = round((present_att / total_att * 100), 1) if total_att > 0 else 0

    # Complaints
    complaints = student.complaints.order_by('-created_at')[:10]

    context = {
        'student': student,
        'current_allocation': current_allocation,
        'roommates': roommates,
        'fee_records': fee_records,
        'total_fee': total_fee,
        'total_paid': total_paid,
        'total_pending': total_pending,
        'attendances': attendances,
        'attendance_rate': attendance_rate,
        'complaints': complaints,
    }
    return render(request, 'admin/students/student_detail.html', context)


@warden_or_admin_required
def student_create_view(request):
    if request.method == 'POST':
        form = StudentAdminForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student {student.user.get_display_name()} ({student.reg_number}) created successfully.")
            return redirect('students:student_detail', pk=student.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = StudentAdminForm()

    return render(request, 'admin/students/student_form.html', {'form': form, 'title': 'Add New Student'})


@warden_or_admin_required
def student_update_view(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    if request.method == 'POST':
        form = StudentAdminForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student profile for {student.user.get_display_name()} updated successfully.")
            return redirect('students:student_detail', pk=student.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = StudentAdminForm(instance=student)

    return render(request, 'admin/students/student_form.html', {'form': form, 'student': student, 'title': f'Edit Student: {student.reg_number}'})


@superadmin_required
def student_delete_view(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    if request.method == 'POST':
        user = student.user
        name = user.get_display_name()
        reg = student.reg_number
        user.delete()
        messages.success(request, f"Student {name} ({reg}) has been permanently deleted.")
        return redirect('students:student_list')

    return render(request, 'admin/students/student_confirm_delete.html', {'student': student})


@warden_or_admin_required
def student_approve_view(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    student.account_status = StudentProfile.AccountStatus.ACTIVE
    student.save()
    student.user.is_approved = True
    student.user.is_active = True
    student.user.save()
    messages.success(request, f"Student registration for {student.user.get_display_name()} ({student.reg_number}) has been APPROVED.")
    return redirect('students:student_list')


@warden_or_admin_required
def student_reject_view(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    student.account_status = StudentProfile.AccountStatus.INACTIVE
    student.save()
    student.user.is_approved = False
    student.user.is_active = False
    student.user.save()
    messages.warning(request, f"Student registration for {student.user.get_display_name()} ({student.reg_number}) has been REJECTED / DEACTIVATED.")
    return redirect('students:student_list')
