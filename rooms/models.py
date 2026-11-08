from django.db import models
from django.core.validators import MinValueValidator
from hostels.models import Hostel, Floor

class Room(models.Model):
    class RoomType(models.TextChoices):
        SINGLE = 'SINGLE', 'Single Sharing'
        DOUBLE = 'DOUBLE', 'Double Sharing'
        TRIPLE = 'TRIPLE', 'Triple Sharing'
        FOUR = 'FOUR', 'Four Sharing'

    class RoomStatus(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        PARTIALLY_OCCUPIED = 'PARTIALLY_OCCUPIED', 'Partially Occupied'
        FULL = 'FULL', 'Full'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance'

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=20, choices=RoomType.choices, default=RoomType.DOUBLE)
    capacity = models.PositiveIntegerField(default=2, validators=[MinValueValidator(1)])
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    room_status = models.CharField(max_length=20, choices=RoomStatus.choices, default=RoomStatus.AVAILABLE)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['hostel', 'room_number']
        unique_together = ('hostel', 'room_number')

    def __str__(self):
        return f"{self.hostel.code} - Room {self.room_number} ({self.get_room_status_display()})"

    @property
    def current_occupancy(self):
        return self.allocations.filter(status='ACTIVE').count()

    @property
    def available_beds(self):
        occ = self.current_occupancy
        return max(0, self.capacity - occ)

    def is_fully_occupied(self):
        return self.current_occupancy >= self.capacity

    def update_occupancy_status(self):
        if self.room_status == self.RoomStatus.MAINTENANCE:
            return
        active_count = self.current_occupancy
        if active_count == 0:
            self.room_status = self.RoomStatus.AVAILABLE
        elif active_count < self.capacity:
            self.room_status = self.RoomStatus.PARTIALLY_OCCUPIED
        else:
            self.room_status = self.RoomStatus.FULL
        self.save(update_fields=['room_status'])
