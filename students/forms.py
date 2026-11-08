from django import forms
from django.core.exceptions import ValidationError
from accounts.models import User
from .models import StudentProfile

class StudentAdminForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'student@college.edu'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Set initial password (optional, default: hostel123)'}))

    class Meta:
        model = StudentProfile
        fields = [
            'reg_number', 'roll_number', 'dob', 'gender', 'course',
            'department', 'academic_year', 'address', 'parent_name',
            'parent_phone', 'emergency_contact', 'account_status'
        ]
        widgets = {
            'reg_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. REG-2026-001'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CS-26-042'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course / Degree'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
            'academic_year': forms.Select(choices=[('1st Year', '1st Year'), ('2nd Year', '2nd Year'), ('3rd Year', '3rd Year'), ('4th Year', '4th Year'), ('Postgraduate', 'Postgraduate')], attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Address'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Parent Name'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Parent Phone'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Contact'}),
            'account_status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone'].initial = self.instance.user.phone
            self.fields['password'].required = False
            self.fields['password'].widget.attrs['placeholder'] = 'Leave blank to keep current password'

    def clean_reg_number(self):
        reg = self.cleaned_data.get('reg_number').strip().upper()
        qs = StudentProfile.objects.filter(reg_number__iexact=reg)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("This Registration Number is already used by another student.")
        return reg

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
            # Edit existing
            profile = super().save(commit=False)
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.phone = self.cleaned_data['phone']
            if self.cleaned_data.get('profile_picture'):
                user.profile_picture = self.cleaned_data['profile_picture']
            if self.cleaned_data.get('password'):
                user.set_password(self.cleaned_data['password'])
            if profile.account_status == StudentProfile.AccountStatus.ACTIVE:
                user.is_approved = True
                user.is_active = True
            elif profile.account_status in [StudentProfile.AccountStatus.INACTIVE, StudentProfile.AccountStatus.SUSPENDED]:
                user.is_active = False
            user.save()
            profile.save()
            return profile
        else:
            # Create new
            email = self.cleaned_data['email']
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            password = self.cleaned_data.get('password') or 'hostel123'
            user = User.objects.create(
                username=username,
                email=email,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                phone=self.cleaned_data['phone'],
                role=User.Role.STUDENT,
                is_approved=True,
                is_active=True
            )
            user.set_password(password)
            if self.cleaned_data.get('profile_picture'):
                user.profile_picture = self.cleaned_data['profile_picture']
            user.save()

            profile = super().save(commit=False)
            profile.user = user
            profile.account_status = StudentProfile.AccountStatus.ACTIVE
            profile.save()
            return profile
