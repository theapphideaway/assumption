"""
The scripture store.

Passages live as JSON per book under `data/scripture/<edition>/`, not in the
database: they never change, they benefit from version control, and keeping
them as files lets the whole prayers package stay pure Python.

Nothing ships in the repo yet. `manage.py load_scripture` ingests an edition
per language. For Greek and Russian the free option is also the ecclesiastically
correct one; only English forces a compromise.

    en  World English Bible (WEB)      public domain, modern English. Chosen
                                       over the KJV for readability. The ESV
                                       and NKJV are copyrighted and cannot be
                                       bundled at any price we can justify.
        Brenton's Septuagint           public domain; the LXX-based Old
                                       Testament, which is the correct OT for
                                       Orthodox use. ALREADY LXX-NUMBERED.
    el  Patriarchal Text of 1904       the official ecclesiastical text of the
                                       Church of Constantinople. Public domain,
                                       and exactly what GOARCH reads. NT only,
                                       and UNACCENTED in the edition we ingest.
        Swete's Septuagint             Old Testament, POLYTONIC, and carrying
                                       the full Orthodox deuterocanon. Swete's
                                       text is public domain by age; the
                                       First1KGreek digitisation is CC BY-SA
                                       4.0, so ATTRIBUTION IS REQUIRED.
                                       Ecclesiastes is absent from that repo.
    ru  Синодальный перевод (1876)     the standard Russian Bible, public
                                       domain. Its psalter follows Slavonic/LXX
                                       numbering — verify on load.

Church Slavonic is NOT here. Slavonic belongs to the prayer books, which print
their own psalms and never read from this store.

PSALM NUMBERING. The Orthodox Psalter follows the Septuagint, which runs one
behind the KJV/Masoretic for most of the book and disagrees about where several
psalms divide. Every psalm reference in the prayer documents carries
`"numbering": "lxx"`. Editions that are themselves LXX-numbered — Brenton, the
Synodal, Rahlfs — are listed in LXX_NATIVE below and are NOT converted;
converting them would shift the psalm a second time. Getting this wrong does
not error — it silently serves the wrong psalm.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache

from .books import code_for
from pathlib import Path

_DATA = Path(__file__).parent / "data" / "scripture"

_REF = re.compile(r"^\s*((?:[1-3]\s+)?[A-Za-z]+)\s+(\d+)(?::([\d,\s\-]+))?\s*$")

# One Bible edition per language. The Bible is the Bible — prayer books are a
# separate domain and never read from here.
#
#   ru is the SYNODAL translation (modern Russian). Church Slavonic belongs to
#   the prayer books, not to Bible reading; a reader looking up a Gospel
#   passage wants Russian they can read, not Slavonic.
EDITIONS: dict[str, str] = {
    "en": "web",
    "el": "patriarchal",
    "ru": "synodal",
}

# Optional Septuagint-based Old Testaments. Orthodox Old Testament reading
# follows the LXX, so these are preferred for OT passages where loaded.
OT_EDITIONS: dict[str, str] = {
    "en": "brenton",
    "el": "swete",      # Swete's Septuagint: polytonic, and carries the
                        # Orthodox deuterocanon the Patriarchal NT does not.
}

# Editions whose psalms already follow Septuagint numbering. Converting these
# would shift the psalm twice.
#
# VERIFY EVERY EDITION ON LOAD — do not infer this from the translation's name.
# A printed Russian Synodal Bible is LXX-numbered, but the Zefania file we
# actually ingest has been renumbered to Masoretic chapters to fit the 66-book
# schema, keeping the Synodal reference inline as "(50:3)". So `synodal` is
# NOT listed here: the penitential psalm lives at chapter 51 in that file and
# must be converted like any Masoretic edition. The same translation from a
# different source could well need the opposite.
LXX_NATIVE: frozenset[str] = frozenset(
    {"brenton", "elizabeth", "rahlfs", "swete"})

# The Septuagint and Masoretic psalters do not merely differ by one — they
# disagree about where several psalms divide, so some LXX psalms span two
# Masoretic chapters and some Masoretic chapters cover two LXX psalms. A single
# integer cannot express that, and returning one silently serves wrong text.
_LXX_IRREGULAR: dict[int, tuple[int, ...]] = {
    9:   (9, 10),        # LXX 9 was split into Masoretic 9 and 10
    113: (114, 115),     # LXX 113 was split
    114: (116,),         # Masoretic 116 covers LXX 114 and 115
    115: (116,),
    146: (147,),         # Masoretic 147 covers LXX 146 and 147
    147: (147,),
}


def lxx_to_masoretic(psalm: int) -> tuple[int, ...]:
    """Septuagint psalm number -> the Masoretic chapter(s) covering it.

    Returns a tuple because the mapping is not one-to-one. LXX 113 spans
    Masoretic 114 and 115; LXX 114 and 115 both fall inside Masoretic 116.
    """
    if psalm in _LXX_IRREGULAR:
        return _LXX_IRREGULAR[psalm]
    if 10 <= psalm <= 112 or 116 <= psalm <= 145:
        return (psalm + 1,)
    return (psalm,)                   # 1-8 and 148-150 agree


_OT_BOOKS = frozenset({
    "gen", "genesis", "ex", "exodus", "lev", "leviticus", "num", "numbers",
    "deut", "deuteronomy", "josh", "judg", "ruth", "kingdoms", "chron",
    "ezra", "neh", "esther", "job", "ps", "psalm", "psalms", "prov",
    "proverbs", "eccl", "song", "wisdom", "sirach", "isa", "isaiah", "jer",
    "jeremiah", "lam", "ezek", "ezekiel", "dan", "daniel", "hos", "joel",
    "amos", "obad", "jonah", "micah", "nahum", "hab", "zeph", "hag", "zech",
    "mal", "tobit", "judith", "maccabees",
})


def _is_ot(ref: str) -> bool:
    book = ref.strip().split()[0].lower() if ref.strip() else ""
    return book.rstrip(".") in _OT_BOOKS


def edition_for(lang: str, ref: str, loaded: set[str] | None = None) -> str | None:
    """Which Bible edition serves this reference in this language."""
    if _is_ot(ref):
        ot = OT_EDITIONS.get(lang)
        if ot and (loaded is None or ot in loaded):
            return ot
    return EDITIONS.get(lang)


def available() -> list[str]:
    if not _DATA.exists():
        return []
    return sorted(p.name for p in _DATA.iterdir() if p.is_dir())


@lru_cache(maxsize=128)
def _book(edition: str, book: str) -> dict | None:
    code = code_for(book)
    if not code:
        return None
    path = _DATA / edition / f"{code}.json"
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

    convert = (numbering == "lxx" and book.lower().startswith("ps")
               and edition not in LXX_NATIVE)
    chapters = lxx_to_masoretic(chapter) if convert else (chapter,)

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


def trilingual_resolver(languages=None, loaded: set[str] | None = None):
    """A callable for assembler.assemble(scripture=...).

    Used for actual Bible citations — the daily Gospel, a reading looked up on
    its own. Prayer rules do NOT come through here; their psalms are printed in
    the prayer book itself.
    """
    languages = languages or list(EDITIONS)

    def _get(ref: str, numbering: str = "masoretic"):
        per_lang = {}
        for lang in languages:
            edition = edition_for(lang, ref, loaded)
            if not edition:
                continue
            got = passage(ref, edition=edition, numbering=numbering)
            if got:
                per_lang[lang] = {v["n"]: v["en"] for v in got}
        if not per_lang:
            return None
        numbers = sorted({n for verses in per_lang.values() for n in verses})
        return [{"type": "verse", "n": n,
                 "text": {lang: verses[n] for lang, verses in per_lang.items()
                          if n in verses}}
                for n in numbers]
    return _get
