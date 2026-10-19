# INDIA-DATA

Shared engineering standard: @.claude/engineering-standards.md. It applies to all work in this repository. This file adds what is specific to the project, and wins where the two disagree.

The SIR analyses hub at offtheroll.in: All India (the reasons for
removal, state by state), Bihar (2025), five Old City constituencies of
Hyderabad (2026), Tamil Nadu, Karnataka, West Bengal, Kerala, Rajasthan, Uttar Pradesh, Delhi, Maharashtra, Gujarat and Uttarakhand (2026), Assam's Special Revision (2025-26), and every other state and union territory in the revision on one shared page.  Static HTML, Chart.js from cdnjs, one
stylesheet (`assets/sir.css`) and one helper script (`assets/sir.js`) shared by
every page. Netlify deploys the repository root from `main` to offtheroll.in
(Netlify DNS; the domain is registered at Porkbun with Netlify's nameservers,
and forindia.netlify.app redirects to it). There is no GitHub Pages copy:
the workflow that made one failed on every push from March 2026, because Pages
is not enabled on the repository, and was removed in October.

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
- **Electors in 2025 come from the Commission's Detailed Results** (the
  `_electors` rows of `ae_party_votes_2020_2025.csv`, 7,46,91,135), not the
  Wikipedia seat list, which has slips in five seats (Bahadurpur by 9,000,
  Bahadurganj by 1,100). Every rate per 100 electors divides by it.
- **Phase 2 (3,51,150) is below Format 4B's removals after the draft
  (3,66,742) in every seat**, by 4 to 586, and tracks it seat by seat: an
  earlier count of the same removals, though neither table is dated. Keep the
  two apart and say which one a figure uses.
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
  2019-20); only density and urban share are still Census 2011, read from the
  Registrar General's table A-01 by `scripts/census_a01.py`
  (`data/india/raw/census2011_a01_districts.csv`, all 640 districts).
- **Rates are stored to four decimals.** Every builder rounds a rate or
  share to 4 places and the pages show 1 through `SIR.d`, which rounds a half
  up. Stored at 2 places, 10.645 became 10.65 and then 10.7, and ties at the
  rounded value put seats in the wrong third. Do not round a stored figure to
  the precision it is shown at.
- **Caste is not identified.** Two surname classifications give different
  compositions and wide bounds. The pages say so. Surnames in classification A were
  checked against the official SC, ST and OBC lists for Bihar compiled by
  Jolad, Kalyani and Baharadia (Harvard Dataverse, doi:10.7910/DVN/WT5VIY,
  CC0): Turi, Dom and Bhuiyan are SC, Dhobi is SC for Hindus and OBC for
  Muslims and so spans groups. District income per head is per capita GDDP
  for 2022-23 at constant 2011-12 prices from the Bihar Economic Survey
  2024-25, Table A 1.7 (`raw/gddp_per_capita_2011_12_prices.csv`, read from the
  scanned PDF the owner supplied; the build asserts each year's printed ranks
  run 1 to 38 and follow the values). The old dashboard's income column held
  placeholder values and is never used. Do not collapse them into
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
the census: both migration shares are Census 2011 D-01 counts over the state's own
enumerated population (out: born here, counted in another state; in: counted
here, born in another Indian state), held to `data/india/raw/census2011_d01_states.csv`
by `check_data.py`. `robustness_2011` reruns the correlations on the 2011 values and
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

**Inside the Commission** (`#inside-the-commission` on the process page) is
The Indian Express's account of the objections two Election Commissioners put
on file, November 2025 to October 2026, from `inside` in `process.json`: one
lane per actor (`VIZ.lanes`, numbered markers matching the list under it),
every event linked to the paper's article. It is press, so it says on the
page that the paper has seen the notes and the site has not, and nothing in
it moves into the timeline above without its document. The quote and page in
the Express Plus special issue (October 2026) behind every event are in
`data/india/raw/process_research/inside.json`. The issue itself, which the
paper released free, is `reports/indian-express-plus-election-commission-2026-10.pdf`,
linked under the list with a line that it is the paper's and outside the site's
licence; `terms/` says the same. The paper's own counts (14 objections, Goa's eight messages and 97
electors) are in `inside.goa` and the prose, never counted from the markers,
which show only the dated ones.

