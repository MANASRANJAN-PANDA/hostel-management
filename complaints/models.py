from django.db import models
from django.conf import settings
from students.models import StudentProfile
from wardens.models import WardenProfile

class Complaint(models.Model):
    class Category(models.TextChoices):
        ROOM_ISSUES = 'ROOM_ISSUES', 'Room Issues'
        ELECTRICITY = 'ELECTRICITY', 'Electricity'
        WATER_SUPPLY = 'WATER_SUPPLY', 'Water Supply'
        CLEANING = 'CLEANING', 'Cleaning & Sanitation'
        FOOD_MESS = 'FOOD_MESS', 'Food / Mess'
        INTERNET = 'INTERNET', 'Internet / Wi-Fi'
        SECURITY = 'SECURITY', 'Security'
        OTHER = 'OTHER', 'Other'

    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        REJECTED = 'REJECTED', 'Rejected'

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.ROOM_ISSUES)
    description = models.TextField()
    attachment = models.ImageField(upload_to='complaints/', blank=True, null=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.SUBMITTED)
    assigned_warden = models.ForeignKey(WardenProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_complaints')
    resolution_notes = models.TextField(blank=True, null=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.title} ({self.get_status_display()})"


class ComplaintHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='history')
    action_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    status_from = models.CharField(max_length=30)
    status_to = models.CharField(max_length=30)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Complaint #{self.complaint_id}: {self.status_from} -> {self.status_to}"
