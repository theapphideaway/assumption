from django.contrib import admin

from .models import Announcement, DayOverride, Location, Service


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_primary")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "weekday", "start_time", "location")
    list_filter = ("weekday", "location")


@admin.register(DayOverride)
class DayOverrideAdmin(admin.ModelAdmin):
    list_display = ("date", "title")
    date_hierarchy = "date"


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """Stands in for Father's panel until the real one is built — enough to
    send a push during the demo."""

    list_display = ("created_at", "body", "sent_at", "recipients")
    readonly_fields = ("sent_at", "recipients")
