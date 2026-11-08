from django import forms
from django.utils import timezone
from .models import FeeCategory, FeeRecord, Payment
from students.models import StudentProfile
from hostels.models import Hostel

class FeeCategoryForm(forms.ModelForm):
    class Meta:
        model = FeeCategory
        fields = ['name', 'code', 'default_amount', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Hostel Rent'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. RENT'}),
            'default_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FeeRecordCreateForm(forms.ModelForm):
    class Meta:
        model = FeeRecord
        fields = ['student', 'category', 'title', 'billing_month', 'total_amount', 'due_date', 'notes']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select select2'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. November 2026 Room Rent'}),
            'billing_month': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2026-11'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = StudentProfile.objects.filter(account_status='ACTIVE').select_related('user')
        self.fields['billing_month'].initial = timezone.now().strftime('%Y-%m')
        self.fields['due_date'].initial = timezone.now().date() + timezone.timedelta(days=15)


class BatchFeeGenerateForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=FeeCategory.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Fee Category"
    )
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. December 2026 Hostel Charges'}),
        label="Fee Title"
    )
    billing_month = forms.CharField(
        initial=lambda: timezone.now().strftime('%Y-%m'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2026-12'}),
        label="Billing Month"
    )
    total_amount = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label="Amount per Student (₹)"
    )
    due_date = forms.DateField(
        initial=lambda: timezone.now().date() + timezone.timedelta(days=15),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Due Date"
    )
    target_group = forms.ChoiceField(
        choices=[
            ('ALL_ACTIVE', 'All Active Students'),
            ('HOSTEL_RESIDENTS', 'Only Students with Active Room Allocation'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Target Students"
    )
    hostel = forms.ModelChoiceField(
        queryset=Hostel.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Filter by Hostel (Optional)"
    )


class PaymentRecordForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_date', 'payment_method', 'transaction_reference', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'transaction_reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'UPI Ref / Bank UTR / Cash Voucher #'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Payment notes / Remarks'}),
        }

    def __init__(self, fee_record=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fee_record = fee_record
        if fee_record and not self.initial.get('amount'):
            self.fields['amount'].initial = fee_record.remaining_amount
        self.fields['payment_date'].initial = timezone.now().date()

    def clean_amount(self):
        amt = self.cleaned_data.get('amount')
        if amt <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        if self.fee_record and amt > self.fee_record.remaining_amount:
            raise forms.ValidationError(f"Payment amount cannot exceed remaining balance of ₹{self.fee_record.remaining_amount}.")
        return amt
