# INDIA-DATA

Bihar electoral and demographic dashboard. Static HTML, deployed to GitHub Pages
by `.github/workflows/static.yml`. `index.html` is the dashboard; the data is in
`data/`.

## Commands

```bash
python3 scripts/check_data.py     # integrity checks, run by CI
python3 -m http.server 8000       # then open http://localhost:8000
```

## Read DATA_INTEGRITY.md before citing anything from this repository

The dashboard publishes political claims about electoral roll deletions. Five
defects in `data/ac_deletions_change_2020_2024.csv`, audited 2026-09-22, sit
underneath them. In short:

1. `booths_2020` is a verbatim copy of `booths_2024` in all 243 rows, so four
   derived columns are wrong and the per-booth comparison is arithmetically
   identical to the raw deletion ratio.
2. `deletions_2020` totals 39.2 million, roughly 54% of Bihar's electorate, with
   no source anywhere in the repository.
3. `party_2024` records BSP leading 59 assembly segments and independents 46,
   though neither won a Bihar seat in 2024, gives JD(U) 3 where the result
   implies about 72, and omits RJD and LJP(RV) entirely.
4. `alliance_2024_ls`, derived from it, classifies only 131 of 243
   constituencies, so anything grouped by it drops 46% of Bihar.
5. The headline claim "NDA 81.2 vs INDIA 93.0" **reverses** to NDA 87.4 vs INDIA
   79.6 under the 2020 alliance labels, which cover 104 more constituencies.

**None of this is fixed**, and it should not be fixed by guessing. Repairing it
needs booth counts from the 2020 roll and assembly-segment leads from ECI Form 20
data. Inventing plausible numbers for an electoral integrity analysis would be
much worse than the gap.

What *is* sound: `deletions_2024` totals 6,559,626, close to the reported Special
Intensive Revision figure, and `del_per_booth_2024` recomputes exactly from its
inputs in every row.

## How the defect checks work

`scripts/check_data.py` has two kinds of check. **STRUCTURAL** ones assert
invariants that must hold and currently do. **KNOWN DEFECT** ones assert each
documented defect is still exactly as described, so the state is explicit rather
than remembered.

That inversion is deliberate. When you repair the data, the matching KNOWN DEFECT
check fails and tells you which finding in `DATA_INTEGRITY.md` to delete and which
derived columns to recompute. A list of known problems that nothing enforces
rots into a blindfold; this one cannot go stale without saying so.

## Watch out for

- **`ac_name` is not a key.** Bihar has two Kalyanpur constituencies (16, Purvi
  Champaran; 131, Samastipur) and two Pipra constituencies (17 and 42). These are
  genuinely different seats sharing a name, verified against the constituency
  pages and the Bihar CEO's Form 20 for AC 131. Join on `ac_number`. A join on
  name silently merges two constituencies and nothing errors.
- **The data quality notice in `index.html` is load-bearing.** It is the only
  thing telling a reader that the comparisons below it are unsound. CI fails if
  it or the link to `DATA_INTEGRITY.md` is removed, so taking it out has to be
  deliberate.
- **The SIR was conducted in 2025.** A column named `deletions_2024` holding what
  looks like the SIR total may be mislabelled by a year. Resolve before citing.
- **`BUindex.html` and `backups/` are served publicly.** Seven backup copies of
  the dashboard, 604 KB, are deployed to Pages alongside the real one and are
  reachable by URL. They carry older versions of the same claims and none of them
  carry the data quality notice. Consider moving them out of the published root.
- **`METHODOLOGY_NOTES.md` covers the census, caste survey and GDDP projections
  in detail and says nothing at all about the deletions data.** That gap is how
  findings 1 to 3 survived: the documented half of the repository is not the half
  the dashboard's claims depend on.
