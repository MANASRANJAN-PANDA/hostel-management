from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import superadmin_required
from .models import WardenProfile
from .forms import WardenForm
from hostels.models import Hostel

@superadmin_required
def warden_list_view(request):
    wardens = WardenProfile.objects.select_related('user', 'assigned_hostel').all()

    q = request.GET.get('q', '').strip()
    if q:
        wardens = wardens.filter(
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__email__icontains=q) |
            Q(phone__icontains=q) |
            Q(assigned_hostel__name__icontains=q)
        )

    hostel_id = request.GET.get('hostel', '').strip()
    if hostel_id:
        wardens = wardens.filter(assigned_hostel_id=hostel_id)

    hostels = Hostel.objects.filter(is_active=True)

    context = {
        'wardens': wardens,
        'q': q,
        'hostel_id': hostel_id,
        'hostels': hostels,
        'total_count': wardens.count(),
    }
    return render(request, 'admin/wardens/warden_list.html', context)


@superadmin_required
def warden_create_view(request):
    if request.method == 'POST':
        form = WardenForm(request.POST, request.FILES)
        if form.is_valid():
            warden = form.save()
            messages.success(request, f"Warden {warden.user.get_display_name()} created successfully.")
            return redirect('wardens:warden_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = WardenForm()

    return render(request, 'admin/wardens/warden_form.html', {'form': form, 'title': 'Add New Warden'})


@superadmin_required
def warden_update_view(request, pk):
    warden = get_object_or_404(WardenProfile, pk=pk)
    if request.method == 'POST':
        form = WardenForm(request.POST, request.FILES, instance=warden)
        if form.is_valid():
            warden = form.save()
            messages.success(request, f"Warden {warden.user.get_display_name()} updated successfully.")
            return redirect('wardens:warden_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = WardenForm(instance=warden)

    return render(request, 'admin/wardens/warden_form.html', {'form': form, 'warden': warden, 'title': f'Edit Warden: {warden.user.get_display_name()}'})


@superadmin_required
def warden_delete_view(request, pk):
    warden = get_object_or_404(WardenProfile, pk=pk)
    if request.method == 'POST':
        user = warden.user
        name = user.get_display_name()
        user.delete()
        messages.success(request, f"Warden account {name} has been deleted.")
        return redirect('wardens:warden_list')

    return render(request, 'admin/wardens/warden_confirm_delete.html', {'warden': warden})


@superadmin_required
def warden_toggle_status_view(request, pk):
    warden = get_object_or_404(WardenProfile, pk=pk)
    warden.user.is_active = not warden.user.is_active
    warden.user.save()
    status_str = "activated" if warden.user.is_active else "deactivated"
    messages.success(request, f"Warden account {warden.user.get_display_name()} has been {status_str}.")
    return redirect('wardens:warden_list')
