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
    Directory    one file per book, each line "1:1 text…", the filename naming
                 the book — the shape byztxt/greektext-antoniades ships.

    manage.py load_scripture rus-synodal.zefania.xml --edition synodal
"""

import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

DEST = Path(__file__).resolve().parents[3] / "prayers" / "data" / "scripture"


from prayers.books import code_for


# Some editions prefix each verse with its reference under a different
# numbering, e.g. the Synodal Zefania file writes "(49:1) Псалом Асафа…".
# Useful provenance, but it renders as noise in the app, so it comes off here.
_INLINE_REF = re.compile(r"^\(\d+[:.]\d+[a-z]?\)\s*")


def _strip_inline_ref(text: str) -> str:
    return _INLINE_REF.sub("", text, count=1)


def _slug(book: str, number: int | None = None) -> str:
    """Canonical code, so every edition stores under the same filenames
    regardless of what language it names its books in."""
    code = code_for(book, number)
    if not code:
        raise CommandError(
            f"Unrecognised book {book!r} (number={number}). Add it to "
            "prayers/books.py rather than letting it fall back to a slug — a "
            "silent fallback writes a file nothing will ever look up.")
    return code


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

        if src.is_dir():
            self._lines_dir(src, books)
            return self._write(books, opts["edition"])

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
                books[_slug(book)][str(row["chapter"])][str(row["verse"])] = \
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
            try:
                bnum = int(book.get("bnumber") or 0)
            except ValueError:
                bnum = 0
            name = _slug(book.get("bname") or "", bnum or None)
            for chapter in book.iter("CHAPTER"):
                cnum = chapter.get("cnumber")
                for verse in chapter.iter("VERS"):
                    vnum = verse.get("vnumber")
                    text = " ".join(t.strip() for t in verse.itertext() if t.strip())
                    text = _strip_inline_ref(text)
                    if cnum and vnum and text:
                        books[name][str(cnum)][str(vnum)] = text

    def _lines_dir(self, src: Path, books: dict) -> None:
        """A directory of per-book files whose lines are "chapter:verse text".

        Continuation lines — those not opening with a reference — are appended
        to the verse above, so a verse wrapped across lines is not truncated.
        """
        ref = re.compile(r"^\s*(\d+):(\d+)\s+(.*)$")
        for path in sorted(src.glob("*")):
            if not path.is_file() or path.suffix.lower() not in (".txt", ".ant"):
                continue
            code = code_for(path.stem)
            if not code:
                self.stdout.write(f"  skipping unrecognised book file {path.name}")
                continue
            current = None
            for line in path.read_text(encoding="utf-8").splitlines():
                m = ref.match(line)
                if m:
                    ch, v, text = m.group(1), m.group(2), m.group(3).strip()
                    books[code][ch][v] = text
                    current = (ch, v)
                elif line.strip() and current:
                    books[code][current[0]][current[1]] += " " + line.strip()

    def _write(self, books: dict, edition: str):
        out = DEST / edition
        out.mkdir(parents=True, exist_ok=True)
        verses = 0
        for book, chapters in books.items():
            (out / f"{book}.json").write_text(
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
