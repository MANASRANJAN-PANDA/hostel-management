from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.decorators import warden_or_admin_required, student_required
from .models import Complaint, ComplaintHistory
from .forms import StudentComplaintForm, ComplaintStatusUpdateForm

@warden_or_admin_required
def complaint_list_view(request):
    queryset = Complaint.objects.select_related('student__user', 'assigned_warden__user').prefetch_related('history').all()

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(student__reg_number__icontains=q) |
            Q(student__user__first_name__icontains=q)
        )

    # Category filter
    category = request.GET.get('category', '').strip()
    if category:
        queryset = queryset.filter(category=category)

    # Status filter
    status = request.GET.get('status', '').strip()
    if status:
        queryset = queryset.filter(status=status)

    # If warden, option to view only their assigned hostel or complaints
    if request.user.is_warden() and hasattr(request.user, 'warden_profile'):
        warden = request.user.warden_profile
        my_only = request.GET.get('assigned_to_me')
        if my_only:
            queryset = queryset.filter(assigned_warden=warden)

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'complaints': page_obj,
        'page_obj': page_obj,
        'q': q,
        'category': category,
        'status': status,
        'categories': Complaint.Category.choices,
        'statuses': Complaint.Status.choices,
        'total_count': Complaint.objects.count(),
        'pending_count': Complaint.objects.filter(status__in=['SUBMITTED', 'UNDER_REVIEW']).count(),
        'in_progress_count': Complaint.objects.filter(status='IN_PROGRESS').count(),
        'resolved_count': Complaint.objects.filter(status='RESOLVED').count(),
    }
    return render(request, 'admin/complaints/complaint_list.html', context)


@warden_or_admin_required
def complaint_detail_view(request, pk):
    complaint = get_object_or_404(
        Complaint.objects.select_related('student__user', 'assigned_warden__user').prefetch_related('history__action_by'),
        pk=pk
    )

    if request.method == 'POST':
        form = ComplaintStatusUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            old_status = complaint.status
            new_complaint = form.save(commit=False)
            new_status = form.cleaned_data['status']
            remarks = form.cleaned_data.get('remarks', '')

            if new_status == Complaint.Status.RESOLVED and not new_complaint.resolved_at:
                new_complaint.resolved_at = timezone.now()

            new_complaint.save()

            # Record in history
            ComplaintHistory.objects.create(
                complaint=new_complaint,
                action_by=request.user,
                status_from=old_status,
                status_to=new_status,
                remarks=remarks or f"Status changed from {old_status} to {new_status}."
            )

            messages.success(request, f"Complaint #{complaint.id} status updated to {new_complaint.get_status_display()}.")
            return redirect('complaints:complaint_detail', pk=complaint.pk)
    else:
        form = ComplaintStatusUpdateForm(instance=complaint)

    context = {
        'complaint': complaint,
        'history': complaint.history.all(),
        'form': form,
    }
    return render(request, 'admin/complaints/complaint_detail.html', context)


@student_required
def student_complaint_submit_view(request):
    student = request.user.student_profile
    if request.method == 'POST':
        form = StudentComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.student = student
            complaint.status = Complaint.Status.SUBMITTED
            complaint.save()

            # Initial history record
            ComplaintHistory.objects.create(
                complaint=complaint,
                action_by=request.user,
                status_from="NEW",
                status_to="SUBMITTED",
                remarks="Complaint logged by student."
            )

            messages.success(request, f"Your complaint #{complaint.id} ('{complaint.title}') has been registered successfully. The warden has been notified.")
            return redirect('complaints:my_complaints')
    else:
        form = StudentComplaintForm()

    return render(request, 'student/complaint_submit.html', {'form': form})


@student_required
def student_my_complaints_view(request):
    student = request.user.student_profile
    complaints = Complaint.objects.filter(student=student).prefetch_related('history').order_by('-created_at')

    status = request.GET.get('status', '').strip()
    if status:
        complaints = complaints.filter(status=status)

    paginator = Paginator(complaints, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'complaints': page_obj,
        'page_obj': page_obj,
        'status': status,
        'statuses': Complaint.Status.choices,
    }
    return render(request, 'student/my_complaints.html', context)
