"""
The read API the iOS app consumes.

One endpoint shape, one object. The clients render what this returns and
compute nothing liturgical themselves — the rule that keeps two native
codebases from drifting apart.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from liturgics.resolver import resolve_day

from .models import Announcement, DayOverride, Service

MAX_WINDOW = 400          # the rolling cache the clients hold


def _services_for(d: date) -> list[dict]:
    qs = Service.objects.filter(date=d) | Service.objects.filter(
        date__isnull=True, weekday=d.weekday())
    return [
        {
            "title": {"en": s.title, **({"el": s.greek} if s.greek else {})},
            "time": s.start_time.strftime("%H:%M"),
            "location": s.location.name if s.location else None,
            "note": s.note,
        }
        for s in qs.select_related("location").distinct()
    ]


def _day_payload(d: date, overrides: dict[date, DayOverride] | None = None) -> dict:
    """Engine output plus whatever Father has said about this day."""
    payload = resolve_day(d)
    payload["parish"]["services"] = _services_for(d)

    ov = (overrides or {}).get(d)
    if ov is None:
        ov = DayOverride.objects.filter(date=d).first()
    if ov:
        if ov.title:
            payload["title"] = ov.title
        payload["parish"]["note"] = ov.note or None
        if ov.icon_url:
            payload["icon"] = {"url": ov.icon_url, "credit": ov.icon_credit}
    return payload


@api_view(["GET"])
def today(request):
    return Response(_day_payload(timezone.localdate()))


@api_view(["GET"])
def day(request, iso_date: str):
    try:
        d = datetime.strptime(iso_date, "%Y-%m-%d").date()
    except ValueError:
        return Response({"detail": "Use YYYY-MM-DD."}, status=400)
    return Response(_day_payload(d))


@api_view(["GET"])
def days(request):
    """A window of resolved days, for the client's offline cache."""
    try:
        start = datetime.strptime(
            request.GET.get("start", timezone.localdate().isoformat()),
            "%Y-%m-%d").date()
        count = int(request.GET.get("days", 30))
    except (ValueError, TypeError):
        return Response({"detail": "Bad start or days."}, status=400)

    count = max(1, min(count, MAX_WINDOW))
    window = [start + timedelta(days=i) for i in range(count)]
    overrides = {o.date: o for o in
                 DayOverride.objects.filter(date__in=window)}
    return Response({
        "start": start.isoformat(),
        "days": count,
        "results": [_day_payload(d, overrides) for d in window],
    })


@api_view(["GET"])
def announcements(request):
    qs = Announcement.objects.exclude(sent_at__isnull=True)[:20]
    return Response({"results": [
        {"id": a.id, "body": a.body, "sent_at": a.sent_at.isoformat()}
        for a in qs
    ]})
