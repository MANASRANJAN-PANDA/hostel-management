from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.decorators import warden_or_admin_required
from .models import Visitor
from .forms import VisitorForm

@warden_or_admin_required
def visitor_list_view(request):
    queryset = Visitor.objects.select_related('student__user', 'recorded_by').all()

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(visitor_name__icontains=q) |
            Q(phone_number__icontains=q) |
            Q(student__reg_number__icontains=q) |
            Q(student__user__first_name__icontains=q)
        )

    # Status: currently inside
    status = request.GET.get('status', '').strip()
    if status == 'inside':
        queryset = queryset.filter(exit_time__isnull=True)
    elif status == 'exited':
        queryset = queryset.filter(exit_time__isnull=False)

    # Date filter
    date_filter = request.GET.get('date', '').strip()
    if date_filter:
        queryset = queryset.filter(entry_time__date=date_filter)

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    currently_inside_count = Visitor.objects.filter(exit_time__isnull=True).count()
    today_count = Visitor.objects.filter(entry_time__date=timezone.now().date()).count()

    context = {
        'visitors': page_obj,
        'page_obj': page_obj,
        'q': q,
        'status': status,
        'date_filter': date_filter,
        'currently_inside_count': currently_inside_count,
        'today_count': today_count,
    }
    return render(request, 'admin/visitors/visitor_list.html', context)


@warden_or_admin_required
def visitor_create_view(request):
    if request.method == 'POST':
        form = VisitorForm(request.POST)
        if form.is_valid():
            visitor = form.save(commit=False)
            visitor.recorded_by = request.user
            visitor.save()
            messages.success(request, f"Visitor '{visitor.visitor_name}' entry registered successfully.")
            return redirect('visitors:visitor_list')
    else:
        form = VisitorForm()

    return render(request, 'admin/visitors/visitor_form.html', {'form': form, 'title': 'Register Hostel Visitor'})


@warden_or_admin_required
def visitor_checkout_view(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    if not visitor.exit_time:
        visitor.exit_time = timezone.now()
        visitor.save()
        messages.success(request, f"Visitor {visitor.visitor_name} checked out at {timezone.localtime(visitor.exit_time).strftime('%I:%M %p')}.")
    else:
        messages.info(request, "Visitor already checked out.")
    return redirect('visitors:visitor_list')
