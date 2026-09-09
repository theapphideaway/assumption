"""
Tests for the liturgical engine.

The Pascha fixtures below are the published Orthodox dates. They are the
backstop for the entire calendar: if these pass, every movable feast, the Tone
cycle and most of the fasting rules follow, because all of them are pure
functions of the paschal offset.
"""

import unittest
from datetime import date, datetime, timedelta

from liturgics.fasting import FastLevel, resolve_fast
from liturgics.movable import movable_day, season_for, tone_for
from liturgics.paschalion import (gregorian_to_julian, julian_to_gregorian,
                                  pascha, reference_pascha)
from liturgics.resolver import resolve_day

# Published Orthodox Pascha, civil (Gregorian) dates.
PASCHA = {
    2020: (4, 19), 2021: (5, 2),  2022: (4, 24), 2023: (4, 16),
    2024: (5, 5),  2025: (4, 20), 2026: (4, 12), 2027: (5, 2),
    2028: (4, 16), 2029: (4, 8),  2030: (4, 28), 2031: (4, 13),
    2032: (5, 2),  2033: (4, 24), 2034: (4, 9),  2035: (4, 29),
}


class TestPaschalion(unittest.TestCase):
    def test_published_dates(self):
        for year, (m, d) in PASCHA.items():
            self.assertEqual(pascha(year), date(year, m, d), f"Pascha {year}")

    def test_pascha_is_always_sunday(self):
        for year in range(1900, 2101):
            self.assertEqual(pascha(year).weekday(), 6, f"Pascha {year}")

    def test_julian_gap_widens_in_2100(self):
        """The gap is 13 days now and 14 from 2100 — the reason this engine
        converts through Julian Day Numbers instead of adding a constant."""
        # Today: 13 days.
        self.assertEqual(julian_to_gregorian(2026, 8, 27), date(2026, 9, 9))
        self.assertEqual(gregorian_to_julian(date(2026, 9, 9)), (2026, 8, 27))
        self.assertEqual((date(2026, 9, 9) - date(2026, 8, 27)).days, 13)
        # After Julian 29 February 2100 — a leap day the Gregorian calendar
        # does not have — the gap widens to 14.
        self.assertEqual(julian_to_gregorian(2100, 2, 28), date(2100, 3, 13))
        self.assertEqual(julian_to_gregorian(2100, 2, 29), date(2100, 3, 14))
        self.assertEqual(julian_to_gregorian(2100, 3, 1), date(2100, 3, 15))
        self.assertEqual((date(2100, 3, 15) - date(2100, 3, 1)).days, 14)

    def test_cycle_normalisation_across_new_year(self):
        """January belongs to the *previous* paschal cycle until the Triodion
        opens — the hinge the whole movable calendar turns on."""
        p, off = reference_pascha(date(2027, 1, 15))
        self.assertEqual(p, pascha(2026))
        self.assertGreater(off, 200)
        # The day the Triodion opens flips the reference forward.
        triodion = pascha(2027) - timedelta(days=70)
        p2, off2 = reference_pascha(triodion)
        self.assertEqual(p2, pascha(2027))
        self.assertEqual(off2, -70)
        p3, _ = reference_pascha(triodion - timedelta(days=1))
        self.assertEqual(p3, pascha(2026))


class TestMovable(unittest.TestCase):
    def test_weekday_invariants(self):
        """These never vary, in any year — a cheap, strong regression net."""
        for year in PASCHA:
            p = pascha(year)
            self.assertEqual((p + timedelta(days=-48)).weekday(), 0, "Clean Monday")
            self.assertEqual((p + timedelta(days=-7)).weekday(), 6, "Palm Sunday")
            self.assertEqual((p + timedelta(days=39)).weekday(), 3, "Ascension")
            self.assertEqual((p + timedelta(days=49)).weekday(), 6, "Pentecost")
            self.assertEqual((p + timedelta(days=-16)).weekday(), 4, "Akathist")

    def test_seasons(self):
        cases = {-70: "triodion", -48: "great_lent", -8: "great_lent",
                 -7: "holy_week", -1: "holy_week", 0: "bright_week",
                 7: "pentecostarion", 56: "pentecostarion", 57: "after_pentecost"}
        for off, key in cases.items():
            self.assertEqual(season_for(off).key, key, f"offset {off}")

    def test_tone_cycle(self):
        p = pascha(2027)
        self.assertIsNone(tone_for(p), "Pascha has no Octoechos tone")
        self.assertIsNone(tone_for(p + timedelta(days=-2)), "Great Friday")
        self.assertEqual(tone_for(p + timedelta(days=7)), 1, "Thomas Sunday")
        self.assertEqual(tone_for(p + timedelta(days=14)), 2)
        self.assertEqual(tone_for(p + timedelta(days=7 + 56)), 1, "wraps at 8")

    def test_greek_specific_days(self):
        """Salutations and Clean Monday are central to a GOARCH parish and
        absent from most generic Orthodox calendars."""
        self.assertIn("Salutations", movable_day(-44)[0])
        self.assertIn("Akathist", movable_day(-16)[0])
        self.assertEqual(movable_day(-48)[0], "Clean Monday")


