# INDIA-DATA

The SIR analyses hub at offtheroll.in: All India (the reasons for
removal, state by state), Bihar (2025), five Old City constituencies of
Hyderabad (2026), Tamil Nadu, Karnataka, West Bengal and Kerala (2026). Static HTML, Chart.js from cdnjs, one
stylesheet (`assets/sir.css`) and one helper script (`assets/sir.js`) shared by
every page. Netlify deploys the repository root from `main` to offtheroll.in
(Netlify DNS; the domain is registered at Porkbun with Netlify's nameservers,
and forindia.netlify.app redirects to it); `static.yml` also publishes it to
GitHub Pages.

## Commands

```bash
pip install pandas==3.0.6 openpyxl==3.1.5
python3 scripts/build_bihar.py          # rebuild data/bihar from data/bihar/raw
python3 scripts/build_hyderabad.py      # rebuild data/hyderabad from the explorer
python3 scripts/check_data.py           # 20 checks, run by CI; rebuilds both with --check
python3 scripts/check_contrast.py       # assets/sir.css tokens, both themes
python3 scripts/build_site.py          # every page, from site/places.json and site/pages; --check in CI
python3 scripts/stamp.py               # cache busting; Netlify and Pages run it on every deploy
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
- **Women are compared with the roll, not the census.** `female_share_roll`
  in `identity.json` (by district) and `summary.json` (state) is women's share
  of the roll before the revision: the Format 4B draft roll by sex plus the
  phase 1 removals by sex. Women are over-represented among the removed in all
  38 districts, by 2.8 to 13.7 points. Religion stays on Census 2011, the last
  count by religion at district level, and the pages say so. Beside it,
  `muslim_share_projected_2025` carries each district forward 14 years at its
  2001-2011 Muslim and total growth rates (`data/bihar/raw/census_religion_2001_2011.csv`;
  Jehanabad and Arwal share their 2001 unit). The state comes to 17.34% against
  17.70% in the 2023 caste survey; the same eight districts stay more than a
  point above either way. District literacy and early marriage come from NFHS-5
  (`data/bihar/raw/nfhs5_districts.csv`, fact-sheet definitions, Bihar fielded
  2019-20); only density and urban share are still Census 2011.
- **Caste is not identified.** Two surname classifications give different
  compositions and wide bounds. The pages say so. Do not collapse them into
  one number, and do not reintroduce "Devi" or any title as a caste marker.
- **Religion is a range**, low bound classified names only, high bound adding
  every unclassified name. The census share is inside it in 18 of 38 districts
  and below the low bound in 20.
- **Reasons come from the row-level phase 1 list, as counts.**
  `scripts/aggregate_bihar_reasons.py` reads that list on stdin and writes
  only `data/bihar/raw/reasons_by_ac.csv.gz` (seat, reason, sex, age band) and
  `reasons_by_booth.csv.gz` (seat, booth, reason, sex). The reason cell
  sometimes carries a stray line of text after the reason; only the text
  before the first newline is read. Four reasons, counted as entered: dead,
  shifted, absent, already enrolled. They total 65,59,626, agree with the
  booth file in every booth and with the official women and men in every
  seat (the 217 third-gender entries are the difference). Phase 2 has no
  reasons. Never commit the list itself or its download link.
- **A reason is an officer's entry, not a finding.** Pages say so wherever a
  reason is quoted. "Absent" rests on the least and is where checking starts.

## All India

`data/india/raw/states.csv` is curated by hand, one row per state or union
territory: the draft-roll removals and their reasons as each Chief Electoral
Officer published them, with a flag for rounded figures, a flag for how
complete the split is, and a source link. `scripts/build_india.py` writes
`data/india/states.json` and the downloadable `data/india/states.csv`, and
fails if a "complete" split misses its total by more than 0.5% or a "short"
one does not fall short. Bihar's row is the lists' own count, and a check
holds it equal to `data/bihar/reasons.json`. Reasons are folded into the three
every state reported: dead; shifted, absent or other; enrolled more than once.
Removals after the draft carry no reason anywhere and are kept apart. When a
state publishes a final roll or a primary press note, update its row and its
flags, not the totals.

Two more curated files feed the same build. `data/india/raw/covariates.csv`
holds each state's 2011 characteristics, RBI income per head 2023-24 and Home
Ministry borders; `data/india/raw/benchmarks_recent.csv` holds the post-2011
replacements (`PICK` in `build_india.py`): literacy from PLFS 2023-24, spending
from HCES 2023-24, the urban share projected to 1 March 2026, and Muslim, SC, ST
shares and the sex ratio from NFHS-5. NFHS shares are of households, a little
below shares of people. Migration has no state figure after 2011 and stays on
the census. `robustness_2011` reruns the correlations on the 2011 values and
the method page reports which readings change; `build_india.py` computes
rank correlations with the removal rate and the reason shares, for all states,
by phase and for states of 50 lakh or more. **Report the phase split with
every pooled figure**: the pooled correlations with in-migration, income and
the Muslim share come entirely from phase 3, where destination states and the
North-East differ on all of them at once, and none holds in phase 2.
`data/india/raw/gender.csv` has the ten states with a split by sex, each
flagged exact, rounded, earlier roll or unverified; add a state only with its
source, and keep Tamil Nadu flagged until a primary figure turns up.
`data/india/raw/adults_ls2024.csv` holds the projected population aged 18+
(1 March 2026, 19 states; the North-East and small UTs have none) and the 2024
Lok Sabha electors and votes by state. The rolls before the revision held 98.3%
of projected adults across those 19 states; the drafts hold 84.4%. Keep the
caveat with it: projections count residents, so migrant-receiving states
count adults registered at home.

`data/india/raw/final.csv` holds each final roll: draft, added and removed
after it, names withheld (West Bengal's 60 lakh under adjudication), final,
and whether the figures add up. It is the only source for removals after the
draft. **Several states reported the net rise from draft to final as
"additions"** (Gujarat, Madhya Pradesh, Chhattisgarh, Uttar Pradesh): leave
their gross columns blank and mark them `net only`. The share "made up" is the
net rise over the draft removals; it counts new electors too, so it is an upper
bound on names put back, and every page says so.

**How the SIR was run** (`india/process/`) is the rules and dates of the
revision, from `data/india/process.json`: a timeline of every order, letter,
Supreme Court order and judgment that changed the process, and each state's
schedule drawn as set and as moved (`VIZ.gantt`). Every entry links to the
document it comes from, and **every section but one rests on primary
documents**: Election Commission orders and releases, Chief Electoral
Officers' notes, Supreme Court orders and judgments. Beside the timeline the
page carries "What made it harder to stay on the roll" (`burdens`, each point
with its document), "Form 6, Form 7 and the declaration" (`forms`, and a table
of claims and objections after the draft read from `states.json`), and the
one section that is not primary, "Reported, not confirmed by a document"
(`reported`): press reports from named outlets, each reopened and checked,
attributed to the outlet, with the response it reported. Nothing moves from
that list into the other sections without its document, and no section calls
the revision suppression or claims intent. The research and an independent check of every row,
with the quoted evidence, are in `data/india/raw/process_research/`
(`process.json`, `verified.json`, and for the forms and the reports
`forms_primary.json`, `forms_primary_verified.json`, `reported.json`,
`reported_verified.json`); a row the check could not confirm is left
off the page and named under "What we could not verify". Add an entry only
with its document read, and a press report only to the reported list. The page and the chart are
English only, like the full reports, because the legal detail is not machine
translated. A line drawn from what a state actually published carries
`kind: "published"` and is not counted as a schedule change.
It is reached from the front page (its own section), the places menu (a
`menu` entry under All India in `places.json`), and a line on every state
page and on the Bihar and Hyderabad method pages. `#s-<state>` (lower case,
hyphens: `#s-tamil-nadu`) outlines that state's row and scrolls to its chart;
`#t-<date>` opens on a timeline entry.

