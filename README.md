# INDIA-DATA: Special Intensive Revision analyses

Who was struck off India's electoral rolls in the 2025-26 Special Intensive
Revision, in Bihar and in five Old City constituencies of Hyderabad. Static
site at [forindia.netlify.app](https://forindia.netlify.app).

| Page | What it covers |
|---|---|
| [`/`](https://forindia.netlify.app/) | The Bihar dashboard: eleven tabs of charts and the table of all 243 constituencies, with links to Hyderabad |
| [`/bihar/`](https://forindia.netlify.app/bihar/) | Explorer: 69,10,559 names removed across 243 constituencies and 77,837 booths, every seat and every booth |
| `/bihar/results/` | Deletions against the 2020, 2024 and 2025 results, within seats and across them |
| `/bihar/border/`, `/bihar/districts/` | Nepal and Bengal border seats; district economy and census against deletions |
| `/bihar/people/` | Gender, religion as a range, caste under two classifications with bounds |
| `/bihar/faq/` | Questions and answers: the criticisms put to the analysis, answered from the lists |
| `/bihar/method/` | Sources, how the lists were prepared, research questions, what an audit needs |
| [`/hyderabad/`](https://forindia.netlify.app/hyderabad/) | 6,62,063 of 16,57,207 electors struck off in Charminar, Yakutpura, Malakpet, Chandrayangutta and Bahadurpura |
| `/hyderabad/explorer/` | Any constituency, any of its 1,158 polling parts |
| `/hyderabad/people/`, `/parts/`, `/hearings/`, `/faq/`, `/method/` | Rates by age, sex, religion and 2002 linkage within parts; part outliers; hearings; fourteen research questions |

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
python3 scripts/check_contrast.py     # colour tokens, both themes, run by CI
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
