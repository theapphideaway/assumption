"""
Parish data layered on top of the computed calendar.

Everything here is something a person decides — Father's overrides, service
times, announcements. Nothing in this module computes a liturgical date; that
is `liturgics`, and keeping the boundary clean is what lets the engine stay
testable without a database.

Field types are deliberately portable (no ArrayField, no Postgres-only search)
so the SQLite -> Postgres move stays a dump and load.
"""

from django.db import models
from django.utils import timezone


class Location(models.Model):
    """Services may not all happen at one address — the territory is large."""

    name = models.CharField(max_length=120)
    address = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Service(models.Model):
    """A scheduled service: either a one-off on a date, or weekly."""

    WEEKDAYS = [
        (i, d) for i, d in enumerate(
            ["Monday", "Tuesday", "Wednesday", "Thursday",
             "Friday", "Saturday", "Sunday"]
        )
    ]

    title = models.CharField(max_length=140)
    greek = models.CharField(max_length=140, blank=True)
    date = models.DateField(
        null=True, blank=True,
        help_text="One-off service. Leave blank if this repeats weekly.")
    weekday = models.IntegerField(
        choices=WEEKDAYS, null=True, blank=True,
        help_text="Weekly service. Leave blank if this is a one-off.")
    start_time = models.TimeField()
    location = models.ForeignKey(
        Location, null=True, blank=True, on_delete=models.SET_NULL)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.title} · {self.start_time:%H:%M}"


class DayOverride(models.Model):
    """Father's edits to a single day.

    The engine resolves every day correctly on its own. This is for what no
    algorithm can know: a hierarchical visit, a memorial, a parish observance.
    """

    date = models.DateField(unique=True)
    title = models.CharField(
        max_length=200, blank=True,
        help_text="Replaces the computed title when set.")
    note = models.TextField(blank=True)
    icon_url = models.URLField(
        blank=True, help_text="Photograph of the parish's own icon.")
    icon_credit = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.date} · {self.title or 'note'}"


class Announcement(models.Model):
    """A message from Father to the parish.

    Deliberately plain: no formatting, no attachments, no scheduling in the
    first version. This channel is valuable precisely because it is rare.
    """

    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    recipients = models.IntegerField(
        default=0, help_text="Devices reached — the receipt Father checks.")

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_sent(self):
        return self.sent_at is not None

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d} · {self.body[:48]}"