class TestFasting(unittest.TestCase):
    def _fast(self, d):
        _, off = reference_pascha(d)
        return resolve_fast(d, off)

    def test_bright_week_is_fast_free_on_wednesday(self):
        d = pascha(2027) + timedelta(days=3)
        self.assertEqual(d.weekday(), 2)
        self.assertEqual(self._fast(d).level, FastLevel.FAST_FREE)

    def test_great_friday_is_strict(self):
        self.assertEqual(self._fast(pascha(2027) - timedelta(days=2)).level,
                         FastLevel.STRICT)

    def test_palm_sunday_allows_fish(self):
        self.assertEqual(self._fast(pascha(2027) - timedelta(days=7)).level,
                         FastLevel.FISH)

    def test_lenten_weekend_relaxes_to_wine_and_oil(self):
        p = pascha(2027)
        self.assertEqual(self._fast(p - timedelta(days=42)).level,  # Sun of Orthodoxy
                         FastLevel.WINE_OIL)
        self.assertEqual(self._fast(p - timedelta(days=46)).level,  # Wednesday
                         FastLevel.STRICT)

    def test_cheesefare_week_allows_dairy_on_friday(self):
        d = pascha(2027) - timedelta(days=51)
        self.assertEqual(d.weekday(), 4)
        self.assertEqual(self._fast(d).level, FastLevel.DAIRY)

    def test_twelve_days_of_nativity_are_fast_free(self):
        self.assertEqual(self._fast(date(2026, 12, 30)).level, FastLevel.FAST_FREE)

    def test_dormition_fast_and_transfiguration(self):
        self.assertEqual(self._fast(date(2026, 8, 10)).level, FastLevel.STRICT)
        self.assertEqual(self._fast(date(2026, 8, 6)).level, FastLevel.FISH)

    def test_plain_wednesday_is_strict(self):
        self.assertEqual(self._fast(date(2026, 9, 9)).level, FastLevel.STRICT)

    def test_great_feast_on_a_friday_relaxes_to_fish(self):
        _, off = reference_pascha(date(2028, 9, 8))   # Nativity of the Theotokos
        self.assertEqual(date(2028, 9, 8).weekday(), 4)
        self.assertEqual(resolve_fast(date(2028, 9, 8), off, rank=2).level,
                         FastLevel.FISH)


class TestResolver(unittest.TestCase):
    def test_patronal_feast_is_flagged(self):
        r = resolve_day(date(2026, 8, 15))
        self.assertTrue(r["patronal"])
        self.assertEqual(r["title"]["en"], "The Dormition of the Theotokos")
        self.assertEqual(r["season"]["color"], "lapis")

    def test_pascha_outranks_any_fixed_feast(self):
        r = resolve_day(pascha(2027))
        self.assertEqual(r["rank"], 1)
        self.assertEqual(r["title"]["en"], "Great and Holy Pascha")

    def test_shape_is_stable(self):
        r = resolve_day(date(2026, 9, 9))
        for key in ("date", "julian", "pascha_offset", "season", "title",
                    "rank", "tone", "fast", "commemorations", "parish"):
            self.assertIn(key, r)
        self.assertEqual(r["julian"], "2026-08-27")


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestParishSettings(unittest.TestCase):
    """Pins the parish timezone.

    Idaho straddles two zones — Pocatello is Mountain, the northern panhandle
    is Pacific. A well-meaning "simplify this to America/Denver" edit would
    pass every other test in this file, so it gets one of its own.
    """

    def test_timezone_is_boise(self):
        from zoneinfo import ZoneInfo
        from django.conf import settings
        self.assertEqual(settings.TIME_ZONE, "America/Boise")
        jan = date(2026, 1, 15)
        tz = ZoneInfo(settings.TIME_ZONE)
        self.assertEqual(
            datetime(jan.year, jan.month, jan.day, 12, tzinfo=tz).tzname(), "MST")


