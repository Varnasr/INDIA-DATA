# INDIA-DATA

The SIR analyses hub at forindia.netlify.app: Bihar (2025) and five Old City
constituencies of Hyderabad (2026). Static HTML, Chart.js from cdnjs, one
stylesheet (`assets/sir.css`) and one helper script (`assets/sir.js`) shared by
every page. Netlify deploys the repository root from `main`; `static.yml` also
publishes it to GitHub Pages.

## Commands

```bash
pip install pandas==3.0.6 openpyxl==3.1.5
python3 scripts/build_bihar.py          # rebuild data/bihar from data/bihar/raw
python3 scripts/build_hyderabad.py      # rebuild data/hyderabad from the explorer
python3 scripts/check_data.py           # 11 checks, run by CI; rebuilds both with --check
python3 scripts/check_contrast.py       # assets/sir.css tokens, both themes
python3 -m http.server 8000
```

## Before touching the Bihar numbers

Run `scripts/verify_bihar.py`: it recomputes every headline figure from the raw
files with its own code and fails on any disagreement with the published JSON.
Old working files live in `archive/`, which is never served; do not bring any
of them back into a page.

Things the build depends on, each asserted by `check_data.py`:

- **One row per booth.** The booth file has about three rows per booth (one per
  top-three 2024 party) and the gender-religion file two (one per sex). Any
  join of the two must aggregate first. Totals: 77,837 booths, 6,559,626 phase 1
  deletions in the booth file, 6,910,559 across both phases.
- **2025 margins and votes polled come from `data/bihar/raw/ae2025_results.csv`**
  (winner and runner-up votes and turnout for all 243 seats), not from the
  Wikipedia results table, whose margin column is wrong in seven seats and
  runner-up votes in six more. The margin is winner minus runner-up in every
  row; votes polled are turnout on the 2025 roll. `verify_bihar.py` recomputes
  both.
- **`LABEL_FIXES` in `build_bihar.py`.** Each carries its evidence and a status,
  verified or probable. After the fixes, all 40 seats' top two match the
  declared result within 1 point. A new fix needs evidence, not a plausible
  party.
- **`ac_name` is not a key.** Kalyanpur (16, 131) and Pipra (17, 42) are
  different seats sharing a name. Join on `ac_number`.
- **Minapur (90) is in Vaishali**, not Muzaffarpur, whatever the public table
  says.
- **Caste is not identified.** Two surname classifications give different
  compositions and wide bounds. The pages say so. Do not collapse them into
  one number, and do not reintroduce "Devi" or any title as a caste marker.
- **Religion is a range**, low bound classified names only, high bound adding
  every unclassified name. The census share is inside it in 18 of 38 districts
  and below the low bound in 20.

## Hyderabad

`hyderabad/explorer/index.html` carries the part-level counts inline as
`const D={...}`. `build_hyderabad.py` reads that object and derives
`data/hyderabad/summary.json` and `parts.json`, so the explorer and the analysis
pages cannot disagree. Edit the counts in the explorer, then rebuild.

Malakpet's export has no part numbers and no 2002 linkage: it is read by
polling-station name (60 stations), it has 7,891 electors in none of the three
fates, and it must never be given a linked or unlinked rate. A check enforces
the last point.

## Privacy

Aggregates only. A row-level sample of the Bihar lists exists in the project's
Drive with names and EPIC numbers; it must never be committed or published. A
check fails if any JSON under `data/bihar` carries an EPIC-like field.

## Front end

- **One look on every page: the Bihar dashboard's.** A folk-art band across
  the top (`.band.madhubani` for Bihar, `.band.ikat` for Hyderabad, a
  Pochampally ikat tile drawn as an SVG data URI), a card header with the
  controls, a tab bar, summary cards, key-finding banners and chart cards.
  All of it is in `assets/sir.css`; no page carries its own palette.
- **Two dashboards, many pages.** `index.html` (Bihar) and
  `hyderabad/index.html` are tabbed dashboards built by `assets/dash.js`:
  cards, banners, charts drawn when a tab first opens, PNG export and
  printing. Every other page carries the same header and a tab bar of links,
  written into its markup so it works without JavaScript. Sentences
  are computed from the JSON, including the verdict words: a rank
  correlation under 0.2 is reported as no relationship.
- **The site is "SIR analysis for India"; Bihar and Hyderabad are two
  analyses inside it.** Every page carries the same header: that title, a
  subtitle naming the analysis, a two-way switch (Bihar 2025 / Hyderabad 2026),
  and a Downloads menu with the report in PDF and Word and the slides. The
  header is identical markup on all 15 pages; change it everywhere at once.
