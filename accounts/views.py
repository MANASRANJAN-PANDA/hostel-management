from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, StudentRegistrationForm, StudentProfileUpdateForm
from .models import User

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            remember_me = form.cleaned_data.get('remember_me')

            login(request, user)

            if remember_me:
                # 2 weeks
                request.session.set_expiry(1209600)
            else:
                # browser close
                request.session.set_expiry(0)

            messages.success(request, f"Welcome back, {user.get_display_name()}!")

            # If user is a student and not approved yet
            if user.is_student() and not user.is_approved:
                return redirect('accounts:pending_approval')

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:dashboard_redirect')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = LoginForm()

    return render(request, 'authentication/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Registration successful for {user.get_display_name()}! Your account is pending administrator approval before you can access the student portal."
            )
            return redirect('accounts:pending_approval')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = StudentRegistrationForm()

    return render(request, 'authentication/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')


@login_required
def dashboard_redirect_view(request):
    user = request.user
    if user.is_superadmin():
        return redirect('admin_dashboard')
    elif user.is_warden():
        return redirect('warden_dashboard')
    elif user.is_student():
        if not user.is_approved:
            return redirect('accounts:pending_approval')
        return redirect('student_dashboard')
    else:
        return redirect('admin_dashboard')


def pending_approval_view(request):
    return render(request, 'authentication/pending_approval.html')


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect('accounts:change_password')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'authentication/change_password.html', {'form': form})
