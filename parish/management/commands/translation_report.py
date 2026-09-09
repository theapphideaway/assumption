"""
Report translation coverage across every piece of content.

English, Greek and Slavonic are peers in this project, so a gap in Greek or
Slavonic is a real gap, not a nice-to-have. Nothing falls back to English
silently — this command is how the remaining work stays visible.

    manage.py translation_report
    manage.py translation_report --lang ru --missing
"""

import calendar

from django.core.management.base import BaseCommand

from liturgics.i18n import FAST_LABELS, LANGUAGES, SEASONS, missing_languages
from liturgics.movable import MOVABLE_DAYS
from liturgics.resolver import menaion
from prayers.store import catalogue

NAMES = {"en": "English", "el": "Greek", "ru": "Slavonic"}


def _bar(pct: int, width: int = 24) -> str:
    filled = round(pct / 100 * width)
    return "█" * filled + "·" * (width - filled)


class Command(BaseCommand):
    help = "Translation coverage for the Menaion, movable days and prayers."

    def add_arguments(self, parser):
        parser.add_argument("--lang", choices=list(LANGUAGES))
        parser.add_argument("--missing", action="store_true",
                            help="List what is untranslated, not just counts.")

    def handle(self, *args, **opts):
        sections = {
            "Fixed vocabulary": [t for t in {**SEASONS, **FAST_LABELS}.values()],
            "Movable days": [
                {k: v for k, v in
                 (("en", m[0]), ("el", m[2]), ("ru", m[3] if len(m) > 3 else ""))
                 if v}
                for m in MOVABLE_DAYS.values()],
            "Menaion (366 days)": [v["title"] for v in menaion().values()],
            "Prayer blocks": [b["text"] for d in catalogue().values()
                              for b in d["blocks"] if b.get("text")],
        }

        self.stdout.write("")
        for name, items in sections.items():
            self.stdout.write(self.style.HTTP_INFO(f"{name}  ({len(items)})"))
            for lang in LANGUAGES:
                if opts["lang"] and lang != opts["lang"]:
                    continue
                have = sum(1 for t in items if t.get(lang))
                pct = round(have / len(items) * 100) if items else 0
                style = (self.style.SUCCESS if pct == 100
                         else self.style.WARNING if pct >= 50
                         else self.style.ERROR)
                self.stdout.write(
                    f"   {NAMES[lang]:<10} {_bar(pct)} "
                    + style(f"{pct:>3}%") + f"   {have}/{len(items)}")
            self.stdout.write("")

        if opts["missing"]:
            lang = opts["lang"] or "ru"
            self.stdout.write(self.style.WARNING(
                f"Untranslated in {NAMES[lang]} — Menaion\n" + "=" * 60))
            gaps = [(k, v) for k, v in sorted(menaion().items())
                    if not k.startswith("_") and lang in missing_languages(v["title"])]
            for k, v in gaps[:40]:
                m, d = int(k[:2]), int(k[3:])
                self.stdout.write(
                    f"  {calendar.month_abbr[m]} {d:>2}  {v['title']['en'][:56]}")
            if len(gaps) > 40:
                self.stdout.write(f"  … and {len(gaps) - 40} more")
            self.stdout.write("")
