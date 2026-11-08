from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from decimal import Decimal
from accounts.decorators import warden_or_admin_required, student_required
from .models import FeeCategory, FeeRecord, Payment
from .forms import FeeCategoryForm, FeeRecordCreateForm, BatchFeeGenerateForm, PaymentRecordForm
from students.models import StudentProfile

@warden_or_admin_required
def fee_list_view(request):
    queryset = FeeRecord.objects.select_related('student__user', 'category').all()

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(student__user__first_name__icontains=q) |
            Q(student__user__last_name__icontains=q) |
            Q(student__reg_number__icontains=q) |
            Q(title__icontains=q)
        )

    # Status filter
    status = request.GET.get('status', '').strip()
    if status:
        queryset = queryset.filter(status=status)

    # Category filter
    category_id = request.GET.get('category', '').strip()
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    # Billing month filter
    month = request.GET.get('month', '').strip()
    if month:
        queryset = queryset.filter(billing_month=month)

    # Aggregates for dashboard summary
    total_invoiced = queryset.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    total_collected = queryset.aggregate(total=Sum('paid_amount'))['total'] or Decimal('0.00')
    total_outstanding = queryset.aggregate(total=Sum('remaining_amount'))['total'] or Decimal('0.00')

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = FeeCategory.objects.all()

    context = {
        'fee_records': page_obj,
        'page_obj': page_obj,
        'q': q,
        'status': status,
        'category_id': category_id,
        'month': month,
        'categories': categories,
        'total_invoiced': total_invoiced,
        'total_collected': total_collected,
        'total_outstanding': total_outstanding,
    }
    return render(request, 'admin/fees/fee_list.html', context)


@warden_or_admin_required
def fee_create_view(request):
    if request.method == 'POST':
        form = FeeRecordCreateForm(request.POST)
        if form.is_valid():
            fee = form.save(commit=False)
            fee.remaining_amount = fee.total_amount
            fee.status = FeeRecord.PaymentStatus.PENDING
            fee.save()
            messages.success(request, f"Fee record '{fee.title}' created for {fee.student.reg_number}.")
            return redirect('fees:fee_list')
    else:
        form = FeeRecordCreateForm()

    return render(request, 'admin/fees/fee_form.html', {'form': form, 'title': 'Create Student Fee Record'})


@warden_or_admin_required
def fee_batch_generate_view(request):
    if request.method == 'POST':
        form = BatchFeeGenerateForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            title = form.cleaned_data['title']
            billing_month = form.cleaned_data['billing_month']
            total_amount = form.cleaned_data['total_amount']
            due_date = form.cleaned_data['due_date']
            target_group = form.cleaned_data['target_group']
            hostel = form.cleaned_data.get('hostel')

            students = StudentProfile.objects.filter(account_status='ACTIVE')
            if target_group == 'HOSTEL_RESIDENTS':
                students = students.filter(allocations__status='ACTIVE')
                if hostel:
                    students = students.filter(allocations__room__hostel=hostel)
            elif hostel:
                students = students.filter(allocations__room__hostel=hostel, allocations__status='ACTIVE')

            students = students.distinct()

            created_count = 0
            with transaction.atomic():
                for student in students:
                    FeeRecord.objects.create(
                        student=student,
                        category=category,
                        title=title,
                        billing_month=billing_month,
                        total_amount=total_amount,
                        remaining_amount=total_amount,
                        due_date=due_date,
                        status=FeeRecord.PaymentStatus.PENDING
                    )
                    created_count += 1

            messages.success(request, f"Successfully batch generated {created_count} fee records of ₹{total_amount} each for {title}.")
            return redirect('fees:fee_list')
    else:
        form = BatchFeeGenerateForm()

    return render(request, 'admin/fees/batch_fee_form.html', {'form': form, 'title': 'Batch Generate Student Fees'})


@warden_or_admin_required
def payment_record_view(request, fee_id):
    fee_record = get_object_or_404(FeeRecord.objects.select_related('student__user', 'category'), pk=fee_id)

    if fee_record.remaining_amount <= Decimal('0.00'):
        messages.info(request, "This fee record is already fully paid.")
        return redirect('fees:fee_list')

    if request.method == 'POST':
        form = PaymentRecordForm(fee_record=fee_record, data=request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.fee_record = fee_record
            payment.received_by = request.user
            payment.save()

            messages.success(request, f"Payment of ₹{payment.amount} recorded successfully. Receipt #{payment.receipt_number} generated.")
            return redirect('fees:receipt_detail', receipt_number=payment.receipt_number)
    else:
        form = PaymentRecordForm(fee_record=fee_record)

    context = {
        'form': form,
        'fee_record': fee_record,
        'title': f'Record Payment for {fee_record.student.reg_number}'
    }
    return render(request, 'admin/fees/payment_form.html', context)


@warden_or_admin_required
def payment_list_view(request):
    queryset = Payment.objects.select_related('fee_record__student__user', 'fee_record__category', 'received_by').all()

    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(receipt_number__icontains=q) |
            Q(transaction_reference__icontains=q) |
            Q(fee_record__student__reg_number__icontains=q) |
            Q(fee_record__student__user__first_name__icontains=q)
        )

    method = request.GET.get('method', '').strip()
    if method:
        queryset = queryset.filter(payment_method=method)

    paginator = Paginator(queryset, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_amount = queryset.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    context = {
        'payments': page_obj,
        'page_obj': page_obj,
        'q': q,
        'method': method,
        'total_amount': total_amount,
    }
    return render(request, 'admin/fees/payment_list.html', context)


def receipt_detail_view(request, receipt_number):
    payment = get_object_or_404(
        Payment.objects.select_related(
            'fee_record__student__user',
            'fee_record__category',
            'received_by'
        ),
        receipt_number=receipt_number
    )

    # Permission check: superadmin or warden or the owner student
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    if request.user.is_student():
        if not hasattr(request.user, 'student_profile') or payment.fee_record.student != request.user.student_profile:
            messages.error(request, "Access denied: You cannot view receipts belonging to other students.")
            return redirect('student_dashboard')

    context = {
        'payment': payment,
        'fee': payment.fee_record,
        'student': payment.fee_record.student,
    }
    return render(request, 'admin/fees/receipt.html', context)


@warden_or_admin_required
def category_list_view(request):
    categories = FeeCategory.objects.all()
    if request.method == 'POST':
        form = FeeCategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f"Fee category '{cat.name}' created.")
            return redirect('fees:category_list')
    else:
        form = FeeCategoryForm()

    return render(request, 'admin/fees/category_list.html', {'categories': categories, 'form': form})
