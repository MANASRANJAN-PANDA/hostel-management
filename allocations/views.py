from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.decorators import warden_or_admin_required
from .models import RoomAllocation
from .forms import RoomAllocationForm, RoomTransferForm, RoomVacateForm
from hostels.models import Hostel
from rooms.models import Room

@warden_or_admin_required
def allocation_list_view(request):
    queryset = RoomAllocation.objects.select_related('student__user', 'room__hostel', 'allocated_by').all()

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(student__user__first_name__icontains=q) |
            Q(student__user__last_name__icontains=q) |
            Q(student__reg_number__icontains=q) |
            Q(room__room_number__icontains=q) |
            Q(room__hostel__name__icontains=q)
        )

    # Status filter
    status = request.GET.get('status', 'ACTIVE').strip()
    if status and status != 'ALL':
        queryset = queryset.filter(status=status)

    # Hostel filter
    hostel_id = request.GET.get('hostel', '').strip()
    if hostel_id:
        queryset = queryset.filter(room__hostel_id=hostel_id)

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    hostels = Hostel.objects.filter(is_active=True)

    context = {
        'allocations': page_obj,
        'page_obj': page_obj,
        'q': q,
        'status': status,
        'hostel_id': hostel_id,
        'hostels': hostels,
        'active_count': RoomAllocation.objects.filter(status='ACTIVE').count(),
        'vacated_count': RoomAllocation.objects.filter(status='VACATED').count(),
    }
    return render(request, 'admin/allocations/allocation_list.html', context)


@warden_or_admin_required
def allocation_create_view(request):
    if request.method == 'POST':
        form = RoomAllocationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    allocation = form.save(commit=False)
                    allocation.allocated_by = request.user
                    allocation.save()
                    messages.success(
                        request,
                        f"Room {allocation.room.room_number} ({allocation.room.hostel.code}) allocated to student {allocation.student.reg_number} ({allocation.student.user.get_display_name()}) successfully."
                    )
                    return redirect('allocations:allocation_list')
            except Exception as e:
                messages.error(request, f"Error completing allocation: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = RoomAllocationForm()

    return render(request, 'admin/allocations/allocation_form.html', {'form': form, 'title': 'Allocate Room to Student'})


@warden_or_admin_required
def allocation_transfer_view(request, pk):
    allocation = get_object_or_404(RoomAllocation.objects.select_related('student__user', 'room__hostel'), pk=pk, status='ACTIVE')

    if request.method == 'POST':
        form = RoomTransferForm(current_room=allocation.room, data=request.POST)
        if form.is_valid():
            new_room = form.cleaned_data['new_room']
            transfer_date = form.cleaned_data['transfer_date']
            reason = form.cleaned_data['reason']

            try:
                with transaction.atomic():
                    # 1. Update old allocation
                    old_room = allocation.room
                    allocation.status = RoomAllocation.AllocationStatus.TRANSFERRED
                    allocation.vacating_date = transfer_date
                    allocation.notes = f"{allocation.notes or ''}\nTransferred to {new_room.hostel.code}-{new_room.room_number}: {reason}".strip()
                    allocation.save()
                    old_room.update_occupancy_status()

                    # 2. Create new allocation
                    new_alloc = RoomAllocation.objects.create(
                        student=allocation.student,
                        room=new_room,
                        allocation_date=transfer_date,
                        status=RoomAllocation.AllocationStatus.ACTIVE,
                        notes=f"Transferred from {old_room.hostel.code}-{old_room.room_number}. Reason: {reason}",
                        allocated_by=request.user
                    )
                    new_room.update_occupancy_status()

                    messages.success(
                        request,
                        f"Student {allocation.student.reg_number} successfully transferred from {old_room.hostel.code}-{old_room.room_number} to {new_room.hostel.code}-{new_room.room_number}."
                    )
                    return redirect('allocations:allocation_list')
            except Exception as e:
                messages.error(request, f"Transfer failed: {str(e)}")
    else:
        form = RoomTransferForm(current_room=allocation.room)

    context = {
        'form': form,
        'allocation': allocation,
        'title': f'Transfer Student: {allocation.student.reg_number}'
    }
    return render(request, 'admin/allocations/allocation_transfer.html', context)


@warden_or_admin_required
def allocation_vacate_view(request, pk):
    allocation = get_object_or_404(RoomAllocation.objects.select_related('student__user', 'room__hostel'), pk=pk, status='ACTIVE')

    if request.method == 'POST':
        form = RoomVacateForm(request.POST)
        if form.is_valid():
            vacate_date = form.cleaned_data['vacate_date']
            remarks = form.cleaned_data['remarks']
            try:
                with transaction.atomic():
                    allocation.status = RoomAllocation.AllocationStatus.VACATED
                    allocation.vacating_date = vacate_date
                    allocation.notes = f"{allocation.notes or ''}\nVacated on {vacate_date}. Clearance: {remarks}".strip()
                    allocation.save()
                    allocation.room.update_occupancy_status()

                    messages.success(
                        request,
                        f"Room {allocation.room.room_number} vacated by student {allocation.student.reg_number}. Room availability updated."
                    )
                    return redirect('allocations:allocation_list')
            except Exception as e:
                messages.error(request, f"Vacating error: {str(e)}")
    else:
        form = RoomVacateForm()

    context = {
        'form': form,
        'allocation': allocation,
        'title': f'Vacate Room: {allocation.room.room_number} ({allocation.student.reg_number})'
    }
    return render(request, 'admin/allocations/allocation_vacate.html', context)
