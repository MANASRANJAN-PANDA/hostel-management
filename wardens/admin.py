from django.contrib import admin
from .models import WardenProfile

@admin.register(WardenProfile)
class WardenProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'assigned_hostel', 'phone', 'joining_date')
    list_filter = ('assigned_hostel',)
    search_fields = ('user__first_name', 'user__last_name', 'phone')
