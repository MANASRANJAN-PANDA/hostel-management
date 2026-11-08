from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.decorators import warden_or_admin_required, superadmin_required
from .models import Room
from .forms import RoomForm
from hostels.models import Hostel, Floor
from allocations.models import RoomAllocation

@warden_or_admin_required
def room_list_view(request):
    queryset = Room.objects.select_related('hostel', 'floor').prefetch_related('allocations__student__user').all()

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(room_number__icontains=q) |
            Q(hostel__name__icontains=q) |
            Q(hostel__code__icontains=q)
        )

    # Filter by hostel
    hostel_id = request.GET.get('hostel', '').strip()
    if hostel_id:
        queryset = queryset.filter(hostel_id=hostel_id)

    # Filter by floor
    floor_id = request.GET.get('floor', '').strip()
    if floor_id:
        queryset = queryset.filter(floor_id=floor_id)

    # Filter by type
    room_type = request.GET.get('type', '').strip()
    if room_type:
        queryset = queryset.filter(room_type=room_type)

    # Filter by status
    status = request.GET.get('status', '').strip()
    if status:
        queryset = queryset.filter(room_status=status)

    # Availability filter
    availability = request.GET.get('availability', '').strip()
    if availability == 'available':
        # Has space
        queryset = [r for r in queryset if r.available_beds > 0 and r.room_status != Room.RoomStatus.MAINTENANCE]
    elif availability == 'full':
        queryset = [r for r in queryset if r.is_fully_occupied()]

    # Pagination
    if isinstance(queryset, list):
        paginator = Paginator(queryset, 12)
    else:
        paginator = Paginator(queryset, 12)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    hostels = Hostel.objects.filter(is_active=True)
    floors = Floor.objects.all()

    context = {
        'rooms': page_obj,
        'page_obj': page_obj,
        'q': q,
        'hostel_id': hostel_id,
        'floor_id': floor_id,
        'room_type': room_type,
        'status': status,
        'availability': availability,
        'hostels': hostels,
        'floors': floors,
        'total_count': Room.objects.count(),
        'available_count': Room.objects.filter(room_status__in=['AVAILABLE', 'PARTIALLY_OCCUPIED']).count(),
        'occupied_count': Room.objects.filter(room_status='FULL').count(),
    }
    return render(request, 'admin/rooms/room_list.html', context)


@warden_or_admin_required
def room_detail_view(request, pk):
    room = get_object_or_404(Room.objects.select_related('hostel', 'floor'), pk=pk)
    active_allocations = room.allocations.filter(status='ACTIVE').select_related('student__user')
    allocation_history = room.allocations.exclude(status='ACTIVE').select_related('student__user')[:20]

    context = {
        'room': room,
        'active_allocations': active_allocations,
        'allocation_history': allocation_history,
    }
    return render(request, 'admin/rooms/room_detail.html', context)


@warden_or_admin_required
def room_create_view(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            messages.success(request, f"Room {room.room_number} ({room.hostel.code}) added successfully.")
            return redirect('rooms:room_detail', pk=room.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = RoomForm()

    return render(request, 'admin/rooms/room_form.html', {'form': form, 'title': 'Create New Room'})


@warden_or_admin_required
def room_update_view(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            room = form.save()
            room.update_occupancy_status()
            messages.success(request, f"Room {room.room_number} details updated.")
            return redirect('rooms:room_detail', pk=room.pk)
    else:
        form = RoomForm(instance=room)

    return render(request, 'admin/rooms/room_form.html', {'form': form, 'room': room, 'title': f'Edit Room: {room.room_number}'})


@superadmin_required
def room_delete_view(request, pk):
    room = get_object_or_404(Room, pk=pk)
    active_allocations = room.allocations.filter(status='ACTIVE').count()
    if active_allocations > 0:
        messages.error(request, f"Cannot delete Room {room.room_number}! There are {active_allocations} active student allocations. Vacate or transfer them first.")
        return redirect('rooms:room_detail', pk=room.pk)

    if request.method == 'POST':
        num = room.room_number
        room.delete()
        messages.success(request, f"Room {num} has been deleted.")
        return redirect('rooms:room_list')

    return render(request, 'admin/rooms/room_confirm_delete.html', {'room': room})


def ajax_load_floors(request):
    hostel_id = request.GET.get('hostel_id')
    floors = Floor.objects.filter(hostel_id=hostel_id).order_by('floor_number').values('id', 'floor_name', 'floor_number')
    return JsonResponse(list(floors), safe=False)
