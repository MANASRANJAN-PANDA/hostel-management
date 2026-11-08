from django.db import models

class Hostel(models.Model):
    class GenderType(models.TextChoices):
        BOYS = 'BOYS', 'Boys Hostel'
        GIRLS = 'GIRLS', 'Girls Hostel'
        COED = 'COED', 'Co-ed Hostel'

    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True)
    gender_type = models.CharField(max_length=20, choices=GenderType.choices, default=GenderType.BOYS)
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def total_rooms(self):
        return self.rooms.count()

    @property
    def total_capacity(self):
        return sum(room.capacity for room in self.rooms.all())

    @property
    def total_occupied_beds(self):
        from allocations.models import RoomAllocation
        return RoomAllocation.objects.filter(room__hostel=self, status='ACTIVE').count()


class Floor(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='floors')
    floor_number = models.IntegerField(default=0)
    floor_name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['hostel', 'floor_number']
        unique_together = ('hostel', 'floor_number')

    def __str__(self):
        return f"{self.hostel.code} - {self.floor_name}"
