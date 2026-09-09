"""
Import the daily readings from orthocal's calendarium fixture.

    https://github.com/brianglass/orthocal-python   (MIT)

orthocal keys movable readings by `pdist` — the paschal distance — which is the
same number this project already calls `pascha_offset`, so the two line up with
no translation. Fixed-date readings carry a sentinel pdist of 999 and are keyed
by month and day instead.

TRADITION. Rows are tagged `common`, `greek` or `slavic`. Assumption is GOARCH,
so `common` + `greek` are taken and `slavic` is dropped. Where the two
traditions differ on a day the difference is real: on 9 September the Greek use
appoints the readings of Ss. Joachim and Anna, while the Slavic keeps the
course reading.

    manage.py import_lectionary path/to/calendarium.json
    manage.py import_lectionary path/to/calendarium.json --tradition slavic
"""

import json
import re
from collections import defaultdict
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

DEST = Path(__file__).resolve().parents[3] / "liturgics" / "data" / "lectionary.json"
FIXED_SENTINEL = 999

# orthocal separates chapter and verse with a dot ("John 1.1-17"); this project
# uses a colon throughout, including in the prayer documents. Normalised on
# import so one convention reaches the app.
_CHAPTER_VERSE = re.compile(r"(\d)\.(\d)")


def _ref(display: str) -> str:
    return _CHAPTER_VERSE.sub(r"\1:\2", display)


class Command(BaseCommand):
    help = "Import daily readings from an orthocal calendarium fixture."

    def add_arguments(self, parser):
        parser.add_argument("source", help="Path to calendarium.json")
        parser.add_argument("--tradition", default="greek",
                            choices=["greek", "slavic"],
                            help="Which use to keep alongside 'common'.")

    def handle(self, *args, **opts):
        src = Path(opts["source"]).expanduser()
        if not src.exists():
            raise CommandError(f"No such file: {src}")

        raw = json.loads(src.read_text(encoding="utf-8"))
        readings = [x["fields"] for x in raw if x["model"] == "calendarium.reading"]
        pericopes = {x["pk"]: x["fields"] for x in raw
                     if x["model"] == "calendarium.pericope"}
        if not readings or not pericopes:
            raise CommandError("Not an orthocal calendarium fixture.")

        keep = {"common", opts["tradition"]}
        movable = defaultdict(list)
        fixed = defaultdict(list)
        dropped = 0

        for r in sorted(readings, key=lambda r: r.get("ordering") or 0):
            if r.get("tradition") not in keep:
                dropped += 1
                continue
            p = pericopes.get(r.get("pericope"))
            if not p or not p.get("display"):
                continue
            entry = {
                "source": r["source"],
                "book": p["book"],
                "display": _ref(p["display"]),
                "short": _ref(p.get("sdisplay") or p["display"]),
                "tradition": r["tradition"],
            }
            if r.get("month"):
                fixed[f"{int(r['month']):02d}-{int(r['day']):02d}"].append(entry)
            elif r.get("pdist") != FIXED_SENTINEL:
                movable[str(r["pdist"])].append(entry)

        out = {
            "_meta": {
                "source": "orthocal-python calendarium fixture",
                "url": "https://github.com/brianglass/orthocal-python",
                "license": "MIT",
                "tradition": f"common + {opts['tradition']}",
                "note": ("Movable readings are keyed by paschal offset, which is "
                         "orthocal's pdist and this project's pascha_offset. "
                         "Fixed readings are keyed month-day."),
            },
            "movable": {k: v for k, v in sorted(movable.items(), key=lambda kv: int(kv[0]))},
            "fixed": dict(sorted(fixed.items())),
        }
        DEST.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

        mv = sum(len(v) for v in movable.values())
        fx = sum(len(v) for v in fixed.values())
        self.stdout.write(self.style.SUCCESS(
            f"{mv:,} movable readings across {len(movable)} offsets; "
            f"{fx:,} fixed readings across {len(fixed)} dates; "
            f"{dropped} dropped as other-tradition -> {DEST.name}"))