class TestMenaionCoverage(unittest.TestCase):
    """Every day of the year must resolve to something.

    A sparse Today screen — a season and a fast and nothing else — is what
    makes an app look unfinished on the one Tuesday somebody actually opens it.
    """

    def test_all_366_days_present(self):
        import calendar as _cal
        from liturgics.resolver import menaion
        data = menaion()
        expected = {f"{m:02d}-{d:02d}" for m in range(1, 13)
                    for d in range(1, _cal.monthrange(2024, m)[1] + 1)}
        self.assertEqual(expected - set(data), set(), "days with no commemoration")
        self.assertEqual(len(data), 366)

    def test_every_day_of_a_year_has_a_title(self):
        d = date(2027, 1, 1)
        while d.year == 2027:
            self.assertTrue(resolve_day(d)["title"].get("en"), f"no title for {d}")
            d += timedelta(days=1)

    def test_leap_day_resolves(self):
        self.assertIn("Cassian", resolve_day(date(2028, 2, 29))["title"]["en"])

    def test_patronal_feast_survived_the_merge(self):
        from liturgics.resolver import menaion
        self.assertTrue(menaion()["08-15"]["patronal"])
        self.assertEqual(menaion()["08-15"]["title"]["ru"],
                         "Успение Пресвятой Богородицы")
        self.assertEqual(menaion()["08-15"]["color"], "lapis")


class TestApostlesFastWindow(unittest.TestCase):
    """The Apostles' Fast is the only fast whose length varies year to year,
    and the only one that can vanish entirely. It is also where a month/day
    comparison quietly swallows January and February, so it gets its own case.
    """

    def _fast(self, d):
        _, off = reference_pascha(d)
        return resolve_fast(d, off)

    def test_february_is_not_the_apostles_fast(self):
        """Regression: offset 303 is past 57, and (2, 9) sorts before (6, 28),
        so a naive month/day test made every February a fish day."""
        f = self._fast(date(2027, 2, 9))
        self.assertEqual(f.level, FastLevel.FAST_FREE)
        self.assertNotIn("Apostles", f.reason)

    def test_june_inside_the_window_is_the_fast(self):
        f = self._fast(date(2026, 6, 16))       # Pascha 12 Apr, fast opens 8 Jun
        self.assertEqual(f.level, FastLevel.FISH)
        self.assertIn("Apostles", f.reason)
        self.assertEqual(self._fast(date(2026, 6, 17)).level, FastLevel.STRICT)

    def test_late_pascha_shortens_the_fast_to_almost_nothing(self):
        p = pascha(2027)                         # 2 May — very late
        self.assertEqual(p + timedelta(days=57), date(2027, 6, 28))
        self.assertIn("Apostles", self._fast(date(2027, 6, 28)).reason)
        self.assertNotIn("Apostles", self._fast(date(2027, 6, 27)).reason)

    def test_window_never_leaks_outside_june_or_july(self):
        for year in (2025, 2026, 2027, 2028, 2029, 2030):
            for month in (1, 2, 3, 10, 11):
                d = date(year, month, 15)
                self.assertNotIn("Apostles", self._fast(d).reason,
                                 f"{d} wrongly inside the Apostles' Fast")


class TestTrilingual(unittest.TestCase):
    """English, Greek and Slavonic are peers.

    The parish has ethnic Greeks and ethnic Russians, and people keep a rule in
    the language they actually pray in. A missing translation must be visible,
    never silently replaced by English — otherwise nobody ever fills it in.
    """

    def test_every_season_and_fast_label_is_complete(self):
        from liturgics.i18n import FAST_LABELS, SEASONS, missing_languages
        for key, t in {**SEASONS, **FAST_LABELS}.items():
            self.assertEqual(missing_languages(t), [], f"{key} incomplete")

    def test_great_feasts_carry_all_three(self):
        from liturgics.i18n import missing_languages
        from liturgics.resolver import menaion
        for key in ("12-25", "01-06", "08-15", "09-08", "11-21", "03-25",
                    "08-06", "09-14", "02-02"):
            self.assertEqual(missing_languages(menaion()[key]["title"]), [],
                             f"Great Feast {key} is not fully translated")

    def test_pascha_and_the_movable_greats_carry_all_three(self):
        from liturgics.i18n import missing_languages
        for off in (0, -7, -48, 39, 49, -2):
            d = pascha(2027) + timedelta(days=off)
            self.assertEqual(missing_languages(resolve_day(d)["title"]), [],
                             f"movable offset {off} is not fully translated")

    def test_english_is_never_used_as_a_silent_fallback(self):
        """A day with no Slavonic title reports the gap rather than echoing
        the English string into the ru field."""
        r = resolve_day(date(2026, 3, 16))       # Martyr Sabinus, English only
        self.assertNotIn("ru", r["title"])
        self.assertIn("ru", r["translation_gaps"]["title"])

    def test_response_declares_its_languages(self):
        self.assertEqual(resolve_day(date(2027, 1, 1))["languages"],
                         ["en", "el", "ru"])


