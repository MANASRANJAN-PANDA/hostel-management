from django.contrib import admin
from .models import RoomAllocation

@admin.register(RoomAllocation)
class RoomAllocationAdmin(admin.ModelAdmin):
    list_display = ('student', 'room', 'allocation_date', 'vacating_date', 'status', 'allocated_by')
    list_filter = ('status', 'room__hostel')
    search_fields = ('student__reg_number', 'student__user__first_name', 'room__room_number')