- **The tab bar is sticky.** On a wide screen the header sticks and the bar
  sticks beneath it (`sir.js` writes the header's height to `--hh`); on a phone
  the header scrolls away and the bar sticks at the top. The bar fades at
  whichever edge has more tabs, and the active tab is scrolled into view.
  Measured at 390px before this: a 176px header and a 1,451px tab bar showing
  two and a half tabs, gone from the screen after the first scroll.
- **On a phone the tab row becomes a section bar** (`sir.js`, built from the
  tabs, so no page markup changes): "Bihar 2025 › Overview · 1 of 11", arrows
  for the previous and next section (disabled at either end, never wrapping),
  and the full list of sections as a grid behind a tap. It follows a
  dashboard's tab changes through a MutationObserver on `aria-selected`.
  Without JavaScript the scrolling row stays, so nothing depends on it.
- **The part explorer takes a link to a part**: `hyderabad/explorer/#Yakutpura-297`.
- No page states the site's own address.
- Colour tokens live in `assets/sir.css`, with the dark block written twice
  (`prefers-color-scheme` and `[data-theme="dark"]`). `check_contrast.py`
  measures 72 pairs, including the tab bar, the banners and the tags, and fails if the two dark blocks differ.
- `SIR.chart` resolves `$token` colours before Chart.js sees them and disables
  the colours plugin; `SIR.recolour` sets option fields in place on a theme
  change. Replacing an options object wholesale breaks Chart.js's proxies
  (`this._fn is not a function`).
- Every finding sentence on a page is computed from the JSON when the page
  loads. Do not hardcode a figure in prose.
- Audited with axe at 1280 and 390, both schemes, all 15 pages: 0 serious or
  critical. In a sandbox cdnjs is unreachable; stub Chart.js by route or the
  audit sees pages with no charts.

## Languages

English, Hindi, Urdu and Telugu, chosen from the menu in the header and kept
in the address (`?lang=hi`) and in the reader's browser.

- `assets/i18n.js` loads first, in `<head>`: it sets `lang` and `dir` (Urdu is
  right to left), loads the Noto font for the script and the dictionary
  `assets/i18n/<lang>.js`, and defines `L()`.
- **A sentence built by a script** goes through
  `L('English template with {placeholders}', {placeholders: values})`. The
  template is the key. The first argument must be one string literal:
  `check_i18n.py` reads the keys from the source and fails on anything else.
  Write whole sentences, never fragments, and pass values already formatted.
  A page-local variable named `L` hides the function; several pages had one.
- **A row of links** (the switch, the Downloads menu) carries `data-i18n-each`,
  so each link is its own key; without it the whole row, addresses and all,
  becomes one key that differs on every page.
- **Fixed text in the markup** is translated by `L.apply()`, which `sir.js`
  calls before a page's own script runs. The key is an element's inner HTML
  as the browser serialises it, so `scripts/i18n_collect.mjs` reads the keys
  with a browser and writes `i18n/catalogue.json`. Re-run it after changing
  any text, then translate the new keys; CI fails until every key in every
  language is translated with its placeholders and links intact.
- Figures stay in Western digits with Indian grouping. Names that arrive from
  the data (constituencies, localities, parties, the Commission's reason and
  rule codes) stay as the data spells them.
- **The menu is off until the translations are signed off.** `MENU` in
  `assets/i18n.js` is `false`, so a language is reached only by a link with
  `?lang=hi|ur|te`, and a translated page carries a notice that the English
  page governs. `scripts/i18n_workbook.py` writes the review workbook; fold the
  reviewer's corrections into `assets/i18n/<lang>.js`, then set `MENU = true`.

## Reports

`reports/` holds the two full reports, PDF and Word, linked from every page's
header ("Full report") and from each dashboard. `scripts/reports/build.sh`
rebuilds them from the published JSON: python-docx writes the Word file, the
same builder writes print-ready HTML, and headless Chromium prints that to PDF
(LibreOffice is not needed). They follow the Sabar Institute's structure: Part
I for the whole area, Part II a chapter per district or constituency, one
section on what the lists show and do not, and what an audit needs. Rebuild
them after any data change; nothing checks that they are current.

Beside them are two slide decks, `*-deck.pptx`, written by
`scripts/reports/decks.js` (pptxgenjs) from the same JSON and linked as
"Slides" from each dashboard's report card. Every figure and every verdict in
them is computed, including the slide titles that make a claim (the Hyderabad
margin slide checks that every seat lost more names than its winner polled
before saying so). The decks state no site address, and the speaker notes
carry the caveats. `build.sh` rebuilds them with the reports.

## Watch out for

- **Publishing**: the site serves only pages and aggregate JSON. `_redirects`
  answers 404 for raw files, scripts, notes and `archive/`; `static.yml` stages
  the same set for Pages. Do not link source files from a page, and describe
  sources without naming the people or organisations who compiled them.
- **Writing**: plain explanatory prose. Never refer to earlier versions of the
  analysis or to corrections on a public page.
- **Framing**: the pages make an accountability case. They lead with the scale
  of the removals, the removals against winning margins, women's
  over-representation and, in Hyderabad, the process (the 2002 link, hearing
  loads), and end with what an audit needs. The alliance comparisons stay on
  the Elections page and in the FAQ, stated plainly: the lists show more
  removals on NDA ground, and no page may say otherwise. The lists cannot show
  intent, and no page may claim they do.
- `pandas` and `openpyxl` are pinned in CI because a reader change could move
  the numbers without an error.
