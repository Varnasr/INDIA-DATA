# Old City SIR 2026: deletion explorer

Live at **https://varnasr-experiments.netlify.app/hyd-sir/**

Every elector on the pre-revision rolls of five Hyderabad Old City assembly
constituencies, as they stood in the Special Intensive Revision of 2026, sorted
into three fates: struck off, kept but summoned to a hearing, or untouched. The
page opens at the constituency and drills to the polling part.

Source: CEO Telangana SIR exports, merged by the HDCC data team. Hearing
schedules run 28 August to 12 October 2026. The Commission extended the
calendar on 7 September (claims to 7 October, hearings to 5 November, final
roll 9 November), so these are figures from the September exports and the final
count will differ.

## What the numbers say

| Constituency | Electors | Deleted | Rate | Summoned | Parts |
|---|---:|---:|---:|---:|---:|
| Charminar | 2,37,483 | 94,174 | 39.7% | 50,168 | 198 |
| Yakutpura | 3,74,948 | 1,54,982 | 41.3% | 87,367 | 332 |
| Malakpet | 3,16,454 | 1,42,688 | 45.1% | 68,188 | 60 |
| Chandrayangutta | 3,77,299 | 1,48,869 | 39.5% | 80,246 | 305 |
| Bahadurpura | 3,51,023 | 1,21,350 | 34.6% | 84,003 | 263 |
| **All five** | **16,57,207** | **6,62,063** | **39.9%** | **3,69,972** | **1,158** |

Two patterns run through every constituency and are visible in the age and
group charts.

Age dominates. Between 70.1% (Bahadurpura) and 76.6% (Malakpet) of electors
aged 80 and over were struck off, against 19.3% to 25.7% of those aged 18 to
24. The climb is steepest above 70. It rises monotonically across all eight
bands in Yakutpura, Chandrayangutta and Bahadurpura; in Charminar and Malakpet
the rate dips slightly through the 40s and 50s (Charminar 42.0% at 30-39,
37.5% at 50-59) before resuming.

The communal split runs opposite to the direction the seats' politics would
suggest. Pooled across the five, the deletion rate among Hindu-name electors is
52.0% and among Muslim-name electors 35.3%; the gap holds in each constituency
separately, widest in Yakutpura (55.8% against 34.5%). Sex barely separates:
39.9% of women against 40.5% of men. Religion here is a name-based estimate,
not a recorded field, and Old City wards with large migrant populations will
carry genuine shifting as well as erroneous deletion, so the gap is a finding
about the revision's output rather than an established account of its cause.

Where a 2002 linkage exists in the file (all except Malakpet), the sharpest
single cut is that link. In Charminar, 26.2% of electors traceable to the 2002
roll were deleted, against 53.1% of those with no 2002 link.

## Definitions the page uses

- **Deleted** means present on the Absent-Shifted-Dead list and absent from the
  draft roll in the September 2026 exports. ECI reason codes: permanently
  shifted, untraceable or absent, death, already enrolled elsewhere.
- **Summoned to a hearing** combines the ECI discrepancy list with the
  no-mapping list. Seven ECI rules send an elector there: unmapped with the
  last SIR, parent name mismatch, self name mismatch, progeny of six or more,
  parent age difference under 15 years, progeny age gap under 9 months,
  grandparent age difference under 40 years.
- **Linked to 2002** means the elector maps to the 2002 intensive revision
  roll. Malakpet's export carries no such linkage, so that pair of bars is
  hidden for it.
- Malakpet is read by polling-station name rather than part number, because its
  export carries no part numbers. Its 7,891 unaccounted records are far above
  the 126 to 249 in the other four, which is a data-quality caveat on that
  constituency rather than a finding about it.
- The 2023 comparison uses ECI results, constituency by constituency. In
  Charminar the deletions run to 4.1 times the 2023 winning margin of 22,853
  and 96.0% of all valid votes cast.

## Data and privacy

The page carries aggregates only: per polling part, counts by fate, ECI reason,
flagging rule, age band, sex, name-estimated religion, 2002 linkage, and the
hearing slots with their case loads. No names, no EPIC numbers, no addresses,
nothing that identifies an elector. The underlying row-level files stay in
Drive and are not in this repository.

Sources, all in the Old City SIR 2026 Drive folder:
`charminar_final.csv.xlsx`, `Yakutpura_Final.csv`, `Malakpet_Final.csv`,
`Chandrayangutta_Final.csv`, `Bahadurpura_Final.csv`, merged into
`OldCity_SIR_master_workbook.xlsx` (one tab per constituency, 188 MB) and
`OldCity_SIR_all_electors_merged.csv` (16,57,207 rows). Neither fits in a git
repository, and neither belongs in a public one.

## Verification

- The embedded aggregates reconcile with the data note: the five constituencies
  sum to 16,57,207 electors, the row count of the merged file.
- The derived KPI reproduces from the stored counts. Charminar's headline 53.1%
  deletion rate among electors with no 2002 link is
  (94,174 − 30,982) / (2,37,483 − 1,18,438) = 63,192 / 1,19,045 = 53.08%.
- Rendered headless in Chromium at 1280, 768, 390 and 320 px: all five charts
  paint, every constituency tab, the part drill-down, the locality search and
  the sortable table work, no console errors, no horizontal page scroll.
- Not checked: the aggregates were not recomputed from the CEO Telangana
  exports. Cell counts are taken as the HDCC data team produced them.

## Changes made for hosting

The analysis, the data and the page's own text are the deliverable as received.
Four changes were made to serve it on this site:

1. `#strip`, `aside`, `.grid` and the panel canvases were given zero minimum
   track sizes. A grid item's automatic minimum size had held the 18-column
   deletion-rate strip at its intrinsic width, which pushed the page to 948 px
   on a phone and forced the whole document to scroll sideways.
2. Page title suffixed with `· Experiments`, matching the other pages here.
3. A meta description added, for links and search results.
4. An inline SVG favicon added, which also removes a 404 on every page load.

One external dependency: Chart.js 4.4.1 from cdnjs, which the repository's
Content-Security-Policy in `netlify.toml` already permits. Everything else,
markup, styles, logic and data, is in the single file. MIT.
