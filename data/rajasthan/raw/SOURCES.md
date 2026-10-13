# Rajasthan raw tables: sources

All files fetched 2026-10-01. One row per assembly constituency (AC 1 to 200)
unless stated. Aggregates only: no list of individual electors was opened or
stored. `check_raw.py` in this folder asserts everything listed under
"Assertions passed" below (1,787 assertions, all pass).

## Scope of the revision: 199 ACs, then Anta

The SIR covered 199 of the 200 ACs. 193 Anta (Baran) was deferred because of
its bye-election of November 2025 and revised later under a separate order
(https://election.rajasthan.gov.in/27.11.2025%20SIR%20order%20for%20Anta%20AC.pdf;
the 199-AC schedule is
https://election.rajasthan.gov.in/199%20ACs%20SIR%20Schedule.pdf). The
16.12.2025 press note says "Figures excluding Assembly Constituency - Anta".
The CEO's state figures therefore come in two scopes, 199 ACs and 200 ACs, and
`sir_state_summary.csv` keeps them apart.

## Not found: asd_ac.csv and draft_roll_ac.csv

No primary table of the names left off the draft roll by AC, by district or by
reason was found, and no AC-level or district-level draft roll by sex. What was
checked:

- The CEO home page, What's New and Citizen Center
  (https://election.rajasthan.gov.in/), Elector's Statistics
  (https://election.rajasthan.gov.in/ElectorsStatistics.aspx, which now links
  only the 12.03.2026 tables), Press Releases
  (https://election.rajasthan.gov.in/Press%20Releases.aspx, notes 53 to 113,
  06.10.2025 to 13.01.2026; read: 16-12-25 and 18-12-25), Important Circulars
  (https://election.rajasthan.gov.in/Circulars.aspx), and both fact sheets
  (below).
- A guessed `Elector Statics/Electors District with AC 16.12.2025.pdf` returns
  the site's error page. `publicreports/Public_Reports.aspx`, which the
  Wayback Machine holds, now returns the error page.
- The Wayback Machine index of election.rajasthan.gov.in from 2025-11-01
  (`web.archive.org/cdx/search/cdx?url=election.rajasthan.gov.in/*`)
  holds no draft-roll or ASD statistics file (two index queries: the first
  1,000 URLs, and 705 after filtering out maps, images and polling-station
  lists).
- eci.gov.in pages and voters.eci.gov.in (including the "Claims & Objections
  (Date_Wise)" statutory report link) answer 406 to both curl and Firecrawl.
- The only AC-level ASD material the CEO publishes is
  https://election.rajasthan.gov.in/ASD_SIR_2026/ASD_List_EPIC.html and
  `ASD_List_EPIC_District.html?district=N`: "List of Electors whose name were
  in the Rajasthan Electoral Rolls of 2025 but are not included in the Draft
  Roll of SIR-2026", i.e. the lists of individual electors. **Not opened.**
  AC totals could in principle be counted from them; that was not done.
- No roll by AC before the revision was found either. The last pre-revision
  AC tables on the site were for 8.2.2024 (archived
  `Elector%20Statics/District%20and%20AC%20wise%20Electors%208.2.24.pdf`), not
  fetched.

So the only figures for the removals are state totals for 199 ACs, in
`sir_state_summary.csv`.

## sir_state_summary.csv

State totals, in both scopes. Columns: item, scope, men, women, total, source.

- `press_note_16-12-25`:
  https://election.rajasthan.gov.in/Media%20Corner/Press%20Note/16-12-25.pdf
  (CEO press note, 16.12.2025, "Rajasthan SIR: Key Findings of Enumeration
  Phase, 04.11.2025 to 11.12.2025"). Roll before the revision 5,46,56,215;
  enumeration forms collected 5,04,71,396; deceased 8.75 lakh, shifted/absent
  29.6 lakh, enrolled at multiple places 3.44 lakh. The three reasons are
  given **only in lakh, to two decimals**, so they are kept in lakh
  (`*_lakh` rows), not converted to counts.
- `fact_sheet_21-02-2026`:
  https://election.rajasthan.gov.in/Elector%20Statics/Fact%20Sheet%2021.02.2026.pdf
  ("SIR 2026 Final Electors Summary (As on 21.02.2026)"). Its footnote says the
  figures are for 199 ACs excluding Anta, except items 16 to 18 (polling
  stations), which cover 200. Draft roll of 16.12.2025: 5,04,71,324. Final
  roll published 21.02.2026: 5,15,19,929 general, 1,33,844 service.
- `fact_sheet_12-03-2026`:
  https://election.rajasthan.gov.in/Elector%20Statics/Fact%20Sheet%2012.03.2026%20new%20map.pdf
  (linked as "Fact Sheet" on the home page). Same layout, now for 200 ACs:
  draft 5,06,80,870, final 5,17,32,266 general, 1,33,883 service.
- Assertions passed: draft + additions - deletions = final, general + service
  = total, and men + women = total, for each scope; the 12.03.2026 final total
  equals the AC table's GRAND TOTAL.

Why the press totals differ (41.79, 41.85, 44 lakh):

- 8.75 + 29.6 + 3.44 = **41.79 lakh**: the sum of the three rounded reason
  figures in the press note.
- Roll before (5,46,56,215) minus draft roll (5,04,71,324) =
  **41,84,891 (41.85 lakh)**: the exact count of names not carried into the
  draft. (Roll before minus forms collected, 5,04,71,396, gives 41,84,819; the
  72-name gap between forms collected and the draft is not explained.) This is
  the primary figure, derived from two CEO totals; no document states 41,84,891
  itself.
- 41,84,891 plus the 2,42,760 deleted between draft and final is 44,27,651
  (**44 lakh**): every name removed by the final roll, before the 12,91,365
  additions.
- The draft roll for Anta alone is 5,06,80,870 - 5,04,71,324 = 2,09,546.

## final_roll_ac.csv and final_roll_district.csv

Electors by sex on the final roll, all 200 ACs, as on 12.03.2026.

- Source: https://election.rajasthan.gov.in/Elector%20Statics/Electors%20District%20with%20AC%2012.03.2026.pdf
  ("District and Assembly Constituency Wise Number of Electors as on
  12.03.2026"; column header "Electors as per Proposed Current Final Roll
  w.r.t. 01/01/2026 as the Qualifying Date to be Published on 12.03.2026"),
  linked from ElectorsStatistics.aspx as "District-Assembly Constituency Wise
  No. of Electors". The site resets plain connections from the sandbox, so the
  PDF was read through Firecrawl's PDF parser and the table transcribed; every
  number is held by the assertions below. A PC-wise version of the same table
  is linked beside it and was not fetched.
- final_roll_ac.csv columns: ac, ac_name, district, polling_stations, men,
  women, total. Names title-cased from the PDF's upper case, (SC)/(ST) kept.
- final_roll_district.csv: the PDF's 41 district TOTAL rows and its GRAND
  TOTAL row, as published. Columns: district, polling_stations, men, women,
  total.
- **No third-gender column.** The PDF has none, and its footnote (in a legacy
  Kruti Dev font, rendering as "uksV%& 565 Vkalts.MlZ ernkrkvksa dks efgyk
  ernkrkvksa esa lfEefyr fd;k x;k gSA") reads "Note: 565 transgender
  electors have been included among women electors". So `women` includes 565
  third-gender electors statewide, not split by AC.
- General electors only: service voters are not in this table (they are in the
  fact sheet, 1,33,883).
- Assertions passed: 200 rows, ACs 1 to 200 once each; men + women = total in
  every row; for each of the 41 districts the AC sums of polling stations,
  men, women and total equal the published district Total row; column sums
  equal the GRAND TOTAL row, 61,404 polling stations, 2,70,68,143 men,
  2,46,64,123 women, 5,17,32,266 total.
- Odd:
  - 111 Merta (SC): the polling-station cell is unreadable in the PDF (it
    parses as a backtick). It is set to **308**, the Nagaur district total
    (1,540) less its other four ACs. Inferred, not read.
  - The PDF's district column is broken across page breaks for 70 Kaman and
    40 Kotputli (blank; assigned to Deeg and Kotputali-Behror, which their
    district total rows confirm), and the Jaisalmer and Sirohi Total rows have
    no district name. Some Total rows carry a stray AC number.
  - The AC table and the 12.03.2026 fact sheet agree on the total
    (5,17,32,266) but not on the split: the fact sheet has 2,70,68,064 men and
    2,46,64,202 women, 79 fewer men and 79 more women. Not resolved.
  - The 200-AC final total less the 199-AC final total (5,15,19,929) is
    2,12,337; this table gives 193 Anta 2,12,334. Three electors apart.
  - Spellings as in the PDF, including "MARWAR JUNCITON" (119). Seven names
    differ in spelling from ECI's 2023 results (33, 68, 72, 110, 119, 139,
    195); same AC numbers.
  - Districts are the 41 of the 2023 reorganisation as the PDF names them
    (Deedwanna-Kuchaman, Kotputali-Behror, Khairthal-Tijara, Balotara, Beawar,
    Deeg, Phalodi, Salumber). Several ACs sit outside their AC-number block
    (e.g. 116 Jaitaran in Beawar, 157 Dhariawad in Pratapgarh).
- Roll of 21.02.2026 by AC (199 ACs) was not found as a separate table; only
  the 12.03.2026 one is published.

## results_2023.csv, results_2023_candidates.csv, results_2023_turnout.csv

Assembly election of 25 November 2023 (results 3 December 2023), with
3 Karanpur, whose poll was countermanded on a candidate's death and held on
5 January 2024.

- Source: ECI, "Rajasthan Legislative Election 2023 (Including AC-03) -
  Statistical Report",
  https://www.eci.gov.in/rajasthan-legislative-election-2023-including-statistical-report
  (also https://www.eci.gov.in/statistical-report/ae/2024/34). Files, fetched
  directly with curl:
  - 10 Detailed Results: https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/rajasthan/2023_Including/Detailed_Results.xlsx
  - 2 List of Successful Candidates: .../2023_Including/List_of_Successful_Candidates.xlsx
  - 11 AC Wise Number Of Electors: .../2023_Including/AC_Wise_Number_Of_Electors.xlsx
- results_2023_candidates.csv: every candidate row of the Detailed Results
  (including NOTA), columns ac, ac_name, candidate, sex, party (ECI
  abbreviation), general_votes, postal_votes, total_votes. ECI's ballot serial
  number, prefixed to each name in the source, is removed.
- results_2023_turnout.csv: the Detailed Results' per-AC "TURN OUT ... TOTAL:"
  rows and its GRAND TOTAL row, as published (general, postal, total votes).
- results_2023.csv columns: ac, ac_name (ECI spelling), winner, winner_party,
  winner_votes, runner_up, runner_up_party, runner_up_votes, margin,
  total_votes (all candidates and NOTA, postal included), nota_votes,
  postal_votes, electors (the Detailed Results' TOTAL ELECTORS: general
  including NRIs, plus service). Winner and runner-up are the two highest
  non-NOTA candidates.
- Assertions passed (check_raw.py): 200 rows, ACs 1 to 200 once each; one NOTA
  row per AC; in every AC the candidates' general, postal and total votes sum
  to the published TOTAL row, and general + postal = total for every
  candidate; winner is the top candidate; margin = winner_votes -
  runner_up_votes > 0; column sums equal the GRAND TOTAL, 3,94,02,992 general,
  4,27,831 postal, 3,98,30,823 total.
- Cross-checked when built (not in check_raw.py, which does not hold the
  source files): winner party, winner votes, runner-up party, runner-up votes
  and margin equal ECI's List of Successful Candidates in all 200 ACs; electors
  equal ECI's AC Wise Number Of Electors (All Electors, total) in all 200,
  5,29,31,152 in all.
- Winners by party: BJP 115, INC 70, IND 8, BHRTADVSIP (Bharat Adivasi Party)
  3, BSP 2, RLD 1, RLTP (Rashtriya Loktantrik Party) 1. Smallest margin 321.
- Not taken: the bye-elections since 2023 (the CEO site has pages for those of
  November 2024 and November 2025, the latter being Anta). Seats that changed
  hands in them are not reflected here.

## Not done

- Nothing in the repository outside data/rajasthan/raw/ was changed.
- No individual-elector list was opened, including the CEO's ASD lists.

## electors_2023_ac.csv

Electors by AC on the roll of the 2023 assembly election, from ECI's
statistical report 11, "AC Wise Number Of Electors"
(https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/rajasthan/2023_Including/AC_Wise_Number_Of_Electors.xlsx,
fetched 2026-10-03; the server answered 406 to a first request and the file to
a second with browser headers). Columns: ac, ac_name, men, women, third
(general electors, including NRIs), general, service, all_electors.

- Assertions passed when written: 200 rows, ACs 1 to 200 once each; men +
  women + third = general and the service split adds up in every row;
  general sums to 5,27,88,931 and service to 1,42,221, the report's Total row;
  all_electors equals the electors in results_2023.csv in all 200 ACs.
- Used by scripts/build_rajasthan.py, against final_roll_ac.csv, which is
  general electors only and counts the 565 third-gender electors among
  women; the 2023 third-gender electors are added to women to match.

## Press tables of the draft: draft_district_press.csv, draft_ac_press.csv, sirohi_sex_press.csv

Read on 13 October 2026. On 16 December 2025, the day the draft was
published, each District Election Officer briefed parties and reporters with
the district's roll on 27 October 2025, the enumeration forms received (the
draft), the forms not received (the names left off) and the five reasons (dead,
permanently shifted, absent, enrolled at more than one place, other). Dainik
Bhaskar's district editions printed them as tables, most with a row for each
constituency; Amar Ujala printed Bundi's and Sirohi's. The officers' own sheets
were not found, so every figure here is press. Each row carries its article's
address in `source`. No list of individual electors was opened.

Coverage: 22 of 41 districts (27,77,424 of 41,84,891 names left off), 110 of
199 constituencies, 99 of them with a roll before, 64 with the five reasons.
Not found in either paper: Bikaner, Hanumangarh, Churu, Karauli, Dholpur, Sawai
Madhopur, Bhilwara, Jalore, Dungarpur, Pratapgarh, Baran, Jhalawar,
Kotputli-Behror, Khairthal-Tijara, Deeg, Beawar, Didwana-Kuchaman, Balotara and
Salumber.

What `build_rajasthan.py` asserts, and the printed disagreements it holds
fixed (`DIST_GAPS`, `SUM_GAPS`); a new one fails the build:

- every district row satisfies roll before less left off equals draft, except
  Kota, whose printed roll before and draft are each off from the sum of its
  constituencies (15,32,550 and 13,72,762, which agree with each other);
- the five reasons add to the names left off in every district that gave
  them, except Alwar (-20), Ajmer (+54) and Jaisalmer (+30);
- the constituency rows add to the printed district row in every column,
  except Alwar (several columns), Ajmer (shifted -54, other +60), Pali (absent
  -3,100, from Sumerpur), Jaisalmer (left off +30) and Kota (roll before +1,000,
  draft -10);
- Sirohi's roll before and draft by sex each add to the district's totals.

Rows kept as printed and flagged in `note`: Ganganagar (2), whose table swaps
the names left off and the draft (its text gives 32,293 left off); Surajgarh,
Jhunjhunu, Mandawa and Khetri, each off by a round thousand that cancels
across the district; Alwar Rural (duplicates printed 147, the row implies
2,147), Alwar Urban, Ramgarh and Rajgarh Laxmangarh; Ajmer North (reasons 60
over); Sumerpur (reasons 3,100 short); Kota South, whose printed roll before
repeats Kota North's and is replaced by its draft plus its names left off.
Jaipur's constituency draft is the roll before less the names left off; the
paper did not print it per constituency. Banswara's roll before is the draft
plus the names left off.

Two press versions of an exact state split of the reasons exist (ETV Bharat,
16 December 2025; Dainik Bhaskar, 22 December 2025). They disagree with each
other and with the CEO's rounded lakh figures, so they are not used.
