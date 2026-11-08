from django.contrib import admin
from .models import Notice

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_audience', 'published_date', 'expiry_date', 'is_published', 'created_by')
    list_filter = ('target_audience', 'is_published', 'published_date')
    search_fields = ('title', 'content')
