"""
The daily readings.

HONESTY NOTE. Sundays, Great Feasts and Holy Week are seeded here and are
reliable. **Ordinary weekdays are not covered.** The weekday lectionary runs on
a continuous course-reading cycle whose hardest feature is the "Lucan jump" —
the course of Luke begins on the Monday after the Elevation of the Cross rather
than at a fixed offset from Pascha — and it interacts with Menaion feasts in
ways that cannot be reconstructed reliably from memory.

Rather than invent plausible-looking references, days with no entry return
nothing and are reported as missing. This is the single largest content gap in
the project and the strongest reason to get written permission from the
Archdiocese or AGES for their lectionary data.
"""

from __future__ import annotations

from datetime import date

__all__ = ["readings_for", "coverage"]

# Movable cycle, keyed by paschal offset. (epistle, gospel)
MOVABLE: dict[int, tuple[str, str]] = {
    -70: ("2 Tim 3:10-15", "Luke 18:10-14"),
    -63: ("1 Cor 6:12-20", "Luke 15:11-32"),
    -57: ("1 Cor 10:23-28", "Luke 21:8-9, 25-27, 33-36"),
    -56: ("1 Cor 8:8-9:2", "Matt 25:31-46"),
    -50: ("Rom 14:19-23, 16:25-27", "Matt 6:1-13"),
    -49: ("Rom 13:11-14:4", "Matt 6:14-21"),
    -42: ("Heb 11:24-26, 32-12:2", "John 1:43-51"),
    -35: ("Heb 1:10-2:3", "Mark 2:1-12"),
    -28: ("Heb 4:14-5:6", "Mark 8:34-9:1"),
    -21: ("Heb 6:13-20", "Mark 9:17-31"),
    -14: ("Heb 9:11-14", "Mark 10:32-45"),
     -8: ("Heb 12:28-13:8", "John 11:1-45"),
     -7: ("Phil 4:4-9", "John 12:1-18"),
     -2: ("", "Matt 27:1-38"),
     -1: ("Rom 6:3-11", "Matt 28:1-20"),
      0: ("Acts 1:1-8", "John 1:1-17"),
      1: ("Acts 1:12-17, 21-26", "John 1:18-28"),
      2: ("Acts 2:14-21", "Luke 24:12-35"),
      3: ("Acts 2:22-38", "John 1:35-51"),
      4: ("Acts 2:38-43", "John 3:1-15"),
      5: ("Acts 3:1-8", "John 2:12-22"),
      6: ("Acts 3:11-16", "John 3:22-33"),
      7: ("Acts 5:12-20", "John 20:19-31"),
     14: ("Acts 6:1-7", "Mark 15:43-16:8"),
     21: ("Acts 9:32-42", "John 5:1-15"),
     24: ("Acts 14:6-18", "John 7:14-30"),
     28: ("Acts 11:19-30", "John 4:5-42"),
     35: ("Acts 16:16-34", "John 9:1-38"),
     39: ("Acts 1:1-12", "Luke 24:36-53"),
     42: ("Acts 20:16-18, 28-36", "John 17:1-13"),
     48: ("Acts 28:1-31", "John 21:15-25"),
     49: ("Acts 2:1-11", "John 7:37-52, 8:12"),
     50: ("Eph 5:8-19", "Matt 18:10-20"),
     56: ("Heb 11:33-12:2", "Matt 10:32-33, 37-38, 19:27-30"),
}

