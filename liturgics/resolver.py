"""
Day resolution: the one object the clients render.

Assembles the movable cycle, the fixed Menaion and the fast resolver into a
single dict. Parish overrides (Father's edits, service times, the patronal
feast) are layered on top of this by the Django layer — this module stays
pure so it can be tested without a database.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

from .fasting import resolve_fast
from .i18n import (FAST_LABELS, LANGUAGES, SEASONS, fast_reason,
                    missing_languages)
from .lectionary import readings_for
from .movable import eothinon_for, movable_day, season_for, tone_for
from .paschalion import gregorian_to_julian, reference_pascha

__all__ = ["resolve_day", "resolve_range", "menaion"]

_DATA = Path(__file__).parent / "data" / "menaion.json"


@lru_cache(maxsize=1)
def menaion() -> dict:
    raw = json.loads(_DATA.read_text(encoding="utf-8"))
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def resolve_day(d: date) -> dict:
    """Fully resolve one civil date into the object the API serves."""
    pascha_date, offset = reference_pascha(d)
    season = season_for(offset)

    fixed = menaion().get(f"{d.month:02d}-{d.day:02d}")
    moving = movable_day(offset)

    # The higher-ranked commemoration supplies the day's title; the other is
    # still listed. Movable wins ties — Pascha outranks anything fixed.
    commemorations = []
    if moving:
        title = {"en": moving[0]}
        if moving[2]:
            title["el"] = moving[2]
        if len(moving) > 3 and moving[3]:
            title["ru"] = moving[3]
        commemorations.append({"title": title, "rank": moving[1],
                               "kind": "movable"})
    if fixed:
        commemorations.append({"title": dict(fixed["title"]),
                               "rank": fixed["rank"], "kind": "fixed",
                               "patronal": fixed.get("patronal", False)})
    commemorations.sort(key=lambda c: c["rank"])

    rank = commemorations[0]["rank"] if commemorations else 6
    title = (commemorations[0]["title"] if commemorations
             else dict(SEASONS[season.key]))
    color = season.color
    if commemorations and commemorations[0]["kind"] == "fixed":
        color = (fixed or {}).get("color", color)

    jy, jm, jd = gregorian_to_julian(d)
    fast = resolve_fast(d, offset, rank=rank)

    # Language gaps are reported, never papered over with English. A reader
    # who prays in Slavonic should see that a text is missing, not quietly
    # receive a different language and assume that is all there is.
    gaps = {"title": missing_languages(title)} if missing_languages(title) else {}

    return {
        "date": d.isoformat(),
        "julian": f"{jy:04d}-{jm:02d}-{jd:02d}",
        "pascha": pascha_date.isoformat(),
        "pascha_offset": offset,
        "languages": list(LANGUAGES),
        "season": {"key": season.key, "label": dict(SEASONS[season.key]),
                   "color": color},
        "title": title,
        "rank": rank,
        "tone": tone_for(d),
        "eothinon": eothinon_for(d),
        "fast": {"level": fast.level,
                 "label": dict(FAST_LABELS[fast.level]),
                 "reason": fast_reason(fast.reason),
                 "is_fast": fast.is_fast},
        "translation_gaps": gaps,
        "commemorations": commemorations,
        "patronal": any(c.get("patronal") for c in commemorations),
        "readings": readings_for(d, offset),
        # filled by the Django layer:
        "icon": None,
        "parish": {"services": [], "note": None},
    }


def resolve_range(start: date, days: int) -> list[dict]:
    """Resolve a window of days — the clients cache roughly +/-400."""
    return [resolve_day(start + timedelta(days=i)) for i in range(days)]
