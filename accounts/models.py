from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
        WARDEN = 'WARDEN', 'Hostel Warden'
        STUDENT = 'STUDENT', 'Student'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        db_index=True
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_approved = models.BooleanField(
        default=False,
        help_text="Designates whether user registration has been approved by administrator."
    )
    address = models.TextField(blank=True, null=True)

    def is_superadmin(self):
        return self.role == self.Role.SUPER_ADMIN or self.is_superuser

    def is_warden(self):
        return self.role == self.Role.WARDEN

    def is_student(self):
        return self.role == self.Role.STUDENT

    def get_display_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username

    def __str__(self):
        return f"{self.get_display_name()} ({self.get_role_display()})"
