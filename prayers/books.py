"""
Canonical book identity across editions and languages.

Each edition names its books in its own language — the Synodal says Псалтирь,
a Greek edition says Ψαλμοί, the WEB says Psalms. Keying stored files by the
edition's own name means a reference can never resolve across languages, so
every edition is normalised to a canonical three-letter code on load.

Codes follow the USFM convention. `bnumber` in Zefania XML is the standard
1-66 ordering and maps directly, which is more reliable than name matching.

CANON. This table covers the 66 books shared with the Protestant canon. The
Orthodox Old Testament is LARGER — Tobit, Judith, Wisdom, Sirach, Baruch, the
Letter of Jeremiah, 1-3 Maccabees, 2 Esdras, the Prayer of Manasseh and Psalm
151. Editions come in both sizes; a 66-book file simply lacks them, and any
reference to one will report missing rather than resolve. Codes for the
deuterocanon are included below so a fuller edition loads without changes.
"""

from __future__ import annotations

import re
import unicodedata

# Zefania / standard bnumber -> canonical code
BY_NUMBER: dict[int, str] = {
    1: "GEN", 2: "EXO", 3: "LEV", 4: "NUM", 5: "DEU", 6: "JOS", 7: "JDG",
    8: "RUT", 9: "1SA", 10: "2SA", 11: "1KI", 12: "2KI", 13: "1CH",
    14: "2CH", 15: "EZR", 16: "NEH", 17: "EST", 18: "JOB", 19: "PSA",
    20: "PRO", 21: "ECC", 22: "SNG", 23: "ISA", 24: "JER", 25: "LAM",
    26: "EZK", 27: "DAN", 28: "HOS", 29: "JOL", 30: "AMO", 31: "OBA",
    32: "JON", 33: "MIC", 34: "NAM", 35: "HAB", 36: "ZEP", 37: "HAG",
    38: "ZEC", 39: "MAL", 40: "MAT", 41: "MRK", 42: "LUK", 43: "JHN",
    44: "ACT", 45: "ROM", 46: "1CO", 47: "2CO", 48: "GAL", 49: "EPH",
    50: "PHP", 51: "COL", 52: "1TH", 53: "2TH", 54: "1TI", 55: "2TI",
    56: "TIT", 57: "PHM", 58: "HEB", 59: "JAS", 60: "1PE", 61: "2PE",
    62: "1JN", 63: "2JN", 64: "3JN", 65: "JUD", 66: "REV",
}

