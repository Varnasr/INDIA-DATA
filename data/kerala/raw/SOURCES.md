# Kerala raw tables: sources

All files fetched 2026-10-01. One row per assembly constituency (AC 1 to 140)
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
- Not fetched: the roll the election was held on. The 2026 election page links
  https://www.ceo.kerala.gov.in/ceokerala/pdf/govt_orders/legislative-assembly-2026/electorate-published-as-on-23-march-2026.pdf
  and statistical report table 11, "AC Wise Number Of Electors"
  (.../statistical-report/11_-_AC_Wise_Number_Of_Electors_1778164525.pdf).

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
