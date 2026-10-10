# Assembly results by constituency

One file per state, the latest general Assembly election, read by scripts/build_margins.py (ASM) for the Assembly spread on india/numbers/. Columns: ac, ac_name, reserved, electors, winner, winner_party, winner_votes, runner_up, runner_up_party, runner_up_votes, margin, total_votes, unopposed. The margin is winner less runner-up in every row, and NOTA is never a runner-up; the build asserts the first. Every file but two is the Election Commission's statistical report, tables 10 and 11, downloaded by the site's owner from the Commission's site; Manipur and Meghalaya are the Chief Electoral Officers' Form 20 sheets. Until 10 October 2026 most were published compilations, checked seat by seat against a second, because the Commission's pages could not be read from the sandbox. Electors are used only as weights, to spread a state's names left off over its seats; whether a source counts service voters is noted where it is known. Each section below is the collector's note, with every source and every disagreement between sources and which figure was kept.


---

# Andhra Pradesh 2024, Assembly results by AC

File: `andhrapradesh_2024.csv`, 175 rows. Every column is from the Election Commission's statistical report for this election, tables 10 (Detailed Results) and 11 (AC Wise Number Of Electors), downloaded in Excel from the Commission's site on 10 October 2026. Electors are table 11's All Electors (general electors, overseas electors included, plus service voters), and in every seat they equal table 10's total electors. winner and runner_up are the two candidates with the most votes, NOTA left out; margin is winner less runner-up; total_votes is every candidate plus NOTA. Party codes are the Commission's.

It replaces a compilation; every margin and every seat's electors agree with it.

---

# Arunachal Pradesh 2024, Assembly results by AC

File: `arunachal_2024.csv`, 60 rows. Every column is from the Election Commission's statistical report for this election, tables 10 (Detailed Results) and 11 (AC Wise Number Of Electors), downloaded in Excel from the Commission's site on 10 October 2026. Electors are table 11's All Electors (general electors, overseas electors included, plus service voters), and in every seat they equal table 10's total electors. winner and runner_up are the two candidates with the most votes, NOTA left out; margin is winner less runner-up; total_votes is every candidate plus NOTA. Party codes are the Commission's.

Ten seats were won unopposed (Mukto, Bomdila, Itanagar, Sagalee, Ziro-Hapoli, Tali, Taliha, Roing, Hayuliang, Chowkham). The report's tables cover only the 50 contested seats, so those ten rows, marked unopposed, keep the compilation's electors, which serve only as weights in the spread. In the 50 contested seats every margin and every elector count agrees with the compilation.

---

# Chhattisgarh 2023, Assembly results by AC

General election to the Chhattisgarh Legislative Assembly, 2023. 90 ACs. Bye-elections since 2023 are not reflected.

## Sources

