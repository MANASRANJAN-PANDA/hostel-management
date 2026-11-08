from django.db import models
from django.conf import settings
from hostels.models import Hostel

class WardenProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='warden_profile')
    assigned_hostel = models.ForeignKey(Hostel, on_delete=models.SET_NULL, null=True, blank=True, related_name='wardens')
    phone = models.CharField(max_length=20, blank=True, null=True)
    joining_date = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        hostel_str = f" - {self.assigned_hostel.name}" if self.assigned_hostel else " (Unassigned)"
        return f"Warden: {self.user.get_display_name()}{hostel_str}"
