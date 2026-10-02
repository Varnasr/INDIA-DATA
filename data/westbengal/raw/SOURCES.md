# West Bengal raw tables: sources

Fetched 2026-10-01. Every table is assembly-constituency (AC) level, 294 rows,
keyed by `ac` (integer, 1 to 294). Numbers were parsed by script from the
fetched text, never typed by hand. No list of individual electors (names,
EPIC numbers) was opened, stored or quoted.

AC names are spelled as each source spells them, so they differ between
files (Manichchak / Manikchak / Manickchak, Naoda / Nowda, Burdwan /
Bardhaman, Keshipur / Keshpur, Labhpur / Labpur, Joynagar / Jaynagar,
Mongalkote / Mangalkot). Join on `ac`, never on `ac_name`. `district` is the
CEO's 23-district list as printed on the draft roll (title case), copied into
the other files from `draft_roll_ac.csv` where the source had none.

## Files

### draft_roll_ac.csv

ac, ac_name, district, men, women, third, total, polling_stations. The SIR
draft roll published 16 December 2025.

- Source: CEO West Bengal, "AC wise Status of Polling Stations and Electors in
  Draft Electoral Roll w.r.t 01.01.2026 (SIR)",
  https://ceowestbengal.wb.gov.in/Downloads/SIR2026/AC%20wise%20Draft%20Elector%20SIR%202026.pdf
  (7 pages; PDF title "AC wise Draft Elector as on 16.12.2025.xlsx").
- Asserts passed: ACs are exactly 1 to 294; men + women + third = total in
  every row; column sums equal the PDF's own Total row and the press-note
  totals: 80,681 polling stations, 3,61,99,391 men, 3,46,15,837 women, 1,402
  third gender, 7,08,16,630 in all.

### electors_nomination_2026_ac.csv

ac, ac_name, district, phase, men, women, third, total. Electors on the last
date of nomination for the April 2026 Assembly election, that is the final
SIR roll of 28 February 2026 as amended by the adjudication supplements and
deletion lists up to that date.

