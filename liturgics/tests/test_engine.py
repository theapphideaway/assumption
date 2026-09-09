"""
Tests for the liturgical engine.

The Pascha fixtures below are the published Orthodox dates. They are the
backstop for the entire calendar: if these pass, every movable feast, the Tone
cycle and most of the fasting rules follow, because all of them are pure
functions of the paschal offset.
"""

import unittest
from datetime import date, timedelta

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
        self.assertEqual(r["title"], "The Dormition of the Theotokos")
        self.assertEqual(r["season"]["color"], "lapis")

    def test_pascha_outranks_any_fixed_feast(self):
        r = resolve_day(pascha(2027))
        self.assertEqual(r["rank"], 1)
        self.assertEqual(r["title"], "Great and Holy Pascha")

    def test_shape_is_stable(self):
        r = resolve_day(date(2026, 9, 9))
        for key in ("date", "julian", "pascha_offset", "season", "title",
                    "rank", "tone", "fast", "commemorations", "parish"):
            self.assertIn(key, r)
        self.assertEqual(r["julian"], "2026-08-27")


if __name__ == "__main__":
    unittest.main(verbosity=2)
