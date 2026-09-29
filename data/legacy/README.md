# Superseded files

These are the files behind the dashboard that served at forindia.netlify.app
until September 2026. They are kept so the corrections can be checked against
what was published. Nothing on the site reads them.

| File | What was wrong |
|---|---|
| `DATA.json`, `index.json` | Built from a join of the booth file (about three rows per booth, one per 2024 party) with the gender-religion file (two rows per booth, one per sex). Each booth's deletions appear about six times; summed, they gave the 39.2 million labelled "2020". |
| `ac_deletions_change_2020_2024.csv`, `ac_correlation_ready.csv` | `deletions_2020` is that six-fold count; `booths_2020` is a copy of `booths_2024`; `party_2024` carries the extract's unreconciled labels (LJP(RV) as "BSP", HAM(S) as "JD(S)"), so `alliance_2024_ls` classified 131 of 243 seats. The caste columns are the state survey shares, identical in every row. |
| `district_caste_block_shares.csv`, `district_caste_summary_master.csv` | Every district carries the 2023 survey's state shares (EBC 36.01, BC 27.12, SC 19.65, ST 1.68, General 15.52) multiplied by its deletions. Not a measurement. |
| `top5_*`, `bottom5_*` | Surname classification in which "Devi", a title, was mapped to Lohar (EBC), putting two million women in the EBC total. |

The corrected figures are built by `scripts/build_bihar.py` from `data/bihar/raw/`.
