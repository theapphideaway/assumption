"""
Three content languages, equally supported.

English, Greek and Russian are peers here — not a base language with two
translations bolted on. The parish has ethnic Greeks and ethnic Russians, and
people keep their prayer rule in the language they actually pray in. Anything
that treats English as the "real" text and the others as extras will feel
wrong to exactly the people it is meant to serve.

Practical consequences of that stance:

  * Every user-facing string in this package is a `Text` mapping, never a bare
    str. Season names, fast labels and commemorations all go through here.
  * The API returns ALL THREE languages on every response. The client chooses,
    and a reader can switch language mid-prayer without a round trip.
  * A missing translation is reported, never silently replaced by English. The
    app falls back visibly (marked), and `translation_report` lists the gaps.

CHURCH SLAVONIC vs RUSSIAN — needs Ian's call. Russian prayer books
(молитвослов) almost always print the prayers in CHURCH SLAVONIC set in the
civil alphabet, because that is what people actually say aloud. A modern
Russian translation is a different text and reads as a study aid, not a rule.
The `ru` field below holds Church Slavonic in civil script, which is the
common practice; if the parish wants modern Russian as well, add a `ru_mod`
language rather than replacing this one.
"""

from __future__ import annotations

LANGUAGES: tuple[str, ...] = ("en", "el", "ru")

LANGUAGE_NAMES = {
    "en": {"en": "English", "el": "Ἀγγλικά", "ru": "Английский"},
    "el": {"en": "Greek", "el": "Ἑλληνικά", "ru": "Греческий"},
    "ru": {"en": "Slavonic", "el": "Σλαβονικά", "ru": "Церковнославянский"},
}

Text = dict          # {"en": ..., "el": ..., "ru": ...}; keys may be absent


def text(en: str = "", el: str = "", ru: str = "") -> Text:
    """Build a Text, omitting empty languages so gaps stay visible."""
    return {k: v for k, v in (("en", en), ("el", el), ("ru", ru)) if v}


def missing_languages(t: Text | None) -> list[str]:
    if not t:
        return list(LANGUAGES)
    return [lang for lang in LANGUAGES if not t.get(lang)]


def coverage(t: Text | None) -> float:
    if not t:
        return 0.0
    return sum(1 for lang in LANGUAGES if t.get(lang)) / len(LANGUAGES)


# --- fixed vocabulary -------------------------------------------------------

SEASONS: dict[str, Text] = {
    "triodion":        text("Triodion", "Τριῴδιον", "Триодь постная"),
    "great_lent":      text("Great Lent", "Μεγάλη Τεσσαρακοστή", "Великий пост"),
    "holy_week":       text("Holy Week", "Μεγάλη Ἑβδομάς", "Страстная седмица"),
    "bright_week":     text("Bright Week", "Διακαινήσιμος", "Светлая седмица"),
    "pentecostarion":  text("Pentecostarion", "Πεντηκοστάριον", "Триодь цветная"),
    "after_pentecost": text("After Pentecost", "Μετὰ τὴν Πεντηκοστήν",
                            "По Пятидесятнице"),
}

FAST_LABELS: dict[str, Text] = {
    "STRICT":    text("Strict Fast", "Αὐστηρὰ νηστεία", "Строгий пост"),
    "WINE_OIL":  text("Wine & Oil", "Κατάλυσις οἴνου καὶ ἐλαίου",
                      "Разрешается вино и елей"),
    "FISH":      text("Fish, Wine & Oil", "Κατάλυσις ἰχθύος",
                      "Разрешается рыба"),
    "DAIRY":     text("Dairy Allowed", "Κατάλυσις γαλακτερῶν",
                      "Сырная седмица"),
    "FAST_FREE": text("Fast-Free", "Κατάλυσις εἰς πάντα", "Поста нет"),
}

FAST_REASONS: dict[str, Text] = {
    "Wednesday":  text("Wednesday", "Τετάρτη", "Среда"),
    "Friday":     text("Friday", "Παρασκευή", "Пятница"),
    "Great Lent": text("Great Lent", "Μεγάλη Τεσσαρακοστή", "Великий пост"),
    "Holy Week":  text("Holy Week", "Μεγάλη Ἑβδομάς", "Страстная седмица"),
    "Bright Week": text("Bright Week", "Διακαινήσιμος", "Светлая седмица"),
    "Cheesefare Week": text("Cheesefare Week", "Τυρινή", "Сырная седмица"),
    "Dormition Fast": text("Dormition Fast", "Νηστεία Δεκαπενταυγούστου",
                           "Успенский пост"),
    "Nativity Fast": text("Nativity Fast", "Νηστεία Χριστουγέννων",
                          "Рождественский пост"),
    "Apostles' Fast": text("Apostles' Fast", "Νηστεία τῶν Ἁγίων Ἀποστόλων",
                           "Петров пост"),
    "The Transfiguration": text("The Transfiguration", "Ἡ Μεταμόρφωσις",
                                "Преображение Господне"),
    "The Annunciation": text("The Annunciation", "Ὁ Εὐαγγελισμός",
                             "Благовещение"),
    "Palm Sunday": text("Palm Sunday", "Κυριακὴ τῶν Βαΐων",
                        "Вход Господень в Иерусалим"),
    "Lazarus Saturday": text("Lazarus Saturday", "Σάββατον τοῦ Λαζάρου",
                             "Лазарева суббота"),
    "Great and Holy Friday": text("Great and Holy Friday", "Μεγάλη Παρασκευή",
                                  "Великая Пятница"),
    "Eve of the Nativity": text("Eve of the Nativity", "Παραμονὴ Χριστουγέννων",
                                "Рождественский сочельник"),
    "The Twelve Days of Nativity": text("The Twelve Days of Nativity",
                                        "Δωδεκαήμερον", "Святки"),
    "Week of the Publican and the Pharisee": text(
        "Week of the Publican and the Pharisee", "Ἑβδομὰς Τελώνου καὶ Φαρισαίου",
        "Седмица о мытаре и фарисее"),
    "Week of the Holy Spirit": text("Week of the Holy Spirit",
                                    "Ἑβδομὰς τοῦ Ἁγίου Πνεύματος",
                                    "Троицкая седмица"),
    "Great Lent — Saturday and Sunday": text(
        "Great Lent — Saturday and Sunday", "Σάββατον καὶ Κυριακὴ τῆς Τεσσαρακοστῆς",
        "Великий пост — суббота и воскресенье"),
    "Great Feast falling on a fast day": text(
        "Great Feast falling on a fast day", "Μεγάλη ἑορτὴ σὲ ἡμέρα νηστείας",
        "Великий праздник в постный день"),
}


def fast_reason(reason: str) -> Text:
    """Translate a fast reason, falling back to English-only when unknown so
    the gap shows up in the coverage report rather than disappearing."""
    return FAST_REASONS.get(reason) or ({"en": reason} if reason else {})
