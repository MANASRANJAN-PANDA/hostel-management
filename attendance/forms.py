from django import forms
from django.utils import timezone
from .models import Attendance
from students.models import StudentProfile
from hostels.models import Hostel

class SingleAttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select select2'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional remarks (e.g. On Leave, Sick)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = StudentProfile.objects.filter(account_status='ACTIVE').select_related('user')
        self.fields['date'].initial = timezone.now().date()