`data/bihar/raw/final_roll_format4b.csv` is the Commission's Format 4B return
for Bihar's final roll, seat by seat and by sex; `scripts/build_bihar_final.py`
writes `data/bihar/final.json` and fails unless every seat adds up and the
totals equal the press note of 30 September 2025. A seat's roll before is its
draft plus its phase 1 list, because the June roll exists only as a state
total. Findings: the net fall still exceeds the 2025 margin in 124 of 243
seats (174 on the draft removals); women were 55.5% of those removed at the
draft and 47.9% of those added.

`scripts/build_bihar_tests.py` sets two reasons against outside records and
writes `data/bihar/tests.json`. Deaths: SRS 2024 death rates by age and sex,
weighted by the 2024 population by age, ages 20 and over (the rates come in
five-year groups), against the names entered as dead: about 3.4 years of adult
deaths, the right ages, but 52.0% women against 43.4% of deaths. Marriage:
Census 2011 D-3, women who moved on marriage in the ten years to 2011, against
the excess of young women marked shifted: about half a year's marriage moves,
but the district pattern runs the other way (rank correlation -0.51). D-3
counts women where they arrived; district out-migration is not published.
Raw tables are in `data/bihar/raw/srs_bihar.csv`, `crs_bihar.csv` and
`census2011_marriage_migration.csv`, each row with its table and page.