**The cities** (`india/cities/`) sets each large city against its state, its
suburbs and the rest of the state. `scripts/build_cities.py` reads the state
pages' own district tables (no new source) and writes `data/india/cities.json`
and the CSV; `check_data.py` runs it with `--check`, and the build fails if a
named district is missing or a city's core, suburbs and rest do not add up to
its state. A city is its districts (`CITIES` in the build), drawn differently
from city to city and listed on the page. The suburbs are the neighbouring
districts: Bangalore Rural and Ramanagaram; Rangareddy, Medchal Malkajgiri and
Sangareddy; Chengalpattu, Kancheepuram and Thiruvallur; Thane and Palghar;
Ghaziabad and Gautam Buddha Nagar for Delhi, measured on Uttar Pradesh's
revision (Haryana's suburbs have no figure); Barabanki and Unnao; Gandhinagar;
Howrah and North 24 Parganas. Findings: all eight cities measured by the names
left off lost more than their state, 1.5 to 2.3 times its rate, and the
suburbs lost less than the city in six of seven (Mumbai is the exception:
Thane and Palghar lost more). **Kolkata and Kochi are measured by the fall in
the roll** and kept apart, never ranked. **Patna is per 100 on Bihar's 2025
roll**, the Bihar pages' rate, so it is compared with Bihar and not ranked;
it is the one city below its state. **Bihar and Hyderabad may appear side by
side on this page only** (owner's decision, October 2026); the rule below
still holds everywhere else. Hyderabad's district figures are press figures
and say so. The page says the "shifted or absent" share cannot tell moved and
doubly registered people from residents who were out, and never claims either.
English only, like the other All India sub-pages.

**Women** (`india/women/`) gathers every count by sex the site holds.
`scripts/build_women.py` reads only files other builds write (`states.json`'s
`gender` rows, the state summaries and district files, Bihar's final roll and
tests) and writes `data/india/women.json` and the CSV; `check_data.py` runs it
with `--check`. Sections: women's share of the names left off against their
share of the roll (eleven states, each with its quality flag); per 100 women
and per 100 men (the roll by sex is the roll before times women's share);
district by district in Bihar, West Bengal, Kerala and Uttarakhand, each in
its own measure; after the draft (Bihar, Uttarakhand, Rajasthan); and Bihar's
deaths and marriage tests. Findings: women were the larger share in 8 of 11
states and 85 of 89 districts; Delhi is the exception (35.3 men against 29.9
women per 100). The page says the lists cannot say why.

**Urban** (`india/urban/`) sets rural, mixed and urban districts against
each other inside each state. `scripts/build_urban.py` reads the district rows
through `build_cities.rows()` (so it cannot disagree with the cities page),
the 2011 urban share from `data/india/raw/census2011_a01_districts.csv`
(written by `scripts/census_a01.py` from the Registrar General's table A-01),
and `data/india/raw/district_2011_parent.csv`, which names the 2011 district
each of today's was made from, with its source (`URBAN_SOURCES.md` beside it).
Each district is counted under its first-listed parent, the one it was mostly
made from, so Telangana's 33 districts become its ten of 2011; adding every
parent would chain them into five. Bands: rural under 20% urban, mixed 20 to
50, urban above 50. Ten states, each in its own measure; Delhi and Rajasthan are left out and
the page says why. Findings: urban above rural in
8 of 9 states (Kerala the exception; Bihar has no urban district), mixed above
rural in 8 of 10, and the order holds without the urban districts (rank
correlation 0.2 or more) in six states. Never claim the share has grown since
2011 without a source.

**District factors** (`india/factors/`) sets each district's rate against
its circumstances inside each state, as rank correlations, never across
states. `scripts/build_factors.py` writes `data/india/factors.json` and the
CSV; `check_data.py` runs it with `--check`. Survey factors (women who can
read, ten years of school, married before 18, clean cooking fuel, sanitation,
deaths registered, sex ratio) are NFHS-5 2019-21, read from the district
pages of each state's IIPS compendium into `data/india/raw/nfhs5_districts.csv`
with file and page (see `FACTORS_SOURCES.md`; the PDFs came from OpenCity's
copies because rchiips.org fails TLS here, and are not committed). Nineteen
states: Bihar, Gujarat, Karnataka, Kerala, Maharashtra, Telangana, West
Bengal, Tamil Nadu, Uttar Pradesh, Rajasthan, Uttarakhand, Delhi, and since
14 October 2026 Andhra Pradesh, Assam, Chhattisgarh, Manipur, Meghalaya,
Mizoram and Odisha (Andhra Pradesh and Chhattisgarh from the Internet
Archive's copies of the Institute's files; their district matches are in
`raw/nfhs5_alias/`, each row with its parents and source; Chhattisgarh and
Mizoram are measured by the rise after the draft, so their signs run the
other way; `SHARED` in `build_cities.py` gives these seven their rows). The build
fails unless Bihar's values agree with Bihar's own reading of the same
compendium. Rates come from `build_cities.rows()`, except Rajasthan (fall in
the roll 2023 to 2026), Uttarakhand (names left off, from the CEO's table of
the draft) and Delhi (the 11 districts of its 2025 roll, which are the
survey's), in `state_rows()`.
The unit is the survey's district, with later districts added into the one
they were made from (`ALIAS`). Urban share and density are 2011 Census on the
urban page's units. Income per head (`INCOME`) is each state's own district
table, on that table's districts: Bihar (its Survey), Karnataka, Maharashtra,
Tamil Nadu and Telangana (OpenCity's transcriptions, in `raw/income/`, each
checked against its own printed total where it has one). A correlation is
"clear of chance" at 1.96 / sqrt(n - 1). The page says the circumstances
move together (schooling and clean fuel correlate 0.39 to 0.77 in the states
with 20 or more districts) and never names one as the cause. English only.

**Charts first, tables folded.** The cities, women and comparisons pages
lead each section with a chart and put the full figures in a
`details.figs` fold. Tables there are drawn by `SIR.table(id, cols, rows)` in
`sir.js`, which gives each cell its column heading as `data-label`; below
600px `table.stack` turns every row into a card with each figure named, and
on a desktop the table keeps to 52rem. Use it for any new table of figures.
`VIZ.dots` skips a null value, so a city or state missing one series still
draws.

**Comparisons** (`india/compare/`) carries three. Each state is set against
itself in its own measure, and states are never ranked against each other.

- **Reserved seats.** `scripts/build_reserved.py` writes
  `data/india/reserved.json` and the CSV. Reservation comes from Bihar's own
  file, from "(SC)"/"(ST)" in Gujarat's and Delhi's seat names, and for Tamil
  Nadu, West Bengal and Kerala from `data/india/raw/reserved_ac.csv` (Wikipedia
  lists). The build fails unless every state's SC and ST counts equal the
  Delimitation Order's (`ORDER`). Each reserved seat is also set against the
  general seats of its own district. Finding: reserved seats lost fewer names
  in every state, which cuts the other way and is stated plainly. A reserved
  seat describes a place, and the page never reads it as the caste of the
  electors removed. Rajasthan and Uttarakhand are left out, because their
  constituency figures cover a different stretch of time.
- **How much came back** reads `made_up_pct` from `states.json`. It is always
  called a ceiling, because the rise counts new voters.
- **Border districts.** `scripts/build_border.py` writes
  `data/india/border.json` and the CSV from `data/india/raw/border_districts.csv`.
  That file holds all 119 rows of the Government of India's List of Border
  Guarding Districts, as printed in Annexure XI (pages 69 to 71) of the Staff
  Selection Commission's notice of 1 December 2025 for constables in the
  Home Ministry's armed police forces. The 2005 and 2015 BADP guidelines and
  the Lok Sabha answers list no districts, and mha.gov.in refuses the sandbox.
  Never use a district list of the site's own. The build fails if a listed
  district is missing, and if Bihar's seven stop matching the Bihar pages'
  Nepal-border districts. They match today.
  - Covered: Uttar Pradesh, Gujarat, Bihar, West Bengal (the fall in the roll)
    and Uttarakhand (names left off).
  - Rajasthan is left out. Its figure is a change over two years, and Barmer
    was split to make Balotara.
  - Finding: there is no single pattern. Border districts lost more in Bihar
    and Uttarakhand, about the same in Uttar Pradesh, and fewer in Gujarat and
    West Bengal. West Bengal's border is above the interior once Kolkata is
    left out.
  - Where reasons exist, "enrolled elsewhere" is a larger share in border
    districts (Uttar Pradesh and Gujarat).
  - Every border sentence says the rate says nothing about citizenship.

**Where the revision stands** (`india/progress/`) is the progress board: for
each of the 32 states and UTs, its stage as of `as_of` in `process.json`,
worked out in the page script from the latest date each schedule step gives
and from `states.json` (a draft is published when `removed` is held, a final
roll when `electors_final` is held, dated by `final_date` when known). A final
roll past its latest scheduled date and not held is "not yet found", never
"late" or "delayed", and the page says that says nothing about why. A state
with no draft yet takes no stage from its order's dates (Tripura's were not
kept). It draws one calendar (`VIZ.gantt` with `single` and `today`) and a
lollipop of days from the first house visit to the final roll, and is English
only like the process page. Update `process.json` and `final.csv`; the page
follows.

**The SIR in numbers** (`india/numbers/`) is the one-page summary: the roll
before, the names left off, by phase and in the ten largest states, each with
its source, with three charts (the roll before against the draft, every
state per 100 electors coloured by phase, and the ten largest against the
rest). Every figure, sentence and chart on it is computed from
`data/india/states.json` when the page loads, so it moves with the state
table. It is English only, like the process page.

The same page carries the electors in every Lok Sabha election since 1984-85,
from the Election Commission's Atlas 2024, Graph 6.1. The figures are curated in
`data/india/raw/lok_sabha_electors.csv`; `scripts/build_electors.py` writes
`data/india/lok_sabha_electors.json` and the downloadable CSV, and
`check_data.py` runs it with `--check`. The Atlas misprints 1991-92 as
5115333598; the row reads 511533598 and says so. The comparison of the names
left off with the 2014 to 2024 gain always says the two counts differ in
coverage (31 states against all India).

Beside the electors the chart draws the population of voting age, from the UN
World Population Prospects 2024 (medium variant, single-year ages, 1 July of
the election year), extracted by `scripts/fetch_wpp_voting_age.py` into
`data/india/raw/wpp2024_voting_age.csv`. It is 21 and over for 1984-85, because
the voting age fell to 18 only with the 61st Amendment in 1989, and the build
asserts that. The roll exceeds that population in every election to 1999
(109.5 per 100 in 1984-85) and falls short of it from 2004 (96 in 2024). Say
"if the population estimate is right" before reading the excess as dead or
moved names, and never call the shortfall missing voters: the population
counts residents who are not citizens.

**Against the winning margins** opens the same page. `scripts/build_margins.py`
writes `data/india/margins.json` and `margins_ls2024.csv` from the four states'
seat files and the 2024 Lok Sabha results (`data/india/raw/ls2024_pc_results.csv`
and `ls2024_ac_pc.csv`, written by hand-run `scripts/fetch_ls2024.py` from a
published compilation of the ECI results and statistical report 34). It makes
three comparisons and keeps them apart: assembly seats in Bihar and Tamil Nadu
(names removed, 385 of 477 over the margin) and in West Bengal and Kerala (fall
in the roll, 177 of 434), never added together; the 141 Lok Sabha seats of those
four states, each summed from its segments; and every state with its removals
spread evenly over its Lok Sabha seats, which is an assumption and is tested on
the page (Tamil Nadu 27 on the even spread against 19 counted). The build fails
if a 2024 margin differs from the published one or from Bihar's Wikipedia table.
A fourth comparison spreads every state's names left off over its Assembly
seats by electors and sets them against the margin at its latest Assembly
election (`ASM` and `OWN` in the build; results in `data/india/raw/assembly/`,
one file per state with `SOURCES.md`). The idea of reading the Assembly
results beside the Lok Sabha came from Manomay Ghoshal's Odisha workbook.
Every file but Manipur's and Meghalaya's (the CEOs' Form 20) is the
Commission's statistical report, tables 10 and 11, which the owner downloaded
from an Indian connection; the sandbox cannot reach eci.gov.in. Arunachal's
ten unopposed seats are in neither table and keep a compilation's electors. The spread is tested on Bihar, Tamil Nadu,
Gujarat and Delhi (the totals come within 15 seats, the seats themselves are
often wrong) and on Odisha's six press seats, and the page says it gives how
many seats, never which. NOTA is never a runner-up (Indore); Surat was unopposed. Over the margin means the
removals were large enough to decide a seat, never that they did: say so, and
carry Bihar's estimate (4 to 6 seats change hands, both ways) beside it.

`data/bihar/raw/final_roll_format4b.csv` is the Commission's Format 4B return
for Bihar's final roll, seat by seat and by sex; `scripts/build_bihar_final.py`
writes `data/bihar/final.json` and fails unless every seat adds up and the
totals equal the press note of 30 September 2025. A seat's roll before is its
draft plus its phase 1 list, because the June roll exists only as a state
total. Findings: the net fall still exceeds the 2025 margin in 124 of 243
seats (174 on every name left off or deleted, both phases); women were 55.5% of those removed at the
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
in the report and in the deck. Results: names left off or deleted (both
phases) exceed the margin in 174 seats, and the net fall to the final roll in 124; women are over-represented in
38 of 38 districts and 242 of 243 seats; more removals on NDA ground holds
inside seats (NDA-led booths higher in 150 of 237) but between seats in the
same district the gap (+0.46 per 100, -0.17 to +1.10) is too small to be sure
of; the swing changes sign with the comparison. Say exactly that.

## Hyderabad

The place is labelled **Telangana 2026** in the places menu (October
2026): it holds the state page (`hyderabad/telangana/`) and the Old City
analysis. The addresses stay under `/hyderabad/` so old links keep working.

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
  press analysis (The Hindu Data Team's count of the named lists), flagged
  unverified; do not move it onto the Tamil Nadu pages as a finding. The
  women section uses the CEO's own final roll of 6 January 2025 by seat and
  sex (`raw/roll_20250106_ac.csv`): the fall from it to the draft, by sex,
  always called the fall and never the names removed (ten months of ordinary
  changes, and that roll is 5,01,637 smaller than the roll of 27 October).
  Women were 51.1% of that fall against 51.0% of the roll; Vedaranyam 60.4%.
- **Turnout is votes over the roll of 6 April 2026**, the roll the election
  was held on (`raw/election_roll_20260406_ac.csv`, the CEO's, larger than the
  final roll in every seat). The claims and objections after the draft are the
  CEO's exact counts as The Hindu printed them (27,53,796 added, 4,23,172
  deleted), which add up to the final roll.
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
(10,796,339 removed of 55,432,314) and the roll of 9 October to 45,161,393.

- **Districts only.** The CEO published the revision by its 34 election
  districts and none of it by assembly constituency, so there is no seat page
  and no comparison with the 2023 margins. `results_2023*.csv` in `raw` is
  TCPD's compilation, not primary, and no page uses it.
- **Bengaluru is four districts**: Bangalore Urban and B.B.M.P North, Central
  and South. Bangalore Rural is not part of it.
- **The latest roll is 9 October 2026** (press note of that date, with notices
  and forms by district in `raw/`), published while notices were being
  heard; the final roll is due 27 October. The roll of 25 September stays in
  `raw/` as a record. The summary's `sep` field holds the latest roll. The rise from the draft counts new
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

## Rajasthan

`scripts/build_rajasthan.py` reads `data/rajasthan/raw` (sources and checks in
`SOURCES.md` there) and writes `summary.json`, `constituencies.json`,
`districts.json` and the two CSVs; `check_data.py` runs it with `--check`.

- **The removals are a state total only.** The CEO's press note of 16 December
  2025 and fact sheet of 21 February 2026 give the roll before (5,46,56,215),
  the draft (5,04,71,324), so 41,84,891 left off, the three reasons in lakh,
  rounded, and the additions, deletions and final roll by sex, all for the 199
  ACs revised together. Anta (193) was revised later and is outside them. The
  only AC-level source is the lists of individual electors, never opened.
- **Below the state the pages measure the change in the roll**, general
  electors only, from the roll of the 2023 election (ECI statistical report
  11, `electors_2023_ac.csv`) to the final SIR roll of 12 March 2026. It spans
  more than two years of new voters, deaths and moves, so it is never called
  the removals; for the state it is 10.6 lakh against 41.8 lakh left off, and
  49 seats grew. Service voters are left out of both, because they cluster in
  districts like Jhunjhunu and would distort the change there.
- The 2026 table counts 565 third-gender electors among women, so the 2023
  third-gender electors are added to women before comparing.
- The pages are English only for now (the article carries `data-no-i18n`),
  with a translated note saying so; only the shell, titles and the front-page
  card are translated. The FAQ in `assets/faq/rajasthan.js` uses plain
  strings for the same reason. Translate before taking the note out.
- The map is by constituency (`data/geo/rajasthan.json`), shaded by the change
  in the roll; a constituency whose roll grew falls in the lightest bin.
- **The District Election Officers' figures for the draft, from the press**
  (October 2026). On 16 December 2025 each officer briefed the district's roll
  before, draft, names left off and five reasons; Dainik Bhaskar and Amar Ujala
  printed them for 22 of 41 districts and 110 of 199 constituencies
  (`raw/draft_district_press.csv`, `draft_ac_press.csv`, Sirohi by sex in
  `sirohi_sex_press.csv`; see `SOURCES.md`). `build_press()` holds every
  printed table to its own sums, with the printed slips pinned in `DIST_GAPS`
  and `SUM_GAPS`, and writes `summary.json` `press`, a `press` object on each
  covered constituency, and `press_districts.csv` and `press_constituencies.csv`.
  The overview's section, the FAQ and the seat pages (`press: true` in
  `seat.js`) show them as press and partial, never added to the CEO's figures.
  They rank places much as the change in the roll does (rank correlation 0.85
  across constituencies, 0.88 across districts), which is the check that the
  change in the roll is a fair stand-in elsewhere. Two press splits of the
  state's reasons disagree with each other and the CEO, so the state reasons
  stay the CEO's lakh figures.

## Uttar Pradesh

`scripts/build_uttarpradesh.py` reads `data/uttarpradesh/raw` (sources in
`SOURCES.md` there) and writes `summary.json`, `districts.json` and
`districts.csv`; `check_data.py` runs it with `--check`.

- **Districts only, from a photograph.** The CEO's site cannot be reached from
  outside India. The district table of 6 January 2026 (roll before, draft, and
  the names left off under five reasons) is read from the photograph India TV
  published, transcribed by eye. Every row must satisfy two identities (roll
  before less draft equals the total, and the five reasons sum to it), and every
  column must sum to the printed State row, so a misread digit fails the build.
  Say on every page that the table is the CEO's, as published in the press.
- No table by assembly constituency was found, so there is no constituency
  page and no comparison with margins. The map is by district
  (`data/geo/uttarpradesh.json`, see `data/geo/SOURCES.md`). Do not count ACs from the
  district ASD lists: they carry names.
- No split by sex of the names left off, at any level. The draft and final by
  sex come from the CEO's own post; the Form 6 and Form 7 counts and the
  8,15,996 removed after the draft are from the press and are said to be.
- The All India row is these exact figures; "shifted, absent or other" there is
  untraceable or absent plus permanently shifted plus others.
- `data/uttarpradesh/raw/check.py` is a research script and is not in CI: its
  `results_2022.csv` check fails in 32 ACs. That file is a copy of Wikipedia's
  table and is wrong in 25 ACs' votes; the Commission's own 2022 results are
  `data/india/raw/assembly/uttarpradesh_2022.csv`, which is the one to use.
- English only, like Rajasthan, with the same translated note.
- **The deep dive (October 2026)** is `analysis.json` and `seats.csv`, written by
  the same build. `raw/press_ceo.csv` holds the CEO's figures as the Hindustan
  Times printed them on 18.01.2026, each with its sentence: the names left off
  by sex (rounded; the page used to say no split existed), urban and rural rolls
  (the report's "1.27 crore" rural fall is a misprint for 1.72, and the build
  uses the difference of the rolls), women at their father's address, the
  notices (1.04 + 2.22 crore, which add to 3.26; The Hindu's 1.4 + 2.02 do not)
  and the 8,751 AEROs. Each district's names left off are spread over its
  constituencies by 2022 electors against the 2022 margin (377 of 403 over the
  margin); say it gives how many seats, never which, and never that a result
  changed. District circumstances are read from `factors.json` and
  `urban.json`, never recomputed here. Notices per officer are averages and
  never a hearing's length.

## Delhi

`scripts/build_delhi.py` reads `data/delhi/raw` (sources and checks in
`SOURCES.md` there; `check_raw.py` rebuilds the raw CSVs from `sources/` and
needs pypdf) and writes `summary.json`, `constituencies.json`,
`districts.json` and the two CSVs; `check_data.py` runs it with `--check`.

- **Constituencies from the CEO's own table.** ceodelhi.gov.in is reachable
  through Firecrawl (not by plain curl from the sandbox). The CEO's
  "Distt/AC Wise Electors and Uncollectable Enumeration Forms" of 31.08.2026
  is transcribed in `sources/ceo_ac_draft_uncollectable_20260831.md`: draft by
  sex and forms not collected for all 70 ACs on the 13 current districts.
  `check_raw.py` holds it equal, row by row, to the data behind Business
  Standard's map of the same table, and to its own district sums and grand
  total; the build fails unless the ACs add up to the CEO's state figures
  (1,45,10,299 before, 97,53,577 draft, 47,56,722 left off). The roll before
  is the roll of 16 June 2026 (CEO press note), not 20 June.
- **Reasons and sex are state figures only.** `secondary_reasons_ac.csv` is a
  consultancy's count of the named ASDD lists by AC. It is kept as a record
  and **not used**, like West Bengal's compilations; do not move it onto a
  page. Men were left off more often than women (35.3 against 29.9 per 100).
- Districts are the 13 of the CEO's table. `district_2025` (the 11 of the
  2025 roll) is kept in `ac.csv` for the record only.
- Margins are from the votes (New Delhi 4,089, Patparganj 28,072, against the
  4,199 and 28,702 two compilations print). The left-off count exceeds the
  2025 margin in 68 of 70 seats (66 at turnout); say it could have decided
  a seat, never that it did.
- The final roll is due 4 December 2026 (CEO letter of 27.09.2026, from the
  Commission's letter of 26.09.2026). Rebuild when it is out.
- English only, like Rajasthan and Uttar Pradesh.

## Maharashtra

`scripts/build_maharashtra.py` reads `data/maharashtra/raw` (sources and checks
in `SOURCES.md` there; `check_raw.py` asserts the press note's annexures) and
writes `summary.json`, `districts.json`, `constituencies.json` and the CSVs;
`check_data.py` runs it with `--check`.

- **Every one of the 288 constituencies, from the CEO's own tables.** The
  statement enclosed with the press note of 16 September 2026 (`ac_roll.csv`,
  roll before and names left off) and the tables of 1 September 2026
  (`ac_reasons.csv`, the five reasons; `ac_draft_sex.csv`, the draft by sex),
  with the reasons and the notices by district beside them
  (`district_reasons.csv`, `district_notices.csv`, the release of 4 September).
  The build fails unless every constituency adds up within itself and to its
  district in every column, and the districts to the press note of 31 August
  (9,78,54,049 before, 7,71,65,562 draft, 2,06,88,487 left off). The 38 seats
  of the CEO's list of 30 September agree with the full table.
- **The state's reasons are exact**: 34,82,231 dead, 76,76,135 shifted,
  75,41,229 absent, 17,66,502 enrolled elsewhere, 2,22,390 other, adding up
  exactly; the All India row carries them and the build asserts it.
- **No split by sex of the names left off, at any level.** The draft is by sex;
  the roll before is a total.
- **The city is five districts**: Mumbai City, Mumbai Suburban, Thane, Palghar
  and Pune (`CITY` in the build), 29.9% of the roll and 48.4% of the names
  left off. Keep the comparison computed.
- **Against the 2024 margins** (`data/india/raw/assembly/maharashtra_2024.csv`):
  more names left off than the margin in 220 of 288 seats, 183 at turnout.
  The party comparison carries `vs_district` and is by party, never by
  alliance; set against their districts the six main parties run from -3.5 to
  +0.8, so say most of the difference is where each party's seats are.
- The note keeps three old district names (Aurangabad, Ahmednagar,
  Osmanabad); `now` in `districts.json` carries the new ones. AC 129 is
  printed "Vekramgrth" and the build uses the Commission's Vikramgad.
- The dates are read from `process.json` (the Commission's letters of 26
  September and 12 October 2026): claims to 26 October, notices to 10
  November, the final roll on 16 November. Rebuild from it when it is out.
- The overview's map is by constituency (`data/geo/maharashtra_ac.json`, cut
  from DataMeet's assembly map, every number checked against its name) with a
  Mumbai inset on wide screens only; the district pages keep
  `data/geo/maharashtra.json`. Every constituency has a page (`seat.js`
  `CFG.maharashtra`, party codes spelt out in `party`), and the district pages
  list their constituencies.
- English only, like Rajasthan, Uttar Pradesh and Delhi, with the same
  translated note.

## Gujarat

`scripts/build_gujarat.py` reads `data/gujarat/raw` (sources and checks in
`SOURCES.md` there; `check_raw.py` asserts them) and writes `summary.json`,
`constituencies.json`, `districts.json`, `final.json` and the two CSVs;
`check_data.py` runs it with `--check`, and `check_raw.py` too.

- **Constituencies with reasons, from images in the press.** The CEO's
  district and AC tables of the draft of 19 December 2025 (roll w.r.t.
  1 October 2025, five reasons, draft) are known only as images of the CEO
  office's printouts carried by DeshGujarat, apparently posted by the CEO on
  X; the CEO's site has nothing on the SIR. Every page says the tables are
  the CEO's as published in the press. The build fails unless each AC's
  reasons add up and before less left off equals the draft, every district
  equals its printed total, and the state equals 73,73,327 left off of
  5,08,43,436.
- **No split by sex or age anywhere.** The women section says so plainly
  and shows nothing.
- **The final roll is by district only**, 34 districts with Vav-Tharad
  printed apart. The build adds Vav-Tharad back into Banaskantha so the
  final table lines up with the 33 draft districts; its ACs (7, 8, 14) are
  only inferred from its draft total and nothing relies on them. The printed
  final is 50 more than draft plus net in seven districts; both are kept as
  printed and the method page computes the list from `final.json`.
- **2022 results are the Election Commission's own statistical report**
  (`raw/eci2022_ac.csv`, reports 10 and 12). The compilation used before
  (`results_2022.csv`) is kept and checked against it: parties agree in all
  182, margins in 180 (Viramgam and Wankaner one vote apart, asserted). With
  the report's electors, turnout is used: the fourth count against the margin
  is the names not entered as dead at each seat's 2022 turnout (40 seats).
- **Ahmedabad's 21 seats after the draft** are press (Gujarat Samachar,
  17 February 2026, `raw/ahmedabad_final_ac_press.csv`); they add to the CEO's
  district row and the build asserts Danilimda carries the district's 25.
- **The city is two districts**, Ahmedabad and Surat (`CITY` in the build),
  21.9% of the roll and 36.7% of the names left off. The party comparison
  carries `vs_district` beside the raw rate, because the BJP won almost every
  city seat.
- The map is by district (`data/geo/gujarat.json`), because DataMeet has no
  shapes for 20 city ACs; a constituency picked in the finder outlines its
  district. English only, like Uttar Pradesh, Delhi and Maharashtra.

## Uttarakhand

`scripts/build_uttarakhand.py` reads `data/uttarakhand/raw` (sources and checks
in `SOURCES.md` there; `check_raw.py` asserts them) and writes `summary.json`,
`constituencies.json`, `districts.json` and the two CSVs; `check_data.py` runs
both with `--check`.

- **The names left off are by constituency, the reasons for the state only.**
  The CEO's PN 36/2026 gives the roll on 8 June 2026 (79,60,762), the draft
  (71,33,785) and four reasons. The CEO's table of the draft of 14.07.2026
  (`raw/ac_draft_asdd.csv`, read from the PDF's text by
  `parse_ac_draft_asdd.py`) gives every constituency's names marked ASDD and
  left off, the electors with an anomaly and with no mapping; a seat's roll
  before is its draft plus its names left off, which adds to 79,60,762
  exactly. Anomalies plus no mapping are the 24,30,608 notices; the nine
  anomaly categories overlap and are never added. Kichha lost 18.2 per 100,
  Didihat 4.2; notices and removals after the draft go together across seats
  (rank correlation 0.81). No sex or reason below the state.
- **Constituencies from the CEO's own table**, pages 3 and 4 of PN 63/2026
  (3 October 2026), transcribed by hand from a scan: draft, claims admitted,
  objections admitted and final, by sex, for all 70. Every row satisfies draft
  plus claims less objections equals final for each sex, and the rows add to
  the printed district and state totals; the build fails otherwise.
- **Rates after the draft are per 1,000 on the draft roll.** Claims and
  objections are a few per cent of a roll.
- **The plains are four districts** (Dehradun, Haridwar, Nainital, Udham Singh
  Nagar, `PLAINS` in the build); Dehradun and Nainital also hold hill seats, so
  the pages call it a split by district. 60.1% of the draft, 87.2% of the
  names removed after it.
- **Women were 53.0% of the names removed after the draft** against 47.8% of
  the draft, more than their share in 63 of 70 seats (Dharchula 83%). The table
  gives no reason, and the pages say it cannot say why.
- **No comparison with the 2024 roll below the state.** The 2024 segment
  electors include service voters, who cluster in the hill seats; the SIR rolls
  are general electors.
- The map is by constituency (`data/geo/uttarakhand.json`), shaded by names
  left off per 100 on the roll before. The finder, the factors, border and
  urban pages read Uttarakhand by the names left off. English only, like the other 2026 pages.

## Assam

`scripts/build_assam.py` reads `data/assam/raw` (sources and checks in
`SOURCES.md` there) and writes `summary.json` and `assam.csv`; `check_data.py`
runs it with `--check`.

- **A Special Revision, not an SIR.** The Commission's order of 17 November
  2025 (read in full from a Scribd copy, the Commission's own answered 406)
  asks existing electors for no form and no document, links to no earlier
  roll and does not mention the NRC. D-voters were kept out of the check and
  carried onto the draft unchanged. `rules.csv` sets each rule beside the SIR's.
  Assam is not in `states.csv` or any All India total.
- **Flagged, never removed.** The 10,56,291 (dead, shifted, multiple) were
  reported as identified for deletion; no CEO figure says they were off the
  draft, and the draft is 2,76,490 above the January 2025 roll. Every page
  says flagged.
- **The constituency tables are the CEO's own** (`raw/ac_rolls.csv`, read by
  `raw/read_ac_tables.py` from the three PDFs in `raw/sources`, which the
  owner downloaded): the final roll of 8 February 2024, the draft and the final
  roll, every seat by sex. The build asserts they add to the press's state
  totals by sex and to 31,486 polling stations. A seat's change is net, names
  added less names removed; never call it the names removed. Women were 62.9%
  of the net fall from draft to final against 50.1% of the draft. The flagged
  count and its reasons are still press only.
- **The two drafts differ by 1,151** (27 December against the figure given with
  the final roll); both kept as printed.
- **Context**: D-voters, Foreigners Tribunals, detention centres and the NRC
  are Ministry of Home Affairs Lok Sabha answers of 2019 to 2021 (primary,
  PDFs in `raw/sources/`), and the July 2026 Assembly reply as The Assam
  Tribune and The Wire reported it (press, flagged). Detention figures are
  from 2019 and 2020 and the page says they are the latest primary ones found.
  Nothing on the pages says anything about any person's citizenship.
- English only, with the translated note, like the other 2026 state pages.

## Every other state, on one shared page

Twenty places have no page of their own: Chhattisgarh, Madhya Pradesh, Andhra
Pradesh, Odisha, Jharkhand, Haryana, Punjab, Goa, Manipur, Meghalaya,
Mizoram, Nagaland, Sikkim, Arunachal Pradesh, Tripura, Puducherry,
Chandigarh, Lakshadweep, Andaman and Nicobar, and Dadra and Nagar Haveli and
Daman and Diu. Each is one file, `data/<slug>/raw/normal.json`, in the shape
set out in `scripts/state_schema.md`.

- `scripts/build_states.py` (`STATES` lists them) checks every identity the
  schema names and writes `summary.json` and `tables.csv`; `check_data.py`
  runs it with `--check`. A figure that came through the press carries
  `press`, a figure printed in lakh carries `rounded`, and a table that is a
  press extract carries `partial`, so it is checked row by row only.
- `assets/statepage.js` draws all three pages (overview, questions, method)
  from the summary, findings and questions included. The page sources hold no
  figures; `scripts/make_state_pages.py` writes them and the places entry, and
  is run once when a state is added. The pages are English only, with the
  translated note.
- `revision: "no_draft"` (Tripura today) draws "Where the revision stands" in
  place of the figures. When its draft is out, fill in the figures and change
  the field.
- A state here whose constituency table is complete gets a page per
  constituency and per district (`SEATS` in `build_states.py`, `SEATED` in
  `statepage.js`, which adds a finder): Meghalaya, Manipur and Odisha since
  13 October 2026. `MEASURE` in `statepage.js` adds a district chart and table
  and, for those three, the winning-margin chart and every constituency; with
  Andhra Pradesh, Chhattisgarh and Mizoram (district only) the five with seats
  or full district tables are in `FULL` since 14 October. The tables name no district, so each carries
  `raw/ac_district.csv`, and the build fails unless every district's
  constituencies add up exactly to the state's own district table. Puducherry
  has only its final roll by constituency, nothing to measure a change by,
  so it has no constituency pages.
- Add a state by writing its `normal.json` with every source read, adding it
  to `STATES`, and running `build_states.py`, `make_state_pages.py`,
  `build_site.py` and `og_cards.mjs`. Keep its row in
  `data/india/raw/states.csv` equal to its figures.

**Madhya Pradesh** was corrected from the Jagran report of the draft: the
three reasons are exact (8,46,184 dead, 31,50,997 shifted, absent or other,
2,76,961 duplicate), women were 55.3% of the names left off against 48.8% of
the roll, and the notices figure is the 8,65,832 whose forms were incomplete.
8,46,184 is the count of the dead and is never used as the no-mapping count.

**Territories** (`india/uts/`) sets the six union territories in the revision
side by side from `states.json`: names left off per 100 against the All India
rate, the reason shares, the net change after the draft and women's share
where both rolls were published by sex. Jammu and Kashmir and Ladakh were not
in the order and the page says so. It is English only.

**Constituencies** (`india/constituencies/`) opens with a finder over every
constituency with a figure anywhere on the site, in nine places, linked from
every page by the floating "Find your constituency" button.
`build_ac_change.py` writes `data/india/ac_finder.json` from `FINDER`: each
place's lead count and its own measure (names removed, names left off, fall
in the roll, or removed after the draft per 1,000), named beside every figure.
The finder never ranks one state's seats against another's. Below it, the page
puts every constituency of the
four states that published their rolls by constituency (Tamil Nadu, Kerala,
West Bengal, Uttarakhand) in one table and one download,
`data/india/ac_change.csv`. `scripts/build_ac_change.py` reads only those
states' own `constituencies.json` and fails unless Uttarakhand's draft plus
claims less objections is its final roll and Tamil Nadu's roll before less the
names left off is its draft; `check_data.py` runs it with `--check`. Each state
measures a different thing (`STATES` in the build names every roll), nothing is
added across states, and only Uttarakhand has gross additions and deletions by
constituency. Everywhere else the change from the draft is net, counts new
voters too, and is never called names restored. English only.

**A page for every constituency** (`<state>/seat/<n>/`, 1,721 of them) in
the nine states with constituency tables: Tamil Nadu, West Bengal, Kerala,
Delhi, Uttarakhand, Gujarat (press images of the CEO's tables), Rajasthan (the
change in the roll since 2023), Maharashtra and Bihar (both phases, with a link to the
seat's booths in the explorer). `scripts/make_seat_pages.py` writes a
three-line source per seat (its state and number in `data-seat-state` and
`data-seat-ac` on `<body>`, which `build_site.py` carries from the page's
`body` meta) and `assets/seat.js` draws everything from
`data/<state>/constituencies.json` when the page loads: the seat against its
district and state in that state's own measure (named in every sentence), its
rank, the district's seats, and the reasons, women, after-the-draft and
margin sections a state's tables can fill; the rest are hidden and the limits
line says what is missing. `CFG` in `seat.js` holds each state's fields. A
state's measure is never compared with another's. The pages are English only
(`data-no-i18n`); `i18n_collect.mjs` skips them, because their shell is every
page's shell. Search, the All India finder and each state's finder card
(`seatPages: true`) link to them. `check_data.py` runs `make_seat_pages.py
--check`. A new state needs a line in `STATES`, an entry in `CFG` (with `map`
for its own winner, runner-up and margin field names, and `say`, `short` and
`to` where its count is not the names left off the draft), `SEAT_PAGES` in
`build_site.py`, and `seatPages` on its finder. Hyderabad's five seats are
not included: the part explorer covers them.

**A page for every district** (`<state>/district/<slug>/`, 557) in twenty
states: Assam, Meghalaya, Manipur, Odisha, Andhra Pradesh, Chhattisgarh,
Mizoram and Telangana (`hyderabad/telangana/district/`, read from
`telangana.json` through `FILE` and `OUT` in the generator) added the same day to: Uttar Pradesh, Maharashtra and Karnataka (published by district only),
and Bihar, Tamil Nadu, West Bengal, Kerala, Delhi, Gujarat, Rajasthan and
Uttarakhand (13 October 2026). Each is drawn in its state's own measure, set
in `CFG` in `district.js`: names left off, names removed (Bihar, per 100 on
the 2025 roll), or the fall in the roll (West Bengal, Kerala, Rajasthan, with
`fall: true`, which words every sentence as a fall and a negative fall as a
rise; Chhattisgarh and Mizoram, where most districts grew after the draft,
add `rise: true` and measure the rise). A state with district figures and no page is a gap the owner counts:
every analysis gets district and constituency pages where its tables allow.
`scripts/make_district_pages.py` writes the sources (the slug is `SIR.slug`'s,
so `#d-<slug>` on the state page and these addresses agree) and
`assets/district.js` draws the district against every district of its state,
its reasons where published, and its NFHS-5 circumstances from
`data/india/factors.json` beside the typical district, with the state's rank
correlation for each; a circumstance is never named as a cause. Finders
(`districtPages: true`) and search link to them; `check_data.py` runs
`--check`. English only, skipped by `i18n_collect.mjs` like the seat pages.

**Case studies** (`india/cases/`, in the All India menu and tab row, Start
Here and a front-page card) take nine places whose figures stand out in their
own state's measure: Kichha (Uttarakhand), Tughlakabad (Delhi), Danilimda
(Gujarat), Murshidabad, Malda and the two Dinajpurs (West Bengal), and since
14 October 2026 Bhiwandi East (Maharashtra), Anna Nagar (Tamil Nadu), Lucknow
district (Uttar Pradesh), B.B.M.P (South) (Karnataka) and Lakhimpur (Assam,
the fall after the draft, always called net). Each sets
the place's figure from the state's own files (worked out when the page loads)
against its district and state, then what the official records show, what was
reported, what officials and parties said, and what could not be found.
`data/india/raw/cases_research/` holds one research file per case, an
independent second reading of every item (`verified_<case>.json`) and
`plain.json`, the site's own sentence for each item and the list of what was
not found. `scripts/build_cases.py` shows an item only if the reading confirmed
or corrected it, it is not in that case's `drop` and it has a sentence, holds
every sentence to the writing rules, and writes `data/india/cases.json`;
`check_data.py` runs it with `--check`. Left out, by the second reading or by
`drop`: anything naming or identifying a private person, resting on religion,
caste or citizenship (a Samserganj detention petition among them), or on an
analysis of the named lists (the Sabar Institute's, SPECT's, the Civic Research
Group's, Newslaundry's Form 7 count), and items about another place (the
Haldwani FIR is in Nainital). The places are never compared with each other.
Each seat's and district's own page links to its case (`CASE` in `seat.js` and
`district.js`). An item's outlet and link never name a file in this
repository: where a source's own address is dead, the item links to the site's
page that carries the figure. English only.

**About the Data** (`about-the-data/`, English only, in Start Here after How to
Use This Site, in the search, and linked from the front page's "How we know",
the guide and Downloads) says what each count means: names left off the draft,
the reason beside a name, names removed, the fall in the roll, the change after
the draft, notices, per 100 and why states are not ranked, women's share,
religion and caste guessed from names, the winning margin, the typical district
and rank correlations, and press and rounding. Its table of each state's
constituency measure is read from `data/india/ac_finder.json`, so it follows
`FINDER`. When a state's measure changes, change the prose there too.

**Page not found** (`404.html` at the root, from `site/404.html`, which sits
outside `site/pages` so it gets no folder of its own). Netlify serves it at
whatever address was asked for, so `build_site.py` renders it through the same
shell and then makes every link and file absolute, sets `data-root="/"`, drops
the canonical link and adds `noindex`. Its script reads `data/search.json` and
offers the pages whose name or address matches the words of the missing one
(Khurdha finds Khurda, a state folder finds that state's overview), and its
Feedback link carries the address that failed. Edit `site/404.html`, never the
built file.

**What's New** (`updates/`, in every footer, in the search and linked from
the front page's "Who made it") lists what was added to the site, by date,
from `data/updates.json`, which is curated by hand: add an entry when
something a reader can use is published. **Additions only.** A changed figure
or finding goes on `corrections/`, never here, so the rule that no public page
refers to earlier versions still holds; the two pages link to each other.
English only.

**Share a list with us** (`share/`, on the front page's place, in every
footer, in the search and in a short section on the front page) is the one
form on the site: a Netlify form named `share-data` (honeypot
`company_website`, file uploads up to 8 MB) asking what a list or table
shows, its source (required), the place, the file, and optionally a name,
an organisation and an email, with a box the sender ticks to say they are
free to share it. It posts to `share/thanks/`, so it works without
JavaScript. The page says every submission is read, a table is used only
when it can be checked against its source, only counts are ever published,
and the sender is not named unless they ask. `terms/` says the form exists
and where what is sent goes. Submissions are in the Netlify dashboard under
Forms. Anything that arrives carrying names or EPIC numbers is treated like
the Bihar lists: counted, never committed.

**Support our work** (`support/`, in every footer and in the search) is a
Netlify form named `support` (honeypot `company_website`: name, email, how
they would like to help, a message) posting to `support/thanks/`, which shows a
UPI QR code (`assets/upi-qr.svg`, made with segno and decoded back before it
went in) and an "Open my UPI app" link, both `upi://pay?pa=impactmojo@ibl&cu=INR`
with no payee name and no amount. The owner asked that the UPI ID not be
written out on the page; the QR and the link still carry it, as any UPI
code must. Contributions are received by ImpactMojo and accepted only from
Indian citizens (FCRA): the form asks, and a supporter who answers no is sent
to `support/thanks/?other=1`, which hides the QR and says we will write about
other ways to help. Keep both lines. Do not use a QR carrying a person's own
name as payee. There is no automatic reply: the owner chose not to run an email service, so
replies are written by hand from the Netlify dashboard (turn on the form's
email notification there). `_redirects` answers 404 on `/netlify/*`. The page says
support buys no influence over what is published; keep that sentence.

**Feedback and corrections** (`feedback/`, in every footer as "Feedback", in
the search, and linked from the front page's "Who made it" and the corrections
page) is a Netlify form named `feedback` (honeypot `company_website`): what it
is about (a figure that looks wrong, something unclear, a page that does not
work, a suggestion, other), the page, the message, where the right figure is,
and an optional name and email. The footer's link carries the page as
`?from=<path>`, which the page script cleans and fills in. It posts to
`feedback/thanks/` (no-indexed) and works without JavaScript. The page names
no service, by the owner's rule; `terms/` names Netlify, because the privacy
section must say where what is sent goes. A reported error is checked against
its source and, if the site is wrong, listed on `corrections/`. Turn on the
form's email notification in the Netlify dashboard.

**Downloads** (`downloads/`, on the front page's place, linked from every
Downloads button and the footer) lists every file the site publishes.
`scripts/build_repository.py` writes one Excel workbook per place into
`downloads/` (the place's published CSVs, the Chief Electoral Officer's own
tables from its `raw/` folder as listed in `EXTRA`, an About sheet saying what
each sheet is and cannot show, and a Columns sheet), `downloads/other-states.xlsx`
for the twenty on the shared page, `downloads/all-tables.zip` (every CSV,
source tables under `sources/`, a README and `columns.csv`), and
`data/downloads.json`, which the page reads. Column meanings come from
`data/india/raw/columns.json` for the published CSVs and `COMMON` in the
script for the raw ones; `check_data.py` runs it with `--check`, which fails
on a stale manifest or any column with no description. Sizes are left out of
that comparison because openpyxl's output is not byte-stable. Re-run it after
any data change. Raw files are still 404 on their own; they reach readers only
inside a workbook or the zip, so a raw file goes into `EXTRA` only if it is
the CEO's or the Election Commission's own table, counts only. Secondary
compilations a `SOURCES.md` marks as unused stay out.

**Protests and disputes** (`india/disputes/`, in the All India menu as
Disputes) lists the court cases, Assembly resolutions, protests and boycotts,
bulk Form 7 objections (with Hyderabad in full), changes to ECINET and ERONET,
instructions given without a written order, errors reported on the rolls and
deaths reported during the revision. `data/india/raw/disputes_research/` holds
four research files (`courts.json`, `protests.json`, `form7.json`,
`software.json`: each item a plain claim, a verbatim quote, outlet, date and
address) and an independent second reading of each (`verified_<name>.json`).
`scripts/build_disputes.py` keeps only items that reading confirmed or
corrected, applies its corrections, adds the process page's own checked press
reports by topic (`FROM_PROCESS`), and writes `data/india/disputes.json` and
the CSV; `check_data.py` runs it with `--check`. Everything else is named
under "What we could not confirm". "Prefilled" in the reporting means Form 7s
with the elector's details already printed and the objector's part
handwritten or blank. Rules: an allegation is the party's, by name; the
Commission's reply sits beside it where reported; no private person is named,
in a claim or a quote (a researcher, voter, objector, booth agent or BLO is
named by role); nothing says what anyone intended or whether anyone is a
citizen. English only.

The page can be searched and filtered by state, issue, court, party or body,
and place. `tags.json` beside the research gives every item its `court`,
`actors` (parties, offices and organisations, never a private person),
`places` (constituencies, districts or cities) and one to three `issues` from
the fixed list `ISSUES` in the build, which fails on an item with no tags or
an issue outside the list. Tag every new item when it is added. The filters
live in the address (`?court=Supreme%20Court&q=form%207`), so a filtered list
can be sent as a link, and the sitewide search carries every item and every
court, party, place and issue as a link into the filtered page.

**RTI replies** (`india/rti/`, pinned on the front page, in the All India
menu and tab row) lists applications under the Right to Information Act about
the revision whose reply, refusal or appeal was published or reported. **It is
a list and never a count**: no authority publishes the number of applications
by subject, state or district (the CIC's returns give each authority's yearly
total only), and the page says so. `data/india/raw/rti_research/rti.json` holds
each application (authority, applicant as an organisation or a role, what was
asked, the outcome from the fixed list `OUTCOMES` in the build, the answer, a
verbatim quote, outlet and address) and `verified.json` an independent second
reading; `scripts/build_rti.py` keeps only items it confirmed or corrected,
applies each `fix`, computes the days to reply (the Act allows 30, section
7(1)) and writes `data/india/rti.json` and the CSV; `check_data.py` runs it
with `--check`. Same rules as the disputes page: no private person named,
nothing on what anyone intended. Replies sent through the share form join the
research file with their filing date. English only.

**Left Off the Roll? What to Do** (`help/`, on the front page's place, pinned on
the front page, first under Start here and in every footer) sets out what the
law and the Commission's orders let an elector do: Form 6, the inquiry before a
deletion, the two appeals, the helpline and the drive after the revision, free
legal aid, the Supreme Court's orders and going to court, each step with the
document it rests on. Below them it lists organisations that helped electors,
filterable by state. `data/india/raw/help_research/` holds `remedies.json`,
`orgs.json`, `orgs2.json` and `orgs3.json` (Uttar Pradesh, October 2026) and an
independent second reading of all of them (`verified.json`, and
`verified_orgs3.json` for the third); APCR is listed on the owner's decision
over the second reading's rejection, and its entry says the UP help is as its
own report gives it; `scripts/build_help.py` writes `data/india/help.json`, fails
on a remedy the reading has not confirmed, and lists only organisations marked
`publish` that the reading confirmed or corrected; `check_data.py` runs it
with `--check`. The owner's rule for the list (October 2026): no political
party and nothing led by a sitting party office-holder, only organisations a
source shows actually helping, no private person named, and the page says the
list is incomplete and no endorsement. Each left-out entry keeps `why_not`.
The page is general information and says it is not legal advice. It reads in
English, Hindi and Bengali: `i18n_hi.json` and `i18n_bn.json` beside the
research map every English sentence to its translation, each read a second
time by a separate reader (`i18n_*_review.md`), and the build fails if a step,
an organisation or a page sentence (`strings_en.json`) has no translation or a
translation changes a placeholder or the helpline numbers. Quotations from the
sources stay in their own words. The page says no native reader has checked
the translation yet and the English governs. Other languages see English with
the translated note. A new sentence on the page goes into `strings_en.json`
and both dictionaries.

**The NRC** (`india/nrc/`) explains the National Register of Citizens from
primary documents only: what the Citizenship Act and the 2003 Rules provide,
Assam's NRC and its figures, the National Population Register, every answer
in Parliament on a nationwide NRC, how the SIR differs (a side-by-side table
whose cells cite the numbered statements under it), and Assam's 2025-26
Special Revision. `data/india/raw/nrc_research/` holds the research
(`nrc.json`: each fact with its verbatim quote, document, page and URL; the
documents in `sources/`) and an independent second reading of every fact
(`verified.json`). `scripts/build_nrc.py` keeps only facts that check
confirmed or corrected, applies its corrections, and writes
`data/india/nrc.json`; `check_data.py` runs it with `--check`. `PLAIN`
rewords a claim into the site's writing rules without changing it, and
`CITE` carries a document or paragraph the check corrected. Things the
documents settle, and the page keeps to:

- **31 August 2019 is when two lists were published**, the supplementary list
  of inclusions and the list of exclusions (3,11,21,004 found eligible,
  19,06,657 left out). Never call it the publication of the final NRC: the
  Ministry told the Lok Sabha in March 2021 that the final NRC had not been
  issued, and no document found says the Registrar General has notified it.
- **The applicants total (3,30,27,661) is press only**, the State
  Coordinator's figure as reported; the Supreme Court's orders say 3.29 crore.
- **The 2018 draft's exclusions are given in two parts** (37,59,630 rejected,
  2,48,077 on hold). The Court's order of 31 July 2018 prints a total,
  40,70,707, that is not their sum; no total is shown.
- **The nationwide answer** is the same sentence from 4 February 2020 to
  21 March 2023, the latest found. Add a later answer only with its document.
- The Supreme Court's judgment of 27 May 2026 (2026 INSC 564) held that
  declining to enrol someone does not declare that person not to be a
  citizen, and that deciding citizenship belongs to the authority under the
  Citizenship Act. Quote it in its own words.

Nothing on the page says whether any person or group is a citizen, and it
names no individual. English only, like the process page. The Assam page links
to it.

## Notices

`data/india/raw/notices/notices.csv` holds every count found of electors kept
on a draft roll but sent a notice, state by state, split where published into
the no-mapping list and the logical discrepancy list, with hearings held and
names deleted after a notice, each with its source, date, quote and whether
it is primary or press (see `SOURCES.md` there). `scripts/build_notices.py`
picks one total per state by written rules (a published total, never a sum,
except where only the two lists were given; one matching its own lists, then
primary, then the latest), and writes `data/india/notices.json` and the
download. It is drawn on the process page, "Notices: the no-mapping list and
the discrepancy list". The two lists overlap, so they can add up to more than
the total. Uttar Pradesh has two press splits of its 3.26 crore (1.4 + 2.02 in The Hindu, 1.04 + 2.22 in The Times of India); the second adds up and is used. Madhya Pradesh's 2.35
crore is an early software flag and is excluded. Most phase 3 figures are
running counts; update the rows, not the rules.

In Hyderabad, `discrepancy_only` in `summary.json` is the summoned less the
no-mapping list (the no-mapping list sits inside the summoned count in every
part, and a check holds that), shown on the hearings page.

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
`scatter` (SVG, optional y = x line over the shared range). On a phone: axis
titles go through `foot()`, which wraps them and grows the chart rather than
clipping; keys go through `keyRow()`, which wraps; label columns are sized by
`fitLw()` to the longest single word; a strip with more than eight rows puts
its names beside the dots, cut to fit. Vary the form
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
  subtitle, folk-art band, tab row and Downloads button. `site/pages/<path>/index.html`
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
  the current place, opening the list of analyses. It folds (`details.grp`):
  a place's own `menu` pages sit under its `nav_label`, and every state and
  union territory sits in one fold, "All States and Union Territories",
  under its zone (`zone` in `places.json`: the Ministry of Home Affairs'
  zonal councils, Northern, Central, Eastern, Western and Southern, with the
  North-East for the eight states of the North Eastern Council; Andaman and
  Nicobar and Lakshadweep are special invitees of the Southern council and
  sit there), A to Z inside each. Nothing moves from day to day, because a
  reader looks for a place where they found it last time. The 13 places with
  a full analysis of their own (`FULL` in `build_site.py`) are in bold, and a
  line at the top of the fold says what bold means. Telangana carries "Old
  City of Hyderabad" beneath it. A new state takes a `zone`; the build fails
  on a place with a `group` and no zone, or on a zone outside the six. A place with `menu` pages is itself one fold, its overview first. A fold
  opens by itself when the reader is inside it. A new state takes the group
  field; each fold's list carries `data-i18n-each`. At 1000px and wider the
  menu is one panel pinned under the header (`position:fixed`): Start here,
  All India and About this site on the left, and every state and territory on
  the right in three columns, one block per zone (`div.zn`), opened by
  `sir.js` whenever the menu opens. Before this it was a single column that
  ran to 1,888px on a state page. "About this site" closes the menu under a
  rule. On a phone the title takes one row and the controls a row
  beneath it (language, install, search, places, downloads, reading font,
  theme; print is hidden there): beside the title, seven controls squeezed
  it to a single word. Credit is to ImpactMojo
  ("Research by ImpactMojo", linked to impactmojo.in), in the footer and on the
  front page. ImpactMojo is also the publisher and grievance contact on the
  terms page (since 13 October 2026; PinPoint Ventures before), and
  info@impactmojo.in (`email` in `places.json`) is the contact everywhere.
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
  Supabase SQL editor. The function caps a day at 3,000 rows and 500,000
  counts and drops calls past either without an error, so a script calling
  it in a loop cannot fill the database.

- **The design is "Off the Roll"** (October 2026, from a mockup the owner
  chose; the last block of `assets/sir.css`). Warm paper `#f6f2ea` and ink
  `#16130f` with one red `#b3261e`; dark mode is the same design in warm
  black, from the two dark token blocks, which `check_contrast.py` measures
  with the light one. Fraunces (OFL, self-hosted in `fonts/`, Latin only) for
  display, the system sans for text, a system mono for small labels. The
  masthead is the wordmark "Off the ~~Roll~~" (aria-hidden; the translated
  site title stays in the markup for screen readers). Every page opens with a
  mono kicker naming the place (put in by `build_site.py`), a large serif
  title and the numbered findings. Text keeps to a 44rem column; maps,
  charts, tables and number strips run full width. **Every block starts at
  the same left edge**: the column is left-aligned (`margin-inline:0`), never
  centred. Centred, a 704px text column sat 208px in from the 1120px maps and
  cards, so the left edge jumped in and out all the way down every page. Give
  any new measure-width block `margin-inline:0`, not `auto`. **A reading
  page is one column** (`body:not(.wide):not(.home)` sets `--measure` to
  48rem and caps every child of `main` at it), so text, charts, maps and tables share one
  width and one left edge, and every reading page starts it at the header's
  left edge. "On this page" sits to the right of the column, so a page with
  it and a page without it line up. Panels stack one to a row inside the
  column. The front page
  keeps the wide page: below the cards each section is its heading on the
  left and its text on the right (`section.fs`), across the full width.
  Dashboards and explorers (`body.wide`) keep 1480px. A sortable table
  (`SIR.table(el, cols, rows)`) stacks into cards on a phone like the others,
  with its headings kept above as sort buttons. Numbers sit in a strip
  between rules; charts on white cards with a hairline. A long reading page
  (four or more h2s, not the front page) gets "On this page" in the left
  margin of a screen 1240px or wider (`SIR.toc`, body class `has-toc`).
  On a phone the header is the wordmark, Search and one menu button; opened,
  the controls sit in a grid of equal tiles, four to a row, because one row of
  eight ran past a 360px screen and cut off the menu button itself.
  The front page follows the mockup: the headline states the count and the
  share as "one in every k electors" (k = 100 / per 100, rounded; 7 on 13
  October 2026), a grid
  of 100 dots shows the share, a four-number strip (the count left off and "1 in k" stay first; the other two come in turn from a list of ten computed from the All India files, three a day by `SIR.day()`), the map beside a ranked
  list of states (so a phone does not depend on hover), cards to each
  analysis led by a count of names with its share of the roll beneath it (each pair from one source; Kerala, which published no count of names left off, shows the fall in the roll and says so; the pinned cards keep their own figure), every state and territory among them (the 20 on
  the shared page take their figure from `states.json`), one featured in the
  large card and the rest in an order shuffled afresh each day from a seed of
  `SIR.day()`, so every visitor sees the same order on the same day. Only a
  state with an analysis of its own (no `data-st`) is featured, so the large
  card always carries a figure; Tripura, with no draft, once took it. A
  finder that links to each state's own, and "How we know". The cards come
  in two grids: "Across India" (`.hubs.pins`), twelve pinned cards (`hub pin`,
  a red border and a pin icon drawn by CSS) in rows of three on a wide screen,
  above a rule: Left Off the Roll? What to Do, Your Rights at a Protest
  (the rights section of the brief page), Protests and Disputes, RTI Replies,
  Every Constituency, All India, Women, The Cities, The SIR in Numbers, Case
  Studies, Where the Revision Stands and What's New. Keep the count a multiple
  of three. **A new page that goes live gets its menu entry, a Start Here entry
  if a new reader needs it, and a card or line on the front page** (the
  owner's rule, October 2026).
  Card titles and every menu, tab and footer label are in title case;
  headings and prose keep sentence case. Then "Every State and Union Territory" (`.hubs.states`).
  The map and the ranked list beside it end at the same line: the list
  scrolls inside the map's height. Nothing on it may claim a feature
  the site does not have. With the dyslexia font on, the display sizes come
  down and nothing is set in italics or capitals (`html.dyslexic-font`
  rules). A new text block that should sit in the column needs its class in
  the column selector.
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
  place, the places menu, and a Downloads button. **Downloads is a link, not a
  menu**: it opens `downloads/#w-<workbook>` (`DL_BOOK` in `build_site.py`;
  the twenty on the shared page go to `#w-other`), where that place's
  workbook is opened, marked with a red rule and carries its report and
  slides beside the workbook (`book` in `downloads.json`). The menu it
  replaced ran to twenty links on All India. It is written once, in `scripts/build_site.py`.
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
- **Every state page says which roll its figures come from**, in a line
  under the kicker (`p.asof`, written by `asof()` in `build_site.py`): the
  final roll's date when `states.json` holds its electors, otherwise the
  draft's date and the final roll's due date from the last schedule step in
  `process.json`, or from its `reported_dates` where a later date was
  reported (a due date before `process.json`'s `as_of` reads "was due
  on ... and we have not found it published"). `ASOF_LATER` holds a roll
  published between draft and final that a state's pages use (Karnataka, 9
  October), `ASOF_EXTRA` Assam's final roll. The sentence is in the markup
  in English and `sir.js` swaps in its `L()` translation. Update
  `states.json`, `process.json` or those two maps and the line follows.
- **Header tooltips and the tour** (the end of `sir.js`). Each header
  control shows one plain line on hover or keyboard focus (never on touch);
  Escape hides it. The front page offers a seven-step tour once per browser
  (`otr-tour` in localStorage, wrapped in try/catch), and "Take the tour" in
  the hero runs it again. On a phone the tour opens the header's menu row for
  the steps that sit in it. A control added to the header gets a line in
  `TIPS`, and a step in `STEPS` if a new reader needs it.
- **Floating buttons** (`.fabs`, written by `build_site.py`). "Share a list"
  (`a.fab-share`, icon `i24`) floats at the bottom right on every screen except
  the share pages, and "Find your constituency" (icon `i23`, a map pin with a
  magnifier) floats beneath it on every screen, on every page but the
  constituencies page. There is no Constituencies button in the header. On a page with its own row of
  buttons (the front page's hero) both stay hidden until that whole row has
  scrolled off. The tour points at the hero's own "Find your constituency" button, and its box
  sits above the buttons.
- **Usage on the front page.** "How much the site has been used", under Who
  made it, reads `offtheroll_public_stats()` (sums only, never a page or a
  day; `supabase/migrations`) and shows page views, shares, downloads and
  searches, leaving out any that are zero, with the date counting began and a
  line saying visits with Do Not Track are not counted.
- **"Start here" is its own header menu**, beside Places (`start` and
  `quick` in `build_site.py`, a compass icon): Find a constituency, If your
  name was left off, Protests and disputes, RTI replies, Further reading and
  viewing, Women and the SIR in numbers, then About this site under a rule.
  Places lists places only: All India's pages and every state and territory,
  both opened side by side on a wide screen. The All India tab row leads with
  the same pages.
- **Further Reading and Viewing** (`india/reading/`, English only) lists
  investigations, data analyses, research, court reporting, the Commission's
  own account and videos. `data/india/raw/reads_research/` holds `reads.json`
  (each item opened by one researcher) and `verified.json` (a second reader
  who opened every item again); `scripts/build_reads.py` keeps only confirmed
  or corrected items, applies the corrections, rewords summaries into the
  site's rules (`PLAIN`) and writes `data/india/reads.json`; `check_data.py`
  runs it with `--check`. A listed piece is vouched for its title, outlet,
  date and one line, never its argument, and the page sets the West Bengal
  pieces, which disagree, side by side.

  The same page carries **panels on what commentators say** (Prannoy Roy,
  The Indian Express, Ravish Kumar, Yogendra Yadav, Debraj Ray, Newslaundry,
  Lokniti-CSDS), each quotation set beside the site's own figures and where
  they stop. `data/india/raw/panels_research/` holds `claims.json` (the
  quotations, verbatim, with the first reader's notes), `verified.json` (a
  second reading of every quotation) and `plain.json` (the site's own words
  around each one, its role line, introduction, strongest points and
  overreach). `scripts/build_panels.py` keeps only confirmed or corrected
  quotations, applies the corrections, drops what `plain.json` drops with a
  reason, fails on the site's own text if it breaks the writing rules, and
  fails if a figure listed under `uses` is no longer in the published file;
  `check_data.py` runs it with `--check`. **This page is different from the
  rest of the site** (owner's rule, 14 October 2026): it exists to check what
  politicians and the media say, so the reading list and the panels may link
  to and quote party office-holders, pieces that quote them, and pieces behind
  a subscription (marked `subscription`). A relayed figure says whose it is
  (Ravish Kumar's Karnataka Form 7 line names the minister). The site's own
  sentences still name no private person. Keep the panels
  respectful: a panel says where an argument goes further than the figures,
  never that the person is wrong. When a site figure a panel quotes changes,
  rewrite the sentence in `plain.json` and its `uses` entry together.

  Search (`search_index()` in `build_site.py`) covers every tab page, every
  page in a place's `menu`, and every piece on the reading page.
- **The SIR in brief** (`india/brief/`, English only, "In Brief" in the All
  India menu and first under Start here) gathers what the site holds for
  anyone who wants to speak or protest, from the published JSON, and adds
  "Your rights at a protest". Those points are in
  `data/india/raw/brief_research/`: `rights.json` and `verified.json` (the
  first round, 27 points) and `rights2.json` and `verified2.json` (the
  second, 10 points drawn from a checked legal note for protesters: written
  grounds of arrest, silence and its limit under BNSS s.180(2), detention
  under s.172, minimal force, the s.215 complaint bar, BNS ss.221, 195 and
  132, children under JJ Act s.10, and complaints under ss.173(4) and 175).
  Each point quotes the act or judgment and was read twice;
  `scripts/build_brief.py` keeps only confirmed or corrected points, applies
  the corrections and orders them by `GROUPS`. Two things the second round
  settled: s.221 BNS is obstructing a public servant (disobeying an order is
  s.223), and s.173(4) names the Superintendent of Police, not Delhi's DCP,
  so do not add an officer the text does not name. The section is general
  information and says it is not legal advice.
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
  `scripts/stamp.py`, which is Netlify's build command. Page references are stamped in the HTML; files fetched by
  script (`SIR.json`, the dictionaries) get theirs from `window.SIR_V`, which
  the script writes into `assets/i18n.js` between `/*stamp*/` markers. A new
  fetch must go through `SIR.json` or read `SIR_V` itself, or it escapes the
  stamp. Pages are served with `max-age=0, must-revalidate`, so a reload
  always picks up the newest addresses; `/assets/*` and `/data/*` may be kept
  an hour (`netlify.toml`), which is safe only because their addresses are
  stamped. `SIR.json` fetches each file once per page and hands every caller
  its own parsed copy.
- **Security headers** are in `netlify.toml`: a Content-Security-Policy
  allowing the site itself, cdnjs, Google Fonts and the Supabase tally, plus
  nosniff, a referrer policy, no framing and a permissions policy. Chart.js is
  4.5.1 from cdnjs with an `integrity` hash on every page; a version change
  needs the new hash from cdnjs's API. A new outside origin goes into the
  policy and into the privacy section of `terms/` in the same commit.
  `script-src` carries no `'unsafe-inline'`. Every inline script a page
  source holds is moved by `build_site.py` (`externalise()`) into
  `assets/js/page/<hash>.js` and loaded from there; JSON blocks stay inline.
  So write page scripts inline in `site/pages` as before, and never put an
  `onclick=` or other inline handler in markup or in a string a script
  writes: it will not run, and nothing on the page shows it. Bind with
  `addEventListener`. A hash read from the address goes through
  `SIR.hashId()`, which survives a malformed `%` escape.
- **Search engines and sharing.** `build_site.py` writes, beside the Open
  Graph tags, a canonical link, Twitter title and description, `og:locale`
  and JSON-LD on every page (`ldjson()`: the WebSite on the front page, a
  WebPage elsewhere, and a Dataset with its CSVs on each place's first page),
  plus `sitemap.xml` and `robots.txt` at the root; `NOINDEX` keeps the share
  form's thank-you page out. `SIR.inShort` puts a share row under every
  page's findings: WhatsApp with the place, the page title and the first
  finding written in, and Copy link. `SIR.pageUrl` keeps `?lang=` so a link
  shared from a translated page opens in that language. No hreflang: the
  translations are drawn in the browser, so every language's address serves
  the same English HTML to a crawler.
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
- **Lakh and crore.** `SIR.lakh` writes a count of a crore or more in crore
  (2.89 crore, never 288.7 lakh), and `SIR.lk(x, k)` does the same in plain
  English for the English-only pages; chart ticks and labels follow the same
  rule. A count under a lakh is written in full. Use these rather than a
  page's own `/ 1e5`.
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
  English page governs. The owner decided on 14 October 2026 that nobody will
  review them, so the notice says the page was translated by machine and stays
  for good. `scripts/i18n_workbook.py` still writes a review workbook if that
  ever changes.

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
names were left off or deleted than the 2025 winning margin", not "Where the
names left off dwarfed the margin". A title that makes a claim checks it first (the
Hyderabad margin slide checks every seat lost more names than its winner
polled; the districts slide names the factor with the largest rank
correlation and lists those under 0.2 as unrelated). The decks state no site
address, and the speaker notes carry the caveats. `build.sh` rebuilds them
with the reports.

Every other analysis (Rajasthan, Uttar Pradesh, Delhi, Maharashtra, Gujarat,
Uttarakhand, Assam, and one for the twenty states on the shared page) has a
PDF and a deck made by `scripts/reports/page_pack.mjs` from its own pages: the
PDF is the pages printed with the site's print stylesheet (merged by
`merge_pdf.py`), and the deck has a cover of the overview's findings and one
slide per chart, titled with the section's computed finding. Serve the site
and run it after any data change. The print stylesheet hides every control,
and `build_site.py` fails if a place's body class is a class `sir.css`
styles: Delhi's was `dl`, the header menus' class, so every Delhi page
printed blank.

The four 2026 states (Tamil Nadu, Karnataka, West Bengal, Kerala) each have a
PDF report and a deck in their Downloads menu, written by
`scripts/reports/state_report.py <state>` and `scripts/reports/state_decks.js`
from the same JSON as their pages, with the same sections. They have no web
page. A section a state cannot have (Kerala's reasons, the split by sex in Tamil
Nadu and Karnataka) says so rather than being dropped. `build.sh` rebuilds them
with the others.

**Say only what the lists record.** No page, report or deck may say how long a
hearing slot lasted or how many minutes an elector had: the lists record cases
per slot, not the slot's length.

## Watch out for

- **Every merge to `main` is a production deploy, and each costs 15 Netlify
  credits.** On 13 October 2026 the Idealog Works team ran out of credits and
  Netlify took all 35 of its sites offline, this one included. This site had
  made 160 production deploys since 26 September, one for every merged PR.
  Gather a day's work on the branch and merge it once, or twice at most.
  Deploy previews cost nothing. Auto-publishing on this site is now locked: a
  merge builds but does not go live, and `tools/publish-locked.py` in the
  Democracy-by-Design repository publishes the newest build once a day at
  20:00 IST (its "Publish locked sites" workflow, run by hand with
  `forindia`, publishes at once). A build that is never published costs
  nothing.
- **The Sabar Institute link.** Every method page ends with "Analysis of the
  named lists", pointing readers who want named-voter analysis to
  sabarinstitute.org, at the owner's request (October 2026). It is a pointer
  for further reading and nothing more: no page says who compiled any list
  this site counts, and the Hyderabad pages still do not name a compiler.
- **Publishing**: Netlify publishes `_site` (gitignored), which
  `scripts/stage_site.py` fills on every deploy from an allowlist: the page
  folders, `assets`, `data`, `downloads`, `fonts`, `reports` and a few root
  files, leaving out every `raw/` folder, `.md`/`.py`/`.mjs`/`.sh` files and
  `DATA_PRIVATE`. Until October 2026 the repository root was published and
  `_redirects` 404s guarded the private paths, but Netlify's file server
  ignores case and the rules do not, so `/Scripts/`, `/Data/bihar/RAW/` and
  `/claude.md` were served. CI runs `stage_site.py` with no argument and fails
  on a top-level entry that is neither published nor kept back; name a new
  folder in `PUBLIC_DIRS` or `PRIVATE`. The `_redirects` 404s stay as a second
  line. Do not link source files from a page, and describe
  sources without naming the people or organisations who compiled them.
- **Left off and deleted are kept apart** (owner's rule, 14 October 2026,
  from a reader who pointed out the legal difference). A name on the roll
  before the revision whose form did not come back was **left off the draft**
  (or excluded from it): no objection, notice or order touched it. Only a name
  taken off after the draft, on a Form 7 objection or the officer's own
  motion, with a hearing and an appealable order (RPA 1950 ss.22 and 24), is
  **deleted**. Bihar's two phases together are **names left off or deleted**;
  a difference between two rolls stays **the fall in the roll**; Assam's
  10,56,291 stay **flagged**. The Supreme Court drew the same line (2026 INSC
  564, paras 134 and 10.9). The sources and both readings are in
  `data/india/raw/terms_research/`, and About the Data's "Words we use" sets
  it out for readers. Quotations, titles and data keys keep their own words.
  `check_writing.py` fails on "removed", "struck off" or "removals" in the
  site's own words outside quotation marks (the corrections page excepted).
  The disputes tag "Deletions" became "Names left off or deleted"; the page
  script maps the old value so old filter links still work.
- **Writing**: plain explanatory prose. Never refer to earlier versions of the
  analysis or to corrections on a public page, with one exception: the
  corrections page (`corrections/`, linked in every footer and from `terms/`,
  English only) lists every correction of substance by date, with what the
  page said, what it says now and why. Add an entry there whenever a figure
  or finding changes; a change of wording that keeps the meaning is not listed. The owner's rules, applied to
  every page, report and deck: no em dashes; no sentences hinged on a colon
  ("X: Y") or strung on semicolons; no "X, not Y" or "not X but Y" turns; say
  the caveat about reasons once per page in plain words ("what the officer wrote
  down, and nobody checked it"), not as "an officer's entry, not a finding";
  prefer "guessed from names" to "estimated", "typical" or "middle" to
  "median" in prose. When rewriting an English key, carry its translations to
  the new key only if the meaning is unchanged; retranslate otherwise.
  `scripts/check_writing.py` (run by `check_data.py`) reads every page
  source, every page and asset script's strings and the published JSON
  (quotations, headlines, laws and contacts excepted, by key in `QUOTED`) and
  fails on an em dash, an en dash between words, "rather than", "not only",
  ", not a/an/the", a semicolon in a page's prose, or a word on the owner's
  banned list. A term of art goes in `ALLOWED` with its reason. It cannot see a
  colon-hinged sentence, a fragment or a flourish, so read what you write.
- **The site talks about the revision, never about itself** (the owner's rule
  for every website, 14 October 2026). No page, panel, FAQ answer or method note
  tells a reader how the site was built or how its research was done: no "read
  twice", "a second reader", "worked out when the page loads", "the build fails
  unless", "from YouTube's captions" or "transcribed by hand". Say what a figure
  is, whose it is, which document it comes from and what it cannot show. The
  two-reader checks, builds and assertions stay; they are described here and in
  the research files, never on a page. `check_writing.py` fails on the phrases a
  regex can catch, so read what you write for the rest.
- **Bihar and Hyderabad are never compared** with each other, on a page,
  in a report or in a deck, except as rows of the cities page
  (`india/cities/`), which the owner allowed in October 2026. Each analysis
  stands on its own.
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
