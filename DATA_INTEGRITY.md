# Data integrity: the September 2026 corrections

Audited 2026-09-22, resolved 2026-09-29. The dashboard that served at
forindia.netlify.app until September 2026 rested on
`data/ac_deletions_change_2020_2024.csv`, and the five findings below were
recorded against it while the cause was unknown. The cause was then found in the
original booth files, and every published figure was rebuilt from those files by
`scripts/build_bihar.py`. The old files are kept, unused, in `data/legacy/`, with
a README saying what was wrong in each.

## What caused the five findings

**A fan-out join.** The booth file carries about three rows per booth, one for
each of its top three 2024 parties; the gender-religion file carries two rows
per booth, one per sex. Joining the two and summing counted each booth's
deletions about six times. 39,248,769 divided by the true 6,559,626 is 5.98; the
source has 464,881 booth rows for 77,837 booths, 5.97. There is no 2020 deletion
series in these files: the column header "deletion by Booth in Jan 2020" refers
to the January 2025 roll the SIR lists are keyed to. That explains findings 1
and 2, and the "83% decline" the dashboard reported.

**Unreconciled party labels.** The 2024 extract names the wrong party in nine
seats (LJP(RV) as BSP in five, HAM(S) as JD(S), JD(U) as IND, and two probable
fixes in Karakat and Kishanganj). Vote shares summed from booths match the
declared result to within 0.62 points in all 40 seats; the names attached to
them did not. After correction the top two in every seat are the declared
winner and runner-up, and `check_data.py` asserts it. That explains findings 3
and 4: every seat now has a 2024 segment leader and an alliance.

**Finding 5 now has an answer.** Measured as deletions per 100 electors on the
2025 roll, with all 243 seats labelled, NDA seats lost more names than INDIA
seats under all three labellings (2020 Assembly 9.58 against 8.79; 2024 Lok
Sabha segment leader 9.36 against 8.50; 2025 Assembly 9.28 against 8.82), and
within the same seat, NDA-leading booths lost 2.4 more names per booth than
INDIA-leading ones. The published headline, which said the reverse, came from
the six-fold count and the mislabelled parties.

**Caste.** Separately from the five findings: the caste figures mapped "Devi", a
title, to Lohar (EBC), which put two million women in the EBC total, and the
district caste figures were the 2023 state survey shares repeated in every
district. Caste is now read from guardians' surnames under two classifications
with bounds, and the pages say plainly what the surname counts can and cannot
identify.

## The findings as recorded before the cause was known

Kept as written, because they are the record of what was published.

### Finding 1: `booths_2020` is a verbatim copy of `booths_2024`

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

### Finding 2: `deletions_2020` totals 39.2 million, which is not plausible

39,248,769 across 243 constituencies, or 504 per booth. Bihar's electorate at the
2020 assembly election was roughly 7.3 crore. This figure is therefore about 54%
of the entire electorate removed in a single revision.

`METHODOLOGY_NOTES.md` documents the Census 2011 baseline, the 2023 caste survey
and the GDDP series in detail. It says **nothing** about the deletions data, the
booth counts, or the electoral roll. There is no source anywhere in the
repository for this number.

Either it is not deletions, or it is not 2020. It should not be published as
either until it is traced.

### Finding 3: `party_2024` cannot be the 2024 Lok Sabha result

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

### Finding 4: `alliance_2024_ls` classifies only 131 of 243 constituencies

It is derived from `party_2024`, so it inherits finding 3. 105 constituencies are
`OTHER` and 7 are blank. Any figure grouped by this column silently drops **46%
of Bihar**.

### Finding 5: the headline political comparison reverses with the labelling year

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

## What remains open

- Caste composition of the removed cannot be identified from surname counts of
  the removed alone. It needs the same counts for the draft roll, so a surname's
  removal rate can be set against its presence on the roll.
- Religion is a name-based range. The census share sits inside it in 18 of 38
  districts; in 20 the classified Muslim share alone exceeds the census share,
  by more than a point in eight south and central Bihar districts (Aurangabad,
  Jehanabad, Sheikhpura, Gaya, Lakhisarai, Nalanda, Nawada, Patna).
- The Karakat (RLM) and Kishanganj (AIMIM) label fixes are marked probable on
  the method page, with the evidence for each.

## Sources

- 2024 Bihar Lok Sabha result: [Wikipedia, 2024 Indian general election in Bihar](https://en.wikipedia.org/wiki/2024_Indian_general_election_in_Bihar);
  [India TV, 4 June 2024](https://www.indiatvnews.com/bihar/news-bihar-lok-sabha-election-results-2024-vote-counting-live-updates-leading-trailing-winning-candidates-of-bjp-jdu-rjd-congress-jharkhand-latest-news-2024-06-04-934921)
- Duplicate constituency names: [Kalyanpur, Purvi Champaran (AC 16)](https://en.wikipedia.org/wiki/Kalyanpur,_Purvi_Champaran_Assembly_constituency);
  [Kalyanpur, Samastipur (AC 131)](https://en.wikipedia.org/wiki/Kalyanpur,_Samastipur_Assembly_constituency);
  [Bihar CEO Form 20, AC 131](https://ceoelection.bihar.gov.in/Form20/include/AC131.pdf)