`scripts/build_impact.py` asks whether the removals could have changed a
result and writes `data/bihar/impact.json` and `data/hyderabad/impact.json`.
Bihar gets three estimates and a break-even figure, each on a low count (net
fall to the final roll) and a high count (every name removed), less the dead,
at 2025 turnout: removed electors voting like their own booth in 2024, or like
their religion or sex in the Axis My India exit poll (NDTV, 12 November 2025).
Seats where the winner or runner-up is outside the two alliances get the
break-even figure only, because both sources lump every other party together.
Findings: in 187 of 243 seats the runner-up could not have won with every
removed voter; the removed lean NDA (49.0% against 37.8%) on the booth
estimate; 4 to 6 seats change hands, both ways; the NDA keeps 200 to 204.
**Do not present the removals as having won Bihar for the NDA**: the lists
point the other way. Hyderabad gets break-even against 2023 and the religion
of the removed only; its runner-ups (Yakutpura's MBT) draw on the same voters
as AIMIM, so no split by religion is assumed.

`scripts/build_swing.py` sets each seat's change in vote share from 2020 to
2025 against its removals per 100 electors and writes `data/bihar/swing.json`.
Its input, `data/bihar/raw/ae_party_votes_2020_2025.csv`, is the Election
Commission's Detailed Results (statistical report 10) for each election,
pooled by party, with NOTA and electors, for every seat; the build asserts the
2025 figures equal the declared result. ECI's party codes are kept except
where a label was needed (VSIP is VIP, RSHTLKM is RLM, LJPRV is LJP(RV)).
In 2025 BLSP is a different party from the 2020 RLSP; do not merge them.
Both years use the 2025 line-up (LJP and RLSP count as NDA in 2020, VIP as
INDIA). The model is within district **and allows for each seat's 2020
NDA lead**, because seats the NDA won big in 2020 gave some of it back
whatever their removals (coefficient about -0.9). Leaving that out is how the
first version went wrong: without it the slope is -0.83 (-1.86 to +0.20) and
looked like evidence against an anti-NDA effect; with it the slope is +0.31
(-0.27 to +0.89), which takes in both no effect and the +0.33 to +0.66 an
anti-NDA pattern would give. Allowing for 2020, the NDA's lead grew 4.0 to 5.2
points in every third of seats by removals. **Say what this is**: the vote
cannot tell whether the removals moved votes between the alliances, and that
question is separate from whether the removals were accurate. Never present
it as the revision being clean, and never lead with the model that omits 2020.
2020 margins come from `data/bihar/raw/ae2020_results.csv`, taken from the
same ECI report: the booth file's differ in eight seats (Gaighat 22,927
against 7,566) and its percentages are rounded to whole points.

