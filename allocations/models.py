from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from students.models import StudentProfile
from rooms.models import Room

class RoomAllocation(models.Model):
    class AllocationStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        TRANSFERRED = 'TRANSFERRED', 'Transferred'
        VACATED = 'VACATED', 'Vacated'

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='allocations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allocations')
    allocation_date = models.DateField(default=timezone.now)
    vacating_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=AllocationStatus.choices, default=AllocationStatus.ACTIVE)
    notes = models.TextField(blank=True, null=True)
    allocated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='allocated_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-allocation_date', '-created_at']

    def __str__(self):
        return f"{self.student.reg_number} -> {self.room.hostel.code}-{self.room.room_number} ({self.status})"

    def clean(self):
        # Prevent duplicate active allocations for the same student
        if self.status == self.AllocationStatus.ACTIVE:
            existing_active = RoomAllocation.objects.filter(
                student=self.student,
                status=self.AllocationStatus.ACTIVE
            ).exclude(pk=self.pk).exists()
            if existing_active:
                raise ValidationError(f"Student {self.student.reg_number} already has an active room allocation. Vacate or transfer the current room first.")

            # Validate room capacity
            current_occupancy = self.room.allocations.filter(status=self.AllocationStatus.ACTIVE).exclude(pk=self.pk).count()
            if current_occupancy >= self.room.capacity:
                raise ValidationError(f"Room {self.room.room_number} has reached maximum capacity of {self.room.capacity}.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        self.room.update_occupancy_status()

    def vacate(self, notes=""):
        self.status = self.AllocationStatus.VACATED
        self.vacating_date = timezone.now().date()
        if notes:
            self.notes = f"{self.notes or ''}\nVacated: {notes}".strip()
        self.save()
        self.room.update_occupancy_status()
