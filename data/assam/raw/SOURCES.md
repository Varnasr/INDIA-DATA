# Assam sources

Assam had a Special Revision (SR) in 2025-26, not a Special Intensive
Revision. Everything here was gathered on 2026-10-06.

**What could not be reached.** ceoassam.nic.in (and ceoassam.assam.gov.in)
refused the sandbox: plain curl was reset or answered 503, and Firecrawl failed
with a tunnel error on every attempt, including Indian and stealth proxies.
web.archive.org is blocked by the egress policy. eci.gov.in answered 406 to
curl and to Firecrawl for the order PDF. nrcassam.nic.in and
assamassembly.gov.in could not be reached. The three constituency tables below
were downloaded by the site's owner on 10 October 2026 and are in `sources/`
(`ceo_final_electors_20240208.pdf`, `ceo_draft_electors_20251227.pdf`,
`ceo_final_electors_20260210.pdf`). `read_ac_tables.py` reads them into
`ac_rolls.csv` (needs pypdf; `--check` compares) and asserts that every row's
men, women and third gender add to its total, that ACs 1 to 126 appear once in
each table, and that each table adds to its printed state total: 2,43,01,960
(February 2024), 2,52,01,624 (draft) and 2,49,58,139 (final). The draft and
final also add to the press figures by sex and to 31,486 polling stations,
which `build_assam.py` asserts. West Karbi Anglong wraps over two lines in the
PDFs and is joined. The tables give each roll's total only, so a seat's change
is net, names added less names removed. The addresses:

- https://ceoassam.nic.in/summary/2026/Draft_Electors_27-12-2025.pdf,
  "Assembly Constituency wise Draft Electors and Polling Stations"
- https://ceoassam.nic.in/summary/2026/Final%20Electors_10-02-2026.pdf,
  "Assembly Constituency wise Final Electors and Polling Stations", with
  district totals
- https://ceoassam.nic.in/summary/special-revision-2026.html, the SR page
  listing both
- https://ceoassam.nic.in/summary/2024/Final%20Elector_08-02-2024.pdf, the
  2024 final roll by district and AC and sex

The draft and final AC tables are aggregates; the part-wise roll PDFs on the same site
and on voters.eci.gov.in are named lists and were not opened.

## The order (part A)

`sources/eci_23-2025-ERS_17.11.2025_assam_special_revision.pdf`

- ECI letter No. 23/2025-ERS (Vol. II) dated 17 November 2025 to the CEO,
  Assam, "Special Revision w.r.t. 01.01.2026 as the qualifying date", signed
  by Pawan Diwan, Secretary. 18 pages of text plus Statements 1 to 3 (21 pages).