# Fixed dates: the Great Feasts and the days most likely to be looked up.
FIXED: dict[str, tuple[str, str]] = {
    "01-01": ("Col 2:8-12", "Luke 2:20-21, 40-52"),
    "01-06": ("Titus 2:11-14, 3:4-7", "Matt 3:13-17"),
    "01-30": ("Heb 13:7-16", "Matt 5:14-19"),
    "02-02": ("Heb 7:7-17", "Luke 2:22-40"),
    "03-25": ("Heb 2:11-18", "Luke 1:24-38"),
    "04-23": ("Acts 12:1-11", "John 15:17-16:2"),
    "06-24": ("Rom 13:11-14:4", "Luke 1:1-25, 57-68, 76, 80"),
    "06-29": ("2 Cor 11:21-12:9", "Matt 16:13-19"),
    "07-20": ("James 5:10-20", "Luke 4:22-30"),
    "08-06": ("2 Peter 1:10-19", "Matt 17:1-9"),
    "08-15": ("Phil 2:5-11", "Luke 10:38-42, 11:27-28"),
    "08-29": ("Acts 13:25-32", "Mark 6:14-30"),
    "09-08": ("Phil 2:5-11", "Luke 10:38-42, 11:27-28"),
    "09-14": ("1 Cor 1:18-24", "John 19:6-11, 13-20, 25-28, 30"),
    "10-26": ("2 Tim 2:1-10", "John 15:17-16:2"),
    "11-08": ("Heb 2:2-10", "Luke 10:16-21"),
    "11-09": ("2 Cor 4:6-15", "Luke 6:17-23"),
    "11-13": ("Heb 7:26-8:2", "John 10:9-16"),
    "11-21": ("Heb 9:1-7", "Luke 10:38-42, 11:27-28"),
    "12-06": ("Heb 13:17-21", "Luke 6:17-23"),
    "12-25": ("Gal 4:4-7", "Matt 2:1-12"),
}


def readings_for(d: date, offset: int) -> dict | None:
    """Epistle and Gospel for a day, or None if not on file.

    Movable entries win: Pascha outranks whatever fixed date it lands on.
    """
    entry = MOVABLE.get(offset) or FIXED.get(f"{d.month:02d}-{d.day:02d}")
    if not entry:
        return None
    epistle, gospel = entry
    out = {"gospel": gospel, "source": "movable" if offset in MOVABLE else "fixed"}
    if epistle:
        out["epistle"] = epistle
    return out


def coverage() -> dict:
    return {"movable_days": len(MOVABLE), "fixed_days": len(FIXED),
            "weekdays_covered": False,
            "gap": "Ordinary weekday course readings, including the Lucan jump."}


# ---------------------------------------------------------------------------
# The course-reading cycle
# ---------------------------------------------------------------------------
#
# Weekday readings run as a course (lectio continua) rather than by paschal
# offset, and the hard part is that the course of Luke does NOT key to Pascha.
# It begins on the Monday after the Sunday following the Elevation of the Cross
# (14 September) — a FIXED date. So the number of weeks in the Matthew course
# varies from year to year with the date of Pascha, and that variation is the
# whole difficulty. It is computed here rather than guessed.
#
# The pericope tables themselves are NOT in this repo. Filling roughly 700
# chapter-and-verse references from memory would produce plausible-looking
# errors in exactly the place a priest would notice them. `PERICOPES` is loaded
# from data/pericopes.json when present; until then the engine reports the day
# as unsourced and says so, which the app renders honestly.

import json as _json
from datetime import timedelta as _td
from functools import lru_cache as _lru
from pathlib import Path as _Path

ELEVATION = (9, 14)
_PERICOPES = _Path(__file__).parent / "data" / "pericopes.json"


@_lru(maxsize=1)
def pericopes() -> dict:
    """The weekday course tables, when someone has supplied them.

    Shape, keyed gospel -> week -> weekday index (0 = Monday):

        {"MAT": {"1": {"0": {"epistle": "Rom 1:1-7",
                             "gospel":  "Matt 4:25-5:13"}}}}

    Drop a file at data/pericopes.json and every weekday resolves; no code
    changes. Absent, the engine reports days as unsourced and says why.
    """
    if not _PERICOPES.exists():
        return {}
    return _json.loads(_PERICOPES.read_text(encoding="utf-8"))


def lucan_jump(year: int) -> date:
    """The Monday the course of Luke begins: after the Sunday following 14 Sept."""
    elevation = date(year, *ELEVATION)
    # The Sunday strictly after the Elevation.
    days_ahead = (6 - elevation.weekday()) % 7 or 7
    sunday_after = elevation + _td(days=days_ahead)
    return sunday_after + _td(days=1)


