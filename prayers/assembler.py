"""
Assembling a prayer document for a particular day.

A prayer rule is not a static document fetched once — it is a rendering of the
day. Morning prayers carry the troparion of the day; the Hours carry psalms.
The same engine that resolves the feast fills those slots, which is why a rule
is always correct without anyone maintaining it.

Where a slot cannot be filled — a troparion whose text we do not have yet, a
psalm before the scripture store is loaded — the block is DROPPED and recorded
in `missing`. The app never renders an empty heading, and `missing` gives us a
machine-readable list of exactly what content still needs sourcing.
"""

from __future__ import annotations

from datetime import date

from .blocks import LITERAL_TYPES
from .store import load

MAX_INCLUDE_DEPTH = 4


def assemble(doc_id: str, day: dict, scripture=None) -> dict:
    """Resolve one document against a resolved day.

    `day` is the object from liturgics.resolver.resolve_day.
    `scripture` is an optional callable (ref, numbering) -> list[block]; when
    absent, every scripture block is reported missing rather than faked.
    """
    doc = load(doc_id)
    missing: list[dict] = []
    blocks = _expand(doc["blocks"], day, scripture, missing, depth=0)
    return {
        "id": doc["id"],
        "title": doc["title"],
        "greek": doc.get("greek", ""),
        "slot": doc.get("slot"),
        "minutes": doc.get("minutes"),
        "abbreviated": doc.get("abbreviated", False),
        "blocks": blocks,
        "missing": missing,
    }


def _expand(blocks, day, scripture, missing, depth):
    out = []
    for b in blocks:
        kind = b.get("type")

        if kind in LITERAL_TYPES:
            out.append(b)

        elif kind == "include":
            if depth >= MAX_INCLUDE_DEPTH:
                missing.append({"type": "include", "ref": b["doc"],
                                "why": "include nesting too deep"})
                continue
            out.extend(_expand(load(b["doc"])["blocks"], day, scripture,
                               missing, depth + 1))

        elif kind == "proper":
            filled = _proper(b, day)
            if filled:
                out.append(filled)
            else:
                missing.append({
                    "type": "proper", "slot": b["slot"],
                    "for": day.get("title", ""),
                    "why": "no hymn text on file for this commemoration"})

        elif kind == "scripture":
            if scripture is None:
                missing.append({"type": "scripture", "ref": b["ref"],
                                "why": "scripture store not loaded"})
                continue
            # Pass the block's numbering through. Prayer documents cite the
            # LXX psalter; dropping this silently serves the wrong psalm.
            got = scripture(b["ref"], numbering=b.get("numbering", "masoretic"))
            if got:
                if b.get("heading"):
                    out.append({"type": "heading", "text": b["heading"]})
                out.extend(got)
            else:
                missing.append({"type": "scripture", "ref": b["ref"],
                                "why": "passage not in the scripture store"})
        else:
            # Unknown type: keep it as text rather than dropping a line of a
            # prayer. Better a plain paragraph than a silent omission.
            out.append({"type": "para", "en": b.get("en", ""),
                        "unknown_type": kind})
    return out


def _proper(block: dict, day: dict) -> dict | None:
    """Fill a proper slot from the resolved day.

    Hymn TEXTS are not on file yet — the Menaion carries commemorations, not
    troparia. Until they are sourced this returns None and the block is
    reported missing, which is the honest behaviour: no placeholder text ever
    reaches a phone.
    """
    text = (day.get("propers") or {}).get(block["slot"])
    if not text:
        return None
    return {"type": "hymn", "kind": block["slot"], "en": text,
            "tone": day.get("tone")}
