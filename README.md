# Assumption GOC — parish server

Django backend for the Assumption Greek Orthodox Church app, Pocatello, Idaho. Serves the
liturgical calendar, parish information and announcements to the iOS client,
and will host Father's panel.

## Layout

```
liturgics/          the calendar engine — PURE PYTHON, no Django imports
  paschalion.py     Pascha, and exact Julian <-> Gregorian conversion
  movable.py        seasons, named days, Tone, Eothinon
  fasting.py        the fast resolver (the most-read output in the app)
  resolver.py       assembles one fully-resolved day
  data/menaion.json fixed-date commemorations (INCOMPLETE — see below)
  tests/            20 tests, run in ~1ms
  lectionary.py     daily readings (Sundays and feasts only - see below)
prayers/            prayer documents and the assembler, also pure Python
  blocks.py         the ten block types, closed and versioned
  assembler.py      include / proper / scripture resolution
  scripture.py      file-backed passage store; LXX <-> Masoretic psalms
  data/*.json       Trisagion, Morning, Evening, Compline, the three Hours
parish/             what people decide: services, overrides, announcements
config/             settings, urls
```

**The engine imports nothing from Django on purpose.** Every liturgical rule is
a pure function of a date, so the whole thing is testable in milliseconds and
stays portable. Keep it that way — parish data layers on top in `parish/`,
never the reverse.

## Run

```bash
./venv/bin/python manage.py migrate
./venv/bin/python manage.py test liturgics parish
./venv/bin/python manage.py runserver
```

Endpoints:

    /api/v1/today/                       resolved day
    /api/v1/day/<YYYY-MM-DD>/            one day
    /api/v1/days/?start=&days=           window, up to 400 — the offline cache
    /api/v1/prayers/?date=               the day's rule, by time-of-day slot
    /api/v1/announcements/
    /api/v1/scripture/books/             book list with per-book languages
    /api/v1/scripture/<book>/<chapter>/  a chapter in every covering language
    /api/v1/scripture/search/?q=&lang=

The clients render this and compute nothing liturgical themselves. That rule is
what keeps two native codebases from drifting apart over years.

## Before this ships — confirm with Father

Grep for `NEEDS_CONFIRMATION`. Current list:

- **Apostles' Fast** — GOARCH practice on fish days differs from Slavic use.
  Do not tune this by copying a Russian calendar.
- **Lazarus Saturday** — many keep fish roe; currently wine and oil.
- **Nativity Fast** — the 18 December strictness change is one common
  formulation, not the only one.
- **Eothinon** — returns a value only after Pentecost; the Triodion and
  Pentecostarion have their own appointed Matins Gospels.
- **Tone during Lent and on Pentecost** — several Sundays have proper hymnody
  rather than the plain cycle value.
- ~~`PARISH_TZ`~~ — settled: `America/Boise` (Pocatello, Idaho). Mountain time.
  Not `America/Denver`; northern Idaho is Pacific, so the zone name matters.
- **`data/menaion.json` covers all 366 days but is UNVERIFIED.** It was
  authored from general knowledge, not transcribed from a published GOARCH
  calendar. The Great Feasts and well-known commemorations are reliable; the
  long tail of minor martyrs is where errors will be. Seven entries are
  flagged for review first — Greek/Slavic divergences (Holy Protection on
  28 October rather than 1 October, St. Catherine on the 25th) and recently
  glorified Greek saints (Paisios, Porphyrios, Iakovos of Evia).

  ```bash
  ./venv/bin/python manage.py menaion_review           # the 7 flagged
  ./venv/bin/python manage.py menaion_review --all     # full-year checklist
  ./venv/bin/python manage.py menaion_review --month 8
  ```

## Three content languages

English, Greek and Slavonic are **peers**, not a base language with two
translations bolted on. The parish has ethnic Greeks and ethnic Russians, and
people keep a prayer rule in the language they actually pray in. Every
user-facing string is a `{"en":…, "el":…, "ru":…}` object; the API returns all
three on every response so a reader can switch mid-prayer without a round trip.

