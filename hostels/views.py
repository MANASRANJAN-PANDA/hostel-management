from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from accounts.decorators import warden_or_admin_required, superadmin_required
from .models import Hostel, Floor
from .forms import HostelForm, FloorForm

@warden_or_admin_required
def hostel_list_view(request):
    hostels = Hostel.objects.prefetch_related('floors', 'rooms').all()
    return render(request, 'admin/hostels/hostel_list.html', {'hostels': hostels})


@superadmin_required
def hostel_create_view(request):
    if request.method == 'POST':
        form = HostelForm(request.POST)
        if form.is_valid():
            hostel = form.save()
            messages.success(request, f"Hostel building '{hostel.name}' created successfully.")
            return redirect('hostels:hostel_list')
    else:
        form = HostelForm()
    return render(request, 'admin/hostels/hostel_form.html', {'form': form, 'title': 'Add New Hostel Building'})


@superadmin_required
def hostel_update_view(request, pk):
    hostel = get_object_or_404(Hostel, pk=pk)
    if request.method == 'POST':
        form = HostelForm(request.POST, instance=hostel)
        if form.is_valid():
            hostel = form.save()
            messages.success(request, f"Hostel building '{hostel.name}' updated successfully.")
            return redirect('hostels:hostel_list')
    else:
        form = HostelForm(instance=hostel)
    return render(request, 'admin/hostels/hostel_form.html', {'form': form, 'hostel': hostel, 'title': f'Edit Hostel: {hostel.name}'})


@superadmin_required
def floor_create_view(request, hostel_id=None):
    initial = {}
    if hostel_id:
        initial['hostel'] = get_object_or_404(Hostel, pk=hostel_id)

    if request.method == 'POST':
        form = FloorForm(request.POST)
        if form.is_valid():
            floor = form.save()
            messages.success(request, f"Floor '{floor.floor_name}' added to {floor.hostel.name}.")
            return redirect('hostels:hostel_list')
    else:
        form = FloorForm(initial=initial)
    return render(request, 'admin/hostels/floor_form.html', {'form': form, 'title': 'Add Floor'})