- Source: CEO West Bengal, GE 2026 page
  (https://ceowestbengal.wb.gov.in/Election_details/4939), link "Assembly
  Constituency-wise Elector data":
  https://ceowestbengal.wb.gov.in/Downloads/Election/GE2026/Elector_WBLA2026.pdf
  (7 pages; PDF title "AC-wise_Elector_WBLA 2026.xlsx").
- Asserts passed: ACs 1 to 294; men + women + third = total in every row;
  phase 1 sums equal the printed Phase 1 Total (1,84,99,496 / 1,75,77,210 /
  465 / 3,60,77,171); phase 2 sums equal the Phase 2 Total (1,64,35,627 /
  1,57,37,418 / 792 / 3,21,73,837); all rows equal the State Total
  (3,49,35,123 men, 3,33,14,628 women, 1,257 third, 6,82,51,008 in all).
- Draft total minus this total is 25,65,622 across the state, ranging from
  -4,685 to +74,605 by AC (57 ACs grew). That is a net change: Form 7
  deletions and adjudication exclusions less Form 6/6A/8 additions. It is not
  a count of removals and must not be used as one.

### roll_2024_ls_ac.csv

ac, ac_name, district, men, women, third, total, polling_stations. Electors on
the last date of filing nomination for the 2024 Lok Sabha election, by
assembly segment. This is the nearest AC-level roll before the revision found
in a primary source. It is NOT the roll of 27 October 2025 (state total
7,66,37,529); it is about 18 months older and 6,27,523 smaller in total.

- Source: CEO West Bengal, PG 2024 page
  (https://ceowestbengal.wb.gov.in/Election_details/3213), link "AC and PCwise
  Polling Stations and Elector (Elector as per last date of filing
  nomination)":
  https://ceowestbengal.wb.gov.in/Downloads/Election/GE2024/Phasewise_PCwise_Elector_Polling%20Station_PE2024.pdf
  (14 pages; the table is laid out by phase and parliamentary constituency
  with merged cells, so rows were read by AC number and checked by sum).
- Asserts passed: every AC 1 to 294 found exactly once; men + women + third =
  total in every row; column sums equal the PDF's State Total: 80,530 polling
  stations, 3,86,13,415 men, 3,73,94,818 women, 1,773 third, 7,60,10,006 in
  all.
- Odd: the PDF's "Total for Phase 4" line (1,943 / 18,57,022) is in fact the
  Birbhum PC total; the next unlabelled line is the phase 4 total. AC 246
  Raghunathpur's number and name share one cell. Neither affects the rows.
- Corrected 2026-10-02: **three rows inside the Jhargram PC block were
  rotated** when the merged cells were read. The PDF prints the seven Jhargram
  PC segments under one merged PC cell, and the block's total (2,018 polling
  stations, 17,79,794 electors) holds whichever segment each row is given to,
  so the sums could not catch it. The polling stations did. The state's count
  barely moved between the 2024 roll and the draft (80,530 against 80,681),
  and as first read Salboni had 287 stations against 314 on the draft, with a
  roll 18.6% smaller than its draft, the only one of 294 seats to grow.
  Rotated, every count lines up: Gopiballavpur 287 (draft 287), Jhargram
  265 (263), Salboni 314 (314), and each draft is about 96% of its 2024 roll,
  like the seats around it. The rows now read 221 Gopiballavpur 2,35,453,
  222 Jhargram 2,42,596, 234 Salboni 2,89,187. `scripts/build_westbengal.py`
  asserts that no seat's polling stations differ from the draft's by more
  than 50 and that no draft exceeds its 2024 roll by more than 2%.
- 2024 minus draft: 51,93,376 across the state, -43,686 to +73,936 by AC
  (one AC grew). The gap mixes 18 months of ordinary roll changes with the
  SIR removals, so it is at best an upper-level proxy, not the removals.

### results_2026.csv

ac, ac_name, winner, winner_party, winner_votes, runner_up, runner_up_party,
runner_up_votes, margin, nota_votes, total_votes, n_candidates, evm_rounds,
note. April 2026 Assembly election, all 294 ACs.

- Source: ECI results site, one page per AC,
  https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseS25{ac}.htm
  for ac = 1 to 294 (all candidates with EVM, postal and total votes, plus
  NOTA). Cross-checked against the 15 state-wise pages
  https://results.eci.gov.in/ResultAcGenMay2026/statewiseS25{1..15}.htm.
- Winner and runner-up are the two highest totals among candidates (NOTA
  excluded). total_votes is the sum of all candidates plus NOTA, postal
  included. Candidate names are as ECI prints them (these are candidates,
  not electors).
- Asserts passed: 294 rows; margin = winner_votes - runner_up_votes in every
  row; winner strictly ahead of runner-up everywhere; exactly one NOTA line
  per AC; the computed margin equals the margin on the state-wise pages for
  all 293 ACs listed there.
- AC 144 Falta: the state-wise pages say "Status Known For 293 out of 293"
  and show Falta as in progress; its constituency page carries the re-poll
  count (22/22 rounds; Debangshu Panda, BJP, 1,49,666 against Sambhu Nath
  Kurmi, CPI(M), 40,645, margin 1,09,021), which matches press reports of the
  re-poll counted on 24 May 2026. Flagged in `note`. ECI's statistical
  report exists in two versions, including and excluding AC-144
  (https://www.eci.gov.in/statistical-report/ae/2026/28 and /27).
- Seats: BJP 208 (207 plus Falta), AITC 80, INC 2, Aam Janata Unnayan Party
  2, CPI(M) 1, All India Secular Front 1. State total votes 6,39,63,262;
  NOTA 4,95,716.
- Electors are not shown on the results pages; use
  electors_nomination_2026_ac.csv (votes / electors = 93.7% statewide).
- Not obtained: ECI's statistical-report spreadsheets (Detailed Results,
  AC-wise electors and voters). The download API behind
  www.eci.gov.in/statistical-report answers "Access denied" / HTTP 406 to
  both the sandbox and Firecrawl.

### results_2021.csv

ac, ac_name, winner, winner_party, winner_votes, runner_up, runner_up_party,
runner_up_votes, margin. 2021 Assembly election, 294 ACs, with Samserganj
(56) and Jangipur (58) from their delayed poll of 30 September 2021.

- Source: SECONDARY. English Wikipedia, "2021 West Bengal Legislative
  Assembly election", section "Results by constituency", read as wikitext:
  https://en.wikipedia.org/w/index.php?title=2021_West_Bengal_Legislative_Assembly_election&action=raw
  The ECI primary sources could not be reached: the 2021 results pages
  (results.eci.gov.in/Result2021/...) are gone (404) and the archived copies
  are pre-count snapshots; the ECI statistical report
  (https://old.eci.gov.in/files/file/14106-west-bengal-general-legislative-election-2021-including-ac-56-58/)
  is a download behind the old site, which refused the connection.
  Replace with ECI's 2021 Detailed Results when it can be fetched.
- Party labels are Wikipedia's abbreviations (AITC, BJP, INC, CPI(M), ISF,
  IND, AJSU).
- Asserts passed: ACs 1 to 294; margin = winner_votes - runner_up_votes in
  every row; seat totals AITC 215, BJP 77, ISF 1, IND 1, which is the 2021
  result including the two delayed seats.

## What was looked for and not found

### AC-level removals (the key table) — no primary source found

No `asd_ac.csv`, `roll_before_ac.csv`, `final_roll_ac.csv` or
`adjudication_ac.csv` was written, because no primary AC-level table exists
that was reachable.

Searched:

- CEO West Bengal SIR page https://ceowestbengal.wb.gov.in/SIR: the AC-wise
  draft roll above, press notes PN-25 (28.10.2025), PN-36 and PN-37
  (16.12.2025), and the daily claims-and-objections bulletins
  (17.12.2025 to 20.01.2026). All state level only.
- The ASDD page https://ceowestbengal.wb.gov.in/asd_sir. Its district and AC
  menus return, per AC, only a list of polling stations with a download
  link for each part's ASDD list and BLO-BLA minutes (handler fields psId,
  name, asd, mom). There are no counts. The counts exist only inside the
  part-wise lists of named electors, which were not opened.