**Nothing falls back to English silently.** A missing translation is reported
as missing — in `translation_gaps` on a day, and in the `missing` array on a
prayer. If English quietly stood in for Slavonic, nobody would ever notice the
gap and it would never get filled.

```bash
./venv/bin/python manage.py translation_report
./venv/bin/python manage.py translation_report --lang ru --missing
```

**One open question for Ian.** The `ru` field currently holds **Church
Slavonic set in the civil alphabet**, which is what a молитвослов prints and
what people actually say aloud. A modern Russian translation is a different
text and reads as a study aid rather than a rule. If the parish wants both,
add a fourth language `ru_mod` rather than replacing this one.

See [CREDITS.md](CREDITS.md) for the attribution the bundled texts require.

## Prayer books and the Bible are separate

Two independent content domains. Mixing them is the mistake to avoid.

**Prayer books** (`prayers/data/*.json`) are the молитвослов, the Horologion,
the English prayer book. In Russian this means **Church Slavonic**. A prayer
book prints its psalms inline — you do not look them up in a Bible — so a
psalm inside a rule is a `psalm` block carrying its own text per language.
Prayer documents never read from the scripture store, and a test enforces it.

**The Bible** (`prayers/data/scripture/`) serves actual citations: the daily
Gospel, a passage read on its own. In Russian this is the **Synodal**
translation — someone looking up a Gospel wants Russian they can read, not
Slavonic. Only a `scripture` block touches this store.

| | Bible | Old Testament | Prayer book |
|---|---|---|---|
| **en** | World English Bible | Brenton's Septuagint | English prayer book |
| **el** | Patriarchal Text 1904 | Rahlfs Septuagint | Ὡρολόγιον |
| **ru** | Синодальный перевод | Синодальный | **молитвослов** (Church Slavonic) |

Orthodox Old Testament reading follows the Septuagint, so an LXX-based edition
is preferred for OT passages where one is loaded. **The ESV and NKJV are
copyrighted** and cannot be bundled; Crossway's ESV permissions cover
quotation and a licence-key API, not distribution inside an app.

### Loaded

All three content languages resolve. The text is **vendored into this repo**
(12 MB, all public domain) so the app is self-contained and deploying to
PythonAnywhere is a `git pull` — the upstream sources are third-party repos
that can move or disappear.

| Edition | Source | Books | Verses | Caveat |
|---|---|---|---|---|
| `web` | TehShrike/world-english-bible | 66 | 31,098 | Masoretic numbering |
| `synodal` | open-bibles `rus-synodal.zefania.xml` | 66 | 31,352 | Masoretic-chaptered; **no deuterocanon** |
| `patriarchal` | byztxt/greektext-antoniades | 27 (NT) | 7,956 | **Unaccented** |
| `swete` | nathans/lxx-swete (First1KGreek) | 52 (OT) | 28,543 | **CC BY-SA — attribution required**; no Ecclesiastes |
| `brenton` | ebible.org `eng-Brenton_html.zip` | 53 (OT) | 28,828 | LXX-numbered; has Ecclesiastes and the full deuterocanon |

```bash
./venv/bin/python manage.py load_scripture ~/Downloads/rus-synodal.zefania.xml --edition synodal
./venv/bin/python manage.py load_scripture path/to/antoniades/textonly/unicode --edition patriarchal
./venv/bin/python manage.py load_scripture path/to/world-english-bible/json --edition web
```

**Three defects in the loaded data, all visible to a reader:**

1. **The Greek is unaccented.** Zero accented vowels in 72,353 Greek letters —
   that text is stripped for searching, not set for reading. Correct edition
   and correct words, but a Greek reader sees it as raw immediately. Needs an
   accented Patriarchal text before it goes in front of the parish.
