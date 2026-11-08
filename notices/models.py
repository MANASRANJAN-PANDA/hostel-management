from django.db import models
from django.conf import settings
from django.utils import timezone

class Notice(models.Model):
    class Audience(models.TextChoices):
        ALL = 'ALL', 'All Users'
        STUDENTS = 'STUDENTS', 'Students Only'
        WARDENS = 'WARDENS', 'Wardens Only'

    title = models.CharField(max_length=200)
    content = models.TextField()
    attachment = models.FileField(upload_to='notices/', blank=True, null=True)
    target_audience = models.CharField(max_length=20, choices=Audience.choices, default=Audience.ALL)
    is_published = models.BooleanField(default=True)
    published_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_date', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.published_date})"

    @property
    def is_active(self):
        if not self.is_published:
            return False
        if self.expiry_date and self.expiry_date < timezone.now().date():
            return False
        return True
