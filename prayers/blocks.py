"""
The block schema, and the rules for resolving it.

Prayer documents are stored as JSON in `data/` rather than in the database:
they are fixed liturgical texts, they benefit from version control, and Father
has no reason to edit them. The Menaion is stored the same way for the same
reasons.

Ten block types, deliberately closed. Both the Swift and Kotlin renderers
implement exactly these, and an unknown type must degrade to plain text rather
than vanish — an old app build must never silently drop a line of a prayer.

    heading    a section title
    rubric     an instruction, rendered in red
    para       a prayer or sentence; carries `en` and optionally `el`
    refrain    a short line said a set number of times ("Lord, have mercy" x12)
    hymn       troparion, kontakion, apolytikion; carries `tone`
    include    splice in another document (the Trisagion, six times over)
    proper     a slot filled from the resolved day (troparion of the day)
    scripture  a passage filled from the scripture store (psalms, the Gospel)
    silence    a marked pause
    dismissal  the closing

`include`, `proper` and `scripture` are resolved on the SERVER. The clients
receive a flat list of literal blocks and render it. This is the same rule as
the calendar: nothing that could differ between two platforms is computed on
either of them.
"""

from __future__ import annotations

LITERAL_TYPES = {"heading", "rubric", "para", "refrain", "hymn",
                 "silence", "dismissal"}
RESOLVED_TYPES = {"include", "proper", "scripture"}
BLOCK_TYPES = LITERAL_TYPES | RESOLVED_TYPES

# Time-of-day slots. The server reports a suggestion using the parish
# timezone; the client is free to prefer the device clock, which is the one
# deliberate exception to "clients compute nothing".
SLOTS = ("morning", "hours", "evening", "compline")

SLOT_WINDOWS = (
    # (start_hour, end_hour_exclusive, slot)
    (4, 11, "morning"),
    (11, 17, "hours"),
    (17, 22, "evening"),
)


def slot_for_hour(hour: int) -> str:
    for start, end, slot in SLOT_WINDOWS:
        if start <= hour < end:
            return slot
    return "compline"          # 22:00 through 03:59


class MissingContent(Exception):
    """Raised only by strict resolution; normally missing content is reported
    rather than raised, so the app never shows an empty section."""
