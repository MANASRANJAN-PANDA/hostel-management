from django import forms
from .models import Hostel, Floor

class HostelForm(forms.ModelForm):
    class Meta:
        model = Hostel
        fields = ['name', 'code', 'gender_type', 'address', 'description', 'contact_phone', 'contact_email', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Aryabhata Hall of Residence'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. BH-1'}),
            'gender_type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Hostel Location / Address'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Brief description'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Office Phone'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'hostel@college.edu'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = ['hostel', 'floor_number', 'floor_name', 'description']
        widgets = {
            'hostel': forms.Select(attrs={'class': 'form-select'}),
            'floor_number': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0 for Ground, 1 for 1st'}),
            'floor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ground Floor, 1st Floor'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional notes'}),
        }
