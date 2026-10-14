# Sources: district circumstances and income for the district factors page

Read on 2026-10-12. Used by `scripts/build_factors.py`.

## NFHS-5 district fact sheets: `nfhs5_districts.csv`

**What it is.** National Family Health Survey 2019-21 (NFHS-5), International Institute
for Population Sciences and the Ministry of Health and Family Welfare, "Compendium of Fact
Sheets: Key Indicators, State and Districts of <state>", one PDF per state. The originals are at
`https://rchiips.org/nfhs/NFHS-5_FCTS/COMPENDIUM/<State>.pdf`. rchiips.org fails TLS
verification at the sandbox's egress, so the PDFs were downloaded from the copies the OpenCity
data portal holds (https://data.opencity.in/dataset/national-family-health-survey-nfhs-5-2019-21,
"NHFS 5 Data - <State> and Districts Combined"). Each copy opens on the IIPS and Ministry
cover. They are not committed (4 to 14 MB each). Their sha256:

| state | sha256 |
|---|---|
| Bihar | 4e122f4bb8a316efa3e217a2db52d10d6a9f343a4cd0272825d77d2f39dbec65 |
| Gujarat | 4fc4147b716fcc4c0f8aaedfb3d3e8c1fda826cee45dd2ea3acfa1fcff7d68fc |
| Karnataka | bb7a0aa57fcdc4b357f22975462130c1a87927149ee202d64d27650f9674db7e |
| Kerala | 4125b76396ffc17a86c887835cf7adbc6cf0222e1d0e67233ebce18a8424fb1c |
| Maharashtra | 7bc40550fee000ce54ca93f4bdaf9a3d92c2de660490abc60883f2f91841a112 |
| Telangana | c21aa18a9a689f4ff125afcd34baeab505da5c2e443df053d0898e1c43bda331 |
| West Bengal | 43b902bd8a43f6e6b34c3256f34e7b2c2a23ab769268f74908412c2016b56c3e |
| Tamil Nadu | 40cf5c83ddbb053fc8352911fa428101b50c423abc96254989cbd9529ffa398a |
| Uttar Pradesh | fc34f7e27908a718d2b8b380273d6dadf9c983ca909e2748473209b6beeffbf0 |
| Rajasthan | b39cb4450a08f82e1eb75f160bebbd0a5da99800fa6414af0faa227f91366733 |
| Uttarakhand | e656a4fca87d766bf75d6e44033c00d880429149caba5e5f66ef4fdfd792fffb |
| NCT Delhi | 7fd127e6c68289ba4cbef9e82c4efbcbc2c0f7d58a80b7567fdfd7d0e5bef5ba |

**How read.** pypdf, page by page. A district page opens "<district>, <state> - Key
Indicators" (Rajasthan's Jalor page omits the comma). Indicators are found by their text,
because two sheets misnumber a line (Mahisagar and Wardha print clean cooking fuel as 11).
Kept: 3 sex ratio, 6 deaths registered, 9 improved sanitation, 10 clean cooking fuel,
14 women literate, 15 women with 10 or more years of school, 16 women 20-24 married before 18.
A value in brackets (25 to 49 unweighted cases) is kept and noted. A star (fewer than 25) is
left blank. Each row carries its file and PDF page. 345 districts in 12 states, none missing.

**Checks.** The 148 Bihar values also in `data/bihar/raw/nfhs5_districts.csv`, read earlier
from the same compendium, agree exactly, and the build fails otherwise. Every value for the
seven first-phase states also agrees exactly with the CSV compilation the page used before
(github.com/pratapvardhan/NFHS-5, NFHS-5-Districts.csv, sha256 55fa761b...), 1,514 of 1,514.

**Matching to today's districts.** The survey used the districts of 2019-20. `ALIAS` in
`build_factors.py` maps each of today's districts to the survey district it lies in, by name
or, for a district made later, by the district it was mostly made from. Telangana's Warangal
and Hanumakonda are matched one to one to Warangal Rural and Warangal Urban, which is
approximate. Delhi is read on the 11 districts of its 2025 roll (`district_2025` in
`data/delhi/raw/ac.csv`), which are the survey's.

## District income: `income/`

Copies transcribed by OpenCity from each state's publication, as CSV. The page says so.

- `karnataka_es2025_26_district_gddp_pci.csv`: Economic Survey of Karnataka 2025-26,
  district GDDP and per capita income, 2024-25, current prices.
  https://data.opencity.in/dataset/economic-survey-of-karnataka-2025-26 . Check: the 31
  districts' NDDP adds to the state row.
- `maharashtra_es2025_26_district_gddp_pci.csv`: Economic Survey of Maharashtra 2025-26,
  per capita nominal NDDP 2024-25 (first revised). Mumbai is the city and suburban districts
  together, and Thane includes Palghar, as printed.
  https://data.opencity.in/dataset/economic-survey-of-maharashtra-2025-26 . Check: each
  division's districts add to its printed division row.
