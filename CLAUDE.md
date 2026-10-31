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
pip install -r requirements.txt
python3 scripts/check_data.py           # data checks, run by CI; rebuilds the data files with --check
python3 scripts/check_contrast.py       # assets/sir.css tokens, both themes
python3 scripts/build_site.py           # every page, from site/places.json and site/pages; --check in CI
python3 scripts/build_i18n.py           # translation pieces, from i18n/<lang>.json; after build_site, before stamp
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
- **Translations live in `i18n/<lang>.json`.** Pages never load them whole:
  `scripts/build_i18n.py` splits each into a core, a file per shared script
  with sentences, and a file per page group, and `check_i18n.py` fails if a
  page shows a string that none of its files holds.
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

## "What to do now" pages

Each state still in the revision has a page at `<state>/now/` (Telangana's is
`hyderabad/telangana/now/`). The states are `PAGES` in `scripts/build_now.py`;
`scripts/make_now_pages.py` writes their sources from one template, and
`build_now.py` writes `data/india/now.json`, the sources each step cites (by
key into help.json, process.json's forms and timeline, and the disputes) and
each state's extras. `assets/now.js` decides the stage in the browser with
`SIR.owin.stage`, the claims box's own code, so the page changes with the date.
A step says only what its cited document says, and a step with no source is
left out. A new state is a row in `PAGES`, a tab in `places.json`, a run of
both scripts, then the usual build and translations. `check_data.py` fails on a
state with no schedule, a cited key that does not resolve, or a page that does
not link back to its overview.

## Final-roll day

`python3 scripts/add_final.py --due` lists every state whose final roll is not
recorded and the date it is due, from `data/india/process.json` (the latest
schedule step, or a later date reported in the press). `check_data.py` fails
once a due date is more than two days past (`FINAL_GRACE_DAYS`, since CEOs
often publish late or the next day) if the roll is not recorded and the state
is not in `FINAL_PENDING` there with a reason that starts with its date.
`FINAL_CHECK_DAY=YYYY-MM-DD` fakes the day for both scripts, to rehearse.

Where each state's Chief Electoral Officer has published before, as the
repository cites it. Look for the final-roll press note first, then the
office's account on X, then the press.

- Maharashtra: ceoelection.maharashtra.gov.in, Downloads, PDF, Notification (English and Marathi notes).
- Haryana: ceoharyana.gov.in, and the state's releases at prms.prharyana.gov.in.
- Andhra Pradesh: x.com/CEOAndhra, and the Commission's documents on eci.gov.in.
- Telangana: x.com/CEO_Telangana. Telangana Today has carried its schedules.
- Nagaland: ceo.nagaland.gov.in, media/sir2026.
- Jharkhand: no CEO site is cited here. The draft came through ETV Bharat and
  The Hindu, and the date of 30 November through Town Post quoting the CEO.
- Delhi: ceodelhi.gov.in, PDFFolders/2026, and x.com/CeodelhiOffice.
- The Commission's schedules are on pib.gov.in.

Read in the note: the final roll of general electors, and service electors
apart from it; men, women and third gender; the names added and deleted after
the draft, by form; any names withheld; and the draft as the note prints it,
which must agree with ours within half a per cent.

Then write the figures to a small JSON file (the keys are in the docstring of
`scripts/add_final.py`) and run, with `PLAYWRIGHT_CORE` set:

```bash
python3 scripts/add_final.py --json mh.json --dry-run   # refusals, warnings and the diff
python3 scripts/add_final.py --json mh.json             # write, rebuild, run every check
```

It refuses a final roll at or below zero, dated before the draft or after
today, whose sexes do not add to it, whose draft plus additions less
deletions misses it (exactly for `exact`, within 0.1 per cent for `rounded`),
or whose source puts the draft more than half a per cent from ours. Use `net`
or `no` with a note otherwise, and leave `electors_draft` out if the source
counts its draft on another footing. Five states in one day are five runs,
one after another, each rebuilding everything (about two minutes each). It warns when the source is not an
official site or a CEO's account. It writes `data/india/raw/final.csv`, the
state's `normal.json` (shared page) or `raw/final.json` (Maharashtra, Delhi,
Telangana, Karnataka), and a published step in `process.json`. The pages of
Maharashtra, Delhi and Telangana switch from "due on" to "published on" by
themselves. It leaves to a person, and prints with drafts: the What's New line
(`data/updates.json`), `SOURCES.md`, a corrections entry if a recorded figure
changed, the front-page card, process.json's prose and the claims dates of
the new schedule step, and the reading-page panel sentences.

The panels are the step that breaks. `data/india/raw/panels_research/plain.json`
quotes, in its own sentences, national figures from `data/india/states.json`
that every final roll moves: the number of states with a final roll (24 on
30 October), the states with a draft and none ("Seven states", "Eight states"
in words), `final.removed` and `final.per_100` (8,87,25,044 and 12.42),
`final.net_after_draft` (1,22,10,672), `final.made_up_pct` (13.8), and
`after_draft.removed` and `after_draft.states` (35,62,366 in 22 states). They
sit in s-y-quraishi claims 3 and 7, p-chidambaram claims 4 and 5,
jean-dreze-yogendra-yadav claim 3, jean-dreze claim 0 and abhijeet-dipke
claim 0. `check_data.py` fails on only some of them, through each claim's
`uses` list. 13.8 still matches another figure in states.json after it has
moved, and the counts of states and abhijeet-dipke's figures are in no `uses`
list at all, so a green run does not mean they are current. `add_final.py`
prints every such sentence with the figures before and after the run. Rewrite
each sentence, change its `uses` value (raw digits, as in states.json) and run
`python3 scripts/build_panels.py`.

Commit the sources only, open the pull request and merge once for the day's
states. Nothing goes live until the 20:00 IST publish. When the owner says
"publish", run the "Publish locked sites" workflow in Democracy-by-Design for
this site.

## Writing

Plain, full sentences with facts in them. No em dashes, no "X, not Y" turns, no
stock vocabulary, no emoji. `scripts/check_writing.py` catches what a pattern can;
read what you write.
