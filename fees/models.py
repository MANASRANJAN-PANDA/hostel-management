from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid

class FeeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    default_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Fee Categories"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (₹{self.default_amount})"


class FeeRecord(models.Model):
    class PaymentStatus(models.TextChoices):
        PAID = 'PAID', 'Paid'
        PENDING = 'PENDING', 'Pending'
        PARTIALLY_PAID = 'PARTIALLY_PAID', 'Partially Paid'
        OVERDUE = 'OVERDUE', 'Overdue'

    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='fee_records')
    category = models.ForeignKey(FeeCategory, on_delete=models.PROTECT, related_name='fee_records')
    title = models.CharField(max_length=150)
    billing_month = models.CharField(max_length=20, help_text="e.g. 2026-11 or Spring 2026")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date', '-created_at']

    def __str__(self):
        return f"{self.student.reg_number} - {self.title} (₹{self.total_amount})"

    def update_balance(self):
        total_paid = self.payments.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        self.paid_amount = total_paid
        self.remaining_amount = max(Decimal('0.00'), self.total_amount - self.paid_amount)

        if self.remaining_amount <= Decimal('0.00') and self.paid_amount > Decimal('0.00'):
            self.status = self.PaymentStatus.PAID
        elif self.paid_amount > Decimal('0.00'):
            self.status = self.PaymentStatus.PARTIALLY_PAID
        elif self.due_date and self.due_date < timezone.now().date():
            self.status = self.PaymentStatus.OVERDUE
        else:
            self.status = self.PaymentStatus.PENDING

        self.save()


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Cash'
        UPI = 'UPI', 'UPI'
        BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
        OTHER = 'OTHER', 'Other'

    fee_record = models.ForeignKey(FeeRecord, on_delete=models.CASCADE, related_name='payments')
    receipt_number = models.CharField(max_length=60, unique=True, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.UPI)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True, help_text="Transaction Ref / UPI ID / Bank UTR / Memo")
    notes = models.TextField(blank=True, null=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='recorded_payments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            date_prefix = timezone.now().strftime('%Y%m')
            random_suffix = uuid.uuid4().hex[:6].upper()
            self.receipt_number = f"RCP-{date_prefix}-{random_suffix}"
        super().save(*args, **kwargs)
        self.fee_record.update_balance()

    def __str__(self):
        return f"{self.receipt_number} - ₹{self.amount} ({self.get_payment_method_display()})"
