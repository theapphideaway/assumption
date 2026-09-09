"""
Reading the Bible directly — browsing a chapter, looking up a reference,
searching.

Separate from the prayer endpoints on purpose: this is the Bible, and prayer
rules never read from it.

Every response carries all languages that have an edition covering the book,
so a reader switches language without another round trip. Editions differ in
scope — the Patriarchal text is New Testament only, Swete and Brenton are Old
Testament only — so a chapter may legitimately come back in fewer than three
languages, and the response says which.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from rest_framework.decorators import api_view
from rest_framework.response import Response

from prayers.books import BY_NUMBER, code_for
from prayers.scripture import EDITIONS, OT_EDITIONS, available, edition_for, passage

_DATA = Path(__file__).parent / "data" / "scripture"
SEARCH_LIMIT = 50
SEARCH_MAX = 200


@lru_cache(maxsize=1)
def _coverage() -> dict[str, list[str]]:
    """Which editions hold which books."""
    out: dict[str, list[str]] = {}
    for edition in available():
        for path in (_DATA / edition).glob("*.json"):
            out.setdefault(path.stem, []).append(edition)
    return {k: sorted(v) for k, v in sorted(out.items())}


def _editions_for(code: str, loaded: set[str]) -> dict[str, str]:
    """Language -> edition, for the languages that actually cover this book."""
    out = {}
    for lang in EDITIONS:
        ed = edition_for(lang, code, loaded)
        if ed and ed in _coverage().get(code, []):
            out[lang] = ed
    return out


@api_view(["GET"])
def books(request):
    """The canonical book list, with per-book language coverage."""
    loaded = set(available())
    cov = _coverage()
    ordered = [c for c in BY_NUMBER.values() if c in cov]
    extra = [c for c in cov if c not in ordered]
    return Response({
        "editions": sorted(loaded),
        "books": [
            {"code": c, "editions": cov[c],
             "languages": sorted(_editions_for(c, loaded))}
            for c in ordered + sorted(extra)
        ],
    })


@api_view(["GET"])
def chapter(request, book: str, number: int):
    """One chapter, in every language whose edition covers the book."""
    code = code_for(book)
    if not code:
        return Response({"detail": f"Unknown book {book!r}."}, status=404)
    loaded = set(available())
    langs = _editions_for(code, loaded)
    if not langs:
        return Response({"detail": f"No edition loaded for {code}."}, status=404)

    numbering = request.GET.get("numbering", "masoretic")
    verses: dict[int, dict[str, str]] = {}
    used = {}
    for lang, edition in langs.items():
        got = passage(f"{code} {number}", edition=edition, numbering=numbering)
        if not got:
            continue
        used[lang] = edition
        for v in got:
            verses.setdefault(v["n"], {})[lang] = v["en"]
    if not verses:
        return Response({"detail": f"{code} {number} not found."}, status=404)

    return Response({
        "book": code, "chapter": number, "numbering": numbering,
        "editions": used,
        "verses": [{"n": n, "text": verses[n]} for n in sorted(verses)],
    })


@api_view(["GET"])
def search(request):
    """Substring search in one language.

    A linear scan over that language's editions. Fine at parish scale and for
    the web panel, but the APP should ship a prebuilt index and search on the
    device — search is exactly what someone wants when they have no signal.
    """
    q = (request.GET.get("q") or "").strip()
    if len(q) < 3:
        return Response({"detail": "Query must be at least 3 characters."},
                        status=400)
    lang = request.GET.get("lang", "en")
    if lang not in EDITIONS:
        return Response({"detail": f"Unknown language {lang!r}."}, status=400)
    try:
        limit = min(int(request.GET.get("limit", SEARCH_LIMIT)), SEARCH_MAX)
    except ValueError:
        limit = SEARCH_LIMIT

    loaded = set(available())
    wanted = {e for e in (EDITIONS.get(lang), OT_EDITIONS.get(lang)) if e in loaded}
    if not wanted:
        return Response({"detail": f"No edition loaded for {lang!r}."}, status=404)

    needle = re.compile(re.escape(q), re.IGNORECASE)
    hits, truncated = [], False
    for edition in sorted(wanted):
        order = {c: i for i, c in enumerate(BY_NUMBER.values())}
        paths = sorted((_DATA / edition).glob("*.json"),
                       key=lambda p: (order.get(p.stem, 999), p.stem))
        for path in paths:
            if len(hits) >= limit:
                truncated = True
                break
            data = json.loads(path.read_text(encoding="utf-8"))
            for ch in sorted(data, key=lambda c: int(c) if c.isdigit() else 0):
                for v, text in data[ch].items():
                    if needle.search(text):
                        hits.append({"book": path.stem, "chapter": int(ch),
                                     "verse": int(v), "text": text,
                                     "edition": edition})
                        if len(hits) >= limit:
                            truncated = True
                            break
                if len(hits) >= limit:
                    break
    return Response({"query": q, "language": lang, "count": len(hits),
                     "truncated": truncated, "results": hits})
