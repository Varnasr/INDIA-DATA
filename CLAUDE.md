# INDIA-DATA

Shared engineering standard: @.claude/engineering-standards.md. It applies to all work in this repository. This file adds what is specific to the project, and wins where the two disagree.

The SIR analyses hub at offtheroll.in: counts of electors left off or deleted in
the Special Intensive Revision, state by state, with Bihar and the other states
analysed in more detail. Static HTML, Chart.js from cdnjs, one stylesheet
(`assets/sir.css`) and one helper script (`assets/sir.js`) shared by every page.
Netlify deploys the repository root from `main`. The full working notes for this
repository are kept in a separate private repository; ask the maintainer.

## Commands

```bash
pip install pandas==3.0.6 openpyxl==3.1.5
python3 scripts/check_data.py           # data checks, run by CI; rebuilds the data files with --check
python3 scripts/check_contrast.py       # assets/sir.css tokens, both themes
python3 scripts/build_site.py           # every page, from site/places.json and site/pages; --check in CI
python3 scripts/stamp.py                # cache busting; run on every deploy
python3 -m http.server 8000
```

## Rules that keep the data honest

- **Aggregates only.** This repository holds counts. Never commit names, EPIC
  numbers or row-level voter lists, or links to them. CI fails on an EPIC-like
  field under `data/bihar`.
- **Never edit a built page.** Every page is written by `scripts/build_site.py`
  from `site/places.json` and `site/pages/<path>/index.html`. A new state or
  place is an entry in `places.json` and a folder in `site/pages`.
- **Sentences come from the data.** Findings on a page are computed from the JSON
  when the page loads. Do not hard-code a figure in prose.
- **Each place is measured in its own measure** (names left off, names removed,
  fall in the roll). Do not rank or add across places.
- **Left off, deleted and fall in the roll are different counts.** Use the words
  the site's "Words we use" section defines, and `scripts/check_writing.py` will
  fail on the ones it can catch.
- **Rates are stored to four decimals.** Pages show one decimal through
  `SIR.d`. Do not round a stored figure to the precision it is shown at.
- **`ac_name` is not a key.** Join constituencies on `ac_number`.
- **Every file a page loads carries `?v=<hash>`**, written by `scripts/stamp.py`.
  A new `fetch` must go through `SIR.json`.
- **Content-Security-Policy:** `script-src` has no `'unsafe-inline'`. Write page
  scripts inline in `site/pages` as before (the build moves them out) and bind
  events with `addEventListener`, never an inline handler.
- **Colours** live in `assets/sir.css` tokens with the dark block written twice.
  `scripts/check_contrast.py` measures them; run it when you touch colour.
- **Every merge to `main` is a production deploy**, and a deploy costs money.
  Batch work and merge once.
- **Publishing is separate from building.** Auto-publishing is locked, so a
  merge builds and nothing goes live until a build is published, once a day at
  20:00 IST, by `tools/publish-locked.py` in the Democracy-by-Design repository,
  which publishes every locked site on the Netlify team. A Claude scheduled task
  starts it at 20:01 IST, because GitHub starts its own scheduled runs hours late.

## Feeds, calendars, embeds and alerts

- `scripts/build_site.py` also writes, through `scripts/build_feeds.py`,
  `feed.xml` (from `data/updates.json`), `calendar.ics` and `calendar/<state>.ics`
  (from `data/india/process.json`, `states.json` and `events.json`),
  `data/index.json` (every published data file) and `_headers`. All are
  committed, deterministic and covered by `--check`. Calendars are CRLF by
  RFC 5545 (`.gitattributes`); read them with `newline=''`.
- **Framing.** Netlify joins the values of a header that two matching rules set,
  so the `/*` block in `netlify.toml` carries no frame rule. `_headers` sends
  `frame-ancestors 'none'` and `X-Frame-Options: DENY` for every published
  folder except `embed/`, which `netlify.toml` opens to any site.
  `check_data.py` fails if either half drifts.
- `/embed/<place>/` pages come from `scripts/make_embed_pages.py`; their shell has
  no header or footer. A state's chart adds its constituency table up by district
  in the measure `assets/seat.js` names, so it never sets one state against another.
- The final-roll alert form (`roll-alert`) is written by `build_site.py` on every
  pending state's overview and on `india/process/`. Nothing sends mail: the owner
  sends each alert by hand. The terms page describes it; keep the two in step.
- "Cite this page" carries the build hash `scripts/stamp.py` writes; the date
  without a script is the latest date in `data/updates.json`.

## Writing

Plain, full sentences with facts in them. No em dashes, no "X, not Y" turns, no
stock vocabulary, no emoji. `scripts/check_writing.py` catches what a pattern can;
read what you write.
