from django.db import models
from django.conf import settings

class StudentProfile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'

    class AccountStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        SUSPENDED = 'SUSPENDED', 'Suspended'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    reg_number = models.CharField(max_length=50, unique=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.MALE)
    course = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    academic_year = models.CharField(max_length=20, default='1st Year')
    address = models.TextField(blank=True, null=True)
    parent_name = models.CharField(max_length=120, blank=True, null=True)
    parent_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    joining_date = models.DateField(auto_now_add=True)
    account_status = models.CharField(max_length=20, choices=AccountStatus.choices, default=AccountStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['reg_number']

    def __str__(self):
        return f"{self.user.get_display_name()} ({self.reg_number})"

    @property
    def current_allocation(self):
        return self.allocations.filter(status='ACTIVE').first()

    @property
    def current_room(self):
        alloc = self.current_allocation
        return alloc.room if alloc else None