- `tamilnadu_2023_24_district_gddp_pci_constant.csv`: Tamil Nadu district income, 2023-24,
  constant 2011-12 prices, per capita income column.
  https://data.opencity.in/dataset/tamil-nadu-district-level-gddp-data . Check: the 38
  districts' GDDP adds to the STATE row.
- `telangana_seo2024_district_gddp_pci_2022_23.csv`: Telangana Socio-Economic Outlook 2024,
  per capita income 2022-23, current prices.
  https://data.opencity.in/dataset/telangana-socio-economic-outlook-2024 . There is no state
  row to check against.
- Bihar is `data/bihar/raw/gddp_per_capita_2011_12_prices.csv`, read from the Survey itself.

These checks catch a misread GDDP figure, not a misread per capita figure. Only ranks inside a
state are used, so the years and prices do not change a result.

## Seven more states (14 October 2026)

Andhra Pradesh, Assam, Chhattisgarh, Manipur, Meghalaya, Mizoram and Odisha: 131 survey
districts, 917 rows, read the same way and appended to `nfhs5_districts.csv` (source_file AP,
AS, CG, MN, ML, MZ, OR). Each compendium opens on the IIPS and Ministry cover.

| state | source | sha256 |
|---|---|---|
| Andhra Pradesh | Internet Archive capture of rchiips.org/nfhs/NFHS-5_FCTS/COMPENDIUM/Andhra_Pradesh.pdf (2 Aug 2023) | f9c839cf1bc439444a5b29e290bd31f1c654b23f2767344f55a23303dc9c3c5a |
| Assam | OpenCity, resource 6681e8f4-255f-427b-a6c2-e09ea56e77c0 | f52257d5139d39a53ee0b273111ec2a9ad23d11745a1db240e1ed86ff9a4cd59 |
| Chhattisgarh | Internet Archive capture of rchiips.org/nfhs/NFHS-5_FCTS/COMPENDIUM/Chhattisgarh.pdf (28 Dec 2022) | e77c6ee4177081a6e8b6902c086fe8f08b7fb1b1a87f9be0378e29b327eb58fa |
| Manipur | OpenCity, resource f713eb4a-1e28-4d50-ae0b-b8e5309c8fff | 8393d8617dda7f6075deeedd121bdb9bc808366eed7b1d3aad630c3d701bdbe9 |
| Meghalaya | OpenCity, resource 82108b4a-9d18-4b14-b7c2-fdc9ebd9468e | 1ac6340c5433ee714990b093aaab490d4339ab7320c102fcb65902a3f36fca69 |
| Mizoram | OpenCity, resource 88601ff5-bf3c-4622-bd61-7f8c4019ff1b | b3685cbfef7a1798faf72040a92af8786f72e6d76b55cfa4afe043429acd0bf8 |
| Odisha | OpenCity, resource a2d37703-c7da-458c-bd34-e248bd5b379c | 7e078ed79b2b278f85e617c89f1bbcc8f4f11bfeea25e4f780409bfc23a1da18 |

OpenCity holds no district compendium for Andhra Pradesh or Chhattisgarh, and rchiips.org
fails TLS from the sandbox, so those two are the Internet Archive's raw (`id_`) captures of
the Institute's own files.

Eight values are bracketed, all deaths registered: Assam's Dima Hasao and Kamrup
Metropolitan, Meghalaya's North, South and West Garo Hills, Mizoram's Lunglei, Mamit and
Saiha. None is starred. 35 sheets print no NFHS-4 column.

**Checks.** The five first-phase states' 518 values agree exactly with the pratapvardhan
compilation. That file has no Chhattisgarh or Odisha. Odisha's Khordha was checked against
OpenCity's CSV for that district, and the other 56 Chhattisgarh and Odisha districts have no
independent check.

**Matching.** `nfhs5_alias/alias_<state>.csv` maps each of today's districts to the survey
district it was mostly made from, with every parent's share of the 2011 population and a
source. Rows worth knowing: Annamayya maps to Chittoor (78%), because since 2025 it holds the
Madanapalle and Pileru divisions; Bapatla is Guntur 58%, Prakasam 42%; Tirupati is Chittoor
64%; Saitual (Mizoram) is about two-thirds Aizawl; Sarangarh-Bilaigarh is Raigarh about 63%;
Bajali and Tamulpur map to Barpeta and Baksa; Sribhumi is the survey's Karimganj. The
Andhra Pradesh shares join a list of mandals to Census 2011 sub-district rows, so they are
approximate.

**Measures.** Andhra Pradesh and Meghalaya: names left off. Manipur: the fall from the roll
before to the final roll. Odisha: the fall from January 2025 to the draft. Assam: the fall
after the draft. Chhattisgarh and Mizoram: the rise after the draft, so the sign of their
correlations runs the other way.
