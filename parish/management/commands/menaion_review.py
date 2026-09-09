"""
Print a review checklist for the fixed-date calendar.

The Menaion in this repo was authored from general knowledge, not transcribed
from an authoritative source. This command produces the sheet to check it
against a published GOARCH calendar — flagged entries first, then everything
else by month.

    manage.py menaion_review              # just the flagged entries
    manage.py menaion_review --all        # the whole year
    manage.py menaion_review --month 8    # one month
"""

import calendar

from django.core.management.base import BaseCommand

from liturgics.resolver import menaion

RANKS = {2: "GREAT FEAST", 3: "major", 4: "notable"}


class Command(BaseCommand):
    help = "Checklist for verifying the fixed-date calendar with Father."

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true",
                            help="Every day, not only the flagged ones.")
        parser.add_argument("--month", type=int, default=None,
                            help="Restrict to one month (1-12).")

    def handle(self, *args, **opts):
        data = menaion()
        entries = sorted(data.items())
        if opts["month"]:
            entries = [e for e in entries
                       if int(e[0][:2]) == opts["month"]]

        flagged = [(k, v) for k, v in entries if v.get("c")]

        if flagged:
            self.stdout.write(self.style.WARNING(
                "\nCHECK THESE FIRST — Greek/Slavic divergence or recent "
                "glorification\n" + "=" * 68))
            for k, v in flagged:
                m, d = int(k[:2]), int(k[3:])
                self.stdout.write(
                    f"  [ ]  {calendar.month_abbr[m]} {d:>2}   {v['title']}")
            self.stdout.write("")

        if not opts["all"] and not opts["month"]:
            self.stdout.write(
                f"{len(entries)} days on file, {len(flagged)} flagged.\n"
                "Run with --all for the full year, or --month N for one month.\n")
            return

        current = None
        for k, v in entries:
            m, d = int(k[:2]), int(k[3:])
            if m != current:
                current = m
                self.stdout.write(self.style.HTTP_INFO(
                    f"\n{calendar.month_name[m].upper()}\n" + "-" * 68))
            rank = RANKS.get(v["rank"], "")
            mark = "*" if v["rank"] == 2 else " "
            self.stdout.write(f"  [ ]{mark}{d:>2}  {v['title'][:52]:<52} {rank}")
        self.stdout.write("")
