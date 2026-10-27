# Karnataka raw tables: sources

All files fetched 2026-10-01. Aggregates only: no list of individual electors
was opened, downloaded or stored. `check_raw.py` in this folder asserts every
check listed below (20 checks, all passing).

## What does not exist, and what was written instead

**The SIR tables were not published by assembly constituency.** The CEO
published the enumeration results and the draft roll by its 34 election
districts only (the 31 revenue districts, with Bengaluru split into Bangalore
Urban and the three B.B.M.P districts). So `asd_ac.csv`, `draft_roll_ac.csv`
and `final_roll_ac.csv` were not written, and the district tables below take
their place. What was checked:

- The CEO SIR page, https://ceo.karnataka.gov.in/382/special-intensive-revision--2026/en:
  a press note, a booklet, forms, the ASDDO elector list and the list of persons
  issued notices. No AC-wise count.
- The CEO press releases page, https://ceo.karnataka.gov.in/348/press-releases-/en.
  The notes of 17.08.2026, 19.08.2026, 24.08.2026, 28.08.2026 and 25.09.2026 were
  read. Every table in them is by district or for the state. The 28.08.2026 note
  runs to 122 pages, but past page 4 it is the gazette notification of
  Assistant Electoral Registration Officers by AC, with no elector counts.
- https://ceo.karnataka.gov.in/PublishASDD/index.php (the "ASDDO Electors List").
  The page offers part-wise PDFs of named electors behind a captcha, and an EPIC
  search. It has no summary table. Only the selector page was read; no part was
  opened. A count by AC could only be made by tallying those named lists, which
  this collection does not do.
- https://voters.eci.gov.in/download-statutory-report?stateCode=S10: AC-wise
  claims and objections (Forms 9, 10, 11, 11A, 11B) behind a captcha. These are
  lists of applications, not the draft roll or the removals, and were not
  downloaded.
- https://voters.eci.gov.in/download-eroll?stateCode=S10, the draft roll itself:
  part-wise lists of named electors. Not opened.
