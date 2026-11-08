from django.contrib import admin
from .models import Hostel, Floor

class FloorInline(admin.TabularInline):
    model = Floor
    extra = 1

@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'gender_type', 'contact_phone', 'is_active', 'total_rooms', 'total_capacity')
    list_filter = ('gender_type', 'is_active')
    search_fields = ('name', 'code', 'contact_phone')
    inlines = [FloorInline]

@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ('hostel', 'floor_number', 'floor_name')
    list_filter = ('hostel',)
