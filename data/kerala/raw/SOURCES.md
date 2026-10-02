# Kerala raw tables: sources

Files fetched 2026-10-01 unless stated. One row per assembly constituency (AC 1 to 140)
unless stated. Aggregates only: no list of individual electors was opened or
stored. `check.py` in this folder re-runs every assertion below
(`python3 data/kerala/raw/check.py`).

## asd_ac.csv: not written

No primary table of the names left off the draft roll by AC, by reason or in
total, was found. What was checked:

- https://www.ceo.kerala.gov.in/sir (the SIR page). It links the draft and
  final electorate PDFs used below, claims-and-objections lists, gallery and
  videos, and "Kerala SIR List of ASD Electors", which goes to
  https://order.ceo.kerala.gov.in/sir/search/index, a station-by-station
  search of the individual names. That was not opened.
- https://www.ceo.kerala.gov.in/asd-list: a notice that the updated ASD list as
  on 23 December is uploaded, and the same two links. No count table.
- The draft electorate PDF (below): sex, district, overseas and age tables for
  the draft roll only. No removals.
- https://www.ceo.kerala.gov.in/elections/legislative-assembly-2026 and
  https://www.ceo.kerala.gov.in/electoral-roll: nothing on ASD.
- Web searches for an AC-wise or district-wise ASD table on ceo.kerala.gov.in
  and eci.gov.in found only newspaper reports of the state total. Those give
  24,08,503 (The Hindu, ThePrint; The News Minute prints 24,80,503) and a split
  by reason that is not found in any primary document reached here, so it is
  not recorded.
- Not checked: the per-day claims and objections pages
  (https://www.ceo.kerala.gov.in/sir/claimsobjections/<date>), which appear to
  be lists of applications, and the Sutharyam GIS portal, which did not
  answer from the sandbox.

Draft roll (25,442,352) plus the press figure of 24,08,503 is 27,850,855,
which agrees with the "2.78 crore" pre-revision roll reported in the press.
That is consistent, not verified.

## draft_roll_ac.csv

Electors by sex on the draft roll of 23.12.2025, general plus overseas.

- Source: https://www.ceo.kerala.gov.in/uploads/sir-2026/draft-electorate-23-12-2025.pdf
  ("DRAFT ELECTORATE PUBLISHED ON 23-12-2025", 8 pages), linked from
  https://www.ceo.kerala.gov.in/sir. Read through Firecrawl's PDF parser; the
  CEO host resets plain connections from the sandbox, so the PDF itself is not
  stored.
- Columns: ac, ac_name, district, men, women, third, total. AC names and
  districts are as the PDF spells them, upper case. The PDF leaves the
  district blank on three continuation rows (72, 73, 110); carried down.
- Assertions passed: 140 rows, ACs 1 to 140 once each; total = men + women +
  third in every row; all 14 DISTRICT TOTAL rows equal the sum of their ACs;
  column sums equal the state row, 12,383,341 men, 13,058,731 women, 280 third
  gender, 25,442,352 total.
- The PDF also gives overseas electors by district (64,394 in all) and
  electors by age band; not taken. Per-AC figures include overseas electors.

## final_roll_ac.csv

Electors by sex on the final SIR roll, same layout.

- Source: https://www.ceo.kerala.gov.in/uploads/sir-2026/final_electorate_sir_2026.pdf,
  linked from https://www.ceo.kerala.gov.in/sir. Via Firecrawl.
- Same columns. Assertions passed: 140 rows; row sums; all 14 district totals;
  column sums equal the state row, 13,126,048 men, 13,827,319 women, 277 third
  gender, 26,953,644 total. The final roll is larger than the draft in all 140
  ACs (by 1,511,292 statewide).
- Odd: the heading reads "FINAL ELECTORATE PUBLISHED ON 21-02-2025" (the year
  is evidently 2026), and the PDF's internal title is "FINAL ELECTORATE
  23-12-2025 (1)". The date of the final roll is therefore taken as
  21.02.2026 on the strength of the heading only. AC 2 Kasaragod shows exactly
  104,866 men and 104,866 women; the row adds up and is copied as printed.
  Overseas electors rise from 64,394 on the draft to 223,558.
- Spellings: the district is printed "KOLLM" (Kollam) in both PDFs and AC 124
  "KOLLM"; AC 8 is "TALIPARAMBA" on the draft and "TALIPARMBA" on the final.
  Not corrected. Otherwise names and districts agree between the two tables.
- The roll the election was held on is election_roll_ac.csv, below.
  Statistical report table 11, "AC Wise Number Of Electors"
  (.../statistical-report/11_-_AC_Wise_Number_Of_Electors_1778164525.pdf),
  was not read.

## roll_before_ac.csv

How the numbers were taken, for both files: the CEO host refuses this sandbox and
no scraper key reaches scripts, so the scraper's text of each AC table was
copied verbatim into a scratch file and the numbers were parsed from that file
by script. A copying slip would break a row sum, a district total or the state
total, and every one of them agrees with the printed figure.

Electors by sex on the final roll of the Special Summary Revision 2025
(qualifying date 1.1.2025), published 06.01.2025: the last roll published by
AC before the revision. General plus overseas. Fetched 2026-10-02.

- Source: https://www.ceo.kerala.gov.in/ceokerala/pdf/ssr-2025-final-electorate.pdf
  ("FINAL ELECTORATE PUBLISHED ON 06.01.2025", 9 pages), linked as item 8 from
  https://www.ceo.kerala.gov.in/content/ssr2025. Read through Firecrawl's PDF
  parser (the CEO host resets plain connections from the sandbox); the parser's
  text of the AC table was saved to a scratch file and parsed by script, and
  the PDF is not stored.
- Date confirmed by the press note linked as item 9,
  https://www.ceo.kerala.gov.in/ceokerala/pdf/ssr2025-pressnote.pdf (Malayalam,
  dated 06/01/2025), which gives the same state figures: 2,78,10,942 electors,
  1,43,69,092 women, 1,34,41,490 men, 360 third gender, 90,124 overseas;
  Malappuram largest (34,01,577), Wayanad smallest (6,42,200). All agree with
  the table.
