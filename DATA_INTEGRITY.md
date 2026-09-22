# Data integrity: known defects in the Bihar deletions dataset

Audited 2026-09-22. Five defects in `data/ac_deletions_change_2020_2024.csv`, the
file behind every political claim on the dashboard. Each is pinned by a check in
`scripts/check_data.py`, so none can be forgotten or silently reintroduced. When
one is repaired its check fails and tells you to delete it and the finding here.

**None of this is fixed.** Repairing it needs authoritative data the repository
does not contain, and inventing plausible numbers for an electoral integrity
analysis would be far worse than leaving the gap visible.

## What is sound

The 2024 column is credible. `deletions_2024` sums to **6,559,626** across the
243 constituencies, close to the roughly 65 lakh deletions widely reported for
the Bihar Special Intensive Revision. `del_per_booth_2024` recomputes exactly
from `deletions_2024 / booths_2024` in every row. `ac_number` covers 1 to 243
once each, and the district files carry 38 rows.

Note that the SIR was conducted in 2025, so the `_2024` suffix on a column
holding what appears to be the SIR figure may itself be mislabelled. That is
worth resolving before the column is cited.

## Finding 1: `booths_2020` is a verbatim copy of `booths_2024`

Identical in **all 243 rows**. Bihar's booth count did change between the 2020
assembly election and 2024, so this is wrong as a matter of fact.

Four columns are derived from it and are therefore also wrong:
`del_per_booth_2020`, `delta_del_per_booth`, `pct_change_del_per_booth`,
`quartile_2020`.

It also makes the dashboard's per-booth comparison vacuous. With the same
denominator on both sides, the ratio of per-booth rates is arithmetically
identical to the ratio of raw deletions:

```
deletions ratio 2020/2024 = 5.9834
per-booth ratio           = 5.9834
```

So "average deletions per booth fell from 504 to 84" states nothing that
"deletions fell from 39.2M to 6.56M" does not, while implying a booth-level
normalisation that was not performed.

## Finding 2: `deletions_2020` totals 39.2 million, which is not plausible

39,248,769 across 243 constituencies, or 504 per booth. Bihar's electorate at the
2020 assembly election was roughly 7.3 crore. This figure is therefore about 54%
of the entire electorate removed in a single revision.

`METHODOLOGY_NOTES.md` documents the Census 2011 baseline, the 2023 caste survey
and the GDDP series in detail. It says **nothing** about the deletions data, the
booth counts, or the electoral roll. There is no source anywhere in the
repository for this number.

Either it is not deletions, or it is not 2020. It should not be published as
either until it is traced.

## Finding 3: `party_2024` cannot be the 2024 Lok Sabha result

Bihar's 40 parliamentary seats in 2024 went BJP 12, JD(U) 12, LJP(RV) 5, RJD 4,
INC 3, CPI(ML)(L) 2, HAM 1. At roughly six assembly segments per parliamentary
seat, segment-level leads should be near BJP 72, JD(U) 72, LJP(RV) 30, RJD 24.

What the column actually holds:

| party | in the data | expected |
|---|---|---|
| BJP | 97 | ~72 |
| **BSP** | **59** | **0** (won no Bihar seat) |
| **IND** | **46** | **0** |
| CPI(ML)(L) | 12 | ~12 |
| CPI | 10 | 0 |
| **JD(U)** | **3** | ~72 |
| INC | 3 | ~18 |
| **RJD** | **absent** | ~24 |
| **LJP(RV)** | **absent** | ~30 |
| HAM | absent | ~6 |

BSP and independents, which won nothing, account for **105 of 243 segments**.
RJD and LJP(RV), which between them won 9 parliamentary seats, do not appear at
all. `CPI(ML)(L)` and `CPIM-L` are two spellings of one party.

This looks like a join or label-mapping failure rather than noise. It has not
been diagnosed.

## Finding 4: `alliance_2024_ls` classifies only 131 of 243 constituencies

It is derived from `party_2024`, so it inherits finding 3. 105 constituencies are
`OTHER` and 7 are blank. Any figure grouped by this column silently drops **46%
of Bihar**.

## Finding 5: the headline political comparison reverses with the labelling year

The dashboard states:

> NDA constituencies average 81.2 deletions per booth vs INDIA's 93.0.

Recomputed from the same file, on the same outcome variable, changing only which
election's alliance labels are used:

| labelling | NDA | INDIA | constituencies covered |
|---|---|---|---|
| `alliance_2024_ls` (as published) | 81.2 | 93.0 | 131 of 243 |
| `alliance_2020_vs` | **87.4** | **79.6** | 235 of 243 |

The direction flips. The published version says INDIA-held seats saw more
deletions per booth; the 2020 labelling, which covers 104 more constituencies,
says the opposite. The claim is presented without either qualification.

## What repairing this would take

1. Booth counts per assembly constituency for the 2020 electoral roll, from the
   Bihar CEO or ECI, to replace the copied column and recompute the four derived
   columns.
2. A source for `deletions_2020`, or its removal.
3. 2024 assembly-segment leads from ECI Form 20 data, to rebuild `party_2024`
   and `alliance_2024_ls`.
4. Once 1 and 3 are done, every claim on the dashboard that compares years or
   groups by alliance needs recomputing, and finding 5 needs re-testing: a
   comparison that reverses with a defensible change of specification should be
   reported with both specifications, not one.

Until then the affected panels should carry the defect on their face or come
down. The dashboard currently states them without qualification.

## Sources

- 2024 Bihar Lok Sabha result: [Wikipedia, 2024 Indian general election in Bihar](https://en.wikipedia.org/wiki/2024_Indian_general_election_in_Bihar);
  [India TV, 4 June 2024](https://www.indiatvnews.com/bihar/news-bihar-lok-sabha-election-results-2024-vote-counting-live-updates-leading-trailing-winning-candidates-of-bjp-jdu-rjd-congress-jharkhand-latest-news-2024-06-04-934921)
- Duplicate constituency names: [Kalyanpur, Purvi Champaran (AC 16)](https://en.wikipedia.org/wiki/Kalyanpur,_Purvi_Champaran_Assembly_constituency);
  [Kalyanpur, Samastipur (AC 131)](https://en.wikipedia.org/wiki/Kalyanpur,_Samastipur_Assembly_constituency);
  [Bihar CEO Form 20, AC 131](https://ceoelection.bihar.gov.in/Form20/include/AC131.pdf)
