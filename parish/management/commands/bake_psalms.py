"""
Bake psalm text into the prayer documents.

Prayer books print their psalms inline; they do not cite a Bible. So this
writes psalm text INTO the prayer documents at build time, with provenance
recorded, rather than the app reaching into the scripture store at render
time. The separation Ian asked for is preserved: a prayer rule still never
reads from the Bible.

Which psalter may be baked is a per-tradition choice, and it is NOT simply the
language's Bible edition:

    el  Swete's Septuagint      The Horologion's psalms ARE the Septuagint
                                psalms. Same text, polytonic.
    en  Brenton                 An English Orthodox psalter follows the LXX.
                                The WEB is translated from the Masoretic text
                                and is deliberately NOT accepted here.
    ru  Elizabeth Bible         The молитвослов prints the CHURCH SLAVONIC
                                psalter. The Synodal is modern Russian and is
                                deliberately NOT accepted here.

A language whose psalter is not loaded is left empty and reported. Filling it
from the nearest available Bible would put a different rendering of the psalm
into someone's rule than the one their prayer book prints — wrong in a way
that looks right.

    manage.py bake_psalms --dry-run
    manage.py bake_psalms
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from prayers.scripture import available, passage

PRAYER_PSALTERS = {
    "el": "swete",
    "en": "brenton",
    "ru": "elizabeth",
}

DATA = Path(__file__).resolve().parents[3] / "prayers" / "data"


class Command(BaseCommand):
    help = "Write psalm text into the prayer documents from each tradition's psalter."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **opts):
        loaded = set(available())
        usable = {lang: ed for lang, ed in PRAYER_PSALTERS.items() if ed in loaded}
        skipped = {lang: ed for lang, ed in PRAYER_PSALTERS.items()
                   if ed not in loaded}

        self.stdout.write(f"\npsalters available: {usable or 'none'}")
        for lang, ed in skipped.items():
            self.stdout.write(self.style.WARNING(
                f"  {lang}: '{ed}' not loaded — psalms left empty, not substituted"))
        if not usable:
            return

        filled = empty = 0
        for path in sorted(DATA.glob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            changed = False
            for b in doc["blocks"]:
                if b.get("type") != "psalm":
                    continue
                ref = b.get("ref", "")
                numbering = b.get("numbering", "masoretic")
                text = dict(b.get("text") or {})
                sources = dict(b.get("sources") or {})
                for lang, edition in usable.items():
                    if text.get(lang):
                        continue
                    verses = passage(ref, edition=edition, numbering=numbering)
                    if not verses:
                        continue
                    text[lang] = " ".join(v["en"] for v in verses)
                    sources[lang] = edition
                    filled += 1
                    changed = True
                if not text:
                    empty += 1
                if changed:
                    b["text"] = text
                    b["sources"] = sources
            if changed and not opts["dry_run"]:
                path.write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                                encoding="utf-8")

        verb = "would fill" if opts["dry_run"] else "filled"
        self.stdout.write(self.style.SUCCESS(
            f"\n{verb} {filled} psalm translations; {empty} psalm blocks still "
            f"have no text in any language."))
        if skipped:
            self.stdout.write(
                "\nTo complete the rule, source a psalter for: "
                + ", ".join(f"{l} ({e})" for l, e in skipped.items()))
