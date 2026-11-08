from django.contrib import admin
from .models import StudentProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('reg_number', 'user', 'course', 'department', 'academic_year', 'gender', 'account_status', 'joining_date')
    list_filter = ('account_status', 'gender', 'course', 'department')
    search_fields = ('reg_number', 'roll_number', 'user__first_name', 'user__last_name', 'user__email')
