from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def superadmin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_superadmin():
            messages.error(request, "Access denied: Super Admin privileges required.")
            return redirect('accounts:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def warden_or_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not (request.user.is_superadmin() or request.user.is_warden()):
            messages.error(request, "Access denied: Staff privileges required.")
            return redirect('accounts:dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_student():
            messages.error(request, "Access denied: Student portal only.")
            return redirect('accounts:dashboard_redirect')
        if not request.user.is_approved:
            return redirect('accounts:pending_approval')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
