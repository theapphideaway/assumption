"""
The Paschalion: computing the date of Pascha.

All Orthodox jurisdictions except the Church of Finland — GOARCH included —
compute Pascha on the JULIAN calendar, then observe it on the corresponding
civil (Gregorian) date. That is true even for New Calendar jurisdictions like
GOARCH, which keep FIXED feasts on the Gregorian date. Holding both calendars
at once is the single most important thing this module gets right.

Conversion is done through Julian Day Numbers rather than a "+13 days" constant.
The 13-day gap is only correct for 1900-2099; it becomes 14 in 2100. JDN
arithmetic is exact for any year and costs nothing.

No Django imports here, by design — this is a pure function library so the
whole engine can be tested in milliseconds.
"""

from __future__ import annotations

from datetime import date, timedelta

__all__ = ["pascha", "julian_to_gregorian", "gregorian_to_julian", "reference_pascha"]

# Offset of the Triodion opening (Sunday of the Publican and the Pharisee)
# from Pascha. A civil date earlier than this belongs to the PREVIOUS
# paschal cycle, not the coming one.
TRIODION_OPENS = -70


def _julian_to_jdn(year: int, month: int, day: int) -> int:
    """Julian-calendar date -> Julian Day Number."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083


def _jdn_to_gregorian(jdn: int) -> date:
    """Julian Day Number -> Gregorian (civil) date."""
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - 146097 * b // 4
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    return date(
        100 * b + d - 4800 + m // 10,
        m + 3 - 12 * (m // 10),
        e - (153 * m + 2) // 5 + 1,
    )


def _gregorian_to_jdn(year: int, month: int, day: int) -> int:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return (day + (153 * m + 2) // 5 + 365 * y
            + y // 4 - y // 100 + y // 400 - 32045)


def _jdn_to_julian(jdn: int) -> tuple[int, int, int]:
    c = jdn + 32082
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    return (d - 4800 + m // 10, m + 3 - 12 * (m // 10),
            e - (153 * m + 2) // 5 + 1)


def julian_to_gregorian(year: int, month: int, day: int) -> date:
    """Convert a Julian-calendar date to the civil date it falls on."""
    return _jdn_to_gregorian(_julian_to_jdn(year, month, day))


def gregorian_to_julian(d: date) -> tuple[int, int, int]:
    """Convert a civil date to its Julian-calendar (Old Style) equivalent.

    Used for the second date line on the Today screen — a good number of
    parishioners still track Old Style.
    """
    return _jdn_to_julian(_gregorian_to_jdn(d.year, d.month, d.day))


def pascha(year: int) -> date:
    """Civil (Gregorian) date of Orthodox Pascha for the given civil year.

    Meeus's Julian algorithm. Returns the Julian result converted to the
    civil calendar, which is the date the parish actually celebrates.
    """
    a = year % 4
    b = year % 7
    c = year % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    month = (d + e + 114) // 31
    day = ((d + e + 114) % 31) + 1
    return julian_to_gregorian(year, month, day)


def reference_pascha(d: date) -> tuple[date, int]:
    """Return (pascha, offset_in_days) for the paschal cycle `d` belongs to.

    A date in, say, January sits *after* the previous Pascha and *before* the
    coming one; which cycle owns it depends on whether the Triodion has opened.
    Everything movable in the calendar is derived from the offset this returns,
    so this function is the hinge of the whole engine.
    """
    p = pascha(d.year)
    offset = (d - p).days
    if offset < TRIODION_OPENS:
        p = pascha(d.year - 1)
        offset = (d - p).days
    return p, offset
