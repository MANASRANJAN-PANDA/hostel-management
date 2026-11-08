from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'hostel', 'floor', 'room_type', 'capacity', 'current_occupancy', 'monthly_rent', 'room_status')
    list_filter = ('hostel', 'room_type', 'room_status')
    search_fields = ('room_number', 'hostel__name')
