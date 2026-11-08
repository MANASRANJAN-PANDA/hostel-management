from django import forms
from django.core.exceptions import ValidationError
from accounts.models import User
from hostels.models import Hostel
from .models import WardenProfile

class WardenForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'warden@college.edu'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}))
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Set password (optional, default: warden123)'}))
    is_active = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = WardenProfile
        fields = ['assigned_hostel', 'phone', 'joining_date', 'address', 'emergency_contact']
        widgets = {
            'assigned_hostel': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Phone'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Residential Address'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Contact Number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone'].initial = self.instance.phone or self.instance.user.phone
            self.fields['is_active'].initial = self.instance.user.is_active
            self.fields['password'].required = False
            self.fields['password'].widget.attrs['placeholder'] = 'Leave blank to keep current password'

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise ValidationError("This email address is already registered.")
        return email

    def save(self, commit=True):
        if self.instance and self.instance.pk:
            profile = super().save(commit=False)
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.phone = self.cleaned_data['phone']
            user.is_active = self.cleaned_data['is_active']
            if self.cleaned_data.get('profile_picture'):
                user.profile_picture = self.cleaned_data['profile_picture']
            if self.cleaned_data.get('password'):
                user.set_password(self.cleaned_data['password'])
            user.save()
            profile.phone = self.cleaned_data['phone']
            profile.save()
            return profile
        else:
            email = self.cleaned_data['email']
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            password = self.cleaned_data.get('password') or 'warden123'
            user = User.objects.create(
                username=username,
                email=email,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                phone=self.cleaned_data['phone'],
                role=User.Role.WARDEN,
                is_approved=True,
                is_staff=True,
                is_active=self.cleaned_data.get('is_active', True)
            )
            user.set_password(password)
            if self.cleaned_data.get('profile_picture'):
                user.profile_picture = self.cleaned_data['profile_picture']
            user.save()

            profile = super().save(commit=False)
            profile.user = user
            profile.phone = self.cleaned_data['phone']
            profile.save()
            return profile
