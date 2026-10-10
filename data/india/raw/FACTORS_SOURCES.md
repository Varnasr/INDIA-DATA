# Sources: district circumstances for the district factors page

Read on 2026-10-10. One file, `nfhs5_districts_phase1.csv`, used by `scripts/build_factors.py`.

## NFHS-5 district fact sheets, phase 1

**What it is.** National Family Health Survey 2019-21 (NFHS-5), International Institute for
Population Sciences and the Ministry of Health and Family Welfare, district fact sheets
("Key Indicators"). The primary documents are the state compendia at
`https://rchiips.org/nfhs/NFHS-5_FCTS/COMPENDIUM/<State>.pdf`. rchiips.org fails TLS
verification at the sandbox's egress proxy, so the compendia could not be read here.

**What was read.** A published compilation of the phase 1 fact sheets as CSV:
`https://raw.githubusercontent.com/pratapvardhan/NFHS-5/master/NFHS-5-Districts.csv`
(341 districts in 21 states and union territories, 4,153,783 bytes, sha256
`55fa761bb577aa4f221751064fecb4e502ff213a08b409e0604f9ff9c53b91ce`), licensed CC BY 4.0.
Its README says the PDFs were converted automatically with some manual edits and that
quality checks were minimal. It is therefore treated as a secondary source and labelled so.

`nfhs5_districts_phase1.csv` keeps the seven states that have a district table on this site
(Bihar, Gujarat, Karnataka, Kerala, Maharashtra, Telangana, West Bengal) and seven indicators:
3 (sex ratio), 6 (deaths registered), 9 (improved sanitation), 10 (clean cooking fuel),
14 (women literate), 15 (women with 10 or more years of schooling), 16 (women aged 20-24
married before 18). Columns: state, district, indicator as printed, the NFHS-5 and NFHS-4
values, and the fact sheet's note (25 to 49 unweighted cases; fewer than 25, not shown).

**Check.** Every Bihar value that also appears in `data/bihar/raw/nfhs5_districts.csv`, which
was read from the Bihar compendium itself, agrees exactly (148 of 148). The build fails on any
difference. The other six states are unchecked against their compendia until those are read.

**Not covered.** Tamil Nadu, Rajasthan, Uttar Pradesh, Uttarakhand and Delhi were released in
the survey's second phase and are not in the compilation.

**Matching to today's districts.** The survey used the districts of 2019-20. `ALIAS` in
`build_factors.py` maps each of today's districts to the survey district it lies in, by name
or, for a district made later, by the district it was made from (Vijayanagara from Bellary,
2021; Mulugu from Jayashankar Bhupalpally and Narayanpet from Mahabubnagar, 2019; Bengaluru's
B.B.M.P districts into Bangalore; Kolkata North and South into Kolkata). Telangana's 2021
reorganisation renamed Warangal Rural and Warangal Urban as Warangal and Hanumakonda with
changed boundaries; they are matched one to one, which is approximate.