2. **Ecclesiastes is missing in Greek.** Swete supplies a polytonic Greek Old
   Testament *with* the Orthodox deuterocanon — Tobit, Judith, Wisdom, Sirach,
   Baruch, 1-3 Maccabees, Susanna, Bel — but the First1KGreek repo has no
   Ecclesiastes. Note Ecclesiasticus is Sirach, a different book.
   **Swete is CC BY-SA 4.0, not public domain: attribution is required.**
3. **The Synodal file is the 66-book canon.** The Orthodox Old Testament is
   larger — Tobit, Judith, Wisdom, Sirach, Baruch, 1-3 Maccabees, the Prayer
   of Manasseh. Readings from those report missing.

**Do not infer psalm numbering from an edition's name.** A printed Synodal
Bible is Septuagint-numbered, but the Zefania file we ingest was renumbered to
Masoretic chapters to fit the 66-book schema, keeping the Synodal reference
inline as `(50:3)`. It is therefore NOT in `LXX_NATIVE`. Verify each edition
after loading: open Psalm 50 and 51 and see which one is penitential.

Editions in `scripture.LXX_NATIVE` — Brenton, Rahlfs, and the Synodal psalter,
which follows Slavonic/LXX numbering — are **not** renumbered on read.
Converting an already-Septuagint-numbered edition shifts the psalm twice.

## Content gaps

The API reports these in a `missing` array on every prayer response, so the
app never renders an empty heading and we always know what is outstanding.

1. **Daily readings — imported, ~97% of days.** `manage.py import_lectionary`
   reads orthocal's calendarium fixture (MIT) and writes
   `liturgics/data/lectionary.json`. orthocal's `pdist` is this project's
   `pascha_offset`, so movable readings key straight across; fixed readings key
   month-day. Common and Greek rows are kept and Slavic dropped.

   Covers the Epistle and Gospel, plus Vespers and Sixth Hour lessons, Matins
   Gospels, the Twelve Passion Gospels and the Royal Hours. A Lenten weekday
   correctly yields Genesis and Proverbs at Vespers and Isaiah at the Sixth
   Hour, with no Gospel, since the full Liturgy is not served.

   The remaining gap is roughly twelve days a year, in the stretch after
   Pentecost that runs long when Pascha falls very late. orthocal resolves
   those with reserve-week logic in code rather than data; those days still
   report `unsourced` with their course and week.

2. **Ecclesiastes is missing in Greek.** Swete supplies a polytonic Greek Old
   Testament *with* the Orthodox deuterocanon — Tobit, Judith, Wisdom, Sirach,
   Baruch, 1-3 Maccabees, Susanna, Bel — but the First1KGreek repo has no
   Ecclesiastes. Note Ecclesiasticus is Sirach, a different book.
   **Swete is CC BY-SA 4.0, not public domain: attribution is required.**
3. **The Synodal file is the 66-book canon.** The Orthodox Old Testament is
   larger — Tobit, Judith, Wisdom, Sirach, Baruch, 1-3 Maccabees, the Prayer
   of Manasseh. Readings from those report missing.

**Do not infer psalm numbering from an edition's name.** A printed Synodal
Bible is Septuagint-numbered, but the Zefania file we ingest was renumbered to
Masoretic chapters to fit the 66-book schema, keeping the Synodal reference
inline as `(50:3)`. It is therefore NOT in `LXX_NATIVE`. Verify each edition
after loading: open Psalm 50 and 51 and see which one is penitential.

Editions in `scripture.LXX_NATIVE` — Brenton, Rahlfs, and the Synodal psalter,
which follows Slavonic/LXX numbering — are **not** renumbered on read.
Converting an already-Septuagint-numbered edition shifts the psalm twice.

## Content gaps

The API reports these in a `missing` array on every prayer response, so the
app never renders an empty heading and we always know what is outstanding.