Primary, the ECI statistical report (listed at https://www.eci.gov.in/chhattisgarh-legislative-election-2023-statistical-report), fetched with curl:

- 10 Detailed Results: https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/chhattisgarh/2023/Detailed_Results.xlsx
- 11 AC Wise Number Of Electors (PDF; the xlsx answered 406): https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/chhattisgarh/2023/AC_Wise_Number_Of_Electors.pdf
- 2 List of Successful Candidates: https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/chhattisgarh/2023/List_of_Successful_Candidates.xlsx

Second sources (compilations, used only to check):

- Wikipedia, "2023 Chhattisgarh Legislative Assembly election", "Results by constituency" (https://en.wikipedia.org/w/index.php?title=2023_Chhattisgarh_Legislative_Assembly_election&action=raw)
- IndiaVotes, https://www.indiavotes.com/vidhan-sabha/chhattisgarh/2023/

## Columns and where each came from

All from table 10, Detailed Results, built exactly as for Madhya Pradesh: ac and ac_name as ECI prints them with the (SC)/(ST) suffix moved into reserved; electors from TOTAL ELECTORS; winner and runner-up the top two non-NOTA candidates by TOTAL votes, ECI party abbreviations; margin their difference; total_votes all candidates and NOTA. unopposed is blank everywhere.

## Checks

- 90 rows against 90 seats, ACs 1 to 90 once each. Reserved: 10 SC, 29 ST.
- Electors sum to 2,04,12,807, equal to the Total row of table 11 (All Electors). Each AC's electors equal table 11's All Electors total, read from the PDF text; in every AC general + service = all electors.
- margin = winner_votes - runner_up_votes in all 90 rows. All positive; smallest 16, AC 81 Kanker. NOTA is never first or second.
- Candidates' general, postal and total votes sum to each AC's TURN OUT TOTAL row; general + postal = total for every candidate; one NOTA row per AC.
- total_votes sum to 1,56,34,933, equal to the GRAND TOTAL row of table 10.
- Winner and runner-up names, parties, votes and margin equal ECI's List of Successful Candidates in all 90 ACs.
- Winners: BJP 54, INC 35, GGP (Gondvana Gantantra Party) 1.

## Second-source comparison

IndiaVotes: all 90 matched; winner party, winner votes, runner-up votes and margin agree in all 90. Runner-up party agrees in 89; AC 24 Marwahi is ECI's "JCCJ" written "JCC(J)" by IndiaVotes, the same party.

Wikipedia: all 90 parsed; winner and runner-up party agree in all 90. Disagreements, ECI kept in each (IndiaVotes agrees with ECI):

- AC 13 Kunkuri: winner votes, ECI 87,604, Wikipedia 87,607; margin, ECI 25,541, Wikipedia 25,544.
- AC 84 Narayanpur: runner-up votes, ECI 49,922, Wikipedia 49,580.

Electors: checked table 10 against table 11 (both ECI). No independent non-ECI source was used, for the reason given in madhyapradesh_2023.md (IndiaVotes' "Voters" figure is not ECI's electors).

---

# Goa 2022, Assembly results by AC

File: `goa_2022.csv`, 40 rows. Every column is from the Election Commission's statistical report for this election, tables 10 (Detailed Results) and 11 (AC Wise Number Of Electors), downloaded in Excel from the Commission's site on 10 October 2026. Electors are table 11's All Electors (general electors, overseas electors included, plus service voters), and in every seat they equal table 10's total electors. winner and runner_up are the two candidates with the most votes, NOTA left out; margin is winner less runner-up; total_votes is every candidate plus NOTA. Party codes are the Commission's.

It replaces a compilation; every margin agrees, and the electors differ in 16 seats.

---

# Haryana 2024, Assembly results by AC

File: `haryana_2024.csv`, 90 rows. Every column is from the Election Commission's statistical report for this election, tables 10 (Detailed Results) and 11 (AC Wise Number Of Electors), downloaded in Excel from the Commission's site on 10 October 2026. Electors are table 11's All Electors (general electors, overseas electors included, plus service voters), and in every seat they equal table 10's total electors. winner and runner_up are the two candidates with the most votes, NOTA left out; margin is winner less runner-up; total_votes is every candidate plus NOTA. Party codes are the Commission's.

It replaces a compilation; every margin agrees, and the electors differ in 82 seats.

---

# Jharkhand 2024, Assembly results by AC

File: `jharkhand_2024.csv`, 81 rows. Every column is from the Election Commission's statistical report for this election, tables 10 (Detailed Results) and 11 (AC Wise Number Of Electors), downloaded in Excel from the Commission's site on 10 October 2026. Electors are table 11's All Electors (general electors, overseas electors included, plus service voters), and in every seat they equal table 10's total electors. winner and runner_up are the two candidates with the most votes, NOTA left out; margin is winner less runner-up; total_votes is every candidate plus NOTA. Party codes are the Commission's.

It replaces a compilation; the margins agree except in Chaibasa (52), 64,871 where the compilation had 64,835, and the electors differ in every seat.

---

# Karnataka 2023, Assembly results by AC

File: `karnataka_2023.csv`, 224 rows. Every column is from the Election Commission's statistical report for this election, two of its tables as downloaded from the Commission's site in Excel on 10 October 2026: 10, Detailed Results (every candidate and NOTA, with each seat's total electors), and 11, AC Wise Number Of Electors. Electors are the report's All Electors, general electors (overseas electors included) plus service voters; in every seat table 10's total electors equals table 11's. winner and runner_up are the two candidates with the most votes, NOTA left out; margin is winner less runner-up; total_votes is every candidate plus NOTA. Party codes are the Commission's. ac_name and reserved are from table 11, which marks (SC) and (ST) after the name. Written by a short script from the two tables, which asserts the winner's votes exceed the runner-up's in every seat.

This replaces a compilation (TCPD's, checked against IndiaVotes). Against it, the winner and the runner-up agree in all 224 seats and the margin in 219. The Commission's margin differs in five: Bijapur City 8,223 (the compilation had 8,233), Raichur 3,832 (3,732), Kadur 12,002 (12,007), Arkalgud 19,898 (19,605) and Hunsur 2,411 (2,412). The electors differ in every seat, because the compilation did not count service voters the same way; the state's All Electors are 5,31,31,579. On the spread, Chitradurga now falls over its margin (53,300 against 53,351 spread there, where the old weights gave 53,276), so Karnataka's count went from 207 to 208.

---

# Madhya Pradesh 2023, Assembly results by AC

General election to the Madhya Pradesh Legislative Assembly, 2023. 230 ACs. Bye-elections since 2023 are not reflected.

## Sources

Primary, the ECI statistical report ("MP Legislative Election 2023", listed at https://www.eci.gov.in/mp-legislative-election-2023-statistical-report), fetched with curl:

- 10 Detailed Results: https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/mp/2023/Detailed_Results.xlsx
- 11 AC Wise Number Of Electors: https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/mp/2023/AC_Wise_Number_Of_Electors.xlsx
- 2 List of Successful Candidates: https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/mp/2023/List_of_Successful_Candidates.xlsx

Second sources (compilations, used only to check):

- Wikipedia, "2023 Madhya Pradesh Legislative Assembly election", section "Results by constituency" (wikitext via https://en.wikipedia.org/w/index.php?title=2023_Madhya_Pradesh_Legislative_Assembly_election&action=raw)
- IndiaVotes, https://www.indiavotes.com/vidhan-sabha/madhya-pradesh/2023/ (table "Full results, all 230 seats")

## Columns and where each came from

All columns come from table 10, Detailed Results.

- ac, ac_name: AC NO. and AC NAME as ECI prints them, with the "(SC)"/"(ST)" suffix removed into reserved.
- reserved: the suffix on ECI's AC NAME.
- electors: TOTAL ELECTORS on the AC's rows (general including NRIs, plus service).
- winner, runner_up: the two highest non-NOTA candidates by TOTAL votes; ECI's ballot serial number prefixed to each name is removed. Parties are ECI abbreviations.
- winner_votes, runner_up_votes: TOTAL (general plus postal).
- margin: winner_votes less runner_up_votes.
- total_votes: sum of TOTAL over all candidates and NOTA.
- unopposed: blank in every row. No AC was uncontested.

## Checks

- 230 rows against 230 seats, ACs 1 to 230 once each. Reserved: 35 SC, 47 ST.
- Electors sum to 5,60,57,953, equal to the Total row of table 11 (All Electors, 5,60,57,953). Every AC's electors equal table 11's All Electors total, and every AC name agrees between tables 10 and 11.
- margin = winner_votes - runner_up_votes in all 230 rows. Every margin is positive; the smallest is 28, AC 167 Shajapur. NOTA is never first or second, and no runner-up is tied with the third candidate.
- In every AC the candidates' general, postal and total votes sum to the TURN OUT TOTAL row, and general + postal = total for every candidate. Exactly one NOTA row per AC.
- total_votes sum to 4,34,93,222, equal to the GRAND TOTAL row of table 10.
- Winner party, winner votes, runner-up party, runner-up votes, margin, and winner and runner-up names equal ECI's List of Successful Candidates in all 230 ACs.
- Winners: BJP 163, INC 66, BHRTADVSIP (Bharat Adivasi Party) 1.

## Second-source comparison

IndiaVotes: all 230 ACs matched; winner party, winner votes, runner-up party, runner-up votes and margin agree in all 230.

Wikipedia: all 230 parsed. It agrees on winner party in 230; it disagrees in these cases, and in each ECI's figure is kept (IndiaVotes agrees with ECI in every one):

- AC 18 Bhitarwar: winner votes, ECI 97,000, Wikipedia 97,700.
- AC 80 Singrauli: margin, ECI 37,977, Wikipedia 36,692 (Wikipedia's margin equals the runner-up's votes).
- AC 87 Anuppur: winner votes, ECI 77,110, Wikipedia 77,710; runner-up votes, ECI 56,691, Wikipedia 55,691.
- AC 126 Chhindwara: winner votes, ECI 1,32,302, Wikipedia 1,32,208.
- AC 137 Hoshangabad: runner-up party, ECI IND (Bhagvati Prasad Chourey), Wikipedia INC.

Electors: no source independent of ECI was found that holds them reliably. IndiaVotes' AC pages give a "Voters" figure that is about double ECI's (Sheopur 5,17,954 against 2,58,978), so it was not used. The electors check is therefore table 10 against table 11, both ECI.

---

# Maharashtra 2024, Assembly results by AC

File: `maharashtra_2024.csv`, 288 rows. Every column is from the Election Commission's statistical report for this election, tables 10 (Detailed Results) and 11 (AC Wise Number Of Electors), downloaded in Excel from the Commission's site on 10 October 2026. Electors are table 11's All Electors (general electors, overseas electors included, plus service voters), and in every seat they equal table 10's total electors. winner and runner_up are the two candidates with the most votes, NOTA left out; margin is winner less runner-up; total_votes is every candidate plus NOTA. Party codes are the Commission's.

It replaces a compilation; every margin and every seat's electors agree with it.

---

# Odisha 2024, Assembly results by AC

File: `odisha_2024.csv`, 147 rows. Every column is from the Election Commission's statistical report for this election, tables 10 (Detailed Results) and 11 (AC Wise Number Of Electors), downloaded in Excel from the Commission's site on 10 October 2026. Electors are table 11's All Electors (general electors, overseas electors included, plus service voters), and in every seat they equal table 10's total electors. winner and runner_up are the two candidates with the most votes, NOTA left out; margin is winner less runner-up; total_votes is every candidate plus NOTA. Party codes are the Commission's.

It replaces a compilation; every margin and every seat's electors agree with it.

---

# Puducherry 2026, Assembly results by AC

File: `puducherry_2026.csv`, 30 rows. Every column is from the Election Commission's statistical report for this election, two of its tables as downloaded from the Commission's site in Excel on 10 October 2026: 10, Detailed Results (every candidate and NOTA, with each seat's total electors), and 11, AC Wise Number Of Electors. Electors are the report's All Electors, general electors (overseas electors included) plus service voters; in every seat table 10's total electors equals table 11's. winner and runner_up are the two candidates with the most votes, NOTA left out; margin is winner less runner-up; total_votes is every candidate plus NOTA. Party codes are the Commission's. ac_name and reserved are from table 11, which marks (SC) and (ST) after the name. Written by a short script from the two tables, which asserts the winner's votes exceed the runner-up's in every seat.

This replaces a file read partly from the Commission's archived counting pages and partly from IndiaVotes and Wikipedia, with IndiaVotes' voters as electors. Every winner, runner-up and margin agrees with that file in all 30 seats. The electors are now the Commission's: 9,50,639 in all, against IndiaVotes' 9,50,311, and they differ in 29 seats. AC 9 Thattanchavady carries the general election result; the bye-election held there on 6 October 2026 is not reflected.

---

# Punjab 2022, Assembly results by AC

File: `punjab_2022.csv`, 117 rows. Every column is from the Election Commission's statistical report for this election, tables 10 (Detailed Results) and 11 (AC Wise Number Of Electors), downloaded in Excel from the Commission's site on 10 October 2026. Electors are table 11's All Electors (general electors, overseas electors included, plus service voters), and in every seat they equal table 10's total electors. winner and runner_up are the two candidates with the most votes, NOTA left out; margin is winner less runner-up; total_votes is every candidate plus NOTA. Party codes are the Commission's.

It replaces a compilation; every margin agrees, and the electors differ in 113 seats.

---

# Sikkim 2024, Assembly results by AC

File: `sikkim_2024.csv`, 32 rows. Every column is from the Election Commission's statistical report for this election, tables 10 (Detailed Results) and 11 (AC Wise Number Of Electors), downloaded in Excel from the Commission's site on 10 October 2026. Electors are table 11's All Electors (general electors, overseas electors included, plus service voters), and in every seat they equal table 10's total electors. winner and runner_up are the two candidates with the most votes, NOTA left out; margin is winner less runner-up; total_votes is every candidate plus NOTA. Party codes are the Commission's.

Seats reserved for the Bhutia-Lepcha are marked BL, as table 11 marks them; Sangha (32) is the monastic seat. It replaces a compilation; every margin and every seat's electors agree with it.

---

# Telangana 2023, Assembly results by AC

General election to the Telangana Legislative Assembly, 2023. 119 ACs. Bye-elections since 2023 are not reflected.

## Sources

Primary, the ECI statistical report (listed at https://www.eci.gov.in/telangana-legislative-election-2023-statistical-report), fetched with curl:

- 10 Detailed Results, PDF: https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/telangana/2023/Detailed_Results.pdf (the .xlsx at the same path answered 406 on every try)
- 11 AC Wise Number Of Electors: https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/telangana/2023/AC_Wise_Number_Of_Electors.xlsx
- 2 List of Successful Candidates: https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/telangana/2023/List_of_Successful_Candidates.xlsx

The spreadsheet of table 10 was read from OpenCity's copy, "Detailed Results for Telangana Assembly Constituencies in 2023", https://data.opencity.in/dataset/62ad1510-22c4-4f9f-a22c-aa5391ec89b6/resource/3632e39e-63c6-4d2f-b240-5decb915f4d0/download/detailed_results.xlsx (ECI's own layout, header "10 - Detailed Results"). It was then held to ECI's PDF, below.

Second sources (compilations, used only to check):

- Wikipedia, "2023 Telangana Legislative Assembly election", "Results by constituency" (https://en.wikipedia.org/w/index.php?title=2023_Telangana_Legislative_Assembly_election&action=raw)
- IndiaVotes, https://www.indiavotes.com/vidhan-sabha/telangana/2023/

## Columns and where each came from

All from table 10, built as for Madhya Pradesh: ac and ac_name as ECI prints them with the (SC)/(ST) suffix moved into reserved; electors from TOTAL ELECTORS; winner and runner-up the top two non-NOTA candidates by TOTAL votes, ECI party abbreviations (BHRS is Bharat Rashtra Samithi); margin their difference; total_votes all candidates and NOTA. unopposed is blank everywhere.

## Checks

- The OpenCity spreadsheet equals ECI's PDF: for all 119 ACs the PDF's TOTAL ELECTORS and TURN OUT TOTAL (general, postal, total) equal the spreadsheet's, and every candidate's general, postal and total triple in the spreadsheet appears in that AC's block of the PDF.
- 119 rows against 119 seats, ACs 1 to 119 once each. Reserved: 19 SC, 12 ST.
- Electors sum to 3,26,18,257, equal to the Total row of table 11 (All Electors). Every AC's electors equal table 11's, and every AC name agrees.
- margin = winner_votes - runner_up_votes in all 119 rows. All positive; smallest 268, AC 53 Chevella. NOTA is never first or second.
- Candidates' votes sum to each AC's TURN OUT TOTAL row; general + postal = total for every candidate; one NOTA row per AC.
- total_votes sum to 2,34,39,945, equal to the PDF's GRAND TOTAL (2,32,39,434 general, 2,00,511 postal, 2,34,39,945 total).
- Winner and runner-up names, parties, votes and margin equal ECI's List of Successful Candidates in all 119 ACs.
- Winners: INC 64, BHRS 39, BJP 8, AIMIM 7, CPI 1.

## Second-source comparison

Winner party agrees with Wikipedia in all 119. IndiaVotes writes AIMIM as "PARTY-UNKNOWN-1920" in the seven AIMIM seats (58, 63, 64, 66, 67, 68, 69) and AIFB as "FBL" in AC 117 Kothagudem; those are labels, not disagreements.

Vote disagreements. ECI's figures are kept throughout; the statistical report (Detailed Results PDF and List of Successful Candidates) is the Commission's final figure, and the differing figures look like counting-day numbers:

- AC 5 Asifabad: winner votes ECI 83,052, Wikipedia and IndiaVotes 83,036; runner-up ECI 60,242, both others 60,238; margin ECI 22,810, others 22,798.
- AC 47 Uppal: winner ECI 1,32,929, others 1,32,927; runner-up ECI 83,900, others 83,897; margin ECI 49,029, others 49,030.
- AC 54 Pargi: winner ECI 98,570, others 98,536; runner-up ECI 74,537, others 74,523; margin ECI 24,033, others 24,013.
- AC 10 Mudhole: runner-up votes ECI 74,253, Wikipedia 74,254 (IndiaVotes agrees with ECI).
- AC 46 Kukatpalle: winner votes ECI 1,35,635, Wikipedia 1,35,636 (IndiaVotes agrees with ECI).
- AC 74 Mahbubnagar: runner-up votes ECI 68,489, Wikipedia 64,489 (IndiaVotes agrees with ECI).

None of these changes a winner. The three ACs where both compilations differ (5, 47, 54) were reread in ECI's PDF and the ECI figures stand there.

Electors: checked table 10 against table 11 (both ECI); no independent non-ECI electors source was used (see madhyapradesh_2023.md).

---

# Uttarakhand 2022, Assembly results by AC

File: `uttarakhand_2022.csv`, 70 rows. Every column is from the Election Commission's statistical report for this election, tables 10 (Detailed Results) and 11 (AC Wise Number Of Electors), downloaded in Excel from the Commission's site on 10 October 2026. Electors are table 11's All Electors (general electors, overseas electors included, plus service voters), and in every seat they equal table 10's total electors. winner and runner_up are the two candidates with the most votes, NOTA left out; margin is winner less runner-up; total_votes is every candidate plus NOTA. Party codes are the Commission's.

It replaces a compilation; every margin and every seat's electors agree with it.

---

# Mizoram 2023, results by assembly constituency

General election to the Mizoram Legislative Assembly, poll 7 November 2023,
counted 4 December 2023. 40 ACs, none returned unopposed, none adjourned.

## Sources

1. Primary, every column: ECI statistical report, "10 - Detailed Results",
   Mizoram 2023 (mPDF, 9 pages, dated 2024-01-10 in its metadata),
   https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/mizoram/2023/Detailed_Results.pdf
   (fetched with curl, and once through WebFetch while curl was refused).
   - ac, ac_name, reserved: the "Constituency N - Name (ST)" header of each AC.
     The "(ST)" suffix is moved to `reserved`.
   - electors: the same header's "TOTAL ELECTORS" (general plus service, as printed).
   - winner, runner_up, their parties and votes: the two highest non-NOTA
     candidates by the TOTAL column (general plus postal). Party is the
     Commission's abbreviation (MNF, ZPM, INC, BJP).
   - total_votes: the AC's "TURN OUT TOTAL:" row, total column (all candidates
     and NOTA, postal included).
   - margin: computed, winner_votes less runner_up_votes.
2. Second source for electors: ECI, Electoral Statistical Pocket Book 2023,
   table 10.8.F2 "AC-wise Voters' Turnout Rate (%) GE to State Legislative
   Assembly of Mizoram-2023" and highlights table 10.8.F1,
   https://www.eci.gov.in/eci-backend/public/api/download?url=LMAhAK6sOPBp%2FNFF0iRfXbEB1EVSLT41NNLRjYNJJP1KivrUxbfqkDatmHy12e%2FzGjJMI0%2FjETs7fjrM8lYn4q0vCivj94MhpU3oJn7R5vrT16TiGkIgrvGfcMND0TasK6qlsuh5iZIkAbkwBAifqg%3D%3D
   (pages 148 to 150 of the book). Same publisher, different table and publication.
3. Second source for margin, winner party and votes: Wikipedia, "2023 Mizoram
   Legislative Assembly election", section "Results by constituency",
   https://en.wikipedia.org/w/index.php?title=2023_Mizoram_Legislative_Assembly_election&action=raw
   (read 2026-10-10). Its infobox also gives the registered voters, 857,063.
4. Looked at and not used: IndiaVotes, https://www.indiavotes.com/vidhan-sabha/mizoram/2023/ .
   Its electors are exactly double the Commission's (Hachhek 42,320 against
   21,160) and its state turnout reads 40.8%, so it is not a usable check.

## Checks

- ACs: 40 rows, ACs 1 to 40 once each, against 40 seats. Reserved: 39 ST,
  1 general (13 Aizawl East-I), as the pocket book's highlights give (GEN 1, ST 39).
- In every AC the candidates' general, postal and total votes sum to the
  printed TURN OUT TOTAL row, and general + postal = total for every candidate.
- The TURN OUT rows sum to the printed GRAND TOTAL: 6,85,763 general,
  16,883 postal, 7,02,646 total.
- Electors: sum 8,57,063, equal to the Commission's state total in the pocket
  book (8,57,063, including service electors) and to Wikipedia's infobox.
  AC by AC, all 40 equal the pocket book's table 10.8.F2.
- margin = winner_votes - runner_up_votes in all 40 rows; every margin is
  positive (smallest 13, in 4 Tuirial).
- Winners: ZPM 27, MNF 10, BJP 2, INC 1, the declared result.

## Disagreements between the sources

Against Wikipedia, winner party and runner-up party agree in all 40 ACs.
Votes and margin agree in 39 ACs. One differs:

| AC | field | Commission | Wikipedia | kept |
|---|---|---|---|---|
| 16 Aizawl West-II | winner_votes | 10,770 | 10,398 | Commission |
| 16 Aizawl West-II | runner_up_votes | 5,917 | 5,579 | Commission |
| 16 Aizawl West-II | margin | 4,853 | 4,819 | Commission |

The Commission's figures add up inside the AC (candidates sum to the printed
total), so they are kept.

No disagreement on electors (pocket book, all 40 equal).


---

# Uttar Pradesh 2022, results by assembly constituency

General election to the Uttar Pradesh Legislative Assembly, seven phases,
10 February to 7 March 2022, counted 10 March 2022. 403 ACs, none unopposed.

## Sources

1. Primary, every number: ECI statistical report "Uttar Pradesh General
   Legislative Election 2022", table "10-Detailed Results" (PDF, 146 pages),
   listed by https://www.eci.gov.in/eci-backend/public/api/old-site-statistical-report-data?docid=14185
   and fetched with curl from
   https://www.eci.gov.in/eci-backend/public/api/download?url=LMAhAK6sOPBp%2FNFF0iRfXbEB1EVSLT41NNLRjYNJJP1KivrUxbfqkDatmHy12e%2FzVx8fLfn2ReU7TfrqYobgItW4eTUyTFD%2BDUyB1G1fBKOuW00SdZqELiEOB05oPhRO74%2F4p%2BuSikD0u7%2BVrCmQyhaJANaxWi%2FXMLUEuMmRVRLJ2%2BdBIBswoUnKE3KB7EMq
   - ac, ac_name: the "Constituency N . Name" header (ECI spelling).
   - electors: the same header's TOTAL ELECTORS.
   - winner, runner_up, parties, votes: the two highest non-NOTA candidates by
     the TOTAL column (general plus postal). Party is the Commission's
     abbreviation: ADAL is Apna Dal (Soneylal), NINSHAD is NISHAD party, JDL is
     Jansatta Dal Loktantrik, APNDLK is Apna Dal (Kamerawadi).
   - total_votes: the AC's TURN OUT TOTAL row (all candidates and NOTA, postal
     included; rejected postal ballots are not in it).
   - margin: computed, winner_votes less runner_up_votes.
   - reserved: **not printed in this table.** It is derived from the same
     table's candidate CATEGORY column: an AC is SC (or ST) when every
     non-NOTA candidate is SC (or ST). That gives 84 SC and 2 ST (Obra 402,
     Duddhi 403), the numbers the Delimitation Order fixes for Uttar Pradesh,
     and every other AC has at least one GENERAL candidate. The Commission's
     own AC-wise table that prints "(SC)", "11-AC Wise Number Of Electors",
     could not be downloaded (see below).
2. Second source, margin, winner party and votes: IndiaVotes, "Uttar Pradesh
   2022", https://www.indiavotes.com/vidhan-sabha/uttar-pradesh/2022/
   (table "Full results, all 403 seats"), matched by AC name and, where the
   names differ, by the pair of vote counts. All 403 matched.
3. The existing file data/uttarpradesh/raw/results_2022.csv in INDIA-DATA,
   compared AC by AC below. It is the Wikipedia table "Results by constituency"
   of https://en.wikipedia.org/wiki/2022_Uttar_Pradesh_Legislative_Assembly_election
   reproduced exactly (re-read 2026-10-10: every winner party, both vote
   counts and the printed margin agree with that table in all 403 ACs), so
   it is not counted as an independent check.

Not obtained, and why: the same report's tables 11 (AC Wise Number Of
Electors), 2 (List of Successful Candidates) and 4 (Highlight) are listed by
the docid=14185 page, but every download of them was refused by the site's
firewall (HTTP 406) on 2026-10-10, while table 10 downloaded repeatedly.
ceouttarpradesh.nic.in did not answer.

## Checks

- ACs: 403 rows, ACs 1 to 403 once each, against 403 seats.
- In every AC the candidates' general, postal and total votes sum to the
  printed TURN OUT TOTAL, and general + postal = total for every candidate.
- The 403 TURN OUT rows sum to the printed GRAND TOTAL: 9,17,20,555 general,
  4,42,342 postal, 9,21,62,897 total.
- Electors: sum 15,12,46,168. The Commission's state total from table 6 or 11
  could not be read; Wikipedia's infobox gives 151,246,168, the same.
  No AC-by-AC second source for electors was read (IndiaVotes AC pages give a
  "Voters" figure that is double the Commission's in Mizoram, so it was not
  used for electors anywhere).
- margin = winner_votes - runner_up_votes in all 403 rows, all positive
  (smallest 203, 20 Dhampur).
- Winners: BJP 255, SP 111, ADAL 12, RLD 8, SBSP 6, NINSHAD 6, INC 2, JDL 2,
  BSP 1, the declared result.

## Disagreements with the second source (IndiaVotes)

Votes and margins agree in all 403 ACs. The only differences are party
labels: IndiaVotes writes ADS for ADAL (17 places), PARTY-UNKNOWN-1990 for
NINSHAD (10), JANSATTADALL for JDL (2) and APNADALKAMER for APNDLK (3). The
Commission's abbreviations are kept.

## Every difference from the existing results_2022.csv

The full list, 389 field-level differences, is also in
uttarpradesh_2022_vs_existing.csv beside this file. In every case the
Commission's figure is kept: its candidates add up to its printed AC totals,
and IndiaVotes agrees with it.

### Votes and margins (25 ACs)

`margin` is the existing file's computed margin column, `margin_printed` its
printed one.

| AC | field | Commission | existing file |
|---|---|---|---|
| 26 Thakurdwara | runner_up_votes | 114707 | 114706 |
| 26 Thakurdwara | margin | 19684 | 19685 |
| 27 Moradabad Rural | winner_votes | 143337 | 114337 |
| 27 Moradabad Rural | margin | 56820 | 27820 |
| 27 Moradabad Rural | margin_printed | 56820 | 27820 |
| 54 Muradnagar | margin_printed | 97095 | 97295 |
| 65 Bulandshahr | winner_votes | 127076 | 127026 |
| 65 Bulandshahr | runner_up_votes | 101246 | 101426 |
| 65 Bulandshahr | margin | 25830 | 25600 |
| 65 Bulandshahr | margin_printed | 25830 | 25600 |
| 74 Chharra | winner_votes | 111293 | 110928 |
| 74 Chharra | margin | 24327 | 23962 |
| 102 Patiyali | winner_votes | 91958 | 91545 |
| 102 Patiyali | margin | 4001 | 3588 |
| 119 Meerganj | margin_printed | 32480 | 32840 |
| 150 Sevata | runner_up_votes | 87776 | 87619 |
| 150 Sevata | margin | 20281 | 20438 |
| 150 Sevata | margin_printed | 20281 | 20438 |
| 154 Sawayazpur | winner_votes | 114263 | 114623 |
| 154 Sawayazpur | margin | 25687 | 26047 |
| 154 Sawayazpur | margin_printed | 25687 | 26047 |
| 160 Balamau | runner_up_votes | 55750 | 55570 |
| 160 Balamau | margin | 26244 | 26424 |
| 160 Balamau | margin_printed | 26244 | 26424 |
| 181 Salon | margin_printed | 2111 | 1511 |
| 194 Farrukhabad | runner_up_votes | 72998 | 72988 |
| 194 Farrukhabad | margin | 39316 | 39326 |
| 194 Farrukhabad | margin_printed | 39316 | 39326 |
| 195 Bhojpur | margin_printed | 27458 | 27468 |
| 202 Bidhuna | winner_votes | 97257 | 92757 |
| 202 Bidhuna | margin | 7765 | 3265 |
| 202 Bidhuna | margin_printed | 7765 | 3265 |
| 264 Bara | margin_printed | 12524 | 12464 |
| 270 Dariyabad | winner_votes | 128219 | 127983 |
| 270 Dariyabad | runner_up_votes | 95817 | 95366 |
| 270 Dariyabad | margin | 32402 | 32617 |
| 270 Dariyabad | margin_printed | 32402 | 32617 |
| 281 Akbarpur | winner_votes | 81931 | 81391 |
| 281 Akbarpur | margin | 12336 | 11796 |
| 288 Kaiserganj | winner_votes | 103135 | 103195 |
| 288 Kaiserganj | margin | 7711 | 7771 |
| 288 Kaiserganj | margin_printed | 7711 | 7771 |
| 291 Tulsipur | winner_votes | 87032 | 87092 |
| 291 Tulsipur | margin | 35781 | 35841 |
| 291 Tulsipur | margin_printed | 35781 | 35841 |
| 295 Mehnaun | winner_votes | 107327 | 107237 |
| 295 Mehnaun | margin | 23218 | 23128 |
| 295 Mehnaun | margin_printed | 23218 | 23128 |
| 296 Gonda | runner_up_votes | 89829 | 89828 |
| 296 Gonda | margin | 6699 | 6700 |
| 296 Gonda | margin_printed | 6699 | 6700 |
| 299 Tarabganj | runner_up_votes | 71635 | 71365 |
| 299 Tarabganj | margin | 53690 | 53960 |
| 313 Khalilabad | margin_printed | 12622 | 12262 |
| 316 Nautanwa | runner_up_votes | 74932 | 74392 |
| 316 Nautanwa | margin | 15331 | 15871 |
| 316 Nautanwa | margin_printed | 15331 | 15691 |
| 327 Bansgaon | margin_printed | 32309 | 32209 |

### Vote shares (18 ACs)

The existing file's own check (data/uttarpradesh/raw/check.py) reports that
votes and shares disagree in 32 ACs: 27, 34, 40, 43, 65, 74, 102, 134, 150,
151, 154, 160, 186, 202, 212, 245, 270, 274, 281, 284, 288, 291, 293, 295,
299, 302, 307, 316, 318, 325, 332, 377. Every one is explained by the
Commission's table. In 15 of them a vote count in the file is wrong (the
table above: 27, 65, 74, 102, 150, 154, 160, 202, 270, 281, 288, 291, 295,
299, 316). In the other 17 the votes are right and a share is wrong:

| AC | field | Commission | existing file |
|---|---|---|---|
| 34 Suar | runner_up_pct | 30.52 | 30.62 |
| 40 Naugawan Sadat | winner_pct | 44.31 | 44.38 |
| 43 Siwalkhas | winner_pct | 43.54 | 43.52 |
| 134 Powayan | runner_up_pct | 33.52 | 33.62 |
| 150 Sevata | winner_pct | 48.43 | 47.43 |
| 151 Mahmoodabad | winner_pct | 41.89 | 41.91 |
| 186 Amethi | runner_up_pct | 36.93 | 39.93 |
| 212 Govindnagar | winner_pct | 61.13 | 61.03 |
| 245 Babaganj | runner_up_pct | 30.88 | 30.80 |
| 274 Bikapur | winner_pct | 44.34 | 44.24 |
| 284 Matera | winner_pct | 48.15 | 48.13 |
| 293 Utraula | runner_up_pct | 33.33 | 33.93 |
| 302 Shohratgarh | runner_up_pct | 24.56 | 22.56 |
| 307 Harraiya | winner_pct | 39.85 | 39.75 |
| 318 Maharajganj | winner_pct | 51.8 | 51.08 |
| 325 Khajani | winner_pct | 45.37 | 45.31 |
| 332 Fazilnagar | runner_up_pct | 31.59 | 31.15 |
| 377 Zahoorabad | runner_up_pct | 28 | 21.49 |

(150 Sevata appears in both lists.) The 13 ACs where check.py finds the printed
margin differing from winner minus runner-up (26, 54, 74, 102, 119, 181, 195,
264, 281, 299, 313, 316, 327) are the `margin_printed` rows above; in 54,
119, 181, 195, 264, 313 and 327 the printed margin alone is wrong.

### Party labels (32 places)

Same parties, different abbreviations: the existing file writes AD(S), NISHAD,
JD(L) and AD(K) where the Commission writes ADAL, NINSHAD, JDL and APNDLK.

| AC | field | Commission | existing file |
|---|---|---|---|
| 34 Suar | runner_up_party | ADAL | AD(S) |
| 177 Bachhrawan | runner_up_party | ADAL | AD(S) |
| 192 Kaimganj | winner_party | ADAL | AD(S) |
| 218 Ghatampur | winner_party | ADAL | AD(S) |
| 220 Kalpi | runner_up_party | NINSHAD | NISHAD |
| 224 Mauranipur | winner_party | ADAL | AD(S) |
| 237 Manikpur | winner_party | ADAL | AD(S) |
| 239 Bindki | winner_party | ADAL | AD(S) |
| 245 Babaganj | winner_party | JDL | JD(L) |
| 246 Kunda | winner_party | JDL | JD(L) |
| 247 Vishwanath Ganj | winner_party | ADAL | AD(S) |
| 248 Pratapgarh | runner_up_party | APNDLK | AD(K) |
| 253 Chail | runner_up_party | ADAL | AD(S) |
| 255 Soraon | runner_up_party | ADAL | AD(S) |
| 257 Pratappur | runner_up_party | ADAL | AD(S) |
| 258 Handia | runner_up_party | NINSHAD | NISHAD |
| 264 Bara | winner_party | ADAL | AD(S) |
| 277 Katehari | runner_up_party | NINSHAD | NISHAD |
| 283 Nanpara | winner_party | ADAL | AD(S) |
| 302 Shohratgarh | winner_party | ADAL | AD(S) |
| 312 Menhdawal | winner_party | NINSHAD | NISHAD |
| 316 Nautanwa | winner_party | NINSHAD | NISHAD |
| 329 Khadda | winner_party | NINSHAD | NISHAD |
| 343 Atrauliya | runner_up_party | NINSHAD | NISHAD |
| 365 Shahganj | winner_party | NINSHAD | NISHAD |
| 370 Mariyahu | winner_party | ADAL | AD(S) |
| 387 Rohaniya | winner_party | ADAL | AD(S) |
| 387 Rohaniya | runner_up_party | APNDLK | AD(K) |
| 393 Gyanpur | winner_party | NINSHAD | NISHAD |
| 395 Chhanbey | winner_party | ADAL | AD(S) |
| 397 Majhawan | winner_party | NINSHAD | NISHAD |
| 398 Chunar | runner_up_party | APNDLK | AD(K) |

### Reservation and AC names

The existing file has 82 SC seats; it misses 106 Jalesar and 192 Kaimganj,
where every candidate is SC.

| AC | field | Commission | existing file |
|---|---|---|---|
| 87 | ac_name | Agra Cantt. | Agra Cantonment |
| 106 | reserved | SC |  |
| 162 | ac_name | Bangermau | Bangarmau |
| 175 | ac_name | Lucknow Cantt. | Lucknow Cantonment |
| 192 | reserved | SC |  |
| 216 | ac_name | Kanpur Cantt. | Kanpur Cantonment |
| 219 | ac_name | Madhaugarh | Madhogarh |
| 319 | ac_name | Paniyra | Paniyara |
| 375 | ac_name | Ghazipur | Ghazipur Sadar |

### Candidate names (290 differences)

Spelling, capitalisation, titles and initials differ; no difference names a
different person in a way the votes do not also match. Listed in full:

| AC | field | Commission | existing file |
|---|---|---|---|
| 2 | runner_up | DR. DHARAM SINGH SAINI | Dharam Singh Saini |
| 3 | winner | RAJEEV GUMBER | Rajiv Gumber |
| 5 | winner | BRIJESH | Th. Brijesh Singh |
| 5 | runner_up | Kartikey Rana | Kartikeya Rana |
| 6 | winner | Devender Kumar Nim | Devendra Kumar Nim |
| 6 | runner_up | RAVINDRA KUMAR | Ravinder Kumar Molhu |
| 9 | runner_up | Suresh Kumar | Suresh Rana |
| 10 | winner | Persann Kumar | Persann Kumar Chaudhary |
| 10 | runner_up | Tejendra Singh | Tejendra Nirwal |
| 14 | winner | Kapil Dev Agarwal | Kapil Dev Aggarwal |
| 14 | runner_up | SAURABH | Saurabh Swaroop |
| 15 | winner | VIKRAM SINGH | Vikram Singh Saini |
| 17 | runner_up | RAJA BHARATENDRA SINGH | Kunwar Bharatendu Singh |
| 18 | runner_up | DR YASHWANT SINGH | Dr. Yashwant |
| 20 | runner_up | NAIM UL HASAN | Naeemul Hasan |
| 22 | winner | Suchi | Suchi Chaudhary |
| 25 | runner_up | Rajesh Kumar Singh Urf Chunnu | Rajesh Kumar Singh |
| 26 | winner | NAVAB JAN | Nawab Jan |
| 27 | winner | MOHD NASIR | Mohd Nasir Qureshi |
| 27 | runner_up | K K MISRA | Krishnakant Mishra |
| 29 | winner | ZIA UR REHMAN | Zia ur Rahman Barq |
| 29 | runner_up | KAMAL KUMAR | Kamal Prajapati |
| 30 | winner | MOHAMMAD FAHEEM IRFAN | Mohammed Faeem |
| 30 | runner_up | PARMESHWAR LAL | Parmeshwar Lal Saini |
| 31 | winner | GULAB DEBI | Gulabo Devi |
| 31 | runner_up | KM VIMLESH KUMARI | Vimlesh Kumar |
| 32 | winner | PINKI SINGH | Pinki Singh Yadav |
| 34 | winner | Mohammad Abdullah Azam Khan | Abdullah Azam Khan |
| 34 | runner_up | Haidar Ali Khan Alias Hamza Mian | Haidar Ali Khan |
| 36 | runner_up | Amarjeet Singh | Amarjit Singh |
| 37 | winner | Mohammad Azam Khan | Azam Khan |
| 37 | runner_up | Akash Saxena (Honey) | Akash Saxena |
| 38 | winner | Rajbala Singh | Rajbala |
| 39 | winner | RAJEEV KUMAR | Rajeev Tarara |
| 42 | winner | MAHENDRA | Mahender Khadakvanshi |
| 43 | winner | GHULAM MOHAMMAD | Ghulam Mohammed |
| 44 | runner_up | Sangeet Singh Som | Sangeet Som |
| 45 | winner | Dinesh | Dinesh Khatik |
| 47 | winner | AMIT AGARWAL | Amit Agrawal |
| 49 | winner | Dr. Somendra Singh Tomar | Somendra Tomar |
| 49 | runner_up | Mohd Adil | Md Adil |
| 50 | runner_up | Sahender Singh Ramala | Sahender Singh |
| 51 | winner | KRISHAN PAL MALIK | Krishnapal Malik |
| 51 | runner_up | JAIVEER | Ch. Jaiveer Singh Tomar |
| 52 | winner | Yogesh Dhama | Chaudhary Yogesh Dhama |
| 53 | winner | NANDKISHOR | Nand Kishor Gurjar |
| 54 | runner_up | Surendra Kumar Munni | Surendra Kumar |
| 57 | winner | DR. MANJU SHIWACH | Manju Shiwach |
| 59 | winner | VIJAYPAL (AADHTI) | Vijay Pal Aadthi |
| 60 | winner | HARENDRA SINGH | Harendra Singh Tewatia |
| 60 | runner_up | RAVINDER CHAUDHARY | Ravindra Chaudhary |
| 64 | winner | Lakshmi Raj | Lakshmi Raj Singh |
| 65 | runner_up | Mohammad Yunus | Haji Yunus |
| 66 | runner_up | Dilnawaz Khan | Dilnawaj Khan |
| 67 | runner_up | Rameshvar | Rameshwar Lodhi |
| 68 | runner_up | HARISH LODHI | Harish Kumar |
| 69 | winner | Anil Kumar | Anil Sharma |
| 70 | winner | Minakshi Singh | Meenakshi Singh |
| 71 | winner | ANOOP SINGH URF ANOOP PRADHAN VALMEEKI | Anoop Pradhan |
| 71 | runner_up | CHARU KAIN KAIN | Charu Kain |
| 72 | winner | Thakur Jaiveer Singh | Thakur Jaivir Singh |
| 75 | runner_up | SHAZ ISHAQ | Shaaz Ishaaq |
| 77 | runner_up | BIRPAL SINGH | Birpal Diwakar |
| 80 | runner_up | DR. Lalit Pratap Baghel | Lalit Pratap Baghel |
| 81 | winner | LAXMI NARAYAN | Ch. Laxmi Narayan Singh |
| 83 | winner | MEGHSHYAM | Karinda Singh |
| 85 | winner | PURAN PRAKASH | Pooran Prakash |
| 86 | winner | DR. DHARMPAL SINGH | Dharampal Singh |
| 87 | winner | Dr. G S Dharmesh | G S Dharmesh |
| 89 | winner | PURSHOTTAM KHANDELWAL | Purushottam Khandelwal |
| 91 | winner | Babulal | Babulal Chaudhary |
| 92 | runner_up | Ramnath Singh Sikarwar | Ramnath Shikarwar |
| 93 | winner | Chhotey Lal Verma | Chotelal Verma |
| 93 | runner_up | Roopali Dixit | Rupali Dixit |
| 96 | runner_up | MANVENDRA PRATAP SINGH | Manvendra Lodhi |
| 97 | winner | MANISH ASIJA | Manish Asiza |
| 97 | runner_up | SAIFURRAHAMAN URF CHHUTTAN BHAI | Saifur Rehman |
| 99 | winner | SARVESH SINGH | Sarvesh Singh Yadav |
| 101 | winner | HARIOM | Hariom Verma |
| 101 | runner_up | SATYABHAN | Satybhan Shakya |
| 102 | winner | Nadira Sultan alias Bitiya | Nadira Sultan |
| 106 | winner | SANJEEV KUMAR | Sanjeev Kumar Diwakar |
| 107 | winner | JAYVEER SINGH | Jaiveer Singh |
| 107 | runner_up | RAJKUMAR URF RAJU YADAV | Raj Kumar |
| 108 | runner_up | Alok Kumar Shakya | Alok Shakya |
| 109 | winner | ENG. BRAJESH KATHERIYA | Brajesh Katheriya |
| 109 | runner_up | DR. PRIYA RANJAN ASHU DIWAKAR | Priya Ranjan Ashu Diwakar |
| 110 | runner_up | Prof. S.P. Singh Baghel | S.P. Singh Baghel |
| 111 | winner | Ramkhiladi Singh | Ramkhiladi Singh Yadav |
| 111 | runner_up | AJEET KUMAR URF RAJU YADAV | Ajeet Kumar Yadav |
| 112 | winner | ASHUTOSH MAURYA URF RAJU | Ashutosh Maurya |
| 113 | runner_up | MUSARRAT ALI | Haji Vittan Musarrat |
| 114 | winner | HARISH CHANDRA | Harish Chandra Shakya |
| 115 | runner_up | Rais Ahmad | Raish Ahmed |
| 116 | runner_up | DHARMENDRA KUMAR SINGH SHAKYA | Dharmendra Shakya |
| 117 | winner | RAJEEV SINGH URF BABBU BHAIYA | Rajeev Kumar Singh |
| 118 | runner_up | CHHATRA PAL SINGH | Chhatrapal Singh Gangwar |
| 119 | winner | DR. D. C. VERMA | DC Verma |
| 119 | runner_up | SULTAN BEG | Sultan Baig |
| 121 | winner | Dr. M. P. Arya | Dr. M. P. Arya Gangwar |
| 122 | winner | PROF. SHYAM BIHARI LAL | Shyam Bihari Lal |
| 123 | winner | DR. RAGHAVENDRA SHARMA | Raghavendra Sharma |
| 123 | runner_up | AGAM KUMAR MAURYA | Agam Maurya |
| 124 | winner | DR ARUN KUMAR | Dr. Arun Kumar Saxena |
| 124 | runner_up | RAJESH KUMAR AGARWAL | Rajesh Aggarwal |
| 126 | winner | DHARMPAL SINGH | Dharampal Singh |
| 126 | runner_up | PT. RADHA KRISHAN SHARMA | Radha Krishan Sharma |
| 127 | runner_up | SHAILENDRA SINGH GANGWAR | Shailendra Gangwar |
| 128 | winner | JAYDRATH URF PRAVAKTANAND | Swami Pravaktanand |
| 129 | winner | BABURAM | Babu Ram Paswan |
| 129 | runner_up | ARTI | Ms Arti |
| 132 | runner_up | Neeraj (Kushwaha) Maurya | Niraj Nilinesh |
| 134 | winner | CHETRAM | Chetram Pasi |
| 137 | winner | Harvinder Kumar Sahni alias Romi Sahni | Harvindar Kumar Sahani |
| 140 | runner_up | Ramsaran | Ram Sharan |
| 141 | runner_up | CHAUDHARY VARUN SINGH | Varun Singh |
| 143 | runner_up | SUNEEL KUMAR LALA | Sunil Kumar Lala |
| 146 | runner_up | Radhey Shyam Jaiswal | Radhe Shyam Jaiswal |
| 152 | runner_up | Dr. Hargovind Bhargava | Dr. Hargovind Bhargawa |
| 153 | runner_up | MANOJ KUMAR RAJVANSHI | Manoj Kumar Raghuvanshi |
| 154 | winner | Madhavendra Pratap Singh | Madhavendra Pratap |
| 155 | winner | RAJNI TIWARI | Rajani Tiwari |
| 155 | runner_up | MOHD ASIF KHAN | Asif Khan Babbu |
| 159 | winner | ASHISH KUMAR SINGH 'ASHU' | Ashish Kumar Singh |
| 159 | runner_up | BRIJESH KUMAR VERMA A/s TILLU BHAIYA | Brijesh Kumar Verma |
| 161 | winner | Alka Singh | Alka Singh Arkvanshi |
| 163 | winner | BAMBA LAL | Bamba Lal Diwakar |
| 164 | winner | BRAJESH KUMAR | Brijesh Kumar Rawat |
| 171 | runner_up | ANJANI KUMAR SRIVASTAVA | Anjali Kumar Srivastava |
| 172 | winner | Dr. Neeraj Bora | Neeraj Bora |
| 173 | winner | Ashutosh Tandon 'Gopal Ji ' | Ashutosh Tandon |
| 173 | runner_up | Anurag Singh Bhadouriya | Anurag Bhadouria |
| 174 | winner | RAVIDAS MEHROTRA | Ravidas Mehotra |
| 175 | runner_up | Surendra Singh Gandhi 'Raju Gandhi' | Raju Gandhi |
| 177 | winner | SHYAM SUNDER | Shyam Sunder Bharti |
| 179 | winner | RAHUL RAJPOOT urf RAHUL LODHI | Rahul Rajpoot |
| 181 | winner | ASHOK KUMAR | Ashok Kori |
| 185 | runner_up | Chandra Prakash Mishra Matiyari | Chandraprakash Mishra |
| 186 | runner_up | DR.SANJAY SINH | Sanjaya Sinh |
| 187 | winner | MOHD TAHIR KHAN | Mohammad Tahir Khan |
| 191 | winner | RAJESH KUMAR GAUTAM | Rajesh Gautam |
| 192 | winner | Dr. SURABHI | Dr. Surabhi Singh |
| 194 | winner | Major Sunil Dutt Dwivedi | Sunil Dutt Dwivedi |
| 195 | winner | Nagendra Singh Rathour | Nagendra Singh Rathore |
| 197 | winner | Kailash Rajput | Kailash Singh Rajput |
| 198 | runner_up | ANIL KUMAR DOHAREY | Anil Kumar Dohare |
| 200 | winner | Sarita Bhadauriya | Sarita Bhadauria |
| 201 | runner_up | Dr. SIDDHARTH SHANKER DOHRE | Siddharth Shanker |
| 209 | winner | RAHUL BACHHA | Rahul Bachha Sonkar |
| 209 | runner_up | RACHNA SINGH GAUTAM | Rachna Singh |
| 210 | runner_up | MUNINDRA SHUKLA | Munendra Shukla |
| 216 | winner | MOHAMMAD HASAN 'ROOMI' | Mohammed Hasan |
| 216 | runner_up | RAGHUNANDAN SINGH BHADAURIYA | Raghunandan Singh Bhadauria |
| 224 | winner | Dr Rashmi Arya | Rashmi Arya |
| 225 | runner_up | Deep Narayan Singh (Deepak Yadav) | Deep Narayan Singh |
| 226 | runner_up | Chandra Bhusan Singh Bundela (Guddu Raja) | Chandrabhusan Bundela |
| 227 | winner | Manohar Lal | Manohar Lal Panth |
| 228 | winner | DR. MANOJ KUMAR PRAJAPATI | Manoj Kumar Prajapati |
| 229 | winner | MANISHA | Manisha Anuragi |
| 229 | runner_up | CHANDRAWATI VERMA | Chandravati |
| 231 | winner | BRIJBHUSHAN RAJPUT | Brijbhushan Rajpoot |
| 231 | runner_up | RAMJEEVAN | Ramjeevan Yadav |
| 232 | winner | RAMKESH NISHAD | Ramakesh Nishad |
| 232 | runner_up | BRAJESH KUMAR PRAJAPATI | Brijesh Prajapati |
| 234 | winner | Ommani Varma | Ommani Verma |
| 236 | winner | ANIL KUMAR ANIL PRADHAN | Anil Pradhan |
| 239 | winner | Jay Kumar Singh Jaiki | Jai Kumar Singh Jaiki |
| 240 | winner | Chandra Prakash | Chandra Prakash Lodhi |
| 242 | runner_up | RANVENDRA PRATAP SINGH ALIAS DHUNNI BHAIYA | Ranvendra Pratap Singh |
| 244 | winner | Aradhana Mishra, Mona | Aradhana Misra Mona |
| 244 | runner_up | NAGESH PRATAP SINGH URF CHHOTE SARKAR | Nagesh Pratap Singh |
| 247 | winner | JEET LAL | Jeet Lal Patel |
| 248 | winner | RAJENDRA KUMAR | Rajendra Maurya |
| 249 | winner | RAM SINGH | Ram Singh Patel |
| 249 | runner_up | RAJENDRA PRATAP SINGH URF MOTI | Rajendra Pratap Singh |
| 250 | winner | RAKESH KUMAR VERMA ALIAS DR. R. K. VERMA | Rakesh Kumar Verma |
| 250 | runner_up | ABHAY KUMAR ALIAS DHIRAJ OJHA | Dhiraj Ojha |
| 251 | winner | DR. PALLAVI PATEL | Pallavi Patel |
| 252 | winner | Indrajeet Saroj | Indrajit Saroj |
| 253 | runner_up | Nagendra Pratap Singh Patel | Nagendra Pratap Singh |
| 255 | winner | Geeta Shastri (Pasi) | Geeta Shastri |
| 255 | runner_up | Dr. Jamuna Prasad Saroj | Jamuna Prasad |
| 256 | runner_up | Mohd.Mujataba Siddiqui | Mujataba Siddiqui |
| 259 | winner | SANDEEP SINGH | Sandeep Singh Patel |
| 259 | runner_up | NEELAM KARVARIYA | Neelam Karwariya |
| 263 | winner | NAND GOPAL GUPTA "NANDI" | Nand Gopal Gupta |
| 264 | runner_up | AJAY | Ajay Munna |
| 265 | winner | Rajmani | Rajmani Kol |
| 265 | runner_up | Ramdev Nidar | Ram Deo |
| 266 | winner | Sakendra Pratap | Sakendra Pratap Verma |
| 266 | runner_up | Rakesh Kumar Verma | Rakesh Verma |
| 270 | winner | Satish Chandra Sharma | Satish Sharma |
| 272 | runner_up | Ram Magan | Ram Magan Rawat |
| 274 | runner_up | FIROZ KHAN URF GABBAR | Firoz Khan |
| 275 | runner_up | TEJ NARAYAN PANDEY (PAWAN PANDEY) | Tej Narayan Pandey |
| 284 | winner | MARIYA | Mariya Shah |
| 288 | winner | ANAND KUMAR YADAV | Anand Kumar |
| 290 | winner | Ram Feran | Ram Feran Pandey |
| 291 | winner | KAILASH NATH | Kailash Nath Shukla |
| 292 | winner | DR. SHIV PRATAP YADAV | Shiv Pratap Yadav |
| 292 | runner_up | SHAILESH KUMAR SINGH "SHAILU" | Shailesh Kumar Singh |
| 293 | winner | RAMPRATAP VERMA URF SHASHIKANT VERMA | Ram Pratap Verma |
| 293 | runner_up | HASIB KHAN | Haseeb Hasan Khan |
| 294 | winner | PALTOO RAM | Paltu Ram |
| 295 | winner | VINAY KUMAR | Vinay Kumar Dwivedi |
| 297 | runner_up | Baijnath | Baijnath Dubey |
| 298 | runner_up | YOGESH PRATAP SINGH URF YOGESH BHAIYA | Yogesh Pratap Singh |
| 299 | winner | PREM NRAYAN PANDEY | Prem Narayan Pandey |
| 300 | runner_up | Ramesh Chandra Gautam | Ramesh Chandra |
| 302 | runner_up | PREM CHANDRA | Prem Chand Nishad |
| 303 | winner | SHYAMDHANI RAHI | Shyam Dhani |
| 303 | runner_up | VIJAY KUMAR | Vinay Paswan |
| 304 | runner_up | Naveen | Monu Dubey |
| 305 | runner_up | DR. SATISH CHANDRA DWIVEDI | Satish Chandra Dwiwedi |
| 307 | winner | AJAY SINGH | Ajay Kumar Singh |
| 307 | runner_up | TARAYAMBAK NATH | Triyambak Pathak |
| 309 | runner_up | Sangeeta Devi Urf Sangeeta Pratap Jaiswal | Sangeeta Pratap Jaiswal |
| 310 | runner_up | Dayaram Chaudhary | Dayaram Choudhary |
| 311 | runner_up | Ravi | Ravi Kumar Sonkar |
| 313 | winner | ANKUR TIWARI | Ankur Raj Tiwari |
| 314 | winner | GANESH CHANDRA | Ganesh Chandra Chauhan |
| 318 | winner | JAY MANGAL | Jai Mangal Kanojiya |
| 319 | runner_up | KRISHNABHAN | Krishnabhan Singh Sainthwar |
| 320 | winner | FATEH BAHADUR | Fateh Bahadur Singh |
| 322 | winner | ADITYANATH | Yogi Adityanath |
| 322 | runner_up | SUBHAWATI UPENDRA DUTT SHUKLA | Subhawati Shukla |
| 324 | runner_up | YASHPAL SINGH RAWAT | Yashwant Singh Rawat |
| 325 | winner | SHRIRAM CHAUHAN | Sriram Chauhan |
| 326 | runner_up | BRIJESH CHANDRA LAL | Brijesh Chandra Lal Paswan |
| 327 | winner | DR. VIMLESH PASWAN | Vimlesh Paswan |
| 327 | runner_up | DR. SANJAY KUMAR | Sanjay Kumar |
| 328 | runner_up | VINAY SHANKAR | Vinay Shankar Tiwari |
| 330 | winner | MANISH KUMAR URF MANTU | Manish Jaiswal |
| 330 | runner_up | VIKRAMA YADAV | Vikram Yadav |
| 333 | winner | Panchanand Pathak (P.N. Pathak) | Panchanand Pathak |
| 333 | runner_up | Rajesh Pratap Rao Urf Banti Bhaiya | Rajesh Pratap Rao |
| 336 | runner_up | RAMBHUAL NISHAD | Ram Bhuwal Nishad |
| 337 | runner_up | Ajay Pratap Singh Alias Pintu | Ajay Pratap Singh |
| 339 | runner_up | FASIHA MANZAR GHAZALA LARI | Ghazala Lari |
| 340 | winner | SABHAKUNWAR | Sabhakunwar Kushawaha |
| 341 | winner | BIJAYLAXMI GAUTAM | Vijay Laxmi Gautam |
| 342 | winner | DEEPAK KUMAR MISHRA "SHAKA" | Deepak Kumar Mishra |
| 343 | winner | DR. SANGRAM YADAV | Sangram Yadav |
| 345 | runner_up | BANDANA SINGH | Smt. Vandana Singh |
| 346 | winner | AKHILESH | Akhilesh Yadav |
| 347 | runner_up | AKHILESH KUMAR MISHRA ''GUDDU" | Akhilesh Kumar Mishra |
| 349 | runner_up | RAM SURAT | Ramsurat Rajbhar |
| 350 | winner | KAMLAKANT RAJBHAR URF PAPPU | Kamlakant Rajbhar |
| 350 | runner_up | DR. KRISHNA MURARI VISHWAKARMA | Krishna Murari Vishwakarma |
| 351 | winner | BECHAI | Bechai Saroj |
| 351 | runner_up | NEELAM | Neelam Sonkar |
| 352 | winner | PUJA | Puja Saroj |
| 352 | runner_up | MANJOO SAROJ | Manju Saroj |
| 354 | runner_up | VIJAY KUMAR RAJBHAR | Vijay Rajbhar |
| 355 | runner_up | POONAM SAROJ | Smt. Poonam Saroj |
| 356 | runner_up | ASHOK KUMAR SINGH | Ashok Singh |
| 357 | runner_up | Chhathu Ram | Chhattu Ram |
| 359 | winner | ZIYAUDDIN RIZVI | Mohammed Ziauddin Rizvi |
| 362 | runner_up | RAM GOVIND | Ram Govind Chaudhary |
| 364 | runner_up | OMPRAKASH BABA DUBEY | Baba Dubey |
| 365 | winner | Ramesh | Ramesh Singh |
| 368 | winner | PANKAJ | Pankaj Patel |
| 368 | runner_up | AJAY SHANKAR DUBEY | Ajay Dubey |
| 369 | winner | DR. RAGINI | Ragini Sonkar |
| 369 | runner_up | MEHI LAL | Mihilal Gautam |
| 370 | winner | DR R.K. PATEL | R.K. Patel |
| 371 | runner_up | Dr. HARENDRA PRASAD SINGH | Harendra Prasad Singh |
| 372 | runner_up | Dinesh Chaudhary | Dinesh Choudhary |
| 373 | winner | BEDI | Triveni Ram |
| 373 | runner_up | RAMRAJ | Ramraj Vanvasi |
| 375 | winner | JAIKISHAN | Jai Kishan Sahu |
| 375 | runner_up | DR. SANGEETA BALWANT | Sangeeta Balwant Bind |
| 376 | runner_up | RAM NARESH KUSHWAHA | Ramnaresh Kushwah |
| 377 | runner_up | KALICHARAN | Kalicharan Rajbhar |
| 378 | winner | SUHAIB Alias MANNU ANSARI | Suhaib Ansari |
| 379 | winner | OM PRAKASH | Omprakash Singh |
| 381 | winner | PRABHU NARAYAN SINGH YADAV | Prabhunarayan Yadav |
| 383 | winner | KAILASH | Kailash Kharwar |
| 389 | winner | Dr. Neelkanth Tiwari | Neelkanth Tiwari |
| 389 | runner_up | Kameshwar alias Kishan Dixit | Kameshwar (Kishan Dixit) |
| 391 | winner | Neel Ratan Singh | Neel Ratan Singh Patel |
| 392 | winner | ZAHID | Zahid Beg |
| 392 | runner_up | RAVINDRA NATH TRIPATHI | Ravindra Tripathi |
| 394 | runner_up | Anjani | Smt. Anjani |
| 396 | runner_up | KAILASH CHAURSIA | Kailash Chaurasia |
| 399 | runner_up | NARENDRA SINGH KUSAWAHA | Narendra Singh Kushwaha |
| 400 | winner | Dr. Anil Kumar Maurya | Anil Kumar Maurya |
| 402 | runner_up | ARVIND KUMAR alias SUNIL SINGH GOND | Arvind Kumar |
| 403 | winner | RAMDULAR | Ramdular Gaur |
| 403 | runner_up | VIJAY SINGH | Vijay Singh Gour |


---

# Manipur 2022, results by assembly constituency

General election to the Manipur Legislative Assembly, two phases, 28 February
and 5 March 2022, counted 10 March 2022. 60 ACs, none unopposed.

## Sources

The Commission's statistical report for this election (docid 14166 on
eci.gov.in, "10.Detailed Results") could not be downloaded: eci.gov.in refused
the request (HTTP 406) every time on 2026-10-10. The Chief Electoral Officer's
own documents were used instead.

1. Every vote figure and electors: CEO Manipur, Form 20 "Final Result Sheet"
   of each AC, signed by the Returning Officer, one PDF per AC,
   https://ceomanipur.nic.in/ResultSheets/StateLegislativeAssembly/2022/01.pdf
   to .../60.pdf (index: https://ceomanipur.nic.in/ResultSheets/StateLegislativeAssembly/2022/results.aspx).
   - ac, ac_name, reserved: "Name of Assembly/segment" in the Form 20 header;
     "(SC)"/"(ST)" moved to `reserved` (1 SC, 19 ST).
   - electors: "Total No. of Electors in Assembly Constituency/segment" in the
     Form 20 header. **Caution, see Checks.**
   - winner_votes, runner_up_votes: the two highest candidate columns of the
     "Total Votes Polled" row (EVM plus postal).
   - total_votes: that row's "Total of Valid Votes" plus its NOTA, the same
     definition as the other states here (rejected postal ballots excluded).
   - margin: computed.
2. Winner and runner-up names and parties: CEO Manipur, "List of Candidates",
   State Assembly Elections 2022,
   https://ceomanipur.nic.in/Affidavits/AssemblyElection/ge_2022.aspx .
   Its contesting candidates are listed in the same order as the Form 20
   columns (same count in all 60 ACs; order checked by name in 1 Khundrakpam
   and 3 Khurai). Party names are written out there and abbreviated here:
   BJP, INC, NPP, JD(U), NPF, KPA (Kuki People's Alliance), IND, SHS, NCP,
   RPI(A), LJPRV, CPI, KNA, RJSP.
3. Second source, margin, winner party and votes: Wikipedia, "2022 Manipur
   Legislative Assembly election", section "Results by constituency",
   https://en.wikipedia.org/w/index.php?title=2022_Manipur_Legislative_Assembly_election&action=raw
   (read 2026-10-10). Matched by AC name, because Wikipedia numbers 46 to 49
   wrongly (it lists Karong as 46, Mao 47, Tadubi 48, Saikul 49).
4. Second source for electors: the Wikipedia article of each AC (infobox
   `electors`, which cites the Commission's 2022 report), read 2026-10-10.
5. Not usable: the CEO's "Statistical Report 2022"
   (https://ceomanipur.nic.in/StatisticalReport/AssemblyElection/Statistical%20Report%202022.pdf,
   82 MB) is a magazine-style report of page images with no text layer.

## Checks

- ACs: 60 rows, ACs 1 to 60 once each, against 60 seats.
- In every Form 20, the candidate columns of "Total Votes Polled" sum to its
  "Total of Valid Votes", and valid + rejected + NOTA = total; EVM + postal =
  total in every column where the postal row was read (59 ACs; in 59 Saikot
  the postal row did not parse, and its EVM and total rows still pass).
- margin = winner_votes - runner_up_votes in all 60 rows, all positive
  (smallest 50, 36 Wabgai).
- Winners: BJP 32, NPP 7, JD(U) 6, INC 5, NPF 5, IND 3, KPA 2, the declared
  result.
- Electors: sum 20,53,141. **No Commission state total was read**, and the
  Form 20 figure does not match the AC articles on Wikipedia in most ACs:
  equal in 13, Wikipedia gives none in 6, and in 41 Wikipedia is higher, by
  between 52 and 1,148. In Meghalaya (2023) the same Form 20 header
  equals the Commission's electors including service electors in 47 of 59
  ACs and falls short by 8 to 45 in the other 12, so the Form 20 figure is
  probably the roll the Returning Officer held at counting, without some or
  all service electors. Treat this column as unverified until the
  Commission's table 11 for Manipur 2022 can be read.

| AC | Form 20 | Wikipedia AC article |
|---|---|---|
| 1 Khundrakpam | 27414 | 27777 |
| 3 Khurai | 35747 | not given |
| 4 Khetrigao | 36651 | 36835 |
| 5 Thongju | 31928 | 32132 |
| 6 Keirao | 29983 | 30224 |
| 7 Andro | 35539 | 35930 |
| 8 Lamlai | 30091 | 30376 |
| 9 Thangmeiband | 28068 | 28212 |
| 10 Uripok | 25583 | 25727 |
| 11 Sagolband | 23920 | not given |
| 12 Keisamthong | 27447 | 27536 |
| 13 Singjamei | 20642 | 20734 |
| 16 Sekmai (SC) | 29971 | 30487 |
| 17 Lamsang | 33437 | 33787 |
| 18 Konthoujam | 29732 | not given |
| 19 Patsoi | 37302 | 37604 |
| 20 Langthabal | 28128 | 28413 |
| 21 Naoriya Pakhanglakpa | 34676 | 35053 |
| 22 Wangoi | 29761 | 30031 |
| 23 Mayang Imphal | 31813 | 32053 |
| 24 Nambol | 32950 | 33399 |
| 26 Bishenpur | 31747 | not given |
| 28 Thanga | 22803 | 22984 |
| 31 Thoubal | 31697 | 32132 |
| 32 Wangkhem | 33274 | 33866 |
| 35 Khangabo | 37094 | 37687 |
| 40 Jiribam | 29298 | 29426 |
| 41 Chandel (ST) | 49255 | 50378 |
| 42 Tengnoupal (ST) | 44525 | 44914 |
| 43 Phungyar (ST) | 34403 | 34789 |
| 44 Ukhrul (ST) | 47780 | not given |
| 45 Chingai (ST) | 47090 | not given |
| 46 Saikul (ST) | 28825 | 29417 |
| 47 Karong (ST) | 54658 | 54916 |
| 48 Mao (ST) | 55333 | 55735 |
| 49 Tadubi (ST) | 48863 | 49410 |
| 50 Kangpokpi | 27545 | 28124 |
| 51 Saitu (ST) | 43981 | 44686 |
| 52 Tamei (ST) | 42045 | 42117 |
| 53 Tamenglong (ST) | 35777 | 35888 |
| 54 Nungba (ST) | 29365 | 29510 |
| 55 Tipaimukh (ST) | 18554 | 18606 |
| 56 Thanlon (ST) | 17934 | 18042 |
| 57 Henglep (ST) | 31535 | 31944 |
| 58 Churachandpur (ST) | 64236 | 65325 |
| 59 Saikot (ST) | 61465 | 62613 |
| 60 Singhat (ST) | 27469 | 27832 |

## Disagreements between the sources on results

Winner party agrees with Wikipedia in all 60 ACs; runner-up party in 59.

| AC | field | Form 20 / CEO list | Wikipedia | kept |
|---|---|---|---|---|
| 3 Khurai | runner_up_votes | 8,894 | 8,767 | Form 20 (8,767 is its EVM-only figure) |
| 3 Khurai | margin | 2,237 | 2,364 | Form 20 |
| 13 Singjamei | runner_up_party | NPP (Oinam Romen Singh) | JD(U) | CEO list |
| 27 Moirang | winner_votes | 14,428 | 14,349 | Form 20 |
| 27 Moirang | runner_up_votes | 12,206 | 12,118 | Form 20 |
| 27 Moirang | margin | 2,222 | 2,231 | Form 20 |
| 38 Hiyanglam | winner_votes | 8,713 | 8,613 | Form 20 |
| 38 Hiyanglam | margin | 2,129 | 2,029 | Form 20 |
| 42 Tengnoupal | winner_votes | 21,663 | 21,597 | Form 20 |
| 42 Tengnoupal | runner_up_votes | 15,252 | 14,115 | Form 20 |
| 42 Tengnoupal | margin | 6,411 | 7,482 | Form 20 |
| 47 Karong | winner_votes | 17,191 | 16,452 | Form 20 |
| 47 Karong | runner_up_votes | 13,649 | 13,566 | Form 20 |
| 47 Karong | margin | 3,542 | 2,886 | Form 20 |
| 49 Tadubi | winner_votes | 21,601 | 21,289 | Form 20 |
| 49 Tadubi | runner_up_votes | 21,052 | 20,821 | Form 20 |
| 51 Saitu | winner_votes | 12,456 | 12,546 | Form 20 |
| 53 Tamenglong | runner_up_votes | 9,147 | 9,156 | Form 20 |
| 58 Churachandpur | winner_votes | 18,231 | 19,231 | Form 20 |
| 60 Singhat | runner_up_votes | 10,079 | 10,179 | Form 20 |
| 60 Singhat | margin | 2,019 | 1,919 | Form 20 |

The Form 20 figures are kept because each sheet adds up internally. Names
are as the CEO's list spells them.

## What is missing

The Commission's own Detailed Results and AC-wise electors for Manipur 2022.
Electors in this file rest on Form 20 alone and disagree with the only other
AC-level figure found.


---

# Meghalaya 2023, results by assembly constituency

General election to the Meghalaya Legislative Assembly, poll 27 February
2023, counted 2 March 2023. 60 ACs, none unopposed.

**23 Sohiong (ST): the poll was adjourned** after the death of the UDP
candidate (ECI press note ECI/PN/25/2023 of 29 March 2023). It was held on
10 May 2023 and counted on 13 May 2023. Its row is that adjourned poll.

## Sources

The Commission's statistical report (docid 15053 on eci.gov.in, "Meghalaya
General Legislative Election 2023 (Including AC-23)", table "10-Detailed
Results") is listed, but every download was refused (HTTP 406) on 2026-10-10.
The CEO's documents and the Commission's Pocket Book were used instead.

1. Votes: CEO Meghalaya, Form 20 "Final Result Sheet" for each AC,
   https://ceomeghalaya.nic.in/electionconducted/mla2023/form20/ac01.pdf to
   ac60.pdf (index .../mla2023/form20.html). ac23.pdf answers 404; Sohiong's
   is the adjourned poll's Form 20,
   https://ceomeghalaya.nic.in/electionconducted/adjourned-poll/2023-adjourned-poll-23-sohiong/form20.pdf,
   a scan without a text layer, read by eye from its last page (Total Votes
   Polled: 1,762; 13,257; 62; 40; 89; 16,679; valid 31,889; rejected 4;
   NOTA 272; total 32,165). Its six candidate figures sum to the printed
   31,889.
   - ac, ac_name, reserved: the Form 20 header; "(ST)" moved to `reserved`
     (55 ST, 5 general, as the Pocket Book's highlights give).
   - winner_votes, runner_up_votes: the two highest candidate columns of
     "Total Votes Polled" (EVM plus postal).
   - total_votes: "Total of Valid Votes" plus NOTA on that row.
   - margin: computed.
2. Names and parties: CEO Meghalaya, "AC Result Report" (the results
   portal's winner/trailing table),
   https://ceomeghalaya.nic.in/electionconducted/mla2023/ac-result-report.pdf ,
   59 ACs (it predates Sohiong). Every winner and runner-up name in it was
   found in that AC's Form 20 header, and its margin equals the Form 20
   margin in all 59. For 23 Sohiong the names are the Form 20's and the
   parties (UDP, NPP) are Wikipedia's (source 4): no first-hand document
   read gives them.
3. Electors: ECI, Electoral Statistical Pocket Book 2023, table 10.8.E2
   "AC-wise Voters' Turnout Rate (%) GE to State Legislative Assembly of
   Meghalaya-2023", Total Electors, and highlights 10.8.E1 ("No. of Electors
   (Including service electors)" 21,79,084),
   https://www.eci.gov.in/eci-backend/public/api/download?url=LMAhAK6sOPBp%2FNFF0iRfXbEB1EVSLT41NNLRjYNJJP1KivrUxbfqkDatmHy12e%2FzGjJMI0%2FjETs7fjrM8lYn4q0vCivj94MhpU3oJn7R5vrT16TiGkIgrvGfcMND0TasK6qlsuh5iZIkAbkwBAifqg%3D%3D
   (book pages 143 to 146).
4. Second source, margin, winner party and votes: Wikipedia, "2023 Meghalaya
   Legislative Assembly election", "Results by constituency",
   https://en.wikipedia.org/w/index.php?title=2023_Meghalaya_Legislative_Assembly_election&action=raw
   (read 2026-10-10).

## Checks

- ACs: 60 rows, ACs 1 to 60 once each, against 60 seats.
- In every Form 20 the candidate columns sum to "Total of Valid Votes", valid
  + rejected + NOTA = total, and EVM + postal = total for every column.
- margin = winner_votes - runner_up_votes in all 60 rows, all positive
  (smallest 10, 47 Rajabala).
- Winners: NPP 26, UDP 12 (11 on 2 March plus Sohiong), INC 5, AITC 5,
  VPP 4, BJP 2, PDF 2, HSPDP 2, IND 2.
- Electors: sum 21,79,084, equal to the Commission's state total. Form 20
  prints the same figure in 47 of 59 ACs (and in Sohiong, 34,790); in 12 it
  prints fewer, and the Pocket Book's figure is kept:

| AC | Form 20 | Pocket Book (kept) |
|---|---|---|
| 26 | 34674 | 34682 |
| 32 | 43091 | 43120 |
| 33 | 39399 | 39415 |
| 34 | 41044 | 41064 |
| 35 | 35719 | 35764 |
| 36 | 37538 | 37565 |
| 37 | 43081 | 43109 |
| 38 | 29197 | 29232 |
| 39 | 30387 | 30411 |
| 40 | 33084 | 33102 |
| 42 | 35330 | 35340 |
| 43 | 37350 | 37359 |

## Disagreements between the sources

Against Wikipedia, winner and runner-up parties agree in all 60 ACs (Wikipedia
writes "Ind" and the full VPP name). Votes agree except:

| AC | field | Form 20 | Wikipedia | kept |
|---|---|---|---|---|
| 5 Sutnga Saipung | runner_up_votes | 15,146 | 14,866 | Form 20 |
| 5 Sutnga Saipung | margin | 1,828 | 2,108 | Form 20 (the CEO's result report also says 1,828) |
| 9 Nongpoh | margin | 6,686 | 6,137 | Form 20 (Wikipedia's own vote figures give 6,686) |

---

# Nagaland 2023, Assembly results by AC

File: `nagaland_2023.csv`, 60 rows. Every column is from the Election Commission's statistical report for this election, two of its tables as downloaded from the Commission's site in Excel on 10 October 2026: 10, Detailed Results (every candidate and NOTA, with each seat's total electors), and 11, AC Wise Number Of Electors. Electors are the report's All Electors, general electors (overseas electors included) plus service voters; in every seat table 10's total electors equals table 11's. winner and runner_up are the two candidates with the most votes, NOTA left out; margin is winner less runner-up; total_votes is every candidate plus NOTA. Party codes are the Commission's. ac_name and reserved are from table 11, which marks (SC) and (ST) after the name. Written by a short script from the two tables, which asserts the winner's votes exceed the runner-up's in every seat.

Akuluto (31) was uncontested (table 11 says so in a note) and has one candidate, the BJP's, in table 10; it is marked `unopposed` with no votes or margin, and the spread counts 59 contested seats. Before these tables were read, Nagaland was held back because its votes could be read only from Wikipedia. Against that Wikipedia table the electors agree in every seat, and the margin differs in five: Kohima Town 1,342 (Wikipedia 1,180), Aonglenden 4,520 (4,390), Alongtaki 3,748 (1,202), Thonoknyu 2,328 (2,325) and Seyochung Sitimi 732 (930). The Commission's figures are used.
