from django.contrib import admin
from .models import Alert

# Register your models here.
@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "channel", "status", "send_at", "delivered_at", "retries")
    list_filter = ("channel", "status")
    search_fields = ("title", "body")