# After Pentecost the SUNDAY and WEEKDAY gospel courses diverge. Sundays run
# through Matthew, but weekdays switch to Mark partway; the same happens in the
# Lucan period. Treating a day's course as one value gets weekdays wrong for
# roughly a third of the year — verified against a published daily reading for
# Wednesday 9 September 2026, week 15 after Pentecost, which appoints Mark.
#
# NEEDS_CONFIRMATION: the switch weeks below are standard Byzantine practice,
# but jurisdictions differ on the exact boundary. Confirm with Father.
MATTHEW_WEEKDAY_WEEKS = 11      # weeks 1-11 weekdays read Matthew, then Mark
LUKE_WEEKDAY_WEEKS = 12         # weeks 1-12 weekdays read Luke, then Mark


def course_for(d: date, offset: int) -> dict | None:
    """Which gospel course a date falls in, and how far into it.

    Returns None inside the Triodion and Pentecostarion, which have their own
    appointed readings rather than a course.
    """
    if offset < 0 or offset <= 49:
        return None                      # Triodion, Holy Week, Pentecostarion

    jump = lucan_jump(d.year)
    is_sunday = d.weekday() == 6

    if d < jump:
        pentecost = d - _td(days=offset - 49)
        week = ((d - pentecost).days // 7) + 1
        sunday_gospel = "MAT"
        weekday_gospel = "MAT" if week <= MATTHEW_WEEKDAY_WEEKS else "MRK"
    else:
        week = ((d - jump).days // 7) + 1
        sunday_gospel = "LUK"
        weekday_gospel = "LUK" if week <= LUKE_WEEKDAY_WEEKS else "MRK"

    return {
        "gospel": sunday_gospel if is_sunday else weekday_gospel,
        "sunday_gospel": sunday_gospel,
        "weekday_gospel": weekday_gospel,
        "week": week,
        "day": d.weekday(),
    }


def lenten_weekday(offset: int, weekday: int) -> bool:
    """Monday to Friday of Great Lent, when the full Liturgy is not served."""
    return -48 <= offset <= -9 and weekday < 5


def readings_detail(d: date, offset: int) -> dict:
    """Readings for a day, or an explicit reason we cannot supply them.

    EVERY day of the year has appointed readings. What changes is WHICH
    services carry them. Outside Lent it is an Epistle and Gospel at the
    Liturgy. On weekdays of Great Lent the full Liturgy is not served, so the
    appointed readings are Old Testament instead — Genesis and Proverbs at
    Vespers, Isaiah at the Sixth Hour, each read as a course through the fast.

    So a Lenten weekday is not an empty day. Reporting it as "no readings"
    would be simply wrong, and would tell a parishioner there is nothing
    appointed when in fact there are three lessons.
    """
    got = readings_for(d, offset)
    if got:
        return {**got, "status": "appointed"}

    if lenten_weekday(offset, d.weekday()):
        return {
            "status": "unsourced",
            "kind": "lenten_old_testament",
            "services": ["vespers", "sixth_hour"],
            "courses": ["GEN", "PRO", "ISA"],
            "note": ("Weekday of Great Lent: no Gospel at Liturgy, but Genesis "
                     "and Proverbs are appointed at Vespers and Isaiah at the "
                     "Sixth Hour. Course tables not yet loaded."),
        }

    course = course_for(d, offset)
    if course:
        table = pericopes().get(course["gospel"], {})
        entry = table.get(str(course["week"]), {}).get(str(course["day"]))
        if entry:
            return {**entry, "status": "appointed", "source": "course",
                    "course": course}
        return {"status": "unsourced", "kind": "weekday_course", "course": course,
                "note": "Weekday course reading — pericope table not yet loaded."}

    if 1 <= offset <= 49:
        return {
            "status": "unsourced", "kind": "pentecostarion_course",
            "services": ["liturgy"], "courses": ["ACT", "JHN"],
            "note": ("Paschal season: Acts and John are read daily. Course "
                     "table not yet loaded."),
        }

    return {"status": "unsourced", "kind": "triodion",
            "note": "Triodion weekday — reading not yet on file."}