# Reference spellings -> canonical code. English is what the lectionary and
# prayer documents cite; Greek and Russian names are here so a local-language
# edition still loads when it carries no bnumber.
_ALIASES: dict[str, tuple[str, ...]] = {
    "GEN": ("gen", "genesis", "бытие", "γενεσις"),
    "EXO": ("ex", "exo", "exodus", "исход", "εξοδος"),
    "LEV": ("lev", "leviticus", "левит"),
    "NUM": ("num", "numbers", "числа", "numeri"),
    "DEU": ("deu", "deut", "deuteronomy", "второзаконие", "deuteronomium"),
    "JOS": ("jos", "josh", "joshua", "иисуснавин", "josue"),
    "JDG": ("jdg", "judg", "judges", "судьи", "judices"),
    "RUT": ("rut", "ruth", "руфь"),
    "1SA": ("1sa", "1sam", "1samuel", "1царств", "regnorumi"),
    "2SA": ("2sa", "2sam", "2samuel", "2царств", "regnorumii"),
    "1KI": ("1ki", "1kings", "3царств", "regnorumiii"),
    "2KI": ("2ki", "2kings", "4царств", "regnorumiv"),
    "JOB": ("job", "иов"),
    "PSA": ("ps", "psa", "psalm", "psalms", "псалтирь", "псалом",
            "ψαλμοι", "ψαλμος", "psalmi"),
    "PRO": ("pro", "prov", "proverbs", "притчи", "proverbia"),
    "ECC": ("ecc", "eccl", "ecclesiastes", "екклесиаст"),
    "SNG": ("sng", "song", "songofsongs", "песньпесней", "songofsolomon", "canticum"),
    "ISA": ("isa", "isaiah", "исаия", "ησαιας", "isaias"),
    "JER": ("jer", "jeremiah", "иеремия", "jeremias"),
    "LAM": ("lam", "lamentations", "плач", "threniseulamentationes", "threni"),
    "EZK": ("ezk", "ezek", "ezekiel", "иезекииль", "ezechiel"),
    "DAN": ("dan", "daniel", "даниил", "dag", "danieltheodotionisversio"),
    "JOL": ("jol", "joel", "иоиль"),
    "AMO": ("amo", "amos", "амос"),
    "JON": ("jon", "jonah", "иона", "jonas"),
    "MIC": ("mic", "micah", "михей", "michaeas"),
    "MAL": ("mal", "malachi", "малахия", "malachias"),
    "MAT": ("mat", "matt", "matthew", "матфея", "ματθαιον", "mt"),
    "MRK": ("mrk", "mk", "mark", "марка", "μαρκον", "mr"),
    "LUK": ("luk", "lk", "luke", "луки", "λουκαν", "lu"),
    "JHN": ("jhn", "jn", "john", "иоанна", "ιωαννην", "joh"),
    "ACT": ("act", "acts", "деяния", "πραξεις", "ac"),
    "ROM": ("rom", "romans", "римлянам", "ρωμαιους", "ro"),
    "1CO": ("1co", "1cor", "1corinthians", "1коринфянам"),
    "2CO": ("2co", "2cor", "2corinthians", "2коринфянам"),
    "GAL": ("gal", "galatians", "галатам", "ga"),
    "EPH": ("eph", "ephesians", "ефесянам"),
    "PHP": ("php", "phil", "philippians", "филиппийцам"),
    "COL": ("col", "colossians", "колоссянам"),
    "1TH": ("1th", "1thess", "1фессалоникийцам", "1thessalonians"),
    "2TH": ("2th", "2thess", "2фессалоникийцам", "2thessalonians"),
    "1TI": ("1ti", "1tim", "1timothy", "1тимофею"),
    "2TI": ("2ti", "2tim", "2timothy", "2тимофею"),
    "TIT": ("tit", "titus", "титу"),
    "PHM": ("phm", "philemon", "филимону"),
    "HEB": ("heb", "hebrews", "евреям", "εβραιους"),
    "JAS": ("jas", "james", "иакова", "ιακωβου"),
    "1PE": ("1pe", "1peter", "1петра"),
    "2PE": ("2pe", "2peter", "2петра"),
    "1JN": ("1jn", "1john", "1иоанна", "1jo"),
    "2JN": ("2jn", "2john", "2иоанна", "2jo"),
    "3JN": ("3jn", "3john", "3иоанна", "3jo"),
    "JUD": ("jud", "jude", "иуды"),
    "REV": ("rev", "revelation", "откровение", "αποκαλυψις", "re"),
    "1CH": ("1ch", "1chron", "1chronicles", "1паралипоменон", "paralipomenoni"),
    "2CH": ("2ch", "2chron", "2chronicles", "2паралипоменон", "paralipomenonii"),
    "EZR": ("ezr", "ezra", "ездры", "esdrasb"),
    "NEH": ("neh", "nehemiah", "неемии"),
    "EST": ("est", "esther", "есфирь", "esg"),
    "HOS": ("hos", "hosea", "осия", "osee"),
    "OBA": ("oba", "obad", "obadiah", "авдия", "abdias"),
    "NAM": ("nam", "nah", "nahum", "наум"),
    "HAB": ("hab", "habakkuk", "аввакум", "habacuc"),
    "ZEP": ("zep", "zeph", "zephaniah", "софония", "sophonias"),
    "HAG": ("hag", "haggai", "аггей", "aggaeus"),
    "ZEC": ("zec", "zech", "zechariah", "захария", "zacharias"),
    # Deuterocanon — present in fuller Orthodox editions.
    "TOB": ("tob", "tobit", "товита", "tobias"),
    "JDT": ("jdt", "judith", "иудифи"),
    "WIS": ("wis", "wisdom", "премудростисоломона", "sapientiasalomonis"),
    "SIR": ("sir", "sirach", "ecclesiasticus", "премудростиисусасирахова"),
    "BAR": ("bar", "baruch", "варуха"),
    "1MA": ("1ma", "1macc", "1maccabees", "1маккавейская", "machabaeorumi"),
    "2MA": ("2ma", "2macc", "2maccabees", "2маккавейская", "machabaeorumii"),
    "3MA": ("3ma", "3macc", "3maccabees", "3маккавейская", "machabaeorumiii"),
    # Septuagint-only. Present in Swete and in fuller Orthodox editions.
    "4MA": ("4ma", "4macc", "4maccabees", "machabaeorumiv"),
    "1ES": ("1es", "1esdras", "esdrasa"),
    "ODA": ("oda", "odes", "odae"),
    "PSS": ("pss", "psalmsofsolomon", "psalmisalomonis"),
    "LJE": ("lje", "letterofjeremiah", "epistulajeremiae"),
    "SUS": ("sus", "susanna", "susannatheodotionisversio"),
    "BEL": ("bel", "belandthedragon", "beletdracotheodotionisversio"),
    "MAN": ("man", "prayerofmanasseh", "молитваманассии"),
}

def _build_lookup() -> dict[str, str]:
    """Flatten the alias table, refusing to let two codes claim one alias.

    A duplicated KEY in the literal above is invisible — Python keeps the last
    and silently discards the earlier entry, which once made every reference to
    Daniel resolve to None. Duplicated VALUES are caught here; the duplicate-key
    case is caught by a test that counts keys in the source.
    """
    out: dict[str, str] = {}
    for code, aliases in _ALIASES.items():
        for alias in aliases:
            if alias in out and out[alias] != code:
                raise ValueError(
                    f"alias {alias!r} claimed by both {out[alias]} and {code}")
            out[alias] = code
    return out


_LOOKUP: dict[str, str] = _build_lookup()


def normalise(name: str) -> str:
    """Fold a book name to its lookup key.

    Lowercase, diacritics stripped, alphanumerics only. Unicode-aware
    throughout: an ASCII-only character class collapses `Псалтирь` to an empty
    string, and leaving accents on means Greek `Ψαλμοί` never matches `ψαλμοι`.
    """
    decomposed = unicodedata.normalize("NFD", name.lower())
    return "".join(ch for ch in decomposed
                   if ch.isalnum() and not unicodedata.combining(ch))


def code_for(name: str = "", number: int | None = None) -> str | None:
    """Canonical code from a book name and/or a Zefania bnumber."""
    if number and number in BY_NUMBER:
        return BY_NUMBER[number]
    key = normalise(name)
    if key in _LOOKUP:
        return _LOOKUP[key]
    # "1-е Иоанна" / "2 Corinthians" — a leading ordinal written any which way.
    m = re.match(r"^([123])[ея]?(.+)$", key)
    if m:
        merged = m.group(1) + m.group(2)
        if merged in _LOOKUP:
            return _LOOKUP[merged]
    return None
