from django.contrib import admin
from .models import Visitor

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('visitor_name', 'phone_number', 'student', 'relationship', 'entry_time', 'exit_time', 'recorded_by')
    list_filter = ('entry_time', 'relationship')
    search_fields = ('visitor_name', 'phone_number', 'student__reg_number')
