# Sources: Census 2011 urban share by district, and 2011 parents of today's districts

Read on 2026-10-06. Two files:

- `census2011_a01_districts.csv`: 640 districts of Census 2011, total, rural and urban population, urban share, area and density, written from the saved A-01 workbook by `scripts/census_a01.py`, which checks every row and the India totals.
- `district_2011_parent.csv`: the 379 districts in the site's eleven district tables, each mapped to its Census 2011 district or districts.

## 1. Census 2011 district totals

**Source.** Office of the Registrar General and Census Commissioner, India. Census 2011,
table A-01 "Number of villages, towns, households, population and area (India, states/UTs,
districts and Sub-districts) - 2011", catalogue id PC11_A01.

- Catalogue page: https://censusindia.gov.in/nada/index.php/catalog/42526
- File: https://censusindia.gov.in/nada/index.php/catalog/42526/download/46152
  (`A-1_NO_OF_VILLAGES_TOWNS_HOUSEHOLDS_POPULATION_AND_AREA.xlsx`, 2,235,660 bytes,
  sha256 `6b649697ed5993da834b674173dab68e1ef9abb97e234155a80884c2fa4584f5`)
- Saved as `sources/census2011_A-01_villages_towns_households_population_area.xlsx`.

**How read.** curl with a browser user agent. censusindia.gov.in serves its leaf certificate
without the intermediate, so the emSign SSL CA - G1 intermediate was fetched from the address in
the certificate's own Authority Information Access field
(http://repository.emsign.com/certs/emSignSSLCAG1.crt) and added to the CA bundle. Verification
stayed on. The workbook was read with openpyxl: rows with sub-district code `00000` and level
DISTRICT, STATE or INDIA; columns Total/Rural/Urban and Population (Persons). Footnote markers
(`@&`, `$`, `##`, `###`) were stripped from names and runs of spaces collapsed. The footnotes
concern area and density only, not population. `census_code` is state code plus the three-digit
district code (`01001` = Kupwara). State names are as printed (upper case, `&`).

**Checks, all passed.**

| check | result |
|---|---|
| rural + urban = total, every row (676 rows: India, 35 states and UTs, 640 districts) | 0 failures |
| district count | 640 |
| districts sum to each of the 35 state rows, total, rural and urban | 0 mismatches |
| districts sum to India | 1,210,854,977 total, 833,748,852 rural, 377,106,125 urban: equal to the published figures |
| populations against `data/bihar/raw/census2011_districts_all_india.csv` (cross-check only) | all 640 equal; district codes in the same order |
| names against that file | 5 spelling differences only (Lahul & Spiti, North District, Dadra & Nagar Haveli, Puducherry, North & Middle Andaman) |

Nine districts are 100.0% urban (New Delhi, Central, Kolkata, Mumbai Suburban, Mumbai,
Hyderabad, Chennai, Yanam, Mahe).

## 2. 2011 parents of the site's districts

Site files read: `data/bihar`, `uttarpradesh`, `gujarat`, `tamilnadu`, `karnataka`,
`maharashtra`, `westbengal`, `kerala`, `uttarakhand`, `rajasthan` (`districts.json`) and
`data/hyderabad/telangana.json` (`districts`). 379 rows: 38 + 75 + 33 + 38 + 34 + 36 + 24 + 14
+ 13 + 41 + 33.

Relation: `same` (269), `renamed` (47, a spelling or name change; where the district also lost
area the note says so), `split_from` (63). `merged_into` is not used. A district that kept its
name but lost area to a new district is `same` or `renamed`, with a note starting "2011 district
kept its name but lost area since". Its 2011 urban share is then for a larger area than today's.

### Sources used for the mapping

Census 2011 A-01 itself (above) is the main check: its sub-district rows show which 2011 district
held each tehsil, taluk or mandal a new district is made of. District websites state the parent;
A-01 confirms the units.

| state | source | URL | how read |
|---|---|---|---|
| Uttar Pradesh | Amethi, Hapur, Shamli, Sambhal district websites (NIC) | https://amethi.nic.in/history/ , https://hapur.nic.in/history/ , https://shamli.nic.in/about-district/ , https://sambhal.nic.in/about-district/ | curl |
| Gujarat | Botad, Morbi, Mahisagar, Devbhumi Dwarka, Gir Somnath, Chhota Udepur district websites | https://botad.nic.in/about-district/ , https://morbi.nic.in/about-district/ , https://mahisagar.nic.in/history/ , https://devbhumidwarka.nic.in/history/ , https://girsomnath.nic.in/about-district/ , https://chhotaudepur.nic.in/about-district/ | curl |
| Tamil Nadu | Chengalpattu, Kallakurichi, Tenkasi, Tirupathur, Ranipet, Mayiladuthurai, Chennai district websites | https://chengalpattu.nic.in/history/ , https://kallakurichi.nic.in/history/ , https://tenkasi.nic.in/about-district/ , https://tirupathur.nic.in/about-district/ , https://ranipet.nic.in/about-district/ , https://mayiladuthurai.nic.in/about-district/ , https://chennai.nic.in/about-district/administrative-setup/revenue-administration/ | curl |
| Karnataka | Vijayanagara district website | https://vijayanagara.nic.in/history/ , https://vijayanagara.nic.in/en/subdivision-blocks-en/ | curl |
| Maharashtra | Palghar district website | https://palghar.gov.in/about-district/ | curl |
| West Bengal | Alipurduar, Jhargram, Paschim Bardhaman district websites | https://alipurduar.gov.in/about-district/ , https://jhargram.gov.in/about-district/ , https://paschimbardhaman.gov.in/history/ | curl |
| Rajasthan | Rajasthan Gazette Extraordinary, 6 Aug 2023, Revenue (Group-1) Department notifications No. P.9(18)Raj-1/2022-(2), (3), (4), (5), (9), (10), (12), dated 5 Aug 2023, effective 7 Aug 2023, each attached to the Local Government Directory (LGD) notification of the new district. Copies deposited on Zenodo | https://zenodo.org/records/8417479 (Beawar, Kekri), 8417606 (Khairthal-Tijara, Kotputli-Behror), 8417565 (Balotra), 8417490 (Salumbar), 8417571 (Deeg), 8417577 (Didwana-Kuchaman), 8417599 (Jodhpur Gramin, Phalodi) | Zenodo API with curl, text from the PDF with pypdf (Hindi text layer) |
| Telangana | G.O.Ms. No. 250, Revenue (DA-CMRF) Dept, 11.10.2016 (Rangareddy), attached to an LGD village notification | https://lgdirectory.gov.in/downloadDraftGovernementOrder.do?filename=eSignGOFile131537_11_08_2026_15_07_14.pdf | curl, pypdf |
| Telangana | G.O.Ms. No. 238, 11.10.2016 (Medak) | https://telanganaslbc.com/wp-content/uploads/2014/10/1476130402515238.Medak_.pdf (copy hosted by the State Level Bankers' Committee) | curl, pypdf |
| Telangana | 25 district websites (`<district>.telangana.gov.in/about-district/` and `/history/`) | e.g. https://siddipet.telangana.gov.in/about-district/ , https://vikarabad.telangana.gov.in/history/ , https://mahabubabad.telangana.gov.in/about-district/ , https://jangaon.telangana.gov.in/about-district/ | curl |

The LGD and gazette PDFs are not saved here, because the LGD pages carry officials' names and
mobile numbers. Firecrawl was used for three searches only, to find documents (the Rangareddy
G.O., the Rajasthan gazette deposit). Nothing was scraped through it.

Not reachable from the sandbox, or not readable: the Rajasthan district websites
(`*.rajasthan.gov.in` render in JavaScript and return an empty shell), aravalli.nic.in,
purbabardhaman.gov.in, bhupalpally / jayashankarbhupalpally / medchalmalkajgiri
`.telangana.gov.in`; www.telangana.gov.in; data.gov.in (connection reset).

### Checks on the mapping

| check | result |
|---|---|
| every site district has exactly one row | 379 of 379 |
| every `district_2011` value (each part of a `;` list) exists in `census2011_a01_districts.csv` under the matching 2011 state | 0 missing |
| every 2011 district of the ten states, and the ten 2011 Telangana districts of Andhra Pradesh, is a parent of at least one site district | 0 uncovered |
| Telangana's 33 districts map only to the 10 Telangana districts of 2011 | yes |

## 3. What did not add up

- **`data/bihar/districts.json` `urban_pct` does not match Census 2011 A-01** in 33 of 38
  districts, by more than a rounding margin: Sheikhpura 5.12 against 17.13, Begusarai 10.11
  against 19.18, Kaimur 8.93 against 4.03, Arwal 4.28 against 7.40, Banka 5.89 against 3.50.
  The Bihar CLAUDE.md section says urban share there is Census 2011. Its source should be
  checked. It has since been fixed: `scripts/build_bihar.py` reads urban share and density
  from A-01.
- **Chennai was enlarged in 2018**, not carved. Today's Chennai district holds taluks
  (Thiruvottriyur, Madhavaram, Ambattur, Madhuravoyal, Alandur, Sholinganallur) that in 2011
  were in Thiruvallur and Kancheepuram. It is mapped `split_from` all three, since the relation
  list has no "enlarged". Its 2011 share (100.0) is for the old city only.
- **Rajasthan, December 2024.** Nine of the 2023 districts were abolished at the end of 2024 and
  their area returned. The mapping assumes the eight surviving new districts kept their 2023
  tehsils and the abolished ones went back to their 2011 parents. The 2024 notification was not
  read.
- **2011 Khammam includes area now in Andhra Pradesh** (the mandals transferred in 2014), so its
  2011 share is for a larger area than Khammam plus Bhadradri today.
- **Amethi** existed from 1 July 2010 but is not a district in Census 2011 (A-01 lists 71 Uttar
  Pradesh districts). Its tehsils are counted under Sultanpur and Rae Bareli.
- **Karnataka B.B.M.P (North, Central, South) and Bangalore Urban** are the Chief Electoral
  Officer's election districts, not revenue districts. All four are within 2011 Bangalore, which
  is one unit in A-01 (90.9% urban).
- **Kolkata North and South** are likewise CEO election districts, both inside 2011 Kolkata.

### Parents that rest on less than a primary statement

| district | parents | why ambiguous |
|---|---|---|
| Jangaon (TS) | Warangal; Nalgonda | the district website says it was part of Warangal and Nalgonda, without naming the Nalgonda mandal; the G.O. was not read |
| Hanumakonda (TS) | Warangal; Karimnagar | Karimnagar rests on Kamalapur, Bheemadevarpalle and Elkathurthi being in Hanumakonda; G.O.Ms. 74 of 12.08.2021 not read |
| Jayashankar Bhupalpalle (TS) | Warangal; Karimnagar | Karimnagar rests on Mahadevpur, Kataram, Malharrao, Mutharam (Mahadevpur); district website unreachable |
| Mulugu (TS) | Warangal; Khammam | Khammam rests on Wazeed and Venkatapuram; the Mulugu website names only Warangal |
| Kalimpong (WB) | Darjiling | district website does not state the parent; A-01 places the Kalimpong blocks in Darjiling |
| Arvalli (GJ) | Sabar Kantha | district website unreachable; A-01 places its talukas in Sabar Kantha |
| Purba Bardhaman (WB) | Barddhaman | its own website unreachable; Paschim Bardhaman's states the bifurcation |
