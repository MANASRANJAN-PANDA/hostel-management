from django import forms
from .models import Complaint, ComplaintHistory
from wardens.models import WardenProfile

class StudentComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'category', 'description', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief summary of issue (e.g. Geyser not working in Room 204)'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed explanation of the issue, specific location, urgency, etc.'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ComplaintStatusUpdateForm(forms.ModelForm):
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes on action taken, vendor assigned, reason for status change, etc.'}),
        label="Action / Resolution Remarks"
    )

    class Meta:
        model = Complaint
        fields = ['status', 'assigned_warden', 'resolution_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_warden': forms.Select(attrs={'class': 'form-select'}),
            'resolution_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Final resolution notes'}),
        }