- "Roll Revision Data" (https://ceowestbengal.wb.gov.in/RollRevisionData):
  HTTP 500.
- Press notes menu, Publications, Electors, Elector Supplement Roll and the
  election pages on the CEO site; ECI's statutory reports page
  (voters.eci.gov.in/download-statutory-report, Forms 9 to 11B, which are
  lists of claims by individual, behind a captcha).
- Final roll of 28 February 2026: press note PN-05-2026
  (https://ceowestbengal.wb.gov.in/Downloads/News/Final%20Press%20Note%20CEO-PN-05-2026.pdf)
  gives state totals only. A guessed AC-wise file name on the pattern of the
  draft roll returned 404.

State-level reason split, from PN-05-2026 (primary): the roll of 27.10.2025
held 7,66,37,529 (3,89,03,865 men, 3,77,31,887 women, 1,777 third gender);
enumeration forms not received 58,20,899: deceased 24,16,852, absent
12,20,039, shifted 19,88,076, already enrolled 1,38,328, others 57,604.
After the draft: additions 1,82,036 (Form 6/6A) and 6,671 (Form 8),
Form 7 deletions 5,46,053, under adjudication 60,06,675, final roll
6,44,52,609. These agree with `data/india/raw/final.csv`.

Compilations that do give AC-level removals, recorded here and NOT used as
data:

- Sabar Institute, SIR deletion map, 294 ACs (ASDD 58,19,653, gross deleted
  90,82,099): https://sabar-institute.github.io/maps/overall/ and factsheet
  https://sabarinstitute.org/research-and-publications/west-bengal-factsheet .
  Built from ECI's published lists of named electors. Cited by Times of
  India (https://timesofindia.indiatimes.com/india/decoding-bengal-sir-data-of-123-margins-49-in-closer-focus/articleshow/130963912.cms).
- The India Forum, Subhasish Dey, 4 June 2026:
  https://www.theindiaforum.in/politics/how-invisible-maths-electoral-roll-revision-altered-west-bengals-election
  (ASDD 58.18 lakh, under adjudication 27.16 lakh, draft roll deletions 5.46
  lakh, by AC; says ECI released constituency-level data for 90.82 lakh
  deletions and 1.88 lakh additions but none for the 5 lakh added on
  18 April 2026).
- The Wire: https://m.thewire.in/article/politics/sir-in-nearly-half-of-bengals-assembly-seats-deletions-outnumber-2024-winning-margins
  and https://m.thewire.in/article/rights/sir-deletions-bjp-win-bengal-asdd-deletions-under-adjudication .
- UNI (Facebook post) quotes "data released by the ECI" on adjudication
  deletions by AC (Samserganj 74,775). The ECI document itself was not found.

Forms the removals could still take from a primary source: (a) the per-part
ASDD and adjudication deletion lists on voters.eci.gov.in, aggregated to
counts by a script that never stores a name, which is how the Bihar reasons
were built; (b) the CEO's AC-wise Format 4B or final-roll table if it is
published; (c) the ECI release cited by UNI and The India Forum.

### border_ac.csv — not written

No primary source listing West Bengal's Bangladesh border districts was
reached in the time available (searched MHA, Lok Sabha answers and the
Border Area Development Programme pages). Press reports speak of "nine
border districts" without naming them in a primary document.

## Not opened

The ASDD lists, the BLO-BLA minutes, the supplementary and deletion lists,
and the roll PDFs all carry names and EPIC numbers. None was downloaded.

## District-wise search, 2026-10-01 (second pass)

### electors_phase1_district.csv

district, men, women, third, total. Electors by district for the 16 districts
polling in phase 1 (23 April 2026), as printed in the CEO's press note. This
is the election roll (final SIR roll as amended to the last date of
nomination), not a count of removals. District names as the note prints them.

- Source: CEO West Bengal, Press Note No. 38/CEO/PN/2026 dated 13.04.2026,
  "Elector data for Phase 1":
  https://ceowestbengal.wb.gov.in/Downloads/PressNoteMenu/Press%20note%2038.pdf
  (1 page), listed at https://ceowestbengal.wb.gov.in/PressNoteMenu.
- Asserts passed: 16 rows; men + women + third = total in every row; column
  sums equal the note's "State Total (Phase - I)" (1,84,99,496 / 1,75,77,210 /
  465 / 3,60,77,171); every district equals the sum of its phase 1 ACs in
  electors_nomination_2026_ac.csv in all four columns.
- No phase 2 counterpart by district was found. Press note 55/CEO/PN/2026
  (27.04.2026) gives phase 2 electors by AC (3,21,73,837 general electors,
  equal to the AC file) and adds 39,961 service electors.

### What was looked for and not found (district level)

None of the four SIR tables exists as a published CEO or ECI document that
could be reached. No asd_district.csv, final_district.csv or
adjudication_district.csv was written.

1. District-wise removals at the draft (ASDD, by reason). Read in full:
   PN-36/2025 of 16.12.2025
   (https://ceowestbengal.wb.gov.in/Downloads/SIR2026/SIR_PressNote/CEO%20PN_36_16.12.2025.pdf,
   state totals only, rounded to lakhs), PN-37/2025 (roll observers only) and
   PN-33. The full lists of SIR press notes and press bulletins on
   https://ceowestbengal.wb.gov.in/SIR (PN 10 to 37 of 2025, PN 01 and 03 of
   2026, bulletins of 17.12.2025 to 20.01.2026) were checked by title; none is
   a district table, and the first pass above found the bulletins state level.
   The CEO page, the 24 district
   links on https://ceowestbengal.wb.gov.in/Dist_link (Paschim Bardhaman's SIR
   page checked: it links back to the CEO's per-part lists),
   https://ceowestbengal.wb.gov.in/Publications and RollRevisionData (HTTP 500)
   carry no district table. Press reports of 12 and 16 December 2025 (PTI via
   ThePrint; The Hindu) attribute their district and AC figures to "a poll
   panel official" and "data shared by the office of the CEO", which points to
   a briefing handout rather than a published document.
2. Final roll of 28.02.2026 by district: PN-05/2026
   (https://ceowestbengal.wb.gov.in/Downloads/News/Final%20Press%20Note%20CEO-PN-05-2026.pdf)
   is state level only. Press notes 08 to 58 of 2026 on
   https://ceowestbengal.wb.gov.in/PressNoteMenu are election-period notes
   (MCC, seizures, nominations, electors); the sampled ones (08, 25, 26, 27,
   29, 30, 31, 38, 46, 51, 55, 58) carry no SIR table.
3. Names under adjudication by district: The Indian Express (7 April 2026,
   https://indianexpress.com/article/political-pulse/54-out-ec-releases-first-data-of-deletions-after-adjudication-10623077/)
   reproduces a 24-district table it attributes to the ECI (action to be
   taken 60,06,675; found eligible 32,68,119; found not eligible 27,16,393),
   and UNI quotes an ECI official that "district-wise data has now been placed
   in the public domain". The ECI document itself was not found: it is not on
   the CEO site, and the ECI press-release listing
   (https://www.eci.gov.in/issue-details-page/press-releases) shows only the
   latest 20 items to a scraper while the file downloads and the listing API
   answer "Access denied" or HTTP 406. The newspaper table is NOT recorded.
4. AC-wise ASDD count by the CEO or ECI: not found. The PTI report of
   12.12.2025 ("EC releases constituency-wise data") quotes an official, not
   a document. The CEO's ASDD page (https://ceowestbengal.wb.gov.in/asd_sir)
   offers only per-part lists of named electors, which were not opened.

Not opened, again: no list of individual electors was downloaded.
