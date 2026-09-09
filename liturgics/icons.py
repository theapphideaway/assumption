"""
Festal icons.

A registry mapping a day to an icon, layered the same way everything else here
is: curated defaults in a data file, and Father's per-date overrides on top via
`parish.DayOverride`.

The lookup returns a FILENAME and its attribution, never a URL. This module is
pure Python with no Django, so it cannot know how static files are served —
the API layer turns the filename into an absolute URL. Keeping that boundary
means the engine stays testable without a web server.

Provenance is not optional. Every entry records its licence and source, because
an icon whose origin nobody can name is one the parish cannot safely publish.
"""

from __future__ import annotations

import json
from datetime import date
from functools import lru_cache
from pathlib import Path

__all__ = ["icon_for", "registry", "coverage"]

_DATA = Path(__file__).parent / "data" / "icons.json"


@lru_cache(maxsize=1)
def registry() -> dict:
    if not _DATA.exists():
        return {}
    raw = json.loads(_DATA.read_text(encoding="utf-8"))
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def icon_for(d: date, offset: int) -> dict | None:
    """The icon for a day.

    Movable keys win: Pascha keeps its own icon whatever fixed date it lands on.
    """
    movable = registry().get(f"P{offset:+04d}")
    if movable:
        return {**movable, "key": f"P{offset:+04d}"}
    fixed = registry().get(f"{d.month:02d}-{d.day:02d}")
    if fixed:
        return {**fixed, "key": f"{d.month:02d}-{d.day:02d}"}
    return None


def coverage() -> dict:
    keys = registry()
    return {
        "total": len(keys),
        "movable": sum(1 for k in keys if k.startswith("P")),
        "fixed": sum(1 for k in keys if not k.startswith("P")),
    }
