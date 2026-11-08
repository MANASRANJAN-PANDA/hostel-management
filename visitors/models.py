from django.db import models
from django.conf import settings
from django.utils import timezone
from students.models import StudentProfile

class Visitor(models.Model):
    visitor_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='visitors')
    relationship = models.CharField(max_length=50, default='Parent')
    purpose = models.CharField(max_length=200, default='Personal Visit')
    id_proof_type = models.CharField(max_length=50, blank=True, null=True, default='National ID / Aadhaar')
    id_proof_number = models.CharField(max_length=50, blank=True, null=True)
    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-entry_time']

    def __str__(self):
        return f"{self.visitor_name} visited {self.student.reg_number} on {self.entry_time.strftime('%Y-%m-%d')}"

    @property
    def is_currently_inside(self):
        return self.exit_time is None
