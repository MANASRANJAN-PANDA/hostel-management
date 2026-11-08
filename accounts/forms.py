from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import User
from students.models import StudentProfile

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email address',
            'autofocus': True,
            'id': 'login-username'
        }),
        label="Username or Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'id': 'login-password'
        }),
        label="Password"
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'remember-me'}),
        label="Remember me"
    )

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username_or_email and password:
            user = None
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email__iexact=username_or_email)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            else:
                user = authenticate(username=username_or_email, password=password)

            if not user:
                raise ValidationError("Invalid username/email or password. Please verify your credentials.")
            elif not user.is_active:
                raise ValidationError("Your account is deactivated. Please contact hostel administration.")
            cleaned_data['user'] = user

        return cleaned_data


class StudentRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'student@college.edu'})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'})
    )
    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create strong password', 'id': 'reg-password'})
    )
    confirm_password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password', 'id': 'reg-confirm-password'})
    )

    # Student specific fields
    reg_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. REG-2026-001'})
    )
    roll_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CS-26-042'})
    )
    dob = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    gender = forms.ChoiceField(
        choices=StudentProfile.Gender.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    course = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. B.Tech Computer Science'})
    )
    department = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CSE / IT / ECE'})
    )
    academic_year = forms.ChoiceField(
        choices=[('1st Year', '1st Year'), ('2nd Year', '2nd Year'), ('3rd Year', '3rd Year'), ('4th Year', '4th Year'), ('Postgraduate', 'Postgraduate')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Permanent Residential Address'})
    )
    parent_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Parent or Guardian Full Name'})
    )
    parent_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Parent Contact Phone'})
    )
    emergency_contact = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Contact Number'})
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose unique username'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email address already exists.")
        return email

    def clean_reg_number(self):
        reg = self.cleaned_data.get('reg_number').strip().upper()
        if StudentProfile.objects.filter(reg_number__iexact=reg).exists():
            raise ValidationError("A student with this Registration Number is already registered.")
        return reg

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = User.Role.STUDENT
        user.is_approved = False  # requires admin approval
        user.save()

        # Create linked StudentProfile
        student_profile = StudentProfile.objects.create(
            user=user,
            reg_number=self.cleaned_data['reg_number'],
            roll_number=self.cleaned_data.get('roll_number'),
            dob=self.cleaned_data.get('dob'),
            gender=self.cleaned_data.get('gender'),
            course=self.cleaned_data.get('course'),
            department=self.cleaned_data.get('department'),
            academic_year=self.cleaned_data.get('academic_year'),
            address=self.cleaned_data.get('address'),
            parent_name=self.cleaned_data.get('parent_name'),
            parent_phone=self.cleaned_data.get('parent_phone'),
            emergency_contact=self.cleaned_data.get('emergency_contact'),
            account_status=StudentProfile.AccountStatus.PENDING
        )
        return user


class StudentProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = StudentProfile
        fields = ['roll_number', 'dob', 'gender', 'course', 'department', 'academic_year', 'address', 'parent_name', 'parent_phone', 'emergency_contact']
        widgets = {
            'roll_number': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_year': forms.Select(choices=[('1st Year', '1st Year'), ('2nd Year', '2nd Year'), ('3rd Year', '3rd Year'), ('4th Year', '4th Year'), ('Postgraduate', 'Postgraduate')], attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
        }
