"""Tests for the prayer documents, the assembler and the lectionary."""

import unittest
from datetime import date, timedelta

from liturgics.lectionary import FIXED, MOVABLE, readings_for
from liturgics.paschalion import pascha, reference_pascha
from liturgics.resolver import resolve_day
from prayers.assembler import assemble
from prayers.blocks import BLOCK_TYPES, slot_for_hour
from prayers.scripture import lxx_to_masoretic, passage
from prayers.store import catalogue, load


class TestDocuments(unittest.TestCase):
    def test_every_document_uses_only_known_block_types(self):
        """A typo in a data file must fail here, not render as a blank line
        in the middle of someone's morning prayers."""
        for doc_id, doc in catalogue().items():
            for i, b in enumerate(doc["blocks"]):
                self.assertIn(b.get("type"), BLOCK_TYPES,
                              f"{doc_id} block {i}: unknown type {b.get('type')!r}")

    def test_every_document_has_required_fields(self):
        for doc_id, doc in catalogue().items():
            for field in ("id", "title", "blocks", "provenance"):
                self.assertIn(field, doc, f"{doc_id} missing {field}")
            self.assertTrue(doc["blocks"], f"{doc_id} has no blocks")

    def test_literal_blocks_carry_english(self):
        for doc_id, doc in catalogue().items():
            for b in doc["blocks"]:
                if b["type"] in ("para", "refrain", "dismissal"):
                    self.assertTrue(b.get("en"), f"{doc_id}: {b['type']} with no text")

    def test_the_seven_documents_are_present(self):
        self.assertEqual(
            set(catalogue()),
            {"trisagion", "morning", "evening", "compline-small",
             "hour-third", "hour-sixth", "hour-ninth"})


class TestAssembler(unittest.TestCase):
    def setUp(self):
        self.day = resolve_day(date(2026, 9, 9))

    def test_include_is_expanded_inline(self):
        """The Trisagion is authored once and spliced into six documents."""
        built = assemble("morning", self.day)
        texts = [b.get("en", "") for b in built["blocks"]]
        self.assertTrue(any("Holy God, Holy Mighty" in t for t in texts))
        self.assertNotIn("include", [b["type"] for b in built["blocks"]])

    def test_unfilled_propers_are_reported_not_invented(self):
        """No placeholder that looks like a hymn ever reaches a phone."""
        built = assemble("morning", self.day)
        self.assertNotIn("proper", [b["type"] for b in built["blocks"]])
        self.assertTrue(any(m["type"] == "proper" for m in built["missing"]))

    def test_scripture_absent_is_reported_not_faked(self):
        built = assemble("hour-sixth", self.day)
        refs = [m["ref"] for m in built["missing"] if m["type"] == "scripture"]
        self.assertEqual(refs, ["Ps 53", "Ps 54", "Ps 90"])
        self.assertNotIn("scripture", [b["type"] for b in built["blocks"]])

    def test_scripture_present_is_spliced_in(self):
        built = assemble("hour-sixth", self.day,
                         scripture=lambda ref, numbering="masoretic":
                         [{"type": "verse", "n": 1, "en": f"[{ref}]"}])
        verses = [b for b in built["blocks"] if b["type"] == "verse"]
        self.assertEqual(len(verses), 3)
        # The troparion of the day is still legitimately missing; scripture is not.
        self.assertEqual([m for m in built["missing"] if m["type"] == "scripture"], [])

    def test_lxx_numbering_reaches_the_scripture_resolver(self):
        """Regression: the assembler used to call scripture(ref) without the
        block's numbering, so every psalm in every prayer was looked up under
        Masoretic numbers and came back one psalm off."""
        seen = {}

        def spy(ref, numbering="masoretic"):
            seen[ref] = numbering
            return [{"type": "verse", "n": 1, "en": ref}]

        assemble("hour-sixth", self.day, scripture=spy)
        self.assertEqual(seen, {"Ps 53": "lxx", "Ps 54": "lxx", "Ps 90": "lxx"})

    def test_slots(self):
        self.assertEqual(slot_for_hour(6), "morning")
        self.assertEqual(slot_for_hour(12), "hours")
        self.assertEqual(slot_for_hour(19), "evening")
        self.assertEqual(slot_for_hour(23), "compline")
        self.assertEqual(slot_for_hour(2), "compline")


class TestLectionary(unittest.TestCase):
    def test_pascha_gospel(self):
        p = pascha(2027)
        _, off = reference_pascha(p)
        self.assertEqual(readings_for(p, off)["gospel"], "John 1:1-17")

    def test_movable_outranks_fixed(self):
        """Pascha keeps its own Gospel whatever fixed date it lands on."""
        p = pascha(2027)
        _, off = reference_pascha(p)
        self.assertEqual(readings_for(p, off)["source"], "movable")

    def test_patronal_feast_has_readings(self):
        d = date(2026, 8, 15)
        _, off = reference_pascha(d)
        r = readings_for(d, off)
        self.assertEqual(r["epistle"], "Phil 2:5-11")

    def test_ordinary_weekday_returns_nothing_rather_than_a_guess(self):
        """The weekday course readings are the project's largest content gap.
        Returning None is the honest behaviour; inventing a plausible
        reference is not."""
        d = date(2026, 11, 18)
        _, off = reference_pascha(d)
        self.assertIsNone(readings_for(d, off))

    def test_no_duplicate_or_malformed_entries(self):
        for off, (ep, gos) in MOVABLE.items():
            self.assertTrue(gos, f"movable {off} has no Gospel")
        for key, (ep, gos) in FIXED.items():
            self.assertRegex(key, r"^\d{2}-\d{2}$")
            self.assertTrue(gos, f"fixed {key} has no Gospel")


class TestPsalmNumbering(unittest.TestCase):
    """LXX vs Masoretic. Getting this wrong does not raise — it silently
    serves a different psalm than the one appointed."""

    def test_common_liturgical_psalms(self):
        self.assertEqual(lxx_to_masoretic(50), (51,))    # the Miserere
        self.assertEqual(lxx_to_masoretic(90), (91,))
        self.assertEqual(lxx_to_masoretic(1), (1,))

    def test_the_splits(self):
        self.assertEqual(lxx_to_masoretic(9), (9, 10))
        self.assertEqual(lxx_to_masoretic(113), (114, 115))
        self.assertEqual(lxx_to_masoretic(114), (116,))
        self.assertEqual(lxx_to_masoretic(115), (116,))
        self.assertEqual(lxx_to_masoretic(146), (147,))

    def test_missing_edition_returns_none(self):
        self.assertIsNone(passage("Ps 50", edition="kjv", numbering="lxx"))
