from django import forms
from django.utils import timezone
from .models import Visitor
from students.models import StudentProfile

class VisitorForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=StudentProfile.objects.filter(account_status='ACTIVE').select_related('user'),
        widget=forms.Select(attrs={'class': 'form-select select2'}),
        label="Student Being Visited"
    )

    class Meta:
        model = Visitor
        fields = [
            'visitor_name', 'phone_number', 'student', 'relationship',
            'purpose', 'id_proof_type', 'id_proof_number', 'address',
            'entry_time', 'remarks'
        ]
        widgets = {
            'visitor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Visitor Full Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Mobile Number'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Father, Mother, Brother, Friend'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Purpose of visit'}),
            'id_proof_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Aadhaar / Voter ID / Driving License'}),
            'id_proof_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID Document Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Visitor residential city / address'}),
            'entry_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Luggage/belongings or other notes'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['entry_time'].initial = timezone.localtime(timezone.now()).strftime('%Y-%m-%dT%H:%M')
