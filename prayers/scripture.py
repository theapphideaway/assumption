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

# The verse spec must admit a colon: a lectionary range can cross a chapter
# boundary ("1 Corinthians 10:28-11:7"), and a spec class without ":" fails the
# whole anchored match, silently returning nothing for every such reading.
_REF = re.compile(
    r"^\s*((?:[1-4]\s+)?[A-Za-z]+)\s+(\d+)(?::([\d,\s\-:]+))?\s*$")

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


# Old Testament, by canonical code. Codes rather than spellings: callers pass
# both raw references ("Ps 50") and resolved codes ("PSA"), and a name-based
# set silently missed the codes — which quietly served Masoretic psalms from
# the WEB instead of Brenton's Septuagint, and dropped Greek psalms entirely.
_OT_CODES = frozenset({
    "GEN", "EXO", "LEV", "NUM", "DEU", "JOS", "JDG", "RUT", "1SA", "2SA",
    "1KI", "2KI", "1CH", "2CH", "EZR", "NEH", "EST", "JOB", "PSA", "PRO",
    "ECC", "SNG", "ISA", "JER", "LAM", "EZK", "DAN", "HOS", "JOL", "AMO",
    "OBA", "JON", "MIC", "NAM", "HAB", "ZEP", "HAG", "ZEC", "MAL",
    # Deuterocanon and Septuagint-only books.
    "TOB", "JDT", "WIS", "SIR", "BAR", "1MA", "2MA", "3MA", "4MA", "1ES",
    "LJE", "SUS", "BEL", "MAN", "ODA", "PSS",
})


def _is_ot(ref: str) -> bool:
    """True when a reference or code names an Old Testament book."""
    from .books import code_for
    code = code_for(ref.strip().split()[0] if ref.strip() else "")
    return code in _OT_CODES


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


# "3[1] Kings" is Septuagint Kingdoms numbering with the modern equivalent in
# brackets: 3 Kingdoms is 1 Kings. Take the bracketed number, which is
# unambiguous, rather than guessing which convention the bare numeral follows.
_BRACKET = re.compile(r"\b(\d)\s*\[(\d)\]\s*")
# Vespers on a Great Feast stitches several passages together; orthocal
# labels these "Composite N - <refs>". The label is not part of the
# reference.
_COMPOSITE = re.compile(r"^Composite\s+\d+\s*-\s*")


def _normalise_ref(ref: str) -> str:
    return _BRACKET.sub(r"\2 ", _COMPOSITE.sub("", ref)).strip()


def _parse(ref: str):
    """Split a reference into a book and one or more (chapter, verse) spans.

    Handles the forms the lectionary actually uses, including ranges that CROSS
    a chapter boundary — "1 Corinthians 10:28-11:7". Epistles do this
    constantly, and a single-chapter parser silently returns nothing for them.
    """
    m = _REF.match(ref)
    if not m:
        return None, []
    book, chapter, spec = m.group(1).strip(), int(m.group(2)), m.group(3)
    if not spec:
        return book, [((chapter, None), (chapter, None))]

    spans = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            try:
                start = (chapter, int(a.strip()))
                if ":" in b:
                    ec, ev = b.split(":", 1)
                    end = (int(ec), int(ev))
                else:
                    end = (chapter, int(b.strip()))
            except ValueError:
                continue
            spans.append((start, end))
        else:
            try:
                v = int(part)
            except ValueError:
                continue
            spans.append(((chapter, v), (chapter, v)))
    return book, spans


def passage(ref: str, edition: str = "web", numbering: str = "masoretic"):
    """Verse blocks for a reference, or None if unavailable.

    Returning None rather than raising is deliberate: the caller reports the
    gap and the app renders nothing, instead of an empty heading or a
    placeholder that looks like scripture but is not.
    """
    # A reading can join two passages with a semicolon; each half is resolved
    # and the results concatenated in order.
    ref = _normalise_ref(ref)
    if ";" in ref:
        out = []
        for part in ref.split(";"):
            got = passage(part.strip(), edition=edition, numbering=numbering)
            if got:
                out.extend(got)
        return out or None

    book, spans = _parse(ref)
    if not book or not spans:
        return None

    data = _book(edition, book)
    if not data:
        return None

    convert = (numbering == "lxx" and book.lower().startswith("ps")
               and edition not in LXX_NATIVE)

    out = []
    for (sc, sv), (ec, ev) in spans:
        chapters = [sc] if not convert else list(lxx_to_masoretic(sc))
        if convert and sc == ec:
            ec = chapters[-1]
            sc = chapters[0]
        for c in range(sc, ec + 1):
            ch = data.get(str(c))
            if not ch:
                continue
            lo = sv if (c == sc and sv is not None) else 1
            hi = ev if (c == ec and ev is not None) else 10 ** 6
            for n in sorted((int(k) for k in ch), key=int):
                if lo <= n <= hi:
                    out.append({"type": "verse", "n": n, "en": ch[str(n)],
                                "chapter": c})
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
