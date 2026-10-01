# INDIA-DATA: Special Intensive Revision analyses

Who was struck off India's electoral rolls in the 2025-26 Special Intensive
Revision, in Bihar and in five Old City constituencies of Hyderabad. Static
site at [offtheroll.in](https://offtheroll.in), by PinPoint Ventures. Every page is built
from `site/` by `scripts/build_site.py`.

| Page | What it covers |
|---|---|
| [`/`](https://offtheroll.in/) | What the site is, why it exists, how to read it, and who made it (PinPoint Ventures) |
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

## Reports

The full reports, in the structure of the Sabar Institute's SIR reports, are
in `reports/` as PDF and Word and are linked from every page:
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
python3 scripts/check_data.py         # 11 checks, run by CI
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

Aggregates only. No names, EPIC numbers or addresses are published or committed.

## Licence

MIT for the code. Election Commission and Census data keep their original terms.

The live site serves the pages and the aggregate JSON they read. Source files,
scripts, notes and `archive/` are not published (`_redirects`, and the staging
step in `static.yml`).
