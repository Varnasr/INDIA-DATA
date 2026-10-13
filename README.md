# INDIA-DATA: Special Intensive Revision analyses

Who was struck off India's electoral rolls in the 2025-26 Special Intensive
Revision: across India, in Bihar, in five Old City constituencies of
Hyderabad, in Tamil Nadu, Karnataka, West Bengal and Kerala. Static
site at [offtheroll.in](https://offtheroll.in), by ImpactMojo. Every page is built
from `site/` by `scripts/build_site.py`.

| Page | What it covers |
|---|---|
| [`/`](https://offtheroll.in/) | What the site is, why it exists, how to read it, and who made it (ImpactMojo) |
| [`/india/`](https://offtheroll.in/india/) | All India: the reasons recorded for 13.39 crore names left off the draft rolls, state by state, with a source for every row |
| [`/bihar/`](https://offtheroll.in/bihar/) | The Bihar dashboard: twelve tabs of charts and the table of all 243 constituencies |
| `/bihar/explorer/` | Explorer: 69,10,559 names removed across 243 constituencies and 77,837 booths, every seat and every booth |
| `/bihar/results/` | Deletions against the 2020, 2024 and 2025 results, within seats and across them |
| `/bihar/border/`, `/bihar/districts/` | Nepal and Bengal border seats; district economy and census against deletions |
| `/bihar/people/` | Gender, religion as a range, caste under two classifications with bounds |
| `/bihar/faq/` | Questions and answers: the criticisms put to the analysis, answered from the lists |
| `/bihar/method/` | Sources, how the lists were prepared, research questions |
| [`/hyderabad/`](https://offtheroll.in/hyderabad/) | The Hyderabad dashboard: 6,62,063 of 16,57,207 electors struck off in Charminar, Yakutpura, Malakpet, Chandrayangutta and Bahadurpura, in ten tabs |
| `/hyderabad/explorer/` | Any constituency, any of its 1,158 polling parts |
| `/hyderabad/people/`, `/parts/`, `/hearings/`, `/faq/`, `/method/` | Rates by age, sex, religion and 2002 linkage within parts; part outliers; hearings; fourteen research questions |
| [`/tamilnadu/`](https://offtheroll.in/tamilnadu/) | Tamil Nadu: 97,37,831 names left off the draft roll in 234 constituencies, by district and reason, and what the final roll put back |
| [`/karnataka/`](https://offtheroll.in/karnataka/) | Karnataka: 1,07,96,339 names left off the draft roll in 34 districts, by reason, with Bengaluru's four districts and the roll of 25 September |
| [`/westbengal/`](https://offtheroll.in/westbengal/) | West Bengal: the state's removals and adjudication, and the fall in the roll from 2024 to the 2026 election in 294 constituencies, against the result |
| [`/kerala/`](https://offtheroll.in/kerala/) | Kerala: the fall in the roll from January 2025 to the draft and the election in 140 constituencies, women's share, and the 2026 result |
| `/tamilnadu/elections/`, `/faq/`, `/method/` | Removals against the 2026 margins and by the party that won, read against each seat's district |

## Reports

The full reports, in the structure of the Sabar Institute's SIR reports, are
in `reports/` as PDF and are linked from every page:
`bihar-sir-2025-report` and `hyderabad-old-city-sir-2026-report`. Rebuild with
`scripts/reports/build.sh`, which also writes the two slide decks
(`bihar-sir-2025-deck.pptx`, `hyderabad-old-city-sir-2026-deck.pptx`).

## The two kinds of evidence

Bihar's files hold the removed only, by booth, so the Bihar pages compare shares
of the removed against the roll and the census. Hyderabad's files hold every
elector on the pre-revision roll, so the Hyderabad pages give true deletion
rates for each group and compare groups inside the same polling part.

## Build and check

```bash
pip install pandas==3.0.6 openpyxl==3.1.5
python3 scripts/build_bihar.py        # data/bihar/raw -> data/bihar/*.json
python3 scripts/build_hyderabad.py    # hyderabad/explorer -> data/hyderabad/*.json
python3 scripts/build_tamilnadu.py    # data/tamilnadu/raw -> data/tamilnadu/*
python3 scripts/check_data.py         # 21 checks, run by CI
python3 scripts/verify_bihar.py       # recomputes every Bihar figure from the raw files, run by CI
python3 scripts/check_contrast.py     # 72 colour pairs, both themes, run by CI
python3 -m http.server 8000
```

## Sources

- Bihar: CEO Bihar SIR deletion lists by booth (phase 1) and by constituency,
  phase and sex; Form 20 booth results for 2024, reconciled to the declared
  seat results; 2020 and 2025 Assembly results; Census 2011; Bihar caste-based
  survey, 2 October 2023.
- Hyderabad: CEO Telangana SIR lists for the five constituencies, September
  2026; ECI 2023 Assembly results.
- Tamil Nadu: CEO Tamil Nadu tables of removals by constituency and reason,
  and of the draft and final rolls; ECI 2026 constituency results; the 2021
  result from the ECI statistical report.
- Karnataka: CEO Karnataka press notes of 24 August 2026 (removals by
  district and reason, draft roll by sex) and 25 September 2026 (the roll by
  district and sex).
- West Bengal: CEO press note PN-05-2026; CEO rolls by AC for the 2024 Lok
  Sabha nominations, the SIR draft and the 2026 nominations; ECI 2026 results.
- Kerala: CEO Kerala rolls by AC of January 2025, the SIR draft and final, and
  March 2026; ECI 2026 results.

Aggregates only. No names, EPIC numbers or addresses are published or committed.

## Licence

MIT for the code. Election Commission and Census data keep their original terms.

The live site serves the pages and the aggregate JSON they read. Source files,
scripts, notes and `archive/` are not published (`_redirects`).
