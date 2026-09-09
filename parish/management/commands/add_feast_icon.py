"""
Register a festal icon.

Copies the image into the served static directory, resizes it for a phone, and
records its licence and source in liturgics/data/icons.json. Refuses to register
anything without a licence, because an unattributed icon is one the parish
cannot publish.

    manage.py add_feast_icon ~/Desktop/assumption-icons/08m15_3.jpg 08-15 \\
        --license "Public domain" \\
        --credit "Andreas Ritzos, late 15th century" \\
        --source "https://commons.wikimedia.org/wiki/File:Dormition_of_Theotokos_Andreas_Ritzos.jpg"
"""

import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from liturgics.icons import registry

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / "parish" / "static" / "icons"
DATA = ROOT / "liturgics" / "data" / "icons.json"
MAX_EDGE = 1400          # ample for a phone hero, a third of the bytes

KEY = re.compile(r"^(?:\d{2}-\d{2}|P[+-]\d{3})$")


class Command(BaseCommand):
    help = "Register a festal icon and record its provenance."

    def add_arguments(self, parser):
        parser.add_argument("image")
        parser.add_argument("key", help="Month-day (08-15) or paschal offset (P+000).")
        parser.add_argument("--license", required=True)
        parser.add_argument("--credit", default="")
        parser.add_argument("--source", default="")
        parser.add_argument("--subject", default="")

    def handle(self, *args, **opts):
        src = Path(opts["image"]).expanduser()
        key = opts["key"]
        if not src.exists():
            raise CommandError(f"No such file: {src}")
        if not KEY.match(key):
            raise CommandError(
                f"Key {key!r} must be month-day like 08-15 or an offset like P+000.")
        if not opts["license"].strip():
            raise CommandError("A licence is required.")

        try:
            from PIL import Image
        except ImportError as exc:
            raise CommandError("Pillow is needed to resize icons: pip install Pillow") from exc

        DEST.mkdir(parents=True, exist_ok=True)
        filename = f"{key.replace('+', 'p').replace('-', 'm') if key.startswith('P') else key}.jpg"
        out = DEST / filename

        with Image.open(src) as image:
            image = image.convert("RGB")
            before = image.size
            image.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
            image.save(out, "JPEG", quality=88, optimize=True, progressive=True)

        raw = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {}
        raw[key] = {
            "file": filename,
            "license": opts["license"].strip(),
            "credit": opts["credit"].strip(),
            "source": opts["source"].strip(),
            "subject": opts["subject"].strip(),
        }
        ordered = {k: raw[k] for k in sorted(raw, key=lambda k: (not k.startswith("_"), k))}
        DATA.write_text(json.dumps(ordered, ensure_ascii=False, indent=1), encoding="utf-8")
        registry.cache_clear()

        kb = out.stat().st_size / 1024
        self.stdout.write(self.style.SUCCESS(
            f"{key} -> static/icons/{filename}  "
            f"{before[0]}x{before[1]} to {image.size[0]}x{image.size[1]}, {kb:.0f} KB"))
        if not opts["source"]:
            self.stdout.write(self.style.WARNING(
                "  No source recorded. Add one before release — a licence with no "
                "source is not something the parish can defend."))