1. **Weekday lectionary — machinery done, ~77% of days still unsourced.**
   Sundays, Great Feasts and Holy Week resolve. The course-reading engine and
   the **Lucan jump** are implemented and tested: the course of Luke begins on
   the Monday after the Sunday following 14 September, a fixed date, so the
   Matthew course varies in length year to year. That variation is what a
   hand-built table gets wrong, and it is computed rather than guessed.

   **Every day of the year has appointed readings.** What varies is which
   services carry them, so days report a `status` and a `kind` and no day ever
   claims to have nothing:

   | kind | 2027 | what is appointed |
   |---|---|---|
   | *(appointed)* | 55 | on file |
   | `weekday_course` | 224 | Epistle and Gospel, Matthew or Luke course |
   | `lenten_old_testament` | 28 | Genesis and Proverbs at Vespers, Isaiah at the Sixth Hour — no Gospel, since the full Liturgy is not served |
   | `pentecostarion_course` | ~50 | Acts and John, read daily in the paschal season |
   | `triodion` | few | pre-Lenten weekdays |

   **Drop a table at `liturgics/data/pericopes.json` and every weekday
   resolves, no code changes.** Shape: `{"MAT": {"1": {"0": {"epistle": …,
   "gospel": …}}}}` — gospel course, week, weekday index (0 = Monday). The
   ~700 references are not invented here; get them from the Archdiocese or
   AGES.
2. **Hymn texts.** The Menaion carries commemorations, not troparia, so every
   `proper` slot currently reports missing rather than showing a placeholder.
3. **Scripture. Nothing is bundled — not one verse.** The loader and reader
   exist; the text does not. See the table above for what to obtain.
4. **Prayer-book psalms — Greek done, English and Slavonic outstanding.**
   `manage.py bake_psalms` writes psalm text into the prayer documents from
   each tradition's own psalter, recorded in a `sources` field:

   | | Psalter | Status |
   |---|---|---|
   | `el` | Swete's Septuagint | **done** — the Horologion's psalms *are* the LXX |
   | `en` | Brenton | **done** — LXX-based, as an English Orthodox psalter is |
   | `ru` | Church Slavonic Psalter (Elizabeth) | **done** — see the licensing note in CREDITS.md |

   The refusals are deliberate and tested. A language without its psalter is
   left empty rather than borrowing from the nearest Bible.
   Psalters disagree on verse numbering — the Slavonic superscription is verse
   0, Brenton's is verses 1-2 — so prayer documents cite **whole psalms only**,
   enforced by both the bake command and a test.
5. **Troparia.** Every `proper` slot is still unfilled in all three languages —
   366 days of hymn texts. This is now the only remaining gap in the rule.
6. **Translations.** Greek and Slavonic cover the Great Feasts, the movable
   cycle and the invariable prayers. The long tail of the Menaion is
   English-only. `translation_report` has the exact numbers.

**Psalm numbering is a live hazard.** The Orthodox Psalter follows the
Septuagint, which runs one behind the KJV for most of the book and disagrees
about where several psalms divide — LXX 113 spans KJV 114 and 115; LXX 114 and
115 both fall inside KJV 116. Every psalm citation in the prayer documents
carries `"numbering": "lxx"` and is converted on read. Getting this wrong does
not raise; it silently serves a different psalm than the one appointed.

## SQLite now, Postgres later

SQLite locally. Set `POSTGRES_DB` (plus user/password/host) and the settings
switch over with no code change. Every model sticks to portable field types —
no `ArrayField`, no Postgres-only search — so the move is a dump and load.

## PythonAnywhere

1. **The $5 Hacker plan is the floor, not the free tier.** Free accounts can
   only reach a proxy whitelist, and `api.push.apple.com` is not on it — push
   notifications do not work at all on free. Hacker also buys the custom domain.
2. Push `venv/` is gitignored; rebuild it there and `pip install -r requirements.txt`.
3. Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, and `DJANGO_ALLOWED_HOSTS` to the
   real domain in the web app's environment variables.
4. Media (icons, PDFs, the scanned catechism) belongs on Cloudflare R2, not on
   PythonAnywhere's 1 GB disk. Django serves small JSON; R2 serves bytes.
5. No Redis and no per-minute worker on this plan. Send announcement pushes
   synchronously in the request; run liturgical reminders from one daily
   scheduled task.
