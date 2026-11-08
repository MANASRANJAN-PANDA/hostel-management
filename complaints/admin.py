from django.contrib import admin
from .models import Complaint, ComplaintHistory

class ComplaintHistoryInline(admin.TabularInline):
    model = ComplaintHistory
    extra = 0
    readonly_fields = ('action_by', 'status_from', 'status_to', 'remarks', 'created_at')

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'student', 'category', 'status', 'assigned_warden', 'created_at')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('title', 'description', 'student__reg_number')
    inlines = [ComplaintHistoryInline]

@admin.register(ComplaintHistory)
class ComplaintHistoryAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'status_from', 'status_to', 'action_by', 'created_at')
