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
    psalm      a psalm AS PRINTED IN THE PRAYER BOOK, carrying its own text
    scripture  a Bible citation resolved from the scripture store
    silence    a marked pause
    dismissal  the closing

PRAYER BOOKS AND THE BIBLE ARE SEPARATE DOMAINS. A молитвослов prints its
psalms inline — you do not look them up in a Bible — so a psalm inside a
prayer rule is a `psalm` block carrying its own text in each language, sourced
from the prayer book. A `scripture` block is an actual Bible citation, used
for the daily Gospel and for reading a passage on its own, and is the only
block that touches the scripture store.

`include`, `proper`, `psalm` and `scripture` are resolved on the SERVER. The clients
receive a flat list of literal blocks and render it. This is the same rule as
the calendar: nothing that could differ between two platforms is computed on
either of them.
"""

from __future__ import annotations

LITERAL_TYPES = {"heading", "rubric", "para", "refrain", "hymn",
                 "silence", "dismissal"}
RESOLVED_TYPES = {"include", "proper", "scripture", "psalm"}
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
