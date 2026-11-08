from django.contrib import admin
from .models import FeeCategory, FeeRecord, Payment

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('receipt_number', 'created_at')

@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'default_amount', 'is_active')
    search_fields = ('name', 'code')

@admin.register(FeeRecord)
class FeeRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'category', 'total_amount', 'paid_amount', 'remaining_amount', 'due_date', 'status')
    list_filter = ('status', 'category', 'billing_month')
    search_fields = ('student__reg_number', 'title')
    inlines = [PaymentInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'fee_record', 'amount', 'payment_method', 'payment_date', 'transaction_reference', 'received_by')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('receipt_number', 'transaction_reference', 'fee_record__student__reg_number')