- Columns: ac, ac_name, district, men, women, third, total. AC names as the PDF
  spells them. District copied from draft_roll_ac.csv; the PDF's own district
  labels agree except that it prints "8-ERANAKULAM".
- Assertions passed: 140 rows, ACs 1 to 140 once each; total = men + women +
  third in every row; all 14 DISTRICT TOTAL rows equal the sum of their ACs;
  column sums equal the state table on page 1, 13,441,490 men, 14,369,092
  women, 360 third gender, 27,810,942 total. AC names equal the draft's except
  8 TALIPARMBA (draft TALIPARAMBA) and 42 VALIKKUNNU (draft VALLIKKUNNU).
  Larger than the draft in all 140 ACs, by 2,368,590 statewide (2.5% to 26.1%
  of the AC's roll).
- Odd: the AC table has no STATE TOTAL row, so the state check is against the
  summary on page 1 and the press note. The last column of the AC table is
  headed "DISTRICT TOTAL" though it holds AC totals. The third-gender district
  table in the same PDF is headed "Final Roll 2024". Overseas electors were
  90,124 here against 64,394 on the draft.
- This is not the roll frozen for the revision. The press gives that roll
  (27.10.2025) as 2,78,50,855; this one is 39,913 smaller, as gender.csv in
  data/india/raw says. So roll_before minus draft (2,368,590) is not the
  number of names left off the draft, which the press puts at 24,08,503; the
  difference is the 39,913 net change between January and October 2025, and
  the AC split of that change is not known.
- Searched and not found: an AC-wise table of the roll as on 27.10.2025.
  Searches on ceo.kerala.gov.in and eci.gov.in found only the state total
  (press reports and the CEO's draft-roll press note of 23.12.2025, seen as a
  copy on getapi.indiatvnews.com and not used). The SIR page and the
  electoral-roll page carry no such table. The 2024 Lok Sabha electors by
  assembly segment were not sought, since a later primary roll was found.

## election_roll_ac.csv

How the numbers were taken, for both files: the CEO host refuses this sandbox and
no scraper key reaches scripts, so the scraper's text of each AC table was
copied verbatim into a scratch file and the numbers were parsed from that file
by script. A copying slip would break a row sum, a district total or the state
total, and every one of them agrees with the printed figure.

Electors by sex on the roll the 2026 assembly election was held on,
"ELECTORATE PUBLISHED AS ON 23 MARCH 2026", general plus overseas. Fetched
2026-10-02.

- Source: https://www.ceo.kerala.gov.in/ceokerala/pdf/govt_orders/legislative-assembly-2026/electorate-published-as-on-23-march-2026.pdf
  (11 pages), linked from
  https://www.ceo.kerala.gov.in/elections/legislative-assembly-2026. Via
  Firecrawl as above; the parser's text of the AC table parsed by script.
- Same columns. District copied from draft_roll_ac.csv; the PDF prints
  "8-ERANAKULAM" and "13-KOLLAM" where the draft has ERNAKULAM and KOLLM.
- Assertions passed: 140 rows; row sums; all 14 DISTRICT TOTAL rows; column
  sums equal the printed STATE TOTAL row and the state table on page 1,
  13,220,811 men, 13,921,868 women, 273 third gender, 27,142,952 total. AC
  names equal the draft's except 61 CHELACKARA (draft CHELAKKARA) and 83
  THRIPKAKARA (draft THRIKKAKARA); AC 124 is printed "KOLLM" here too.
  Larger than the final SIR roll in all 140 ACs (by 339 at least), by 189,308
  statewide. Total votes in results_2026.csv are 79.6% of it.
- Overseas electors 242,093 (204,218 men), against 223,558 on the final SIR
  roll. Service voters (53,984) are printed separately and are not in the AC
  figures, as in the other tables. The PDF also has age, PwD and polling
  station tables; not taken.

## results_2026.csv and results_2026_candidates.csv

Assembly election of 2026; the constituency pages read "Last Updated at ... On 05/05/2026". Kerala is S11 at ECI
(the page headings read "Assembly Constituency 1 - MANJESHWAR (Kerala)").

- Source: https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseS11{ac}.htm
  for ac 1 to 140, and the statewise pages statewiseS111.htm to
  statewiseS117.htm (S118 onward return 404). Fetched directly with curl.
- Columns as in data/tamilnadu/raw: results_2026.csv has ac, ac_name (ECI
  spelling), winner, winner_party, winner_votes, runner_up, runner_up_party,
  runner_up_votes, margin, total_votes (all candidates and NOTA, postal
  included), nota_votes, postal_votes. results_2026_candidates.csv has every
  row of every constituency table, 1,023 rows including NOTA.
- Assertions passed: 140 rows; status "Result Declared" in all 140; candidate
  totals, EVM and postal columns each sum to the page's Total row; EVM +
  postal = total for every candidate; exactly one NOTA row per AC; winner,
  runner-up, both parties, margin and AC name from the constituency page equal
  the statewise page in all 140; margin = winner_votes - runner_up_votes.
  Winners by party: INC 63, CPI(M) 26, IUML 22, CPI 8, Kerala Congress 7,
  Independent 4, RSP 3, BJP 3, RJD 1, RMPI 1, Kerala Congress (Jacob) 1,
  CMP Kerala State Committee 1. Total votes 21,595,055, 80.1% of the final
  SIR roll (70.7% to 86.9% by AC). Smallest margin 126.
- Missing: electors are not on these pages. ECI's disclaimer says the figures
  are as entered by Returning Officers and final data is in Form 20. The CEO's
  statistical report for 2026 (tables 1 to 14, including 10 "Detailed
  Results") is linked from
  https://www.ceo.kerala.gov.in/elections/legislative-assembly-2026 and was
  not reached.
- Spelling: 15 ECI names differ from the CEO roll tables (8 TALIPARAMBA,
  32 THIRUVAMBADI, 34 ERNAD, 42 VALLIKUNNU, 52 OTTAPPALAM, 54 MANNARKKAD,
  59 NEMMARA, 70 IRINJALAKUDA, 71 PUDUKKAD, 72 CHALAKUDY, 105 AMBALAPPUZHA,
  109 MAVELIKKARA, 124 KOLLAM, 126 CHATHANNOOR, 132 KAZHAKOOTTAM). Same AC
  numbers; join on `ac`.

## results_2021.csv: not written

The primary sources exist but were not reached:

- https://results.eci.gov.in/Result2021/ConstituencywiseS111.htm returns 404.
- The CEO's 2021 page
  (https://www.ceo.kerala.gov.in/elections/election-history/la2021-related-info)
  links the statistical report,
  https://www.ceo.kerala.gov.in/pdf/GE-2021/statistical_report.pdf, and
  https://www.ceo.kerala.gov.in/detailedResultsGE2021 (booth-wise results by
  district selector). The CEO host refuses plain connections from the sandbox,
  and the Firecrawl account ran out of credits before the report could be read.
- The ECI site lists an "ae-2021-kerala" page, but its data API was not used.

No secondary source was substituted.

## Not done

- No age, overseas or district-only tables were taken.
- Nothing in the repository outside data/kerala/raw/ was changed.