class TestLectionaryCourse(unittest.TestCase):
    """The Lucan jump is the hard part of the weekday lectionary.

    It does NOT key to Pascha: the course of Luke begins on the Monday after
    the Sunday following the Elevation of the Cross, a fixed date. So the
    Matthew course varies in length year to year, and that variation is exactly
    what a hand-built table gets wrong.
    """

    def test_lucan_jump_is_always_the_right_monday(self):
        from datetime import date as _d
        from liturgics.lectionary import ELEVATION, lucan_jump
        for year in range(2025, 2041):
            jump = lucan_jump(year)
            self.assertEqual(jump.weekday(), 0, f"{year}: not a Monday")
            elevation = _d(year, *ELEVATION)
            self.assertGreater(jump, elevation)
            self.assertLessEqual((jump - elevation).days, 8)
            # The day before must be the Sunday that follows the Elevation.
            self.assertEqual((jump - timedelta(days=1)).weekday(), 6)

    def test_lenten_weekdays_still_have_appointed_readings(self):
        """Corrects an earlier model that marked these days as having no
        readings. The full Liturgy is not served, so there is no Gospel — but
        Genesis and Proverbs are appointed at Vespers and Isaiah at the Sixth
        Hour. Reporting the day as empty would be plainly wrong.
        """
        from liturgics.lectionary import readings_detail
        p = pascha(2027)
        wednesday = p - timedelta(days=46)
        self.assertEqual(wednesday.weekday(), 2)
        r = readings_detail(wednesday, -46)
        self.assertEqual(r["status"], "appointed")
        sources = {e["source"] for e in r["readings"]}
        self.assertIn("Vespers", sources)
        self.assertIn("6th Hour", sources)
        # No Gospel: the full Liturgy is not served on a Lenten weekday.
        self.assertNotIn("Gospel", sources)
        # orthocal marks Old Testament pericopes with a generic book of "OT";
        # the actual book is carried in the display reference.
        shown = " ".join(e["display"] for e in r["readings"])
        for book in ("Genesis", "Proverbs", "Isaiah"):
            self.assertIn(book, shown, f"{book} not appointed: {shown}")

    def test_no_day_of_the_year_claims_to_have_nothing_appointed(self):
        """Every day has readings; the only question is whether we hold them."""
        from liturgics.lectionary import readings_detail
        d = date(2027, 1, 1)
        while d.year == 2027:
            _, off = reference_pascha(d)
            r = readings_detail(d, off)
            self.assertIn(r["status"], ("appointed", "unsourced"))
            d += timedelta(days=1)

    def test_appointed_days_still_resolve(self):
        from liturgics.lectionary import readings_detail
        p = pascha(2027)
        r = readings_detail(p, 0)
        self.assertEqual(r["status"], "appointed")
        self.assertEqual(r["gospel"], "John 1:1-17")

    def test_course_is_none_inside_the_pentecostarion(self):
        from liturgics.lectionary import course_for
        p = pascha(2027)
        for off in (0, 20, 49):
            self.assertIsNone(course_for(p + timedelta(days=off), off))

    def test_every_day_of_a_year_reports_a_status(self):
        from liturgics.lectionary import readings_detail
        d = date(2027, 1, 1)
        while d.year == 2027:
            _, off = reference_pascha(d)
            status = readings_detail(d, off)["status"]
            self.assertIn(status, ("appointed", "unsourced"))
            d += timedelta(days=1)


