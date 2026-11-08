from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.decorators import warden_or_admin_required
from .models import Notice
from .forms import NoticeForm

@warden_or_admin_required
def notice_admin_list_view(request):
    queryset = Notice.objects.select_related('created_by').all()

    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(Q(title__icontains=q) | Q(content__icontains=q))

    audience = request.GET.get('audience', '').strip()
    if audience:
        queryset = queryset.filter(target_audience=audience)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'notices': page_obj,
        'page_obj': page_obj,
        'q': q,
        'audience': audience,
        'audiences': Notice.Audience.choices,
    }
    return render(request, 'admin/notices/notice_list.html', context)


@warden_or_admin_required
def notice_create_view(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.created_by = request.user
            notice.save()
            messages.success(request, f"Notice '{notice.title}' published successfully.")
            return redirect('notices:admin_notice_list')
    else:
        form = NoticeForm()

    return render(request, 'admin/notices/notice_form.html', {'form': form, 'title': 'Publish New Notice'})


@warden_or_admin_required
def notice_update_view(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES, instance=notice)
        if form.is_valid():
            notice = form.save()
            messages.success(request, f"Notice '{notice.title}' updated successfully.")
            return redirect('notices:admin_notice_list')
    else:
        form = NoticeForm(instance=notice)

    return render(request, 'admin/notices/notice_form.html', {'form': form, 'notice': notice, 'title': f'Edit Notice: {notice.title}'})


@warden_or_admin_required
def notice_delete_view(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        title = notice.title
        notice.delete()
        messages.success(request, f"Notice '{title}' deleted.")
        return redirect('notices:admin_notice_list')

    return render(request, 'admin/notices/notice_confirm_delete.html', {'notice': notice})


def notice_student_board_view(request):
    # Public / Student Notice Board
    queryset = Notice.objects.filter(is_published=True).exclude(target_audience='WARDENS_ONLY').order_by('-published_date')

    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(Q(title__icontains=q) | Q(content__icontains=q))

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'student/notices_board.html', {'notices': page_obj, 'page_obj': page_obj, 'q': q})


def notice_detail_view(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    return render(request, 'student/notice_detail.html', {'notice': notice})
