"""
Ingest a public-domain scripture edition into the file-backed store.

Nothing is bundled in the repo — you supply the source file. Two editions are
worth having, both public domain:

    KJV       widely mirrored as JSON; search for a public-domain KJV dataset.
    Brenton   the Septuagint in English. The correct Old Testament for
              Orthodox use, and the one the prayer documents assume for psalms.

Formats vary by source, so the input shape is auto-detected:

    JSON list    [{"book_name": "John", "chapter": 1, "verse": 1, "text": "…"}]
    JSON dict    {"John": {"1": {"1": "…", "2": "…"}}}
    Zefania XML  <XMLBIBLE><BIBLEBOOK bname="John"><CHAPTER cnumber="1">
                 <VERS vnumber="1">…</VERS>  — what open-bibles ships.

    manage.py load_scripture rus-synodal.zefania.xml --edition synodal
"""

import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

DEST = Path(__file__).resolve().parents[3] / "prayers" / "data" / "scripture"


def _slug(book: str) -> str:
    return re.sub(r"[^a-z0-9]", "", book.lower())


class Command(BaseCommand):
    help = "Load a public-domain scripture edition into prayers/data/scripture/."

    def add_arguments(self, parser):
        parser.add_argument("source", help="Path to the JSON file.")
        parser.add_argument("--edition", default="kjv",
                            help="Directory name, e.g. kjv or brenton.")

    def handle(self, *args, **opts):
        src = Path(opts["source"]).expanduser()
        if not src.exists():
            raise CommandError(f"No such file: {src}")

        books: dict[str, dict] = defaultdict(lambda: defaultdict(dict))

        if src.suffix.lower() in (".xml", ".zefania"):
            self._zefania(src, books)
            return self._write(books, opts["edition"])

        raw = json.loads(src.read_text(encoding="utf-8"))

        if isinstance(raw, list):
            for row in raw:
                book = row.get("book_name") or row.get("book")
                if not book:
                    raise CommandError(
                        "List rows need a 'book_name' or 'book' key.")
                books[book][str(row["chapter"])][str(row["verse"])] = \
                    row["text"].strip()
        elif isinstance(raw, dict):
            for book, chapters in raw.items():
                for ch, verses in chapters.items():
                    for v, text in verses.items():
                        books[book][str(ch)][str(v)] = str(text).strip()
        else:
            raise CommandError("Unrecognised JSON shape — see the docstring.")

        return self._write(books, opts["edition"])

    def _zefania(self, src: Path, books: dict) -> None:
        """Zefania XML: BIBLEBOOK / CHAPTER / VERS.

        Book names come from the bname attribute where present, falling back to
        bnumber. Verse text can be split across child elements (notes, styling),
        so text is gathered with itertext rather than .text alone — otherwise
        verses silently truncate at the first inline tag.
        """
        root = ET.parse(src).getroot()
        for book in root.iter("BIBLEBOOK"):
            name = book.get("bname") or f"book{book.get('bnumber')}"
            for chapter in book.iter("CHAPTER"):
                cnum = chapter.get("cnumber")
                for verse in chapter.iter("VERS"):
                    vnum = verse.get("vnumber")
                    text = " ".join(t.strip() for t in verse.itertext() if t.strip())
                    if cnum and vnum and text:
                        books[name][str(cnum)][str(vnum)] = text

    def _write(self, books: dict, edition: str):
        out = DEST / edition
        out.mkdir(parents=True, exist_ok=True)
        verses = 0
        for book, chapters in books.items():
            (out / f"{_slug(book)}.json").write_text(
                json.dumps(chapters, ensure_ascii=False), encoding="utf-8")
            verses += sum(len(c) for c in chapters.values())

        self.stdout.write(self.style.SUCCESS(
            f"{len(books)} books, {verses:,} verses -> {out}"))
        self.stdout.write(self.style.WARNING(
            "\nCHECK THE PSALTER before trusting this edition. Open Psalm 50 "
            "and Psalm 51. If 50 is the penitential psalm (\"Have mercy on me, "
            "O God\"), the edition is Septuagint-numbered and belongs in "
            "scripture.LXX_NATIVE. If 51 is, it is Masoretic and must NOT be "
            "listed there. Getting this wrong does not error — it serves the "
            "wrong psalm, every day, silently."))
