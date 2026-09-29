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

## Read DATA_INTEGRITY.md before touching the Bihar numbers

Until September 2026 this site published a Bihar dashboard built on a join that
counted every booth about six times (39.2 million "2020 deletions" against a
true 6.56 million), with 2024 party labels wrong in nine seats and caste figures
that were the state survey repeated in every district. Its headline comparison
ran the wrong way. Everything was rebuilt from the booth files; the old files
are in `data/legacy/` with a README. Do not bring any of them back into a page.

Things the rebuild depends on, each asserted by `check_data.py`:

- **One row per booth.** The booth file has about three rows per booth (one per
  top-three 2024 party) and the gender-religion file two (one per sex). Any
  join of the two must aggregate first. Totals: 77,837 booths, 6,559,626 phase 1
  deletions in the booth file, 6,910,559 across both phases.
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

- Colour tokens live in `assets/sir.css`, with the dark block written twice
  (`prefers-color-scheme` and `[data-theme="dark"]`). `check_contrast.py`
  measures 50 pairs and fails if the two dark blocks differ.
- `SIR.chart` resolves `$token` colours before Chart.js sees them and disables
  the colours plugin; `SIR.recolour` sets option fields in place on a theme
  change. Replacing an options object wholesale breaks Chart.js's proxies
  (`this._fn is not a function`).
- Every finding sentence on a page is computed from the JSON when the page
  loads. Do not hardcode a figure in prose.
- Audited with axe at 1280 and 390, both schemes, all 15 pages: 0 serious or
  critical. In a sandbox cdnjs is unreachable; stub Chart.js by route or the
  audit sees pages with no charts.

## Watch out for

- `data/Bihar Dashboard Context/` holds the Word reports written on the old
  data. They are served publicly and their conclusions predate the correction.
- `pandas` and `openpyxl` are pinned in CI because a reader change could move
  the numbers without an error.
