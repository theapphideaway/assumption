"""
The movable cycle: everything keyed to Pascha.

Seasons, named days, the eight-week Tone cycle and the eleven Matins Gospels
are all pure functions of the paschal offset, which means they are exactly
testable against any published calendar. Fixed-date commemorations (the
Menaion) are authored data and live elsewhere.

Offsets follow GOARCH usage. Days marked NEEDS_CONFIRMATION should be checked
with Father before the app shows them to the parish.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .paschalion import reference_pascha

__all__ = ["Season", "season_for", "movable_day", "tone_for", "eothinon_for",
           "MOVABLE_DAYS"]


@dataclass(frozen=True)
class Season:
    key: str
    label: str
    color: str      # design token, not a claim about vestments
    greek: str = ""


TRIODION      = Season("triodion", "Triodion", "porphyry", "Τριῴδιον")
GREAT_LENT    = Season("great_lent", "Great Lent", "porphyry", "Μεγάλη Τεσσαρακοστή")
HOLY_WEEK     = Season("holy_week", "Holy Week", "porphyry", "Μεγάλη Ἑβδομάς")
BRIGHT_WEEK   = Season("bright_week", "Bright Week", "gold", "Διακαινήσιμος")
PENTECOSTARION= Season("pentecostarion", "Pentecostarion", "gold", "Πεντηκοστάριον")
AFTER_PENTECOST = Season("after_pentecost", "After Pentecost", "verte")


def season_for(offset: int) -> Season:
    """Season from the paschal offset."""
    if offset < -70:                      # normalised away by reference_pascha
        return AFTER_PENTECOST
    if -70 <= offset <= -49:
        return TRIODION
    if -48 <= offset <= -8:               # Clean Monday .. Lazarus Saturday
        return GREAT_LENT
    if -7 <= offset <= -1:                # Palm Sunday .. Holy Saturday
        return HOLY_WEEK
    if 0 <= offset <= 6:
        return BRIGHT_WEEK
    if 7 <= offset <= 56:                 # Thomas Sunday .. All Saints
        return PENTECOSTARION
    return AFTER_PENTECOST


# offset -> (english, rank, greek, slavonic)
# rank: 1 Pascha · 2 Great Feast · 3 major · 4 notable
MOVABLE_DAYS: dict[int, tuple[str, int, str, str]] = {
    -70: ("Sunday of the Publican and the Pharisee", 4, "", "Неделя о мытаре и фарисее"),
    -63: ("Sunday of the Prodigal Son", 4, "", "Неделя о блудном сыне"),
    -57: ("Saturday of Souls", 4, "Ψυχοσάββατον", "Вселенская родительская суббота"),
    -56: ("Sunday of the Last Judgement (Meatfare)", 4, "Ἀπόκρεω", "Неделя о Страшном Суде"),
    -50: ("Saturday of the Ascetics", 4, "", "Суббота сырная"),
    -49: ("Forgiveness Sunday (Cheesefare)", 4, "Τυρινή", "Прощёное воскресенье"),
    -48: ("Clean Monday", 3, "Καθαρὰ Δευτέρα", "Чистый понедельник"),
    -44: ("First Salutations to the Theotokos", 4, "Α΄ Χαιρετισμοί", "Первые Похвалы Пресвятой Богородице"),
    -43: ("Saturday of St. Theodore the Recruit", 4, "", "Суббота вмч. Феодора Тирона"),
    -42: ("Sunday of Orthodoxy", 3, "Κυριακὴ τῆς Ὀρθοδοξίας", "Торжество Православия"),
    -37: ("Second Salutations to the Theotokos", 4, "Β΄ Χαιρετισμοί", "Вторые Похвалы Пресвятой Богородице"),
    -35: ("Sunday of St. Gregory Palamas", 4, "", "Неделя свт. Григория Паламы"),
    -30: ("Third Salutations to the Theotokos", 4, "Γ΄ Χαιρετισμοί", "Третьи Похвалы Пресвятой Богородице"),
    -28: ("Sunday of the Veneration of the Cross", 3, "Σταυροπροσκυνήσεως", "Крестопоклонная неделя"),
    -23: ("Fourth Salutations to the Theotokos", 4, "Δ΄ Χαιρετισμοί", "Четвёртые Похвалы Пресвятой Богородице"),
    -21: ("Sunday of St. John Climacus", 4, "", "Неделя прп. Иоанна Лествичника"),
    -16: ("The Akathist Hymn", 3, "Ἀκάθιστος Ὕμνος", "Похвала Пресвятой Богородицы · Акафист"),
    -14: ("Sunday of St. Mary of Egypt", 4, "", "Неделя прп. Марии Египетской"),
    -8:  ("Lazarus Saturday", 3, "Σάββατον τοῦ Λαζάρου", "Лазарева суббота"),
    -7:  ("Palm Sunday", 2, "Κυριακὴ τῶν Βαΐων", "Вход Господень в Иерусалим"),
    -6:  ("Great and Holy Monday", 3, "", "Великий Понедельник"),
    -5:  ("Great and Holy Tuesday", 3, "", "Великий Вторник"),
    -4:  ("Great and Holy Wednesday", 3, "", "Великая Среда"),
    -3:  ("Great and Holy Thursday", 3, "", "Великий Четверг"),
    -2:  ("Great and Holy Friday", 2, "Μεγάλη Παρασκευή", "Великая Пятница"),
    -1:  ("Great and Holy Saturday", 2, "Μέγα Σάββατον", "Великая Суббота"),
     0:  ("Great and Holy Pascha", 1, "Τὸ Ἅγιον Πάσχα", "Пасха · Светлое Христово Воскресение"),
     1:  ("Bright Monday", 3, "", "Светлый Понедельник"),
     2:  ("Bright Tuesday", 3, "", "Светлый Вторник"),
     3:  ("Bright Wednesday", 3, "", "Светлая Среда"),
     4:  ("Bright Thursday", 3, "", "Светлый Четверг"),
     5:  ("Bright Friday · the Life-Giving Spring", 3, "Ζωοδόχου Πηγῆς", "Светлая Пятница · Живоносного Источника"),
     6:  ("Bright Saturday", 3, "", "Светлая Суббота"),
     7:  ("Thomas Sunday (Antipascha)", 3, "Τοῦ Θωμᾶ", "Антипасха · Фомина неделя"),
    14:  ("Sunday of the Myrrh-Bearing Women", 4, "Τῶν Μυροφόρων", "Неделя жён-мироносиц"),
    21:  ("Sunday of the Paralytic", 4, "", "Неделя о расслабленном"),
    24:  ("Mid-Pentecost", 4, "Μεσοπεντηκοστή", "Преполовение Пятидесятницы"),
    28:  ("Sunday of the Samaritan Woman", 4, "", "Неделя о самаряныне"),
    35:  ("Sunday of the Blind Man", 4, "", "Неделя о слепом"),
    39:  ("The Ascension of the Lord", 2, "Ἀνάληψις", "Вознесение Господне"),
    42:  ("Sunday of the Fathers of the First Council", 4, "", "Неделя святых отцов I Вселенского Собора"),
    48:  ("Saturday of Souls before Pentecost", 4, "Ψυχοσάββατον", "Троицкая родительская суббота"),
    49:  ("Holy Pentecost", 2, "Πεντηκοστή", "День Святой Троицы · Пятидесятница"),
    50:  ("Monday of the Holy Spirit", 3, "Ἁγίου Πνεύματος", "День Святаго Духа"),
    56:  ("Sunday of All Saints", 3, "Τῶν Ἁγίων Πάντων", "Неделя всех святых"),
}


def movable_day(offset: int) -> tuple[str, int, str, str] | None:
    """English, rank, Greek and Slavonic for a movable commemoration."""
    return MOVABLE_DAYS.get(offset)


def tone_for(d: date) -> int | None:
    """The Tone (Ἦχος) of the week, 1-8.

    The Octoechos cycle restarts at Tone 1 on Thomas Sunday and advances every
    Sunday. Bright Week has no single tone, so this returns None there.
    Dates in the Triodion continue the *previous* year's cycle, which is why
    this falls back to the prior Pascha rather than returning None.
    """
    p, offset = reference_pascha(d)
    if -7 <= offset <= 6:
        # Holy Week and Bright Week set the Octoechos aside entirely.
        return None
    if offset >= 7:
        return ((offset - 7) // 7) % 8 + 1
    from .paschalion import pascha
    prev_offset = (d - pascha(p.year - 1)).days
    return ((prev_offset - 7) // 7) % 8 + 1


def eothinon_for(d: date) -> int | None:
    """The Matins Gospel (Ἑωθινόν), 1-11 — Sundays only.

    NEEDS_CONFIRMATION: the cycle begins on the Sunday of All Saints and is
    interrupted by the Triodion and Pentecostarion, which have their own
    appointed Matins Gospels. This returns a value only in the after-Pentecost
    stretch, where the plain cycle applies. Confirm the boundaries with Father
    before surfacing it.
    """
    if d.weekday() != 6:                  # Sunday
        return None
    _, offset = reference_pascha(d)
    if offset < 56:
        return None
    return ((offset - 56) // 7) % 11 + 1