class TestGospelCourseSplit(unittest.TestCase):
    """Sunday and weekday gospel courses diverge after Pentecost.

    Sundays run through Matthew while weekdays switch to Mark partway, and the
    same happens in the Lucan period. Treating a day's course as a single value
    got weekdays wrong for roughly a third of the year. Caught by checking the
    engine against a published daily reading.
    """

    def test_week_fifteen_weekday_reads_mark_not_matthew(self):
        from liturgics.lectionary import course_for
        d = date(2026, 9, 9)                     # Wednesday, week 15
        _, off = reference_pascha(d)
        c = course_for(d, off)
        self.assertEqual(c["week"], 15)
        self.assertEqual(c["gospel"], "MRK", "weekday should have moved to Mark")
        self.assertEqual(c["sunday_gospel"], "MAT", "Sundays stay in Matthew")

    def test_early_weeks_weekday_still_reads_matthew(self):
        from liturgics.lectionary import course_for
        p = pascha(2026)
        d = p + timedelta(days=52)               # Tuesday, week 1 after Pentecost
        _, off = reference_pascha(d)
        c = course_for(d, off)
        self.assertLessEqual(c["week"], 2)
        self.assertEqual(c["gospel"], "MAT")

    def test_after_the_lucan_jump_sundays_read_luke(self):
        from liturgics.lectionary import course_for, lucan_jump
        jump = lucan_jump(2026)
        sunday = jump + timedelta(days=6)
        _, off = reference_pascha(sunday)
        self.assertEqual(sunday.weekday(), 6)
        self.assertEqual(course_for(sunday, off)["gospel"], "LUK")



class TestImportedLectionary(unittest.TestCase):
    """The imported daily readings, keyed by paschal offset.

    orthocal's `pdist` is the same number as this project's `pascha_offset`,
    so the tables line up with no translation.
    """

    def test_a_known_weekday_matches_the_published_reading(self):
        from liturgics.lectionary import readings_detail
        d = date(2026, 9, 9)
        _, off = reference_pascha(d)
        self.assertEqual(off, 150)
        r = readings_detail(d, off)
        common = {e["display"] for e in r["readings"] if e["tradition"] == "common"}
        self.assertIn("Galatians 3:15-22", common)
        self.assertIn("Mark 6:7-13", common)

    def test_greek_tradition_rows_are_kept_and_slavic_dropped(self):
        from liturgics.lectionary import imported
        traditions = {e["tradition"]
                      for group in (imported()["movable"], imported()["fixed"])
                      for entries in group.values() for e in entries}
        self.assertEqual(traditions, {"common", "greek"})

    def test_coverage_is_effectively_the_whole_year(self):
        from liturgics.lectionary import readings_detail
        d, appointed, total = date(2027, 1, 1), 0, 0
        while d.year == 2027:
            _, off = reference_pascha(d)
            appointed += readings_detail(d, off)["status"] == "appointed"
            total += 1
            d += timedelta(days=1)
        self.assertGreater(appointed / total, 0.95, "lectionary coverage regressed")

    def test_references_use_a_colon_not_a_dot(self):
        from liturgics.lectionary import imported
        for entries in imported()["movable"].values():
            for e in entries:
                self.assertNotRegex(e["display"], r"\d\.\d",
                                    f"{e['display']} kept orthocal's dot form")


class TestFestalIcons(unittest.TestCase):
    """Icons carry provenance or they do not ship.

    An icon whose origin nobody can name is one the parish cannot publish. The
    licence check is not paperwork — it is the difference between a gift and a
    liability.
    """

    def test_every_registered_icon_has_a_licence_and_source(self):
        from liturgics.icons import registry
        for key, entry in registry().items():
            self.assertTrue(entry.get("file"), f"{key} has no file")
            self.assertTrue(entry.get("license"), f"{key} has no licence")
            self.assertTrue(entry.get("source"), f"{key} has no source")

    def test_registered_files_exist_on_disk(self):
        from pathlib import Path
        import liturgics
        from liturgics.icons import registry
        root = Path(liturgics.__file__).resolve().parent.parent / "parish" / "static" / "icons"
        for key, entry in registry().items():
            self.assertTrue((root / entry["file"]).exists(),
                            f"{key}: {entry['file']} is registered but missing")

    def test_patronal_feast_has_an_icon(self):
        from liturgics.icons import icon_for
        icon = icon_for(date(2026, 8, 15), 125)
        self.assertIsNotNone(icon, "the parish's own feast has no icon")
        self.assertEqual(icon["key"], "08-15")

    def test_a_day_without_an_icon_returns_none_rather_than_a_placeholder(self):
        from liturgics.icons import icon_for
        self.assertIsNone(icon_for(date(2026, 9, 9), 150))

    def test_movable_icons_outrank_fixed_ones(self):
        """Pascha keeps its own icon whatever fixed date it falls on."""
        from liturgics.icons import icon_for, registry
        if "P+000" not in registry():
            self.skipTest("Pascha icon not yet registered")
        icon = icon_for(pascha(2027), 0)
        self.assertEqual(icon["key"], "P+000")