- The ECI copy (Instructions listing, item 18, 17 Nov 2025 6:28 PM, 17 MB)
  answered 406. The pages were read from page images of a copy of the same
  letter uploaded to Scribd
  (https://www.scribd.com/document/959537310/Special-Revision-Schedule-2026),
  downloaded as JPEGs and read by eye, all 21 pages. The letterhead, number,
  date, signature and content match the ECI listing's title and date. It is
  the Commission's document, but the copy was not taken from the Commission or
  the CEO, so treat it as primary content from a secondary host.
- Saved as one PDF of the 21 page images (2.2 MB).

`rules.csv`: one row per difference or rule, with the paragraph number and a
verbatim quote from the Assam order, and the SIR Phase II rule beside it. The
SIR side is taken from the site's own record of the 27.10.2025 and 24.06.2025
orders (`data/india/raw/process_research/process.json` and
`forms_primary.json`, read from the CEO Kerala copy), not re-read here.

What the order says, in short:

- Para 1: a Special Revision under section 21 of the RP Act 1950, qualifying
  date 01.01.2026.
- Para 2: schedule (`schedule.csv`): house-to-house 22.11 to 20.12.2025, draft
  27.12.2025, claims to 22.01.2026, disposal by 02.02.2026, final 10.02.2026.
- Para 4(c): BLOs carry a pre-filled register (Statement-1) of existing
  electors and verify it household by household; Statements 2 and 3 for
  un-enrolled and prospective electors; Forms 6, 7, 8 filled as needed.
  **No enumeration form, no document from existing electors, and no link to
  the 2005 roll or any earlier roll is mentioned anywhere in the order.**
- Para 4(d): D-voters are left out of Statement-1, carried to the draft
  unchanged, and changed or removed only on an order of a Foreigners Tribunal
  or a court.
- **The order does not mention the NRC** or people left out of it.
- Para 10(a), 10(e): Form 6 as usual, Aadhaar voluntary, no Declaration Form.
- Para 4(a)(iv), 15, 12(b): deletions of the dead, shifted and duplicate by
  Form 7 before the draft; safeguards; no deletion from the draft without an
  opportunity of hearing.
- Para 9(b)(ii): addition and deletion lists are not printed for parties.
- Para 17(c): BLAs may file 10 forms a day; over 30 in the period, the ERO or
  AERO cross-verifies.
- The order gives no reason why Assam had an SR rather than an SIR.

## The figures (part B)

`state.csv`. Every figure is a CEO Assam figure, but every one was read in the
press or on newsonair (All India Radio, Prasar Bharati), not in a CEO document,
because the CEO site could not be reached. Press texts kept, as extracts, in
`sources/press_*.md`:

- The Hindu, 27.12.2025: draft 2,52,02,775 including more than 93,000
  D-voters; 2,51,09,754 without them; 61,03,103 household visits; quotes the
  CEO's statement.
- New Indian Express and India Today NE, 27.12.2025: dead 4,78,992, shifted
  5,23,680, multiple or similar entries 53,619; 93,021 D-voters; staff counts;
  31,486 polling stations.
- newsonair, India Today and The Tribune, 10.02.2026: final 2,49,58,139 (men
  1,24,82,213, women 1,24,75,583, third gender 343); draft 2,52,01,624;
  fall 2,43,485; quotes the CEO's statement.
- Free Press Journal, 11.02.2026: the CEO's press conference; 6,27,696
  un-enrolled eligible citizens and 1,46,342 prospective electors identified;
  no D-voter deleted.
- ThePrint, 10.02.2026: the previous final roll (January 2025) had 2,49,26,285;
  the SR "did not have enumeration forms, but did have verification of electors
  through a house to house drive".

Not found anywhere: the roll on which the house-to-house began (the roll as of
November 2025), claims (Form 6) and objections (Form 7) received or admitted,
names added and deleted after the draft as separate counts, and any split of
the removals by sex. The fall from draft to final is a **net** figure.

### Checks

- Draft without D-voters plus D-voters equals the draft with them:
  2,51,09,754 + 93,021 = 2,52,02,775. OK.
- Dead + shifted + multiple = 10,56,291, which the press rounds to 10.56 lakh.
  No total was printed, so this is a sum, not a check against a total.
- Final men + women + third gender = 2,49,58,139. OK.
- Draft (as stated with the final roll) less final = 2,52,01,624 less
  2,49,58,139 = 2,43,485, the stated fall. OK.
- **Discrepancy:** the draft as stated on 27.12.2025 (2,52,02,775) is 1,151
  more than the draft as stated with the final roll (2,52,01,624). Neither
  source explains it. Both are recorded as printed.
- Implied roll before the draft, if the draft is the roll less the removals:
  2,52,02,775 + 10,56,291 = 2,62,59,066. **No source states this figure**, and
  names added during house-to-house (Form 6) would make it wrong, so it is not
  in `state.csv`.
- Draft against the January 2025 final roll: up 2,76,490 (1.1%), which matches
  ThePrint's "around 1.2 percent" only roughly (2,52,01,624 gives 1.1%).

## Context (part C)

Primary: Lok Sabha answers of the Ministry of Home Affairs, downloaded as PDFs
from the Lok Sabha digital library (elibrary.sansad.in, DSpace API) and read
as text with pymupdf. All in `sources/ls_*.pdf`.

| file | question | what it gives |
|---|---|---|
| ls_20191203_doubtful.pdf | LS USQ 2386, 03.12.2019 | D-voters as of October 2019: 1,13,738, of them women 70,723 |
| ls_20191203_detention_camps.pdf | LS USQ 2340, 03.12.2019 | 6 detention centres; inmates by centre and sex on 28.11.2019 |
| ls_20191210_ft_declaration.pdf | LS USQ 3558, 10.12.2019 | to October 2019: 4,68,905 matters referred to FTs; 1,14,225 declared Indian; 1,29,009 declared foreigners; no children; 4 + 2 deported |
| ls_20191210_detention_declared.pdf | LS USQ 3561, 10.12.2019 | detention over 3 years, 2019 detentions, 290 women declared foreigners, 128 released, 227 deported |
| ls_20200317_detention_assam.pdf | LS USQ 3880, 17.03.2020 | capacity of the 6 centres (3,331); Matia under construction (3,000); 10 deaths 01.03.2019 to 29.02.2020 |
| ls_20200920_doubtful_pending.pdf | LS USQ 1485, 20.09.2020 | pending D-voter cases 83,008; 86,756 declared foreigners 2015 to 30.06.2020 |
| ls_20210209_nrc_assam.pdf | LS USQ 1264, 09.02.2021 | 19,06,657 not found eligible; appeal period 120 days; 200 appellate FTs added in 2019 |
| ls_20210316_nrc_assam.pdf | LS USQ 3448, 16.03.2021 | 3,11,21,004 eligible, 19,06,657 left out; decision on D-voters and descendants on hold on the Supreme Court's direction |
| ls_20210316_ft_constitution.pdf | LS USQ 3280, 16.03.2021 | 300 FTs; 200 more approved in principle; 1,40,050 pending to December 2020 |
| ls_20210323_ft_pending.pdf | LS USQ 4401, 23.03.2021 | 1,40,050 pending on 31.12.2020; disposals by year 2016-2020 |
| ls_20210323_ft_appeals.pdf | LS USQ 4425, 23.03.2021 | appeals by people excluded from the NRC: nil, as rejection orders were not issued |
| ls_20211214_nrc_list.pdf | LS USQ 2624, 14.12.2021 | NRC figures again; cost Rs 1,602.66 crore |
| ls_20211214_ft_appeal.pdf | LS USQ 2627, 14.12.2021 | rejection orders still not issued |

Files: `d_voters.csv`, `foreigners_tribunals.csv`, `nrc_2019.csv`,
`detention_centres.csv`, `detention_state.csv`. Each row carries `primary`.

Press only (primary=false), kept in the same files and marked:

- Assam Legislative Assembly reply of 13.07.2026 by the Chief Minister (Home),
  as reported by The Assam Tribune (13.07.2026): 91,385 D-voters on the roll;
  1,99,596 in 1997; 2,44,144 D-voter cases referred, 2,05,659 disposed, 56,728
  declared foreigners (831 more by courts), 65,171 declared Indian (42 by the
  High Court, 3 by the Supreme Court); Border Police cases 1,90,657 referred,
  1,55,490 disposed, 1,15,945 declared foreigners; 31,789 expelled in all.
  The Assembly's own record could not be reached.
- The same session, as reported by The Wire (14.07.2026): 1,679 people sent to
  Bangladesh between 01.07.2024 and 30.06.2026, 193 of them declared
  foreigners (67 by expulsion, 126 "sent back").
- NRC applicants, 3,30,27,661 through 68,37,660 applications: the State
  Coordinator's statement of 31.08.2019 as quoted by the press (search
  excerpts only). It equals 3,11,21,004 + 19,06,657 exactly.
- 93,021 D-voters on the draft (CEO statement via press, above).

### Checks

- Detention centres: capacities sum to 3,331 (printed 3,331); inmates men 646,
  women 324, total 970, each equal to the printed Total row; men + women =
  total in every centre. OK.
- FT disposals 2016-2020 sum to 1,36,064, the printed total. OK.
- NRC: 3,11,21,004 + 19,06,657 = 3,30,27,661, the applicants figure. OK.
- Assembly reply (press): declared foreigners plus declared Indian among D-voter
  cases is 1,21,899, against 2,05,659 disposed. The other 83,760 disposals are
  not described in the report. Referred less disposed is 38,485; a search
  excerpt of another Assam Tribune post gave 41,059 D-voter cases pending "as on
  31st May, 2026", which was not read in full and is not recorded.
- D-voters fall from 1,13,738 (October 2019, primary) to 93,021 (draft,
  December 2025) to 91,385 (July 2026); the last two are press.

## Rules kept

Aggregates only. No name, EPIC number, address or link to a named list was
saved. One press extract named a photographer in a caption; that line was
removed. Nothing here says anything about any person's citizenship.