- A search of ceo.karnataka.gov.in for "constituency wise" electors in 2026
  returned only the home page. OpenCity's Karnataka SIR dataset
  (https://data.opencity.in/dataset/karnataka-sir-2026) likewise holds only the
  district-level press notes.

**The roll before the revision by sex was not found in a primary source.** The
CEO notes give the roll of 16.06.2026 by district as a total only. The repo's
`data/india/raw/gender.csv` takes Karnataka's removals by sex from a newspaper
report of a "frozen roll" by sex. The CEO notes of 29.06.2026 and 30.06.2026,
which may carry that roll by sex, were not read: the Firecrawl account ran out of
credits at that request, and ceo.karnataka.gov.in refuses direct connections
from this sandbox. They are the next place to look:
https://ceo.karnataka.gov.in/uploads/media_to_upload1782732956.pdf (29.06) and
https://ceo.karnataka.gov.in/uploads/DAILY_PRESS_NOTE_30.06.2026_06.00PM.pdf (30.06).

**The final roll was published on 27 October 2026, and only for the state.**
The CEO schedule in the 24.08.2026 note set its publication for that day. Claims
and objections closed on 23.09.2026, and the notice phase ran to 22.10.2026. No
district or constituency table of the final roll was found (see the last section).

## asd_district.csv

Names left off the draft roll (marked ASDDO, "uncollectable enumeration forms"),
by election district and reason.

- Source: CEO Karnataka press note No. DPAR 163 ChuMaPa 2026 of 24.08.2026,
  "Special Intensive Revision-2026: Draft Electoral Roll Publication",
  https://ceo.karnataka.gov.in/uploads/PRESS%20NOTE%2024th%20Aug.pdf, Annexure-1
  (page 10, digitisation) and Annexure-2 (page 11, ASDDO by reason).
  The original was read through Firecrawl (country IN). The numbers were
  extracted with pdfplumber from OpenCity's copy of the same PDF,
  https://data.opencity.in/dataset/51e6e2e7-8e40-4006-808e-fd2d652b6e74/resource/8c704681-a18b-4be4-97c3-6af20f2a05f1/download/press-note-24th-aug.pdf
  (sha256 f115c7a7a677ffd0...). That copy has the same 23 pages and the same
  document title ("Microsoft Word - PRESS FINAL DISTRICT WISE DATA - Copy"),
  and its figures agree with the original as read.
- Columns: district, electors_before (roll as on 16.06.2026), absent, shifted
  ("permanently shifted"), dead, duplicate ("already enrolled"), other, total,
  digitised (enumeration forms digitised, which became the draft roll).
  Rows in the order of Annexure-2. District names are upper-cased as in
  Annexure-1. Two spellings were normalised: "Mandy" as Firecrawl read
  Annexure-2 (the PDF text says Mandya) and "DUPI" (Udupi) in later annexures.
- Assertions passed: 34 districts, each once; absent + shifted + dead +
  duplicate + other = total in every row; digitised + total = electors_before in
  every row; every column sums to the published "Karnataka State" row:
  55,432,314 before, 1,517,042 absent, 6,545,679 shifted, 1,639,864 dead,
  709,870 duplicate, 383,884 other, 10,796,339 removed (19.48%), 44,635,975
  digitised.
- Odd: the daily note of 17.08.2026 (the last day of enumeration) gave
  10,831,945 marked ASDDO; the draft-roll figures are 35,606 lower, after
  roll-backs. The 24.08.2026 figures are the ones taken. Shares removed are
  highest in B.B.M.P (South) 49.33%, B.B.M.P (Central) 45.54%, B.B.M.P (North)
  45.12% and Bangalore Urban 42.71%, and lowest in Udupi 5.95%.

## draft_roll_district.csv

Electors on the draft roll of 24.08.2026, by election district and sex.

- Source: the same 24.08.2026 press note, Annexure-5 (page 15, "District wise
  General Electors") and Annexure-10 (page 20, "District wise Service Electors").
- Columns: district, men, women, third (general electors), general_total,
  service_men, service_women, service_total, total (general plus service).
- Assertions passed: 34 rows; men + women + third = general_total in every row;
  general_total equals Annexure-1's digitised count in all 34 districts; the
  general columns sum to the published totals, 22,159,240 men, 22,473,864 women,
  2,871 third gender, 44,635,975.
- Odd: **Annexure-10 lists 32 districts. Yadgir and Vijayanagara are missing**,
  and the 32 rows sum to 42,027 men and 1,682 women (43,709), while its state
  row says 42,487, 1,689 and 44,176. The shortfall, 460 men and 7 women, is most
  likely the two missing districts together, but the note does not say so and
  does not split it. Their service and total cells are left blank, not zero, and
  the check asserts the shortfall is exactly 460 / 7 / 467. Service electors have
  no third-gender column. The note's state total is 44,680,151 with service
  electors.

## roll_20260925_district.csv

The roll during claims and objections, by district and sex. Not the final roll.

- Source: CEO Karnataka press note No. DPAR 172 ChuMaPa 2026 of 25.09.2026,
  https://ceo.karnataka.gov.in/uploads/PRESS%20NOTE-%2025_1790322207.pdf,
  "ELECTORS as on 25.09.2026" (page 3), read through Firecrawl's PDF parser.
- Columns: district, men, women, third, total.
- Assertions passed: 34 rows; men + women + third = total in every row; columns
  sum to the published state row, 22,255,071 men, 22,586,136 women, 2,873 third
  gender, 44,844,080.
- Odd: the note does not say whether service electors are included. The figures
  sit close to the draft's general electors (Bangalore Urban 2,303,825 against
  2,303,623 general, while its service electors alone are 749), so they are
  probably general electors only. The state total is 208,105 above the draft's
  general electors.

## results_2023.csv and results_2023_candidates.csv

The general election to the Karnataka Legislative Assembly, May 2023.

- **Not a primary source.** ECI's own results pages for 2023
  (results.eci.gov.in/ResultAcGenMay2023/...) now answer 404. The ECI
  statistical report, https://old.eci.gov.in/files/file/15163-karnataka-2023/
  (14 parts including "10 - Detailed Results" and "11 - AC Wise Number Of
  Electors"), was found. But its files sit behind a session-keyed download, and
  old.eci.gov.in and www.eci.gov.in refuse this sandbox (connection reset, and
  HTTP 406 from the www.eci.gov.in firewall). The CEO's 2023 page,
  https://ceo.karnataka.gov.in/333/general-assembly-election-2023/en, carries
  Form 20 but no AC result summary.
- Used instead, as for Tamil Nadu 2021: the TCPD Lok Dhaba candidate-level file
  for Karnataka (built by TCPD from the ECI statistical reports), as mirrored by
  OpenCity in https://data.opencity.in/dataset/karnataka-assembly-elections-2023,
  resource "Karnataka Election Result Details 2023":
  https://data.opencity.in/dataset/7c4d5e03-28b9-4e45-9916-5ae892d8fe1b/resource/d24bee34-312f-42dc-8094-8af7992fcdcc/download/ea07fb5e-fb01-427f-99f4-9ac8793ed2f4.csv
  (sha256 c8553a92119f80d2...). It holds every Karnataka election to 2023; only
  Year 2023, Assembly_No 11, Poll_No 0 was taken (2,839 rows, all general
  election, none a bye-election).
- results_2023.csv columns: ac, ac_name (TCPD spelling, upper case), ac_type
  (GEN/SC/ST), district (TCPD's district, the pre-2026 revenue district; this is
  not the CEO's 34 election districts), winner, winner_party, winner_votes,
  runner_up, runner_up_party, runner_up_votes, margin, valid_votes (all
  candidates and NOTA, postal included), electors. Party codes are TCPD's.
- results_2023_candidates.csv: every row for every AC, including NOTA, with
  columns ac, ac_name, position, candidate, sex, party, votes.
- Assertions passed: ACs 1 to 224, each once; positions run 1..n with one NOTA
  row per AC, never first or second; candidate votes with NOTA sum to
  valid_votes in every AC; margin = winner_votes - runner_up_votes in every row;
  winner and runner-up agree with positions 1 and 2 of the candidate file.
  Winners by party: INC 135, BJP 66, JD(S) 19, IND 2, Kalyana Rajya Pragathi
  Paksha 1, Sarvodaya Karnataka Paksha 1, which is the declared result. State
  sums: 39,154,967 valid votes, 53,768,590 electors (not compared with a
  published total). Narrowest margin: AC 173, 16 votes.
- **Primary cross-check against Form 20.** OpenCity mirrors the CEO's Form 20
  final result sheets for the 28 Bengaluru Urban ACs (150 to 177),
  https://data.opencity.in/dataset/karnataka-assembly-elections-2023-form-20s.
  The CEO's own Form 20 gallery could not be reached here. Three were compared in
  full: 150 Yelahanka (text layer, read programmatically), 165 Rajajinagar and
  176 Bangalore South (scanned, read by eye from the "Total Votes Polled" row).
  In all three, every candidate's total and NOTA equal the TCPD file exactly.
  The other 25 are scans and there is no OCR in this sandbox, so they were not
  compared.
- Odd: **the electors column does not match the Form 20 headers.** Yelahanka:
  Form 20 says 439,024, TCPD 438,429. Bangalore South: Form 20 says 695,797,
  TCPD 740,527. Not resolved. Treat `electors` as TCPD's (from the ECI report)
  until the ECI "AC Wise Number Of Electors" part can be read.
- Not included: bye-elections after May 2023. The CEO's Elections page lists
  Assembly bye-election pages for 2024
  (https://ceo.karnataka.gov.in/347/assembly-bye-election-2024/en,
  https://ceo.karnataka.gov.in/358/assembly-bye-election-2024/en) and 2026
  (https://ceo.karnataka.gov.in/376/assembly-bye-election-2026/en). These were
  not fetched, so a seat's holder at the time of the revision may differ from
  the 2023 winner.

## Not done

- No AC-level SIR table (none published; see above).
- The CEO press notes of 29.06.2026 and 30.06.2026 (the roll by sex at the start
  of enumeration) and the ECI statistical report were not read.
- Nothing in the repository outside data/karnataka/raw/ was changed.

## ac_district.csv

Which of the 34 election districts each of the 224 assembly constituencies
belongs to, used only to draw the district map (`data/geo/karnataka.json`).

- Source: the Election Commission's voter portal lookup, retrieved 2 October
  2026: `https://gateway-voters.eci.gov.in/api/v1/common/districts/S10` lists
  the 34 districts (names identical to `asd_district.csv`) and
  `.../common/acs/<district code>` lists each district's constituencies. Across
  the 34 it returns all 224 constituencies, each once.
- The `source` column carries the ECI address for the 38 constituencies whose
  district differs from the older 30-district list: the 28 Bengaluru seats
  (Bangalore Urban and B.B.M.P North, Central and South, seven each), the nine
  seats of the old Bellary district (Ballari 91 to 95; Vijayanagara 88, 89, 90,
  96 and 104) and Harapanahalli (104), which the older list puts in Davangere.
  The other 186 say `results_2023.csv`, whose district agrees with ECI's for
  every one of them.
- Cross-checked: bengaluruurban.nic.in lists the same seven Bangalore Urban
  seats; vijayanagara.nic.in gives the District Election Officer's jurisdiction
  as 88, 89, 90, 96 and 104; the Karnataka Legislative Assembly members list of
  February 2024 agrees for Ballari and Vijayanagara.
- B.B.M.P (Central) includes Rajarajeshwarinagar (154), away from the city
  core, so it is drawn in two pieces.

## roll_20261009_district.csv, notices_20261009_district.csv, forms_20260616_20261008_district.csv

The press note of 9 October 2026, the latest roll before the final one.

- Source: CEO Karnataka press note No. DPAR 172 ChuMaPa 2026 of 09.10.2026,
  https://ceo.karnataka.gov.in/uploads/Press%20Note%20-%2009_1791527846.pdf
  (linked from the CEO's Facebook post of 9 October; not yet on the press
  releases page on that day), read through Firecrawl's PDF parser. Eight
  pages: the note (pages 1 and 2), Annexure 1 electors by district and sex,
  Annexure 2 notices by district, Annexure 3 Forms 6, 6A, 7 and 8 received
  16.06.2026 to 08.10.2026 by district, Annexures 4 and 5 letters.
- Electors as on 09.10.2026: 22,403,422 men, 22,755,113 women, 2,858 third
  gender, 45,161,393. Like the note of 25 September it does not say whether
  service electors are included.
- Notices: 43,82,315 generated, 43,73,745 delivered, 8,570 not delivered,
  40,88,099 hearings held, 2,85,646 pending. Last hearing 12.10.2026, disposal
  by 22.10.2026, final roll 27.10.2026, unchanged.
- The note counts hearings held and gives no outcome, and gives no count of
  claims and objections admitted, so no removal after the draft is recorded.
- Annexure 3 prints "DUPI" for Udupi and "BANGALORE Rural"; the files use the
  names of the other tables.
- check_raw.py asserts every row identity and that each column sums to the
  printed state row.
- Checked on 9 October 2026: a second reader could not open the PDF (the
  site answered 503 and Firecrawl timed out), so the district rows rest on the
  first reading through Firecrawl's PDF parser. The state row (45,161,393;
  22,403,422 men; 22,755,113 women; 2,858 third gender), the 40,88,099
  hearings, the 1,10,654 Form 7s and the final roll of 27 October were
  matched to India Today and a PTI report of the same day. Read the district
  rows against the PDF when it opens.

## The final roll of 27 October 2026 (in build_karnataka.py, no raw file)

The figures are for the state only, so they are constants in
`scripts/build_karnataka.py` (`FINAL`) and not a raw table.

- Read on 27 October 2026. ceo.karnataka.gov.in refuses direct connections from
  this sandbox. Through Firecrawl, the press releases page
  (https://ceo.karnataka.gov.in/348/press-releases-/en) listed notes up to
  "PRESS NOTE 23" (23.10.2026) and no note on the final roll, and the SIR page
  (https://ceo.karnataka.gov.in/382/special-intensive-revision--2026/en) linked
  "Final Electoral Roll-SIR-2026" to the Election Commission's part-wise rolls of
  named electors (https://voters.eci.gov.in/download-eroll?stateCode=S10), which
  were not opened.
- Total 4,55,00,011 electors, against 5,54,32,314 before the revision, and a net
  rise of 8.64 lakh over the draft: The Hindu, "SIR: Over 99.32 lakh names struck
  off voter list in Karnataka", 27 October 2026, 11:32 am IST,
  https://www.thehindu.com/news/national/karnataka/sir-over-9932-lakh-names-struck-off-voter-list-in-karnataka/article71629941.ece
  (also its live page at 11:57 am IST,
  https://www.thehindu.com/news/national/cec-row-sir-live-updates-supreme-court-hearing-gyanesh-kumar-oct-27-2026/article71629879.ece).
  4,55,00,011 less the draft's 4,46,35,975 general electors is 8,64,036.
- By sex, 2,25,40,493 men, 2,29,12,355 women and 2,841 third gender, "according
  to the CEO's office": ETV Bharat, 27 October 2026, 2:24 PM IST,
  https://www.etvbharat.com/en/state/karnataka-sir-final-voter-list-deleted-voters-special-intensive-revision-enn26102703563.
  The Hindu gives the same in rounded form (2.25 crore, 2.29 crore, 2,841).
- Odd: the three add up to 4,54,55,689, which is 44,322 less than the total.
  Neither report says whether the total includes service electors. The draft
  roll carried 44,176 service electors besides its general electors (above).
  The rise from the draft is therefore measured as the reports measure it, from
  the 4,46,35,975 general electors to the reported total.
- Not published, in either report or on the CEO's site: names added or deleted
  after the draft, the outcome of the hearings, and any table by district or
  constituency. `build_karnataka.py` asserts the 8.64 lakh rise and the 44,322
  gap.