`scripts/build_robust.py` puts each headline Bihar finding through the
checks that could undo it (Simpson's paradox included) and writes
`data/bihar/robust.json`, shown as "How sure are we?" on the Elections page,
in the report and in the deck. Results: removals exceed the margin on the
draft count (174) and on the final roll (124); women are over-represented in
38 of 38 districts and 242 of 243 seats; more removals on NDA ground holds
inside seats (NDA-led booths higher in 150 of 237) but between seats in the
same district the gap (+0.46 per 100, -0.17 to +1.10) is too small to be sure
of; the swing changes sign with the comparison. Say exactly that.

## Hyderabad

`site/pages/hyderabad/explorer/index.html` carries the part-level counts inline as
`const D={...}`. `build_hyderabad.py` reads that object and derives
`data/hyderabad/summary.json` and `parts.json`, so the explorer and the analysis
pages cannot disagree. Edit the counts in that source, then run
`build_hyderabad.py` and `build_site.py`.

**Why five seats.** The elector-by-elector lists were compiled for these five
only. The Chief Electoral Officer, Telangana publishes the ASDD and notice
lists per part as PDFs behind a captcha, from Indian networks only, in Telugu;
the pre-revision roll with ages is not public. The other ten Hyderabad seats
(2,670 parts) therefore appear as the state's totals on the Telangana page.
Say this plainly wherever the five are introduced; do not name who compiled
the lists.

Malakpet's export has no part numbers and no 2002 linkage: it is read by
polling-station name (60 stations), it has 7,891 electors in none of the three
fates, and it must never be given a linked or unlinked rate. A check enforces
the last point.

`data/hyderabad/raw/telangana_districts.csv` and `hyderabad_district_acs.csv`
are the state's draft-roll totals for all 33 districts and Hyderabad
district's 15 seats; `scripts/build_telangana.py` writes
`data/hyderabad/telangana.json` for the `hyderabad/telangana/` page and checks
that the districts add to the state, the seats to the district, and that
Charminar and Yakutpura equal the lists exactly. The finding it carries: the
Old City seats (39.9%) removed no more than Hyderabad's other ten (41.6%);
the removals follow the capital region. Totals only; do not bring in a
per-seat split by reason that is not the state's own.

## Tamil Nadu

`scripts/build_tamilnadu.py` reads `data/tamilnadu/raw` (each file's source
and checks are in `SOURCES.md` there) and writes `summary.json`,
`constituencies.json`, `districts.json` and the two CSVs; `check_data.py` runs
it with `--check`. Every table is the Chief Electoral Officer's or the
Election Commission's own, constituency by constituency, and the build fails
unless each adds up to the published totals (9,737,831 removed; draft
54,376,756; final 56,707,380).

- **The roll before the revision is the draft plus the names removed.** No
  constituency table of the 27 October 2025 roll is published, and the sum
  equals the state total announced with the draft.
- **There is no split of the removals by sex or age.** The CEO has not
  published one. The All India gender table carries a Tamil Nadu row from a
  press analysis, flagged unverified; do not move it onto the Tamil Nadu pages
  as a finding.
- **Turnout is votes over the final roll of 23 February**, because the 2026
  result pages carry no electors. The roll of 7 April 2026 is published and
  not yet used.
- **Removals by the party that won are read against the district.** TVK won
  most of the city seats and the city seats lost the most names, so the raw
  comparison mostly measures Chennai. `vs_district` is each seat's rate less
  its district's; report it beside the raw figure, never instead of it.
- **2021 is from a compilation of the ECI statistical report** whose seat
  totals equal the declared result. The page says "the Election Commission's
  statistical report, through a published compilation of it" and does not
  name the compiler.

## Karnataka

`scripts/build_karnataka.py` reads `data/karnataka/raw` (sources and checks in
`SOURCES.md` there; `check_raw.py` asserts them) and writes `summary.json`,
`districts.json` and `districts.csv`; `check_data.py` runs it with `--check`.
The build fails unless the 34 districts add up to the CEO's state row
(10,796,339 removed of 55,432,314) and the roll of 25 September to 44,844,080.

- **Districts only.** The CEO published the revision by its 34 election
  districts and none of it by assembly constituency, so there is no seat page
  and no comparison with the 2023 margins. `results_2023*.csv` in `raw` is
  TCPD's compilation, not primary, and no page uses it.
- **Bengaluru is four districts**: Bangalore Urban and B.B.M.P North, Central
  and South. Bangalore Rural is not part of it.
- **The latest roll is 25 September 2026**, published while notices were being
  heard; the final roll is due 27 October. The rise from the draft counts new
  voters too, so call it the most that could have been restored. Rebuild from
  the final roll when it is out, by district and sex.
- **No split of the removals by sex.** The roll of 16 June is published as a
  total only. The All India gender row for Karnataka comes from a newspaper;
  do not move it onto the Karnataka pages as a finding.

## West Bengal

`scripts/build_westbengal.py` reads `data/westbengal/raw` and writes
`summary.json`, `constituencies.json`, `districts.json` and the two CSVs.

- **No removals below the state.** The CEO's press note PN-05-2026 gives the
  removals by reason, the claims and objections and the 60,06,675 held for
  adjudication, all for the state; the build asserts they add up step by step.
  Below that the pages measure **the fall in the roll** from the 2024 Lok Sabha
  roll to the draft and to the roll at the 2026 nominations, by AC and sex.
  It takes in 18 months of ordinary changes, so never call it the removals.
  The 2024 roll is 6.3 lakh smaller than the October 2025 roll, so the fall
  understates the fall from the roll the revision started from.
- **The 2024 table is read from merged cells.** Three Jhargram PC rows were
  once read against the wrong segment (see `SOURCES.md`). The build fails if
  an AC's polling stations differ from the draft's by more than 50 or its
  draft exceeds its 2024 roll by more than 2%.
- The gap between the draft fall and the election-roll fall is where the
  adjudication cuts show, largest in Murshidabad, Malda and the Dinajpurs;
  say it is the nearest the tables come, not a count.
- **Adjudication outcomes are state totals, as reported.**
  `raw/adjudication_state.csv` holds the Commission's split (32,68,119 found
  eligible, 27,16,393 not) and its 16 September affidavit's appeals (22,21,118
  by the excluded, 16,10,311 against inclusion, 37,05,235 pending) as the press
  reported them, flagged `reported`; 22,163 cases are not accounted for and are
  shown as such. Say "as reported" wherever they appear. Religion splits of the
  adjudicated from press analyses are not used.
- `results_2021.csv` is secondary and no page uses it. Compilations of AC
  removals by others are recorded in `SOURCES.md` and not used.

## Kerala

`scripts/build_kerala.py` reads four rolls by AC and sex from
`data/kerala/raw` (January 2025 summary-revision final roll, SIR draft of
23.12.2025, SIR final of 21.02.2026, roll of 23.03.2026) and the 2026 result.
No table of the names left off has been published, even for the state; the
pages measure the fall from January 2025, which statewide is 23.69 lakh
against the 24.09 lakh reported with the draft. The rise after the draft counts
new voters (and overseas electors, which nearly tripled), so it is never
called names restored; five northern districts end above their January roll.
Party comparisons are by party (INC, CPI(M), IUML, others), not by front,
because the independents' fronts are not in the data.

## One order on the four 2026 state pages

Tamil Nadu, Karnataka, West Bengal and Kerala follow one order, with the same
headings: find a constituency or district (with the map); the roll, step by
step; West Bengal's adjudication; per 100 electors, by district; the reasons
(where published); the city (Chennai, Bengaluru); women; after the draft;
every district; every constituency. A section a state cannot have says why
rather than being left out silently: Tamil Nadu and Karnataka have no split
of the removals by sex, so their women sections show what can be counted
(Tamil Nadu, women's share of the net rise after the draft; Karnataka, the
share of each roll) and say the rest cannot be. Method pages carry, for each
state, the map, the checks the build makes, and, where the elections page
uses it, the comparison against the district.

