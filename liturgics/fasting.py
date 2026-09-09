"""
The fast resolver.

This is the most-read output in the entire app — the answer to "can I eat
cheese today" — and also the part most likely to need pastoral correction.
Practice varies between jurisdictions, between parishes, and by a spiritual
father's direction to an individual.

So: every rule below is a named, editable constant rather than clever logic,
and anything uncertain is marked NEEDS_CONFIRMATION. Take this list to Father
before it ships. Do not tune it by copying a Slavic calendar — GOARCH practice
differs, most visibly in the Apostles' Fast.

Precedence, strongest first:
    1. fast-free periods          5. other fasting seasons
    2. Cheesefare week            6. weekly Wednesday and Friday
    3. Great Lent / Holy Week     7. otherwise, no fast
    4. great-feast relaxation
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

__all__ = ["FastLevel", "Fast", "resolve_fast"]


class FastLevel:
    STRICT    = "STRICT"       # xerophagy: no meat, dairy, fish, wine or oil
    WINE_OIL  = "WINE_OIL"     # wine and oil permitted
    FISH      = "FISH"         # fish, wine and oil permitted
    DAIRY     = "DAIRY"        # no meat; dairy, eggs and fish permitted
    FAST_FREE = "FAST_FREE"


LABELS = {
    FastLevel.STRICT:    "Strict Fast",
    FastLevel.WINE_OIL:  "Wine & Oil",
    FastLevel.FISH:      "Fish, Wine & Oil",
    FastLevel.DAIRY:     "Dairy Allowed",
    FastLevel.FAST_FREE: "Fast-Free",
}


@dataclass(frozen=True)
class Fast:
    level: str
    label: str
    reason: str          # shown as the small line under the chip

    @property
    def is_fast(self) -> bool:
        return self.level != FastLevel.FAST_FREE


WEDNESDAY, FRIDAY, SATURDAY, SUNDAY = 2, 4, 5, 6

# --- fixed-date seasons (month, day) inclusive, Gregorian for GOARCH ---
NATIVITY_FAST_START = (11, 15)
NATIVITY_FAST_STRICTER = (12, 18)     # NEEDS_CONFIRMATION
NATIVITY_FAST_END = (12, 24)
DORMITION_FAST = ((8, 1), (8, 14))
APOSTLES_FAST_END = (6, 28)
NATIVITY_TO_THEOPHANY = ((12, 25), (1, 4))
ANNUNCIATION = (3, 25)
TRANSFIGURATION = (8, 6)

# --- paschal-offset ranges ---
PUBLICAN_WEEK = (-70, -64)
CHEESEFARE_WEEK = (-55, -49)
GREAT_LENT = (-48, -8)
HOLY_WEEK = (-7, -1)
BRIGHT_WEEK = (0, 6)
PENTECOST_WEEK = (50, 56)
APOSTLES_FAST_BEGINS = 57


def _md(d: date) -> tuple[int, int]:
    return (d.month, d.day)


def _within(d: date, start: tuple[int, int], end: tuple[int, int]) -> bool:
    """Inclusive month/day range, handling ranges that wrap the new year."""
    md = _md(d)
    if start <= end:
        return start <= md <= end
    return md >= start or md <= end


def resolve_fast(d: date, offset: int, rank: int | None = None) -> Fast:
    """Resolve the fasting rule for a civil date.

    `offset` is the paschal offset; `rank` is the day's feast rank if it is a
    ranked feast (1 Pascha, 2 Great Feast), which relaxes the weekly fast.
    """
    dow = d.weekday()

    # 1 — fast-free -----------------------------------------------------
    if _within(d, *NATIVITY_TO_THEOPHANY):
        return Fast(FastLevel.FAST_FREE, LABELS[FastLevel.FAST_FREE],
                    "The Twelve Days of Nativity")
    if PUBLICAN_WEEK[0] <= offset <= PUBLICAN_WEEK[1]:
        return Fast(FastLevel.FAST_FREE, LABELS[FastLevel.FAST_FREE],
                    "Week of the Publican and the Pharisee")
    if BRIGHT_WEEK[0] <= offset <= BRIGHT_WEEK[1]:
        return Fast(FastLevel.FAST_FREE, LABELS[FastLevel.FAST_FREE],
                    "Bright Week")
    if PENTECOST_WEEK[0] <= offset <= PENTECOST_WEEK[1]:
        return Fast(FastLevel.FAST_FREE, LABELS[FastLevel.FAST_FREE],
                    "Week of the Holy Spirit")

    # 2 — Cheesefare: no meat, but dairy all week including Wed and Fri --
    if CHEESEFARE_WEEK[0] <= offset <= CHEESEFARE_WEEK[1]:
        return Fast(FastLevel.DAIRY, LABELS[FastLevel.DAIRY], "Cheesefare Week")

    # 3 — Great Lent and Holy Week --------------------------------------
    if GREAT_LENT[0] <= offset <= HOLY_WEEK[1]:
        if offset == -2:
            return Fast(FastLevel.STRICT, LABELS[FastLevel.STRICT],
                        "Great and Holy Friday")
        if offset == -7:
            return Fast(FastLevel.FISH, LABELS[FastLevel.FISH], "Palm Sunday")
        if _md(d) == ANNUNCIATION:
            return Fast(FastLevel.FISH, LABELS[FastLevel.FISH], "The Annunciation")
        if offset == -8:
            # NEEDS_CONFIRMATION: many keep fish roe on Lazarus Saturday.
            return Fast(FastLevel.WINE_OIL, LABELS[FastLevel.WINE_OIL],
                        "Lazarus Saturday")
        if HOLY_WEEK[0] <= offset <= HOLY_WEEK[1]:
            return Fast(FastLevel.STRICT, LABELS[FastLevel.STRICT], "Holy Week")
        if dow in (SATURDAY, SUNDAY):
            return Fast(FastLevel.WINE_OIL, LABELS[FastLevel.WINE_OIL],
                        "Great Lent — Saturday and Sunday")
        return Fast(FastLevel.STRICT, LABELS[FastLevel.STRICT], "Great Lent")

    # 4 — Apostles' Fast (variable length; can be very short) ------------
    if offset >= APOSTLES_FAST_BEGINS and _md(d) <= APOSTLES_FAST_END:
        # NEEDS_CONFIRMATION: GOARCH practice on fish days differs from Slavic.
        if dow in (WEDNESDAY, FRIDAY):
            return Fast(FastLevel.STRICT, LABELS[FastLevel.STRICT],
                        "Apostles' Fast")
        return Fast(FastLevel.FISH, LABELS[FastLevel.FISH], "Apostles' Fast")

    # 5 — Dormition Fast — the parish's own season -----------------------
    if _within(d, *DORMITION_FAST):
        if _md(d) == TRANSFIGURATION:
            return Fast(FastLevel.FISH, LABELS[FastLevel.FISH],
                        "The Transfiguration")
        if dow in (SATURDAY, SUNDAY):
            return Fast(FastLevel.WINE_OIL, LABELS[FastLevel.WINE_OIL],
                        "Dormition Fast")
        return Fast(FastLevel.STRICT, LABELS[FastLevel.STRICT], "Dormition Fast")

    # 6 — Nativity Fast --------------------------------------------------
    if _within(d, NATIVITY_FAST_START, NATIVITY_FAST_END):
        stricter = _md(d) >= NATIVITY_FAST_STRICTER
        if _md(d) == NATIVITY_FAST_END:
            return Fast(FastLevel.STRICT, LABELS[FastLevel.STRICT],
                        "Eve of the Nativity")
        if stricter:
            level = (FastLevel.WINE_OIL if dow in (SATURDAY, SUNDAY)
                     else FastLevel.STRICT)
        elif dow in (WEDNESDAY, FRIDAY):
            level = FastLevel.STRICT
        else:
            level = FastLevel.FISH
        return Fast(level, LABELS[level], "Nativity Fast")

    # 7 — the weekly fast, relaxed for great feasts ----------------------
    if dow in (WEDNESDAY, FRIDAY):
        if rank is not None and rank <= 2:
            return Fast(FastLevel.FISH, LABELS[FastLevel.FISH],
                        "Great Feast falling on a fast day")
        day = "Wednesday" if dow == WEDNESDAY else "Friday"
        return Fast(FastLevel.STRICT, LABELS[FastLevel.STRICT], day)

    return Fast(FastLevel.FAST_FREE, LABELS[FastLevel.FAST_FREE], "")
