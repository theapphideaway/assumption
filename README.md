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

Endpoints: `/api/v1/today/`, `/api/v1/day/<YYYY-MM-DD>/`,
`/api/v1/days/?start=&days=`, `/api/v1/announcements/`, `/api/v1/prayers/`.

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

## Content gaps

The API reports these in a `missing` array on every prayer response, so the
app never renders an empty heading and we always know what is outstanding.

1. **Weekday lectionary.** Sundays, Great Feasts and Holy Week are on file.
   Ordinary weekday course readings are not — that cycle turns on the "Lucan
   jump" and interacts with Menaion feasts in ways that cannot be
   reconstructed from memory. This is the strongest reason to get written
   permission from the Archdiocese or AGES for their lectionary.
2. **Hymn texts.** The Menaion carries commemorations, not troparia, so every
   `proper` slot currently reports missing rather than showing a placeholder.
3. **Scripture.** Nothing is bundled. `manage.py load_scripture <file>`
   ingests a public-domain edition (KJV, and Brenton for the Septuagint).

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