## Charts

`assets/viz.js` draws every non-Chart.js chart: sankey, waterfall, strip
(beeswarm), dumbbell, forest, lollipop, rank, dots, heat, and the three added
for the state pages, `multiples` (small multiples of a path, one shared scale),
`slope` (two columns, highlighted rows named on the right, nudged apart) and
`scatter` (SVG, optional y = x line over the shared range). Vary the form
within a page; a page of one chart type reads as a table.

`map` draws a choropleth from `data/geo/<state>.json` (DataMeet's assembly
map, CC BY 2.5 India; see `SOURCES.md` there): five quantile bins of one red,
a `<title>` per shape, a click handed to `o.pick`, `__select` taking one id or
several, and an optional enlarged city panel (`o.inset`: Chennai, Kolkata,
Bengaluru city). Every page that draws one credits DataMeet under it.
The front page carries an all-India state map from `data/geo/india.json`
(DataMeet, CC BY 4.0, India's official outline), shaded from
`data/india/states.json`; a state with its own analysis opens it on a tap.
Keep the official outline on any map of India here. Karnataka's map is by
election district: its constituencies are dissolved by
the Election Commission's own constituency-to-district list
(`data/karnataka/raw/ac_district.csv`).

Every viz chart keeps its rows on `box.__csv`. `SIR.tools()`, called from
`SIR.showFaq`, puts a row under every chart panel with an id: PNG, CSV, a
WhatsApp link carrying the panel's finding sentence and the page address with
the chart's `#id`, and Copy link. Chart.js charts get the same row, read from
their own data.

`SIR.finder` is the "Find a constituency or district" box on the Bihar
results, Tamil Nadu, West Bengal, Kerala and Karnataka (district only) pages.
`o.more` adds the district set: a district card sums or reads the district
row, lists its constituencies as buttons (`SIR.goList`), outlines all its
seats on the map, and opens from `#d-<slug>` (`SIR.slug`). Picking a seat
writes a card of its figures, puts `#ac-<n>` (`#d-<slug>` in Karnataka) in the
address so the link opens on that seat, highlights it on the map, and offers
WhatsApp, Copy link and Copy text. The share text is one `L()` template per
page, written as plain sentences that say where the counts come from and, for
West Bengal and Kerala, that the fall in the roll is a different count from the names
struck off. Keep that sentence in it.

**Search.** The header's Search button, Ctrl or Command and K, or "/" opens
one box for the whole site (the end of `sir.js`). It reads
`data/search.json`, which `build_site.py` writes on every build: every page
in `places.json`, every constituency and district a finder opens, and the
five Hyderabad seats in the part explorer. A result on the current page sets
the hash and the finder follows it; anything else navigates, keeping
`?lang=`. Add a place's finder and its rows join the search with one line in
`search_index()`.

**Dyslexia-friendly font.** `assets/dyslexia-font.js` is the same drop-in
script the other sites use (OpenDyslexic, OFL, in `fonts/`), loaded on every
page by the shell, its button placed before the theme toggle through
`data-dyslexia-slot` on `.controls`. OpenDyslexic has Latin glyphs only, so
`sir.css` keeps each Indian script in its own Noto face when it is on.

**Installs as an app.** `manifest.webmanifest`, the icons in `assets/app`
(written by `scripts/app_icons.mjs` from the favicon's mark) and `sw.js` at
the root. The service worker goes to the network first for every same-origin
GET and keeps a copy for offline, so a reader online never sees a stale page;
PDF, slides and CSV are not kept, and Chart.js from cdnjs is not either, so
Chart.js charts do not draw offline. Bump `CACHE` in `sw.js` only to throw
the stored copies away. The header's Install app button stays hidden until
the browser fires `beforeinstallprompt` (Android Chrome, Edge, Samsung
Internet). Keep `sw.js` out of `stamp.py`: its address must not change.

**Link previews.** `build_site.py` writes Open Graph and Twitter tags into
every page head, with `og:image` pointing at `assets/og/<place>.png`. The head
is the one place the site's own address appears (`url` in `places.json`),
because previews need absolute addresses. The cards carry each place's
headline figure and are written by `scripts/og_cards.mjs` from the published
JSON (same `PLAYWRIGHT_CORE` and `CHROME` as `i18n_collect.mjs`). **Re-run it
after any data change**; nothing checks that a card is current.

## Privacy

Aggregates only. A row-level sample of the Bihar lists exists in the project's
Drive with names and EPIC numbers; it must never be committed or published.
The same goes for the full phase 1 list behind the reason counts. A
check fails if any JSON under `data/bihar` carries an EPIC-like field.

## Front end

- **Never edit a page's `index.html` directly.** Every page is written by
  `scripts/build_site.py` from two things. `site/places.json` lists the
  places (the front page, All India, Bihar, Hyderabad) with each one's
  subtitle, folk-art band, tab row and Downloads menu. `site/pages/<path>/index.html`
  holds a page's own content: a first line `<!--page {json} -->` with its
  title, description and place (plus `own_tabs` for a dashboard, `head` for
  extra head markup), the content, then `<!--scripts-->` and its scripts.
  The build puts the shared shell round it (head, band, header, places menu,
  tab row, footer) and writes the section bar's lists into `assets/sir.js`
  between `/*sites*/` markers. CI runs `--check`. **A new state or city is an
  entry in `places.json` and a folder in `site/pages`**; nothing is copied
  from another page. `scripts/reports/web.py` writes the report pages'
  sources and runs the build; `build_hyderabad.py` reads the part counts from
  the explorer's source.
- **Addresses.** `/` is the front page: what the site is, why it exists, how
  to read it, who made it. `/bihar/` is the Bihar dashboard and
  `/bihar/explorer/` the booth explorer, matching `/hyderabad/` and
  `/hyderabad/explorer/`. Old links forward in the page scripts: a Bihar tab
  hash on `/` goes to `/bihar/#tab`, and `/bihar/#acNNN` to the explorer.
- **One centred column per page.** `--page` in `sir.css` is 1160px for reading
  pages and 1480px (`body.wide`, set by the build for dashboards and
  explorers); the header, the tab row's links and the content share its
  edges. Do not set a wider `max-width` on a block inside `main`: text capped
  at a reading measure beside a full-width chart is what left wide screens
  half empty.
- **The header carries a places menu**, not a switch: a pin button naming
  the current place, opening the list of analyses. It scales to any number
  of places. On a phone the title takes one row and the controls a row
  beneath it (language, install, search, places, downloads, reading font,
  theme; print is hidden there): beside the title, seven controls squeezed
  it to a single word. Credit is to PinPoint
  Ventures, in the footer and on the front page.
- **Footer, terms and privacy.** Every page's footer carries the credit, About
  this site, Terms and privacy (`terms/`, its own page in `site/pages`, on the
  front page's place) and the contact address (`email` in `places.json`).
  `terms/` says who publishes, what the figures are, how to ask for a
  correction (acknowledged in 24 hours, answered in 15 days), the licences
  (analysis CC BY 4.0, code MIT, DataMeet's and the fonts' own), and exactly
  what the site records. Keep it true: if the site starts loading anything
  new from another service, or counting anything new, the privacy section
  changes in the same commit.
- **Anonymous counts.** The end of `sir.js` adds one to a daily tally per
  page view, share, download, install and search destination, through
  `offtheroll_track()` in the Democracy by Design Supabase project (Mumbai);
  `supabase/migrations` holds the SQL. Nothing else is sent, nothing is
  counted on localhost or deploy previews, and Do Not Track or Global Privacy
  Control turns it off. The table is closed to the public key; read it in the
  Supabase SQL editor.

- **One look on every page: the Bihar dashboard's.** A folk-art band across
  the top (`.band.madhubani` for Bihar, `.band.ikat` for Hyderabad, a
  Pochampally ikat tile drawn as an SVG data URI), a card header with the
  controls, a tab bar, summary cards, key-finding banners and chart cards.
  All of it is in `assets/sir.css`; no page carries its own palette.
- **Two dashboards, many pages.** `bihar/index.html` and
  `hyderabad/index.html` are tabbed dashboards built by `assets/dash.js`:
  cards, banners, charts drawn when a tab first opens, PNG export and
  printing. Every other page carries the same header and a tab bar of links,
  written into its markup so it works without JavaScript. Sentences
  are computed from the JSON, including the verdict words: a rank
  correlation under 0.2 is reported as no relationship.
- **The site is "SIR analysis for India"; each place is an analysis inside
  it.** Every page carries the same header: that title, a subtitle naming the
  place, the places menu, and a Downloads menu with the report online, the
  PDF and the slides. It is written once, in `scripts/build_site.py`.
- **The tab bar is sticky.** On a wide screen the header sticks and the bar
  sticks beneath it (`sir.js` writes the header's height to `--hh`); on a phone
  the header scrolls away and the bar sticks at the top. The bar fades at
  whichever edge has more tabs, and the active tab is scrolled into view.
  Measured at 390px before this: a 176px header and a 1,451px tab bar showing
  two and a half tabs, gone from the screen after the first scroll.
- **On a phone the tab row becomes a section bar** (`sir.js`, built from the
  tabs, so no page markup changes): "Bihar 2025 › Overview · 1 of 11", arrows
  for the previous and next section (disabled at either end, never wrapping),
  and a menu behind a tap with two headings: the dashboard's tabs and the
  analysis's other pages. The arrows and count run over the list the reader
  is in. The tabs and pages, with icons, are one map in `sir.js` (`SITES`),
  written from `site/places.json` by the build; add a page there only. It follows a
  dashboard's tab changes through a MutationObserver on `aria-selected`.
  Without JavaScript the scrolling row stays, so nothing depends on it.
- **Every page but the full reports opens with 3 to 6 numbered findings and
  ends with its own questions.** The findings are a plain list (`ol.summary`)
  straight under the heading, with no banner and no caveats: they say what the
  data shows. Each page's limits go in one line at the foot (`#shortNote`,
  `.note.limits`), before its questions, and in full on the method page. Do
  not put a second intro paragraph or banner above the content. Inside a
  page, a run of `.finding` banners shows only the first as a banner and the
  rest as plain text, and `.caveat` is a quiet note; `sir.css` does both, so
  write the markup as before. The findings, the limits line and the questions
  come from one file per analysis, `assets/faq/bihar.js`, `hyd.js` and
  `india.js`: it loads the data once and returns `{qa, short}`, where each
  question carries the page keys it belongs to (`dash`, `explorer`, `results`,
  `people`, `border`, `districts`, `parts`, `hearings`, `telangana`, `method`,
  `main`) and `short` maps a page key to `[findings, limits line]`. A page
  calls `SIR.showFaq(site, key)`; the FAQ tab calls `SIR.showFaq(site)` and
  shows every question. Answers are written for the FAQ tab, and their
  relative links are resolved against it wherever they appear, so write
  links as seen from `<site>/faq/`. The All India landing page builds its own
  list in its page script. `check_data.py` fails if a page loses either block.
- **Every section has its own address.** `build_site.py` gives every `h2`
  and `h3` in a page's source an id made from its English text
  (`heading_ids`), so `#women` opens on the same section in every language,
  and `SIR.anchors` puts a copy-link button beside each. `SIR.jump` scrolls
  to the hash again whenever charts or the findings list are added above it,
  until the reader scrolls. Renaming a heading changes its address; keep an
  old one alive with an explicit `id=` on the new heading. Dashboard tabs keep
  their own hashes, and the report pages their `s0`... ids.
- **On a wide screen the header is one row**: theme and print show icons only
  (their labels stay for screen readers) and the Ctrl K hint is hidden, because
  seven labelled controls came to 917px and wrapped under the title, leaving
  the right of the header empty. Adding a control means checking the header
  still fits one row at 1280px.
- **Header menus on a phone hang from the whole controls row**
  (`.controls{position:relative}`, `.dl{position:static}`), because a menu
  anchored to its own button opened off the left of the screen.
- **The part explorer takes a link to a part**: `hyderabad/explorer/#Yakutpura-297`.
- **Every file a page loads carries `?v=<content hash>`**, written by
  `scripts/stamp.py`, which is Netlify's build command and a step in
  `static.yml`. Page references are stamped in the HTML; files fetched by
  script (`SIR.json`, the dictionaries) get theirs from `window.SIR_V`, which
  the script writes into `assets/i18n.js` between `/*stamp*/` markers. A new
  fetch must go through `SIR.json` or read `SIR_V` itself, or it escapes the
  stamp. Pages are served with `max-age=0, must-revalidate`, so a reload
  always picks up the newest addresses.
- No page states the site's own address.
- Colour tokens live in `assets/sir.css`, with the dark block written twice
  (`prefers-color-scheme` and `[data-theme="dark"]`). `check_contrast.py`
  measures 72 pairs, including the tab bar, the banners and the tags, and fails if the two dark blocks differ.
- **Charts on a phone go through `SIR.fitPhone`** (both `SIR.chart` and the
  dashboards' `draw`): below 600px it wraps axis titles and category labels,
  keeps labels level only where they fit, thins value ticks and writes big
  counts in lakh. A chart's own tick callback is left alone. A bar chart with
  more than about ten categories should be laid on its side on a phone, as
  `cAdult` on the All India page is.
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

English, Hindi, Urdu, Telugu, Tamil and Bengali, chosen from the menu in the
header and kept in the address (`?lang=hi`) and in the reader's browser.

- **A new language** is an entry in `LANGS` in `assets/i18n.js` (name, short
  label, direction, Noto font), a font rule in `sir.css`, the code in
  `LANGS` in `scripts/check_i18n.py` and `NAMES` in `scripts/i18n_workbook.py`,
  and a dictionary covering every key in `i18n/catalogue.json`. Translators
  working in parallel need a folder each: two sharing one scratch folder
  overwrote each other's batches when Tamil was added.

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
- `scripts/i18n_collect.mjs` walks the folder of every place in `site/places.json` for pages,
  and reads `assets/faq/*.js`, rather than keeping a list, so a new page is
  collected without anyone remembering.
- **Fixed text in the markup** is translated by `L.apply()`, which `sir.js`
  calls before a page's own script runs. The key is an element's inner HTML
  as the browser serialises it, so `scripts/i18n_collect.mjs` reads the keys
  with a browser and writes `i18n/catalogue.json`. Re-run it after changing
  any text, then translate the new keys; CI fails until every key in every
  language is translated with its placeholders and links intact.
- Figures stay in Western digits with Indian grouping. Names that arrive from
  the data (constituencies, localities, parties, the Commission's reason and
  rule codes) stay as the data spells them.
- **The menu is on** (`MENU` in `assets/i18n.js`), in every page's header,
  and a reader's choice is remembered. No native reader has signed off the
  translations yet, so every translated page carries a notice that the
  English page governs. `scripts/i18n_workbook.py` writes the review
  workbook; fold the reviewer's corrections into `assets/i18n/<lang>.js`, and
  only then take the notice out.

## Reports

Each full report is published twice: as a page on the site
(`bihar/report/`, `hyderabad/report/`, a tab on every sub-page and first in
the Downloads menu) and as a PDF in `reports/`. There is no Word file on the
site. `scripts/reports/build.sh` rebuilds both from the published JSON: the
builder (python-docx, via `docxkit.Report`) writes print-ready HTML that
headless Chromium prints to PDF, and a web fragment with its figures as PNGs
that `scripts/reports/web.py` puts into the site's page shell, taken from the
method page. The Word file the builder writes on the way is deleted. They
follow the Sabar Institute's structure: Part I for the whole area, Part II a
chapter per district or constituency, one section on what the lists show and
do not, and what the Election Commission should do. Rebuild them after any data change; nothing
checks that they are current.

The report pages are in English only: the article carries `lang="en"` and
`data-no-i18n`, and a translated page shows a line saying so. Translating
them would add some 70,000 characters to the review.

Beside them are two slide decks, `*-deck.pptx`, written by
`scripts/reports/decks.js` (pptxgenjs) from the same JSON: Bihar 27 slides,
Hyderabad 20. Each has one section per page of the site (Bihar: the scale,
elections, women/religion/caste, border, districts, the FAQ, limits, method;
Hyderabad: overview, age/sex/religion/2002, polling parts, hearings, the FAQ,
limits, method), named in a small label above every title, and a contents
slide numbered from the sections. **Titles are plain sentences stating the
finding, computed from the data**, never a slogan: "In 174 of 243 seats, more
names were removed than the 2025 winning margin", not "Where the removals
dwarfed the margin". A title that makes a claim checks it first (the
Hyderabad margin slide checks every seat lost more names than its winner
polled; the districts slide names the factor with the largest rank
correlation and lists those under 0.2 as unrelated). The decks state no site
address, and the speaker notes carry the caveats. `build.sh` rebuilds them
with the reports.

**Say only what the lists record.** No page, report or deck may say how long a
hearing slot lasted or how many minutes an elector had: the lists record cases
per slot, not the slot's length.

## Watch out for

- **The Sabar Institute link.** Every method page ends with "Analysis of the
  named lists", pointing readers who want named-voter analysis to
  sabarinstitute.org, at the owner's request (October 2026). It is a pointer
  for further reading and nothing more: no page says who compiled any list
  this site counts, and the Hyderabad pages still do not name a compiler.
- **Publishing**: the site serves only pages and aggregate JSON. `_redirects`
  answers 404 for raw files, scripts, notes and `archive/`; `static.yml` stages
  the same set for Pages. Do not link source files from a page, and describe
  sources without naming the people or organisations who compiled them.
- **Writing**: plain explanatory prose. Never refer to earlier versions of the
  analysis or to corrections on a public page. The owner's rules, applied to
  every page, report and deck: no em dashes; no sentences hinged on a colon
  ("X: Y") or strung on semicolons; no "X, not Y" or "not X but Y" turns; say
  the caveat about reasons once per page in plain words ("what the officer wrote
  down, and nobody checked it"), not as "an officer's entry, not a finding";
  prefer "guessed from names" to "estimated", "typical" or "middle" to
  "median" in prose. When rewriting an English key, carry its translations to
  the new key only if the meaning is unchanged; retranslate otherwise.
- **Bihar and Hyderabad are never compared** with each other, on a page,
  in a report or in a deck. Each analysis stands on its own.
- **Lead with what was lost.** Summaries, key insights and deck titles open
  with the scale of the removals, the seats where the removed could have
  changed the result, and who was removed. Facts that cut the other way (the
  Old City lost no more than the rest of Hyderabad, Hindu-name electors were
  struck off more often inside a part, the NDA keeps its majority on every
  estimate) stay in the body and the FAQ, written as plain facts and never as
  reassurance or as a page's headline.
- **Framing**: this is an analysis, not a petition site. The pages lead with
  the scale of the removals, the removals against winning margins, women's
  over-representation and, in Hyderabad, the process (the 2002 link, hearing
  loads). Where something is asked for, it is a short, plain section on what
  the Election Commission should do or publish; never "what an audit needs",
  never "where checking should start", never a call to readers. The alliance comparisons stay on
  the Elections page and in the FAQ, stated plainly: the lists show more
  removals on NDA ground, and no page may say otherwise. The lists cannot show
  intent, and no page may claim they do.
- `pandas` and `openpyxl` are pinned in CI because a reader change could move
  the numbers without an error.
