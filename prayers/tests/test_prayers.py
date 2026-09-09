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
                    self.assertTrue(b.get("text", {}).get("en"),
                                    f"{doc_id}: {b['type']} with no English")

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
        texts = [b.get("text", {}).get("en", "") for b in built["blocks"]]
        self.assertTrue(any("Holy God, Holy Mighty" in t for t in texts))
        self.assertNotIn("include", [b["type"] for b in built["blocks"]])

    def test_unfilled_propers_are_reported_not_invented(self):
        """No placeholder that looks like a hymn ever reaches a phone."""
        built = assemble("morning", self.day)
        self.assertNotIn("proper", [b["type"] for b in built["blocks"]])
        self.assertTrue(any(m["type"] == "proper" for m in built["missing"]))

    def test_no_prayer_document_reads_from_the_bible(self):
        """Prayer books and the Bible are separate domains. A молитвослов
        prints its psalms inline; it does not cite a Bible. A `scripture`
        block appearing inside a rule means that separation has been broken."""
        for doc_id, doc in catalogue().items():
            kinds = {b["type"] for b in doc["blocks"]}
            self.assertNotIn("scripture", kinds,
                             f"{doc_id} reads from the Bible store")

    def test_prayerbook_psalms_are_reported_not_fetched(self):
        """An unsourced psalm reports missing. It must never fall back to a
        Bible translation, which would put a different rendering of the psalm
        into someone's rule than the one their prayer book prints."""
        built = assemble("hour-sixth", self.day)
        refs = [m["ref"] for m in built["missing"] if m["type"] == "psalm"]
        self.assertEqual(refs, ["Ps 53", "Ps 54", "Ps 90"])
        self.assertNotIn("psalm", [b["type"] for b in built["blocks"]])

    def test_psalms_are_not_affected_by_the_scripture_store(self):
        """Even with a Bible loaded, prayer-book psalms stay missing until the
        prayer-book text itself is sourced."""
        built = assemble("hour-sixth", self.day,
                         scripture=lambda ref, numbering="masoretic":
                         [{"type": "verse", "n": 1, "text": {"en": "from a Bible"}}])
        self.assertTrue(any(m["type"] == "psalm" for m in built["missing"]))
        self.assertEqual([b for b in built["blocks"] if b["type"] == "verse"], [])

    def test_sourced_psalm_text_is_emitted(self):
        from prayers.assembler import _expand
        blocks = _expand(
            [{"type": "psalm", "ref": "Ps 50", "numbering": "lxx",
              "text": {"en": "Have mercy on me, O God",
                       "ru": "Помилуй мя, Боже"}}],
            self.day, None, [], 0)
        self.assertEqual(blocks[0]["type"], "psalm")
        self.assertEqual(blocks[0]["ref"], "Ps 50")
        self.assertIn("ru", blocks[0]["text"])

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


class TestPrayerTranslations(unittest.TestCase):
    """The invariable prayers — the ones said aloud from memory — must carry
    all three languages. These are what a Greek yiayia and a Russian babushka
    each open the app expecting to find."""

    CORE = [
        "Holy God, Holy Mighty, Holy Immortal, have mercy on us.",
        "Lord, have mercy.",
        "Glory to Thee, our God, glory to Thee.",
    ]

    def test_core_texts_are_complete_in_all_three(self):
        from liturgics.i18n import missing_languages
        found = {}
        for doc in catalogue().values():
            for b in doc["blocks"]:
                t = b.get("text") or {}
                if t.get("en") in self.CORE:
                    found[t["en"]] = missing_languages(t)
        for line in self.CORE:
            self.assertIn(line, found, f"not found in any document: {line}")
            self.assertEqual(found[line], [], f"incomplete: {line}")

    def test_the_lords_prayer_is_complete(self):
        from liturgics.i18n import missing_languages
        blocks = load("trisagion")["blocks"]
        pater = next(b for b in blocks
                     if b.get("text", {}).get("en", "").startswith("Our Father"))
        self.assertEqual(missing_languages(pater["text"]), [])
        self.assertIn("Отче наш", pater["text"]["ru"])
        self.assertIn("Πάτερ ἡμῶν", pater["text"]["el"])

    def test_no_block_is_slavonic_only_or_greek_only(self):
        """English is the working language of the repo; every block must have
        it so a gap in another language is always diffable against something."""
        for doc_id, doc in catalogue().items():
            for i, b in enumerate(doc["blocks"]):
                t = b.get("text")
                if t:
                    self.assertIn("en", t, f"{doc_id} block {i} has no English")


class TestBibleSeparation(unittest.TestCase):
    """The Bible store serves actual citations — the daily Gospel, a passage
    read on its own. It is a different domain from the prayer books."""

    def test_editions_are_one_per_language(self):
        from prayers.scripture import EDITIONS
        self.assertEqual(EDITIONS["ru"], "synodal",
                         "Bible reading in Russian is Synodal, not Slavonic")
        self.assertEqual(EDITIONS["en"], "web")
        self.assertEqual(EDITIONS["el"], "patriarchal")

    def test_old_testament_prefers_a_septuagint_edition(self):
        from prayers.scripture import edition_for
        loaded = {"web", "brenton", "patriarchal", "rahlfs", "synodal"}
        self.assertEqual(edition_for("en", "Ps 50", loaded), "brenton")
        self.assertEqual(edition_for("en", "Isaiah 7:14", loaded), "brenton")
        self.assertEqual(edition_for("en", "John 1:1", loaded), "web")

    def test_ot_edition_falls_back_when_not_loaded(self):
        self.assertEqual(edition_for_web_only("en", "Ps 50"), "web")

    def test_numbering_is_a_property_of_the_file_not_the_translation(self):
        """This test previously asserted the opposite, and the real file proved
        it wrong — worth keeping as a record of why.

        A printed Russian Synodal Bible IS Septuagint-numbered: Псалом 50 is
        the penitential psalm. But the Zefania file we actually ingest was
        renumbered to Masoretic chapters to fit the 66-book schema, keeping the
        Synodal reference inline as "(50:3)". So the edition needs converting
        like any Masoretic text, and inferring otherwise from the translation's
        name would have served the wrong psalm every day, silently.

        The rule: verify each file after loading. Never infer from the name.
        """
        from prayers.scripture import LXX_NATIVE
        self.assertNotIn("synodal", LXX_NATIVE)
        self.assertIn("brenton", LXX_NATIVE)
        self.assertNotIn("web", LXX_NATIVE)


def edition_for_web_only(lang, ref):
    from prayers.scripture import edition_for
    return edition_for(lang, ref, loaded={"web"})
