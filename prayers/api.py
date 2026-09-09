"""
The prayer endpoints.

`/api/v1/prayers/` returns every document for the day, already assembled with
the day's propers and any scripture that is on file, keyed by time-of-day slot.

The server also reports a `suggested` slot using the parish timezone. The
client is free to prefer the device clock — that is the one deliberate
exception to "clients compute nothing", and it is safe because a time-of-day
comparison cannot drift between two platforms the way a liturgical rule can.
"""

from __future__ import annotations

from datetime import datetime

from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from liturgics.resolver import resolve_day
from prayers.assembler import assemble
from prayers.blocks import SLOTS, slot_for_hour
from prayers.scripture import EDITIONS, available, trilingual_resolver
from prayers.store import catalogue


def _payload(d):
    day = resolve_day(d)
    loaded = set(available())
    editions = {lang: ed for lang, ed in EDITIONS.items() if ed in loaded}
    scripture = trilingual_resolver(loaded=loaded) if loaded else None

    docs, missing = [], []
    for doc in catalogue().values():
        if doc.get("slot") is None:
            continue                      # building blocks, not standalone
        built = assemble(doc["id"], day, scripture=scripture)
        missing.extend(built.pop("missing"))
        docs.append(built)

    # Resolve the day's readings into actual text. A citation nobody can read
    # without leaving the app is a citation nobody reads.
    readings = dict(day["readings"] or {})
    if readings and scripture:
        for key in ("gospel", "epistle"):
            ref = readings.get(key)
            if not ref:
                continue
            verses = scripture(ref)
            if verses:
                readings[f"{key}_text"] = verses
            else:
                missing.append({"type": "reading", "ref": ref,
                                "why": "passage not in the loaded editions"})

    by_slot = {s: [d_ for d_ in docs if d_["slot"] == s] for s in SLOTS}
    return {
        "date": day["date"],
        "suggested": slot_for_hour(timezone.localtime().hour),
        "day": {"title": day["title"], "fast": day["fast"],
                "tone": day["tone"], "readings": readings or None},
        "slots": by_slot,
        "scripture_editions": editions,
        "missing": missing,
    }


@api_view(["GET"])
def prayers(request):
    iso = request.GET.get("date")
    try:
        d = (datetime.strptime(iso, "%Y-%m-%d").date() if iso
             else timezone.localdate())
    except ValueError:
        return Response({"detail": "Use YYYY-MM-DD."}, status=400)
    return Response(_payload(d))
