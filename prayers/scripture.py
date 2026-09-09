"""
The scripture store.

Passages live as JSON per book under `data/scripture/<edition>/`, not in the
database: they never change, they benefit from version control, and keeping
them as files lets the whole prayers package stay pure Python.

Nothing ships in the repo yet. `manage.py load_scripture` ingests a
public-domain edition:

    KJV        — New Testament and Old Testament. Public domain.
    Brenton    — the Septuagint in English. Public domain, and the correct
                 Old Testament for Orthodox use.

PSALM NUMBERING. The Orthodox Psalter follows the Septuagint, which runs one
behind the KJV/Masoretic for most of the book (LXX 50 = KJV 51). Every psalm
reference in the prayer documents carries `"numbering": "lxx"`, and this module
converts when reading from a Masoretic-numbered edition. Getting this wrong
does not error — it silently serves the wrong psalm.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).parent / "data" / "scripture"

_REF = re.compile(r"^\s*((?:[1-3]\s+)?[A-Za-z]+)\s+(\d+)(?::([\d,\s\-]+))?\s*$")


# The Septuagint and Masoretic psalters do not merely differ by one — they
# disagree about where several psalms divide, so some LXX psalms span two KJV
# chapters and some KJV chapters cover two LXX psalms. A single integer cannot
# express that, and returning one silently serves the wrong text.
_LXX_IRREGULAR: dict[int, tuple[int, ...]] = {
    9:   (9, 10),        # LXX 9 was split into KJV 9 and 10
    113: (114, 115),     # LXX 113 was split
    114: (116,),         # KJV 116 covers LXX 114 and 115
    115: (116,),
    146: (147,),         # KJV 147 covers LXX 146 and 147
    147: (147,),
}


def lxx_to_masoretic(psalm: int) -> tuple[int, ...]:
    """Septuagint psalm number -> the KJV/Masoretic chapter(s) covering it.

    Returns a tuple because the mapping is not one-to-one. LXX 113 spans KJV
    114 and 115; LXX 114 and 115 both fall inside KJV 116.
    """
    if psalm in _LXX_IRREGULAR:
        return _LXX_IRREGULAR[psalm]
    if 10 <= psalm <= 112:
        return (psalm + 1,)
    if 116 <= psalm <= 145:
        return (psalm + 1,)
    return (psalm,)                   # 1-8 and 148-150 agree


@lru_cache(maxsize=1)
def available() -> list[str]:
    if not _DATA.exists():
        return []
    return sorted(p.name for p in _DATA.iterdir() if p.is_dir())


@lru_cache(maxsize=128)
def _book(edition: str, book: str) -> dict | None:
    path = _DATA / edition / f"{book.lower().replace(' ', '')}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def passage(ref: str, edition: str = "kjv", numbering: str = "masoretic"):
    """Return verse blocks for a reference, or None if unavailable.

    Returning None rather than raising is deliberate: the assembler reports the
    gap and the app renders nothing, instead of showing an empty heading or a
    placeholder that looks like scripture but is not.
    """
    m = _REF.match(ref)
    if not m:
        return None
    book, chapter, verses = m.group(1), int(m.group(2)), m.group(3)

    chapters = (lxx_to_masoretic(chapter)
                if numbering == "lxx" and book.lower().startswith("ps")
                else (chapter,))

    data = _book(edition, book)
    if not data:
        return None

    out = []
    for c in chapters:
        ch = data.get(str(c))
        if not ch:
            continue
        # A verse range only makes sense against a single chapter. Where an LXX
        # psalm spans two KJV chapters we serve both in full rather than guess
        # how the verse numbers should carry across the seam.
        spec = verses if len(chapters) == 1 else None
        out.extend({"type": "verse", "n": n, "en": ch[str(n)], "chapter": c}
                   for n in _verse_numbers(spec, ch) if str(n) in ch)
    return out or None


def _verse_numbers(spec: str | None, chapter: dict) -> list[int]:
    if not spec:
        return sorted(int(k) for k in chapter)
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return out


def resolver(edition: str = "kjv"):
    """A callable for assembler.assemble(scripture=...)."""
    def _get(ref: str, numbering: str = "masoretic"):
        return passage(ref, edition=edition, numbering=numbering)
    return _get
