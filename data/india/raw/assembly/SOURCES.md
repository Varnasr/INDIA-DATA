# Assembly results by constituency

One file per state, the latest general Assembly election, read by scripts/build_margins.py (ASM) for the Assembly spread on india/numbers/. Columns: ac, ac_name, reserved, electors, winner, winner_party, winner_votes, runner_up, runner_up_party, runner_up_votes, margin, total_votes, unopposed. The margin is winner less runner-up in every row, and NOTA is never a runner-up; the build asserts the first. The Election Commission's own pages could not be read from the sandbox for most states (results.eci.gov.in answers 404 for these elections and eci.gov.in 406), so most files are a published compilation of the Commission's results checked seat by seat against a second. Madhya Pradesh, Chhattisgarh, Telangana, Mizoram and Uttar Pradesh are from the Commission's statistical report, and Manipur and Meghalaya from the Chief Electoral Officers' Form 20 sheets. Nagaland is held back: its votes could be read only from Wikipedia. Electors are used only as weights, to spread a state's names left off over its seats; whether a source counts service voters is noted where it is known. Each section below is the collector's note, with every source and every disagreement between sources and which figure was kept.


---

# Andhra Pradesh Legislative Assembly election, 2024: results by constituency

File: `andhrapradesh_2024.csv`, 175 rows, one per assembly constituency (AC), numbered as the Commission numbers them. The general election polled 13 May 2024 with the Lok Sabha; counted 4 June 2024. Retrieved 10 October 2026.

## The Commission's own pages could not be read

- The Commission's statistical report for this election is listed at https://www.eci.gov.in/statistical-report/ae/2024/2 (read through a Firecrawl render for Odisha, which shows 14 report files including "10-Detailed Results" and "11 - AC Wise Number Of Electors"). The files are served only through `https://www.eci.gov.in/eci-backend/public/api/election-result?category_id=N` and the encrypted `api/download` route, and both answered HTTP 406 ("Request was blocked due to suspicious behavior") from this sandbox, with curl and with a Firecrawl scrape. Guessed direct paths under `eci-backend/public/all_files/full-statistical-reports/` also answered 406, which is how that server answers a missing file.
- The results pages on results.eci.gov.in for 2024 (`AcResultGenJune2024`, `ResultAcGenNov2024`) now answer 404. Archived copies exist on the Wayback Machine, but web.archive.org could not be reached from here (connection reset) and WebFetch refuses that host.
- So every figure in the CSV comes from published compilations of the Commission's results, checked against each other. None was read from an ECI page directly, with the exceptions named below.

## Sources and URLs

1. **IndiaVotes** (compilation of ECI results). State page https://www.indiavotes.com/vidhan-sabha/andhra-pradesh/2024/ and one page per AC, https://www.indiavotes.com/vidhan-sabha/andhra-pradesh/2024/<slug>/ (175 pages, read from each page's embedded `iv-page-context` JSON: every candidate with party abbreviation and votes, NOTA, `voters_eligible`, `votes_polled`, `winning_margin`, AC category).
2. **Wikipedia, results by constituency**: https://en.wikipedia.org/wiki/2024_Andhra_Pradesh_Legislative_Assembly_election (section "Results by constituency", wikitext via `action=raw`): AC number, AC name, winner, runner-up, their parties and votes, margin.
3. **Wikipedia, list of constituencies**: https://en.wikipedia.org/wiki/List_of_constituencies_of_the_Andhra_Pradesh_Legislative_Assembly : AC number and reservation.
4. **Wikipedia AC articles**, one per AC, https://en.wikipedia.org/wiki/<AC>_Assembly_constituency (`action=raw`): the 2024 election box (candidates, votes) and the infobox `electors`, used only to break ties between 1 and 2.
5. **ECI statistical report 34 (Lok Sabha 2024, "Details of Assembly Segment of PC")** as compiled by OpenCity, https://data.opencity.in/dataset/85a345c6-78c0-4f57-adfc-236c726c5456/resource/881d1489-a8fc-46b1-b00d-d4824e08e797/download/142dc4e5-49e3-4412-a751-d712970b0dd5.csv , read from the copy already in the repository, `INDIA-DATA/data/india/raw/ls2024_ac_pc.csv` (column `electors_ac`). The Assembly and Lok Sabha polls here were simultaneous, on the same roll, so this is a check on electors.
6. **ECI statistical report 12 (Lok Sabha 2024, State-wise voters turnout)**, https://www.eci.gov.in/eci-backend/public/all_files/GE-2024-statistical-report/12-State-Wise-Voters-Turn-Out.pdf , as recorded in `INDIA-DATA/data/india/raw/adults_ls2024.csv` (`electors_2024` = 41,401,887). That file now answers 406 here too, so the figure is taken from the repository's record of it.
7. A web search (2026-10-10) for AC 57 Palakollu returned the Commission's own page https://results.eci.gov.in/AcResultGenJune2024/ConstituencywiseS0157.htm in its index with Nimmala Ramanaidu 113114 and Gudala Sri Hari Gopala Rao 45169. That page itself now answers 404; the figures are the search engine's copy of it.

### Which source each column came from

| column | source |
|---|---|
| ac | Wikipedia results table and constituency list (they agree on every number) |
| ac_name | IndiaVotes spelling (closer to the Commission's than Wikipedia's, which uses native spellings such as Padamapur, Baragada); all-capital names put in title case. Not checked against the Commission's own spelling. |
| reserved | Wikipedia list of constituencies, whose counts equal the Delimitation Order's allocation; checked against the results table and IndiaVotes |
| electors | IndiaVotes `voters_eligible` |
| winner, runner_up | IndiaVotes candidate names (ECI-style transliteration) |
| winner_party, runner_up_party | IndiaVotes party abbreviation (ECI style), with `POUI_ABBR_JLKM_01` written as JLKM; checked against Wikipedia |
| winner_votes, runner_up_votes | IndiaVotes, checked against Wikipedia; disagreements decided as listed below |
| margin | computed, winner_votes - runner_up_votes |
| total_votes | computed from IndiaVotes: every candidate's votes plus NOTA (postal included) |
| unopposed | Wikipedia results table ("Elected unopposed") and IndiaVotes (one candidate, 0 votes) |

Runner-up is the second candidate by votes; NOTA is never a candidate in IndiaVotes' list and never a runner-up here.

## Checks

- **ACs**: 175 rows, numbered 1 to 175 once each, against the state's 175 seats. Passed.
- **Electors**: the CSV sums to 41,401,887. The Commission's Lok Sabha 2024 total for the state (source 6) is 41,401,887: equal. The Commission's Assembly report total was not read (see above).
- **Margin**: margin = winner_votes - runner_up_votes in 175 of 175 contested rows. The margin IndiaVotes prints (`winning_margin`) equals the written margin in 175 of 175.
- **Winner above runner-up**, margin > 0: 175 of 175.
- **total_votes** (candidates plus NOTA) equals IndiaVotes' own `votes_polled` in 175 of 175 contested ACs. It equals the turnout in the AC's Wikipedia election box in 153 of the 165 ACs whose box gives one; the others are AC 22 (box 139,339, CSV 139,328), AC 35 (box 184,592, CSV 189,445), AC 51 (box 199,219, CSV 202,058), AC 55 (box 182,503, CSV 182,496), AC 62 (box 175,990, CSV 178,049), AC 65 (box 166,257, CSV 166,275), AC 66 (box 208,237, CSV 211,659), AC 99 (box 235,995, CSV 238,697), AC 101 (box 219,763, CSV 220,099), AC 127 (box 152,366, CSV 153,805), AC 129 (box 199,492, CSV 189,492), AC 165 (box 206,911, CSV 209,674). Differences of exactly 10,000 are typing errors in the box; the others look like boxes that leave out postal votes. Kept IndiaVotes, whose candidate votes sum to its own total..
- **Second source**: winner party, runner-up party, winner votes and runner-up votes were compared between IndiaVotes and the Wikipedia results table in every contested AC; 174 of 175 agree on all four. Unopposed winners and their parties agree in every case.

## Disagreements and what was kept

| AC | field | IndiaVotes | Wikipedia table | tie-break | kept |
|---|---|---|---|---|---|
| 57 Palacole | winner votes | 113,114 | 111,471 | wikipedia ac article 113,114; search-engine copy of the ECI page: 113114 and 45169 | indiavotes |
| 57 Palacole | runner-up votes | 45,169 | 44,590 | wikipedia ac article 45,169; search-engine copy of the ECI page: 113114 and 45169 | indiavotes |

**Names and party labels.**

- Candidate names differ in form, not person, in ACs 32, 51, 99, 101, 129, 146, 158, 166 and 171 (for example AC 129 runner-up "B.tech Ravi" in IndiaVotes, Mareddy Ravindranatha Reddy in Wikipedia; AC 32 "Kanna Babu" against Uppalapati Venkata Ramanamurthy Raju). Votes and parties agree in each. Names are IndiaVotes' throughout, and in most ACs IndiaVotes puts the surname last where Wikipedia puts it first.

**Electors.**

- In 161 ACs the only disagreement is the Wikipedia AC infobox, which is lower than IndiaVotes in 155 of them and higher in 6, while IndiaVotes and report 34 agree; kept IndiaVotes. ACs: 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 45, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 83, 84, 85, 86, 88, 89, 90, 91, 92, 93, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 168, 169, 172, 173, 174.
- The AC infoboxes cite earlier rolls (AC 57's, for example, gives the roll of 25 March 2019), so they are not evidence against the 2024 figure.

## What is missing

- The Commission's own Detailed Results and AC-wise electors files were not read; every row rests on two or more compilations that agree, or on the tie-breaks above.

---

# Arunachal Pradesh Legislative Assembly election, 2024: results by constituency

File: `arunachal_2024.csv`, 60 rows, one per assembly constituency (AC), numbered as the Commission numbers them. The general election polled 19 April 2024 with the Lok Sabha; counted 2 June 2024. Retrieved 10 October 2026.

## The Commission's own pages could not be read

- The Commission's statistical report for this election is listed at https://www.eci.gov.in/statistical-report/ae/2024/3 (read through a Firecrawl render for Odisha, which shows 14 report files including "10-Detailed Results" and "11 - AC Wise Number Of Electors"). The files are served only through `https://www.eci.gov.in/eci-backend/public/api/election-result?category_id=N` and the encrypted `api/download` route, and both answered HTTP 406 ("Request was blocked due to suspicious behavior") from this sandbox, with curl and with a Firecrawl scrape. Guessed direct paths under `eci-backend/public/all_files/full-statistical-reports/` also answered 406, which is how that server answers a missing file.
- The results pages on results.eci.gov.in for 2024 (`AcResultGenJune2024`, `ResultAcGenNov2024`) now answer 404. Archived copies exist on the Wayback Machine, but web.archive.org could not be reached from here (connection reset) and WebFetch refuses that host.
- So every figure in the CSV comes from published compilations of the Commission's results, checked against each other. None was read from an ECI page directly, with the exceptions named below.

## Sources and URLs

1. **IndiaVotes** (compilation of ECI results). State page https://www.indiavotes.com/vidhan-sabha/arunachal-pradesh/2024/ and one page per AC, https://www.indiavotes.com/vidhan-sabha/arunachal-pradesh/2024/<slug>/ (60 pages, read from each page's embedded `iv-page-context` JSON: every candidate with party abbreviation and votes, NOTA, `voters_eligible`, `votes_polled`, `winning_margin`, AC category).
2. **Wikipedia, results by constituency**: https://en.wikipedia.org/wiki/2024_Arunachal_Pradesh_Legislative_Assembly_election (section "Results by constituency", wikitext via `action=raw`): AC number, AC name, winner, runner-up, their parties and votes, margin.
3. **Wikipedia, list of constituencies**: https://en.wikipedia.org/wiki/List_of_constituencies_of_the_Arunachal_Pradesh_Legislative_Assembly : AC number and reservation.
4. **Wikipedia AC articles**, one per AC, https://en.wikipedia.org/wiki/<AC>_Assembly_constituency (`action=raw`): the 2024 election box (candidates, votes) and the infobox `electors`, used only to break ties between 1 and 2.
5. **ECI statistical report 34 (Lok Sabha 2024, "Details of Assembly Segment of PC")** as compiled by OpenCity, https://data.opencity.in/dataset/85a345c6-78c0-4f57-adfc-236c726c5456/resource/881d1489-a8fc-46b1-b00d-d4824e08e797/download/142dc4e5-49e3-4412-a751-d712970b0dd5.csv , read from the copy already in the repository, `INDIA-DATA/data/india/raw/ls2024_ac_pc.csv` (column `electors_ac`). The Assembly and Lok Sabha polls here were simultaneous, on the same roll, so this is a check on electors.
6. **ECI statistical report 12 (Lok Sabha 2024, State-wise voters turnout)**, https://www.eci.gov.in/eci-backend/public/all_files/GE-2024-statistical-report/12-State-Wise-Voters-Turn-Out.pdf , as recorded in `INDIA-DATA/data/india/raw/adults_ls2024.csv` (`electors_2024` = 898,442). That file now answers 406 here too, so the figure is taken from the repository's record of it.

### Which source each column came from

| column | source |
|---|---|
| ac | Wikipedia results table and constituency list (they agree on every number) |
| ac_name | IndiaVotes spelling (closer to the Commission's than Wikipedia's, which uses native spellings such as Padamapur, Baragada); all-capital names put in title case. Not checked against the Commission's own spelling. |
| reserved | Wikipedia list of constituencies, whose counts equal the Delimitation Order's allocation; checked against the results table and IndiaVotes |
| electors | IndiaVotes `voters_eligible`, except the 10 ACs returned unopposed, which take the ECI report 34 figure (source 5); see below |
| winner, runner_up | IndiaVotes candidate names (ECI-style transliteration) |
| winner_party, runner_up_party | IndiaVotes party abbreviation (ECI style), with `POUI_ABBR_JLKM_01` written as JLKM; checked against Wikipedia |
| winner_votes, runner_up_votes | IndiaVotes, checked against Wikipedia; disagreements decided as listed below |
| margin | computed, winner_votes - runner_up_votes |
| total_votes | computed from IndiaVotes: every candidate's votes plus NOTA (postal included) |
| unopposed | Wikipedia results table ("Elected unopposed") and IndiaVotes (one candidate, 0 votes) |

Runner-up is the second candidate by votes; NOTA is never a candidate in IndiaVotes' list and never a runner-up here.

## Checks

- **ACs**: 60 rows, numbered 1 to 60 once each, against the state's 60 seats. Passed.
- **Electors**: the CSV sums to 898,442. The Commission's Lok Sabha 2024 total for the state (source 6) is 898,442: equal. The Commission's Assembly report total was not read (see above).
- **Margin**: margin = winner_votes - runner_up_votes in 50 of 50 contested rows. The margin IndiaVotes prints (`winning_margin`) equals the written margin in 50 of 50.
- **Winner above runner-up**, margin > 0: 50 of 50.
- **total_votes** (candidates plus NOTA) equals IndiaVotes' own `votes_polled` in 50 of 50 contested ACs. It equals the turnout in the AC's Wikipedia election box in 47 of the 47 ACs whose box gives one.
- **Second source**: winner party, runner-up party, winner votes and runner-up votes were compared between IndiaVotes and the Wikipedia results table in every contested AC; 46 of 50 agree on all four. Unopposed winners and their parties agree in every case.

## Disagreements and what was kept

| AC | field | IndiaVotes | Wikipedia table | tie-break | kept |
|---|---|---|---|---|---|
| 16 Yachuli | winner votes | 8,255 | 8,285 | wikipedia ac article 8,255 | indiavotes |
| 31 Along East | runner-up party | PPA | NPEP | wikipedia ac article PPA | indiavotes |
| 36 Nari-Koyu | runner-up party | ANCHDMCP | IND | wikipedia ac article Arunachal Democratic Party | indiavotes |
| 56 Khonsa West | runner-up votes | 3,289 | 4,289 | wikipedia ac article 3,289 | indiavotes |

Wikipedia's printed margin does not equal its own votes in these ACs (the CSV computes the margin from the votes kept):

- AC 16: printed 228, its votes give 258; IndiaVotes margin 228.
- AC 56: printed 804, its votes give -196; IndiaVotes margin 804.

**Names and party labels.**

- AC 23 Taliha (unopposed): IndiaVotes names the winner Nyato Dukam, both Wikipedia pages Nyato Rigia. The Arunachal Times (arunachaltimes.in/?p=237859, via search) and Organiser report Nyato Dukam among the ten returned unopposed. Kept Nyato Dukam; party BJP in every source.
- AC 36 Nari-Koyu: the runner-up's party is IND in the Wikipedia results table and Arunachal Democratic Party in the AC article; IndiaVotes gives the abbreviation ANCHDMCP. Kept ANCHDMCP (two sources against one); the abbreviation is IndiaVotes', not checked against the Commission's list of parties.

**Reservation.** Kept: the constituency list.

- The Wikipedia results table marks no AC as reserved. The list and IndiaVotes both give ST for 59 ACs and general for 49 Bordumsa-Diyum, which matches the 59 ST seats of the Delimitation Order. Kept as ST/blank accordingly.

**Electors.**

IndiaVotes against report 34, every AC where they differ:

| AC | IndiaVotes | report 34 | Wikipedia infobox | kept |
|---|---|---|---|---|
| 3 Mukto | 7,342 | 8,075 | 7,995 | 8,075 (ls2024 segment) |
| 7 Bomdila | 10,062 | 10,927 | 10,840 | 10,927 (ls2024 segment) |
| 13 Itanagar | 61,256 | 64,035 | 63,995 | 64,035 (ls2024 segment) |
| 15 Sagalee | 12,750 | 14,641 | 14,625 | 14,641 (ls2024 segment) |
| 17 Ziro-Hapoli | 23,349 | 25,637 | - | 25,637 (ls2024 segment) |
| 20 Tali | 13,124 | 14,569 | 14,564 | 14,569 (ls2024 segment) |
| 23 Taliha | 10,377 | 11,457 | 11,397 | 11,457 (ls2024 segment) |
| 43 Roing | 12,238 | 11,844 | 11,815 | 11,844 (ls2024 segment) |
| 45 Hayuliang | 12,275 | 13,191 | 13,160 | 13,191 (ls2024 segment) |
| 46 Chowkham | 14,084 | 14,369 | 14,338 | 14,369 (ls2024 segment) |

- In 47 further ACs the only disagreement is the Wikipedia AC infobox, which is lower than IndiaVotes in 47 of them and higher in 0, while IndiaVotes and report 34 agree; kept IndiaVotes. ACs: 1, 2, 4, 5, 8, 9, 10, 11, 12, 14, 16, 18, 19, 21, 22, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 60.
- In all 50 contested ACs IndiaVotes equals report 34 exactly. In the 10 ACs returned unopposed it does not, by up to 2,779, in both directions. The Assembly and Lok Sabha rolls were the same roll on the same day, so the report 34 figure is kept for those 10 and IndiaVotes' figure is treated as of uncertain vintage. With it the state sums to the Commission's Lok Sabha total exactly; with IndiaVotes' figures it would fall 11,888 short. Not checked against the Assembly report itself. The infobox figures for ACs 51 to 60 are all lower than both and look like an older roll.

## What is missing

- The Commission's own Detailed Results and AC-wise electors files were not read; every row rests on two or more compilations that agree, or on the tie-breaks above.

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

# Goa Legislative Assembly election 2022: results by constituency

File: `goa_2022.csv`, 40 rows, one per AC, ACs 1 to 40. Compiled 2026-10-10.

## The Commission's own pages could not be read

Tried first, all from this sandbox on 2026-10-10:

- results.eci.gov.in: the 2022 and 2024 results pages are gone (`https://results.eci.gov.in/ResultAcGenNov2024/index.htm`, `.../ResultAcGenOct2024/index.htm` and their `candidateswise-*`/`Constituencywise*` pages answer 404; the root redirects to the October 2026 bye-elections).
- www.eci.gov.in statistical reports: every HTML page answers HTTP 406 (WAF). The reports index (`https://www.eci.gov.in/statistical-reports`, read once through Firecrawl) gives Maharashtra 2024 as `https://www.eci.gov.in/statistical-report/ae/2024/8`, Haryana 2024 as `https://www.eci.gov.in/statistical-report/ae/2024/6`, and Punjab, Uttarakhand and Goa 2022 as `https://old.eci.gov.in/files/file/14165-punjab-general-legislative-election-2022/`, `.../14169-uttarakhand-general-legislative-election-2022/`, `.../14168-goa-general-legislative-election-2022/`. The Maharashtra report page, rendered through Firecrawl, lists 10 Detailed Results and 11 AC Wise Number Of Electors as XLSX/PDF but exposes no file address (download is a script action). Guessed file paths under `https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/` on the pattern that serves Rajasthan 2023 (`rajasthan/2023_Including/Detailed_Results.xlsx`, which answered 200 as a control) all answered 406 for these states (`maharashtra/2024/...`, `Maharashtra/2024/...`, `haryana/2024/...`, `punjab/2022/...`, `uttarakhand/2022/...`, `goa/2022/...`, with several file-name variants). old.eci.gov.in and web.archive.org reset the connection. Firecrawl credits are low, so no further renders were attempted.
- No figure in the CSV is from the Commission directly. Replace with the Detailed Results and AC Wise Number Of Electors when they can be fetched.

## Sources used

1. **IndiaVotes** (states 'Election results sourced from the Election Commission of India'), state page https://www.indiavotes.com/vidhan-sabha/goa/2022/ and one page per AC, `https://www.indiavotes.com/vidhan-sabha/goa/2022/<slug>/` (all 40 listed at the end), fetched with curl. Each page gives every candidate's votes and party code, NOTA, 'Voters' (`voters_eligible`) and the AC category (GEN/SC/ST).
2. **Wikipedia, results table** of https://en.wikipedia.org/wiki/2022_Goa_Legislative_Assembly_election (AC number, name with (SC)/(ST), winner, runner-up, parties, votes, margin).
3. **Wikipedia, one article per AC** (all 40 listed at the end): infobox 'Constituency No.' and 'Reservation', and the 2022 election box ('Registered electors', candidate votes, 'Margin of victory'/'Majority', turnout).
4. **CEO Goa**, 'General Elections 2022 to Goa Legislative Assembly - AC wise Voter Turnout', https://ceogoa.nic.in/pdf/ELECTION/Voter%20Turnout%20GE-2022.pdf (male, female, third gender and total electors by AC, total 11,64,224).

## Which source each column came from

- `ac`: Wikipedia results table; agrees with the 'Constituency No.' of the AC's own Wikipedia article in 40 of 40 ACs. IndiaVotes pages carry no AC number; each was matched to its AC by name, or where spellings differ by the winner's votes (listed below).
- `ac_name`: Wikipedia results table spelling, '(SC)'/'(ST)' removed. Not the Commission's spelling.
- `reserved`: majority of the readings of IndiaVotes' category, the Wikipedia results table and the Wikipedia AC article and the Wikipedia candidates table; each disagreement is listed below.
- `electors`: Wikipedia AC article 'Registered electors' for 38 ACs. ACs 23 Marcaim and 39 Sanguem have no Wikipedia figure and take the CEO Goa total, which is general electors only. IndiaVotes 'Voters' equals the CEO Goa total electors (general only: male + female + third gender) in all 40 ACs; Wikipedia is equal or higher by up to 38 in the other 38, consistent with service electors.
- `winner`, `winner_votes`, `runner_up`, `runner_up_votes`, `total_votes`: IndiaVotes. Winner and runner-up are the two highest candidates; NOTA is never among them. `total_votes` is every candidate plus NOTA as IndiaVotes prints them (whether postal votes are inside each candidate's figure is not stated there).
- `winner_party`, `runner_up_party`: IndiaVotes party code, except where it prints an internal placeholder, where Wikipedia's abbreviation is used (listed below). Codes are IndiaVotes', not necessarily the Commission's (e.g. SHSUBT, NCPSP).
- `margin`: winner_votes less runner_up_votes. `unopposed`: no AC was uncontested.

## Checks

- ACs: 40 rows against 40 seats; numbers 1 to 40 each once: True.
- margin = winner_votes - runner_up_votes in 40 of 40 rows; every margin positive: True.
- Sum of electors: 1,164,395. The Commission's state total could not be read. The CEO Goa general-elector total is 1,164,224; the difference (171) is the Wikipedia surplus in 38 ACs.
- Against the Wikipedia results table: winner votes agree in 40/40, runner-up votes in 40/40, margin in 40/40.
- Against the Wikipedia AC articles: margin agrees in 38/40 (2 articles print no margin); total votes (Wikipedia 'Turnout' count) agree in 16/38.
- Winner party agrees with the Wikipedia results table in 40/40 (treating IND/Ind, SHSUBT/SS(UBT), NCPSP/NCP-SP, UKKD/UKD, SAD(S)/SADS as the same party).
- Seats by winner party: BJP 20, INC 11, IND 3, MAG 2, AAP 2, RGP 1, GFP 1.
- Reserved: general 39, SC 1.

## Disagreements between sources, and what was kept

- Votes and margins: none.
- AC 2 Pernem: reserved readings IndiaVotes='', Wikipedia results table='', Wikipedia AC article='SC', Wikipedia candidates table='SC'; kept 'SC'.
- AC 23 Marcaim: no Wikipedia elector figure; electors 28272 from the CEO Goa table, which counts general electors only (no service electors).
- AC 39 Sanguem: no Wikipedia elector figure; electors 26657 from the CEO Goa table, which counts general electors only (no service electors).
- Matching: AC 13 St. Cruz: matched to IndiaVotes Santa Cruz by winner votes, names differ.
- Electors: see the column note above; the per-AC IndiaVotes and Wikipedia figures are both in `goa_2022_electors_compare.csv`.

## Not covered

- Bye-elections held since the general election are not reflected.
- No Commission figure was read; party codes are IndiaVotes', AC names Wikipedia's.

## URLs

- https://www.indiavotes.com/vidhan-sabha/goa/2022/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/mandrem/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/pernem/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/bicholim/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/tivim/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/mapusa/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/siolim/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/saligao/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/calangute/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/porvorim/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/aldona/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/panaji/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/taleigao/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/santa-cruz/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/santo-andre/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/cumbarjua/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/maem/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/sanquelim/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/poriem/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/valpoi/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/priol/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/ponda/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/siroda/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/marcaim/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/mormugao/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/vasco-da-gama/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/dabolim/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/cortalim/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/nuvem/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/curtorim/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/fatorda/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/margao/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/benaulim/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/navelim/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/cuncolim/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/velim/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/quepem/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/curchorem/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/sanvordem/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/sanguem/
- https://www.indiavotes.com/vidhan-sabha/goa/2022/canacona/
- https://en.wikipedia.org/wiki/2022_Goa_Legislative_Assembly_election
- https://en.wikipedia.org/wiki/Mandrem_Assembly_constituency
- https://en.wikipedia.org/wiki/Pernem_Assembly_constituency
- https://en.wikipedia.org/wiki/Bicholim_Assembly_constituency
- https://en.wikipedia.org/wiki/Tivim_Assembly_constituency
- https://en.wikipedia.org/wiki/Mapusa_Assembly_constituency
- https://en.wikipedia.org/wiki/Siolim_Assembly_constituency
- https://en.wikipedia.org/wiki/Saligao_Assembly_constituency
- https://en.wikipedia.org/wiki/Calangute_Assembly_constituency
- https://en.wikipedia.org/wiki/Porvorim_Assembly_constituency
- https://en.wikipedia.org/wiki/Aldona_Assembly_constituency
- https://en.wikipedia.org/wiki/Panaji_Assembly_constituency
- https://en.wikipedia.org/wiki/Taleigao_Assembly_constituency
- https://en.wikipedia.org/wiki/St._Cruz_Assembly_constituency
- https://en.wikipedia.org/wiki/St._Andre_Assembly_constituency
- https://en.wikipedia.org/wiki/Cumbarjua_Assembly_constituency
- https://en.wikipedia.org/wiki/Maem_Assembly_constituency
- https://en.wikipedia.org/wiki/Sanquelim_Assembly_constituency
- https://en.wikipedia.org/wiki/Poriem_Assembly_constituency
- https://en.wikipedia.org/wiki/Valpoi_Assembly_constituency
- https://en.wikipedia.org/wiki/Priol_Assembly_constituency
- https://en.wikipedia.org/wiki/Ponda_Assembly_constituency
- https://en.wikipedia.org/wiki/Siroda_Assembly_constituency
- https://en.wikipedia.org/wiki/Marcaim_Assembly_constituency
- https://en.wikipedia.org/wiki/Mormugao_Assembly_constituency
- https://en.wikipedia.org/wiki/Vasco_Da_Gama_Assembly_constituency
- https://en.wikipedia.org/wiki/Dabolim_Assembly_constituency
- https://en.wikipedia.org/wiki/Cortalim_Assembly_constituency
- https://en.wikipedia.org/wiki/Nuvem_Assembly_constituency
- https://en.wikipedia.org/wiki/Curtorim_Assembly_constituency
- https://en.wikipedia.org/wiki/Fatorda_Assembly_constituency
- https://en.wikipedia.org/wiki/Margao_Assembly_constituency
- https://en.wikipedia.org/wiki/Benaulim_Assembly_constituency
- https://en.wikipedia.org/wiki/Navelim_Assembly_constituency
- https://en.wikipedia.org/wiki/Cuncolim_Assembly_constituency
- https://en.wikipedia.org/wiki/Velim_Assembly_constituency
- https://en.wikipedia.org/wiki/Quepem_Assembly_constituency
- https://en.wikipedia.org/wiki/Curchorem_Assembly_constituency
- https://en.wikipedia.org/wiki/Sanvordem_Assembly_constituency
- https://en.wikipedia.org/wiki/Sanguem_Assembly_constituency
- https://en.wikipedia.org/wiki/Canacona_Assembly_constituency
- https://ceogoa.nic.in/pdf/ELECTION/Voter%20Turnout%20GE-2022.pdf

---

# Haryana Legislative Assembly election 2024: results by constituency

File: `haryana_2024.csv`, 90 rows, one per AC, ACs 1 to 90. Compiled 2026-10-10.

## The Commission's own pages could not be read

Tried first, all from this sandbox on 2026-10-10:

- results.eci.gov.in: the 2022 and 2024 results pages are gone (`https://results.eci.gov.in/ResultAcGenNov2024/index.htm`, `.../ResultAcGenOct2024/index.htm` and their `candidateswise-*`/`Constituencywise*` pages answer 404; the root redirects to the October 2026 bye-elections).
- www.eci.gov.in statistical reports: every HTML page answers HTTP 406 (WAF). The reports index (`https://www.eci.gov.in/statistical-reports`, read once through Firecrawl) gives Maharashtra 2024 as `https://www.eci.gov.in/statistical-report/ae/2024/8`, Haryana 2024 as `https://www.eci.gov.in/statistical-report/ae/2024/6`, and Punjab, Uttarakhand and Goa 2022 as `https://old.eci.gov.in/files/file/14165-punjab-general-legislative-election-2022/`, `.../14169-uttarakhand-general-legislative-election-2022/`, `.../14168-goa-general-legislative-election-2022/`. The Maharashtra report page, rendered through Firecrawl, lists 10 Detailed Results and 11 AC Wise Number Of Electors as XLSX/PDF but exposes no file address (download is a script action). Guessed file paths under `https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/` on the pattern that serves Rajasthan 2023 (`rajasthan/2023_Including/Detailed_Results.xlsx`, which answered 200 as a control) all answered 406 for these states (`maharashtra/2024/...`, `Maharashtra/2024/...`, `haryana/2024/...`, `punjab/2022/...`, `uttarakhand/2022/...`, `goa/2022/...`, with several file-name variants). old.eci.gov.in and web.archive.org reset the connection. Firecrawl credits are low, so no further renders were attempted.
- No figure in the CSV is from the Commission directly. Replace with the Detailed Results and AC Wise Number Of Electors when they can be fetched.

## Sources used

1. **IndiaVotes** (states 'Election results sourced from the Election Commission of India'), state page https://www.indiavotes.com/vidhan-sabha/haryana/2024/ and one page per AC, `https://www.indiavotes.com/vidhan-sabha/haryana/2024/<slug>/` (all 90 listed at the end), fetched with curl. Each page gives every candidate's votes and party code, NOTA, 'Voters' (`voters_eligible`) and the AC category (GEN/SC/ST).
2. **Wikipedia, results table** of https://en.wikipedia.org/wiki/2024_Haryana_Legislative_Assembly_election (AC number, name with (SC)/(ST), winner, runner-up, parties, votes, margin, turnout %).
3. **Wikipedia, one article per AC** (all 90 listed at the end): infobox 'Constituency No.' and 'Reservation', and the 2024 election box ('Registered electors', candidate votes, 'Margin of victory'/'Majority', turnout).

## Which source each column came from

- `ac`: Wikipedia results table; agrees with the 'Constituency No.' of the AC's own Wikipedia article in 90 of 90 ACs. IndiaVotes pages carry no AC number; each was matched to its AC by name, or where spellings differ by the winner's votes (listed below).
- `ac_name`: Wikipedia results table spelling, '(SC)'/'(ST)' removed. Not the Commission's spelling.
- `reserved`: majority of the readings of IndiaVotes' category, the Wikipedia results table and the Wikipedia AC article; each disagreement is listed below.
- `electors`: IndiaVotes 'Voters'. Recomputed turnout (total votes / electors) agrees with the Wikipedia results table's turnout % within rounding in most ACs (see checks). The Wikipedia AC articles print lower figures in every AC (by 266 to 7,903; largest in Badshahpur, Gurgaon, Panipat), which looks like an earlier roll, and were not used.
- `winner`, `winner_votes`, `runner_up`, `runner_up_votes`, `total_votes`: IndiaVotes. Winner and runner-up are the two highest candidates; NOTA is never among them. `total_votes` is every candidate plus NOTA as IndiaVotes prints them (whether postal votes are inside each candidate's figure is not stated there).
- `winner_party`, `runner_up_party`: IndiaVotes party code, except where it prints an internal placeholder, where Wikipedia's abbreviation is used (listed below). Codes are IndiaVotes', not necessarily the Commission's (e.g. SHSUBT, NCPSP).
- `margin`: winner_votes less runner_up_votes. `unopposed`: no AC was uncontested.

## Checks

- ACs: 90 rows against 90 seats; numbers 1 to 90 each once: True.
- margin = winner_votes - runner_up_votes in 90 of 90 rows; every margin positive: True.
- Sum of electors: 20,463,100. The Commission's state total could not be read.
- Against the Wikipedia results table: winner votes agree in 90/90, runner-up votes in 90/90, margin in 90/90.
- Against the Wikipedia AC articles: margin agrees in 89/90; total votes (Wikipedia 'Turnout' count) agree in 83/88.
- Winner party agrees with the Wikipedia results table in 90/90 (treating IND/Ind, SHSUBT/SS(UBT), NCPSP/NCP-SP, UKKD/UKD, SAD(S)/SADS as the same party).
- Seats by winner party: BJP 48, INC 37, IND 3, INLD 2.
- Reserved: general 73, SC 17.
- Turnout recomputed as total_votes / electors agrees with the Wikipedia results table's turnout % within 0.01 point in 86 of 90 ACs. Exceptions (AC, name, Wikipedia %, recomputed %): 54 Loharu 79.73 vs 82.28; 55 Badhra 71.36 vs 67.87; 56 Dadri 67.04 vs 68.3; 76 Badshahpur 54.08 vs 54.1. In 54 Loharu, 55 Badhra and 56 Dadri the recomputed figure differs by 0.5 to 3.5 points, but total votes equal the Wikipedia AC articles' turnout counts and IndiaVotes' electors are within 1,100 of the AC articles' electors, so the results table's turnout % is taken to be the outlier; electors kept from IndiaVotes.

## Disagreements between sources, and what was kept

- AC 44 Rania: margin IndiaVotes 4,191, Wikipedia results table 4,191, Wikipedia AC article 4,673. Kept IndiaVotes, which the results table supports.
- AC 60 Meham: runner_up_party: IndiaVotes prints the placeholder "TSP_ABBR_HJSP_2" with party slug "haryana-jan-sevak-party"; the Wikipedia AC article names the party "Haryana Jansevak Party"; the Wikipedia results table says "Ind". Written as HJSP.
- Matching: AC 31 Sonipat: matched to IndiaVotes Sonepat by winner votes, names differ.
- Matching: AC 42 Kalanwali: matched to IndiaVotes Kalawali (SC) by winner votes, names differ.
- Matching: AC 52 Hisar: matched to IndiaVotes Hissar by winner votes, names differ.
- Matching: AC 88 Ballabgarh: matched to IndiaVotes Ballabhgarh by winner votes, names differ.
- Electors: the Wikipedia AC-article figures differ from IndiaVotes as described above; per-AC values in `haryana_2024_electors_compare.csv`.

## Not covered

- Bye-elections held since the general election are not reflected.
- No Commission figure was read; party codes are IndiaVotes', AC names Wikipedia's.

## URLs

- https://www.indiavotes.com/vidhan-sabha/haryana/2024/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/kalka/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/panchkula/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/naraingarh/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/ambala-cantonment/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/ambala-city/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/mulana/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/sadhaura/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/jagadhri/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/yamunanagar/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/radaur/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/ladwa/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/shahbad/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/thanesar/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/pehowa/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/guhla/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/kalayat/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/kaithal/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/pundri/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/nilokheri/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/indri/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/karnal/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/gharaunda/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/assandh/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/panipat-rural/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/panipat-city/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/israna/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/samalkha/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/ganaur/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/rai/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/kharkhauda/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/sonepat/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/gohana/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/baroda/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/julana/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/safidon/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/jind/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/uchana-kalan/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/narwana/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/tohana/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/fatehabad/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/ratia/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/kalanwali/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/dabwali/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/rania/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/sirsa/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/ellenabad/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/adampur/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/uklana/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/narnaund/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/hansi/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/barwala/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/hissar/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/nalwa/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/loharu/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/badhra/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/dadri/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/bhiwani/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/tosham/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/bawani-khera/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/meham/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/garhi-sampla-kiloi/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/rohtak/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/kalanaur/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/bahadurgarh/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/badli/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/jhajjar/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/beri/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/ateli/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/mahendragarh/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/narnaul/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/nangal-chaudhry/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/bawal/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/kosli/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/rewari/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/pataudi/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/badshahpur/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/gurgaon/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/sohna/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/nuh/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/ferozepur-jhirka/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/punahana/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/hathin/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/hodal/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/palwal/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/prithla/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/faridabad-nit/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/badkhal/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/ballabhgarh/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/faridabad/
- https://www.indiavotes.com/vidhan-sabha/haryana/2024/tigaon/
- https://en.wikipedia.org/wiki/2024_Haryana_Legislative_Assembly_election
- https://en.wikipedia.org/wiki/Kalka_Assembly_constituency
- https://en.wikipedia.org/wiki/Panchkula_Assembly_constituency
- https://en.wikipedia.org/wiki/Naraingarh_Assembly_constituency
- https://en.wikipedia.org/wiki/Ambala_Cantonment_Assembly_constituency
- https://en.wikipedia.org/wiki/Ambala_City_Assembly_constituency
- https://en.wikipedia.org/wiki/Mulana_Assembly_constituency
- https://en.wikipedia.org/wiki/Sadhaura_Assembly_constituency
- https://en.wikipedia.org/wiki/Jagadhri_Assembly_constituency
- https://en.wikipedia.org/wiki/Yamunanagar_Assembly_constituency
- https://en.wikipedia.org/wiki/Radaur_Assembly_constituency
- https://en.wikipedia.org/wiki/Ladwa_Assembly_constituency
- https://en.wikipedia.org/wiki/Shahbad_Assembly_constituency
- https://en.wikipedia.org/wiki/Thanesar_Assembly_constituency
- https://en.wikipedia.org/wiki/Pehowa_Assembly_constituency
- https://en.wikipedia.org/wiki/Guhla_Assembly_constituency
- https://en.wikipedia.org/wiki/Kalayat_Assembly_constituency
- https://en.wikipedia.org/wiki/Kaithal_Assembly_constituency
- https://en.wikipedia.org/wiki/Pundri_Assembly_constituency
- https://en.wikipedia.org/wiki/Nilokheri_Assembly_constituency
- https://en.wikipedia.org/wiki/Indri_Assembly_constituency
- https://en.wikipedia.org/wiki/Karnal_Assembly_constituency
- https://en.wikipedia.org/wiki/Gharaunda_Assembly_constituency
- https://en.wikipedia.org/wiki/Assandh_Assembly_constituency
- https://en.wikipedia.org/wiki/Panipat_Rural_Assembly_constituency
- https://en.wikipedia.org/wiki/Panipat_City_Assembly_constituency
- https://en.wikipedia.org/wiki/Israna_Assembly_constituency
- https://en.wikipedia.org/wiki/Samalkha_Assembly_constituency
- https://en.wikipedia.org/wiki/Ganaur_Assembly_constituency
- https://en.wikipedia.org/wiki/Rai_Assembly_constituency
- https://en.wikipedia.org/wiki/Kharkhauda_Assembly_constituency
- https://en.wikipedia.org/wiki/Sonipat_Assembly_constituency
- https://en.wikipedia.org/wiki/Gohana_Assembly_constituency
- https://en.wikipedia.org/wiki/Baroda_Assembly_constituency
- https://en.wikipedia.org/wiki/Julana_Assembly_constituency
- https://en.wikipedia.org/wiki/Safidon_Assembly_constituency
- https://en.wikipedia.org/wiki/Jind_Assembly_constituency
- https://en.wikipedia.org/wiki/Uchana_Kalan_Assembly_constituency
- https://en.wikipedia.org/wiki/Narwana_Assembly_constituency
- https://en.wikipedia.org/wiki/Tohana_Assembly_constituency
- https://en.wikipedia.org/wiki/Fatehabad_(Haryana_Assembly_constituency)
- https://en.wikipedia.org/wiki/Ratia_Assembly_constituency
- https://en.wikipedia.org/wiki/Kalanwali_Assembly_constituency
- https://en.wikipedia.org/wiki/Dabwali_Assembly_constituency
- https://en.wikipedia.org/wiki/Rania_Assembly_constituency
- https://en.wikipedia.org/wiki/Sirsa_Assembly_constituency
- https://en.wikipedia.org/wiki/Ellenabad_Assembly_constituency
- https://en.wikipedia.org/wiki/Adampur,_Haryana_Assembly_constituency
- https://en.wikipedia.org/wiki/Uklana_Assembly_constituency
- https://en.wikipedia.org/wiki/Narnaund_Assembly_constituency
- https://en.wikipedia.org/wiki/Hansi_Assembly_constituency
- https://en.wikipedia.org/wiki/Barwala_Assembly_constituency
- https://en.wikipedia.org/wiki/Hisar_Assembly_constituency
- https://en.wikipedia.org/wiki/Nalwa_Assembly_constituency
- https://en.wikipedia.org/wiki/Loharu_Assembly_constituency
- https://en.wikipedia.org/wiki/Badhra_Assembly_constituency
- https://en.wikipedia.org/wiki/Dadri_(Haryana_Vidhan_Sabha_constituency)
- https://en.wikipedia.org/wiki/Bhiwani_Assembly_constituency
- https://en.wikipedia.org/wiki/Tosham_Assembly_constituency
- https://en.wikipedia.org/wiki/Bawani_Khera_Assembly_constituency
- https://en.wikipedia.org/wiki/Meham_Assembly_constituency
- https://en.wikipedia.org/wiki/Garhi_Sampla-Kiloi_Assembly_constituency
- https://en.wikipedia.org/wiki/Rohtak_Assembly_constituency
- https://en.wikipedia.org/wiki/Kalanaur_Assembly_constituency
- https://en.wikipedia.org/wiki/Bahadurgarh_Assembly_constituency
- https://en.wikipedia.org/wiki/Badli,_Haryana_Assembly_constituency
- https://en.wikipedia.org/wiki/Jhajjar_Assembly_constituency
- https://en.wikipedia.org/wiki/Beri_Assembly_constituency
- https://en.wikipedia.org/wiki/Ateli_Assembly_constituency
- https://en.wikipedia.org/wiki/Mahendragarh_Assembly_constituency
- https://en.wikipedia.org/wiki/Narnaul_Assembly_constituency
- https://en.wikipedia.org/wiki/Nangal_Chaudhry_Assembly_constituency
- https://en.wikipedia.org/wiki/Bawal_Assembly_constituency
- https://en.wikipedia.org/wiki/Kosli_Assembly_constituency
- https://en.wikipedia.org/wiki/Rewari_Assembly_constituency
- https://en.wikipedia.org/wiki/Pataudi_Assembly_constituency
- https://en.wikipedia.org/wiki/Badshahpur_Assembly_constituency
- https://en.wikipedia.org/wiki/Gurgaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Sohna_Assembly_constituency
- https://en.wikipedia.org/wiki/Nuh_Assembly_constituency
- https://en.wikipedia.org/wiki/Ferozepur_Jhirka_Assembly_constituency
- https://en.wikipedia.org/wiki/Punahana_Assembly_constituency
- https://en.wikipedia.org/wiki/Hathin_Assembly_constituency
- https://en.wikipedia.org/wiki/Hodal_Assembly_constituency
- https://en.wikipedia.org/wiki/Palwal_Assembly_constituency
- https://en.wikipedia.org/wiki/Prithla_Assembly_constituency
- https://en.wikipedia.org/wiki/Faridabad_NIT_Assembly_constituency
- https://en.wikipedia.org/wiki/Badkhal_Assembly_constituency
- https://en.wikipedia.org/wiki/Ballabgarh_Assembly_constituency
- https://en.wikipedia.org/wiki/Faridabad_Assembly_constituency
- https://en.wikipedia.org/wiki/Tigaon_Assembly_constituency

---

# Jharkhand Legislative Assembly election, 2024: results by constituency

File: `jharkhand_2024.csv`, 81 rows, one per assembly constituency (AC), numbered as the Commission numbers them. The general election polled 13 and 20 November 2024; counted 23 November 2024. Retrieved 10 October 2026.

## The Commission's own pages could not be read

- The Commission's statistical report for this election is listed at https://www.eci.gov.in/statistical-report/ae/2024/9 (read through a Firecrawl render for Odisha, which shows 14 report files including "10-Detailed Results" and "11 - AC Wise Number Of Electors"). The files are served only through `https://www.eci.gov.in/eci-backend/public/api/election-result?category_id=N` and the encrypted `api/download` route, and both answered HTTP 406 ("Request was blocked due to suspicious behavior") from this sandbox, with curl and with a Firecrawl scrape. Guessed direct paths under `eci-backend/public/all_files/full-statistical-reports/` also answered 406, which is how that server answers a missing file.
- The results pages on results.eci.gov.in for 2024 (`AcResultGenJune2024`, `ResultAcGenNov2024`) now answer 404. Archived copies exist on the Wayback Machine, but web.archive.org could not be reached from here (connection reset) and WebFetch refuses that host.
- So every figure in the CSV comes from published compilations of the Commission's results, checked against each other. None was read from an ECI page directly, with the exceptions named below.

## Sources and URLs

1. **IndiaVotes** (compilation of ECI results). State page https://www.indiavotes.com/vidhan-sabha/jharkhand/2024/ and one page per AC, https://www.indiavotes.com/vidhan-sabha/jharkhand/2024/<slug>/ (81 pages, read from each page's embedded `iv-page-context` JSON: every candidate with party abbreviation and votes, NOTA, `voters_eligible`, `votes_polled`, `winning_margin`, AC category).
2. **Wikipedia, results by constituency**: https://en.wikipedia.org/wiki/2024_Jharkhand_Legislative_Assembly_election (section "Results by constituency", wikitext via `action=raw`): AC number, AC name, winner, runner-up, their parties and votes, margin.
3. **Wikipedia, list of constituencies**: https://en.wikipedia.org/wiki/List_of_constituencies_of_the_Jharkhand_Legislative_Assembly : AC number and reservation.
4. **Wikipedia AC articles**, one per AC, https://en.wikipedia.org/wiki/<AC>_Assembly_constituency (`action=raw`): the 2024 election box (candidates, votes) and the infobox `electors`, used only to break ties between 1 and 2.

### Which source each column came from

| column | source |
|---|---|
| ac | Wikipedia results table and constituency list (they agree on every number) |
| ac_name | IndiaVotes spelling (closer to the Commission's than Wikipedia's, which uses native spellings such as Padamapur, Baragada); all-capital names put in title case. Not checked against the Commission's own spelling. |
| reserved | Wikipedia list of constituencies, whose counts equal the Delimitation Order's allocation; checked against the results table and IndiaVotes |
| electors | IndiaVotes `voters_eligible` |
| winner, runner_up | IndiaVotes candidate names (ECI-style transliteration) |
| winner_party, runner_up_party | IndiaVotes party abbreviation (ECI style), with `POUI_ABBR_JLKM_01` written as JLKM; checked against Wikipedia |
| winner_votes, runner_up_votes | IndiaVotes, checked against Wikipedia; disagreements decided as listed below |
| margin | computed, winner_votes - runner_up_votes |
| total_votes | computed from IndiaVotes: every candidate's votes plus NOTA (postal included) |
| unopposed | Wikipedia results table ("Elected unopposed") and IndiaVotes (one candidate, 0 votes) |

Runner-up is the second candidate by votes; NOTA is never a candidate in IndiaVotes' list and never a runner-up here.

## Checks

- **ACs**: 81 rows, numbered 1 to 81 once each, against the state's 81 seats. Passed.
- **Electors**: the CSV sums to 26,100,936. No Commission total for this election could be read; press reports of the Commission's figure give only rounded totals (about 2.60 crore), so this check is **not done**.
- **Margin**: margin = winner_votes - runner_up_votes in 81 of 81 contested rows. The margin IndiaVotes prints (`winning_margin`) equals the written margin in 81 of 81.
- **Winner above runner-up**, margin > 0: 81 of 81.
- **total_votes** (candidates plus NOTA) equals IndiaVotes' own `votes_polled` in 0 of 81 contested ACs. It equals the turnout in the AC's Wikipedia election box in 80 of the 80 ACs whose box gives one.
  IndiaVotes' own `votes_polled` for Jharkhand excludes NOTA (it equals the candidates' sum in all 81), unlike the other states, which is why total_votes is computed rather than copied.
- **Second source**: winner party, runner-up party, winner votes and runner-up votes were compared between IndiaVotes and the Wikipedia results table in every contested AC; 78 of 81 agree on all four. Unopposed winners and their parties agree in every case.

## Disagreements and what was kept

| AC | field | IndiaVotes | Wikipedia table | tie-break | kept |
|---|---|---|---|---|---|
| 69 Bishunpur | winner votes | 100,336 | 100,366 | wikipedia ac article 100,336 | indiavotes |
| 72 Lohardaga | runner-up party | AJSUP | BJP | wikipedia ac article AJSUP | indiavotes |
| 74 Latehar | winner votes | 98,062 | 98,063 | wikipedia ac article 98,062 | indiavotes |

Wikipedia's printed margin does not equal its own votes in these ACs (the CSV computes the margin from the votes kept):

- AC 38: printed 3,488, its votes give 3,448; IndiaVotes margin 3,448.
- AC 69: printed 32,756, its votes give 32,786; IndiaVotes margin 32,756.
- AC 74: printed 434, its votes give 435; IndiaVotes margin 434.

**Electors.**

- In 21 ACs the only disagreement is the Wikipedia AC infobox, which is lower than IndiaVotes in 21 of them and higher in 0; kept IndiaVotes. ACs: 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 17, 19, 23, 28, 29, 35, 43, 44, 63.

## What is missing

- The Commission's own Detailed Results and AC-wise electors files were not read; every row rests on two or more compilations that agree, or on the tie-breaks above.
- Electors rest on IndiaVotes alone: report 34 is for the May 2024 Lok Sabha roll, not the November roll, and no Commission total for the Assembly roll was found. The Wikipedia infobox figure agrees in 0 of the 21 ACs that give one.

---

# Karnataka 2023, Assembly results by AC

**This file is not from ECI.** The task was to check the repository's TCPD file (`data/karnataka/raw/results_2023.csv`) against ECI's own 2023 results and write this file from ECI. No ECI figure for Karnataka 2023 could be read from this sandbox, so `karnataka_2023.csv` is the TCPD file reshaped to the brief's columns, checked against two compilations. Do not cite it as ECI until the checks below marked "not done" are done.

## Why ECI could not be read

- results.eci.gov.in/ResultAcGenMay2023/ (statewiseS10*.htm, ConstituencywiseS10<ac>.htm) answers 404.
- ECI's statistical report for Karnataka 2023 is listed only on the old site, https://old.eci.gov.in/files/file/15163-karnataka-2023/ (from the index at https://www.eci.gov.in/statistical-reports). old.eci.gov.in resets the connection to curl and answers 503 to WebFetch. Guessed paths under https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/karnataka/2023/ (the pattern that serves MP, Chhattisgarh and Telangana 2023) answer 406.
- The Wayback Machine holds the ECI results pages (for example https://web.archive.org/web/20241225035256/https://results.eci.gov.in/ResultAcGenMay2023/ConstituencywiseS10224.htm and statewiseS101.htm, S102, S105 to S1012), but web.archive.org is blocked to curl and WebFetch here, and the Firecrawl credits that reach it were used up on Puducherry.

Not done, and needed for an ECI file: winner, party, votes and margin for 224 ACs from ECI (the archived results pages above, or table 2 / table 10 of the statistical report), and electors from table 11, AC Wise Number Of Electors.

## Sources used

- TCPD Lok Dhaba via the repository: /home/user/INDIA-DATA/data/karnataka/raw/results_2023.csv and results_2023_candidates.csv (read only; its SOURCES.md gives the OpenCity download address). Every column comes from it: ac, ac_name (TCPD spelling), reserved (ac_type, GEN left blank), electors, winner, winner_party, winner_votes, runner_up, runner_up_party, runner_up_votes, margin, total_votes (TCPD valid_votes, all candidates and NOTA). Party codes are TCPD's. unopposed blank everywhere.
- IndiaVotes, https://www.indiavotes.com/vidhan-sabha/karnataka/2023/ (state table) and the 224 AC pages https://www.indiavotes.com/vidhan-sabha/karnataka/2023/<slug>/ (Voters, every candidate, NOTA). IndiaVotes says its results are sourced from ECI.
- Wikipedia, "2023 Karnataka Legislative Assembly election", "Results by constituency" (https://en.wikipedia.org/w/index.php?title=2023_Karnataka_Legislative_Assembly_election&action=raw). Its table cites ECI's Detailed Results.

## Checks

- 224 rows against 224 seats, ACs 1 to 224 once each.
- margin = winner_votes - runner_up_votes in all 224; all positive; smallest 16, AC 173.
- Electors sum to 53,768,590 (TCPD). No ECI state total was read to compare.
- total_votes sum to 39,154,967.
- Winners: INC 135, BJP 66, JD(S) 19, IND 2, Kalyana Rajya Pragathi Paksha 1, Sarvodaya Karnataka Paksha 1.

## TCPD against IndiaVotes

- Winner party, winner votes, runner-up party, runner-up votes and margin agree in all 224 ACs.
- total_votes (IndiaVotes' candidates plus NOTA) agree in all 224.
- **Electors disagree in all 224.** IndiaVotes' Voters sum to 53,126,653 against TCPD's 53,768,590. The gap ranges from 13 to 44,833 in absolute size. Neither is an ECI figure read here, so no electors figure has been chosen; the CSV carries TCPD's. Two points against TCPD's electors: the repository already found TCPD's 438,429 for AC 150 Yelahanka and 740,527 for AC 176 Bangalore South against Form 20 headers of 439,024 and 695,797, and IndiaVotes gives 439,005 and 695,694, much closer to Form 20.

## TCPD against Wikipedia

Winner party and runner-up party agree in all 224. Vote disagreements (TCPD's figure kept in each, since IndiaVotes agrees with TCPD in every one; not decided against ECI):

- AC 4 KAGWAD: winner_votes TCPD 83387 vs Wikipedia 83887
- AC 4 KAGWAD: margin TCPD 8827 vs Wikipedia 9327
- AC 7 HUKKERI: runner_up_votes TCPD 61023 vs Wikipedia 42551
- AC 7 HUKKERI: margin TCPD 42551 vs Wikipedia 61023
- AC 20 TERDAL: runner_up_votes TCPD 66520 vs Wikipedia 66529
- AC 31 NAGTHAN: runner_up_votes TCPD 48175 vs Wikipedia 48275
- AC 34 AFZALPUR: winner_votes TCPD 56313 vs Wikipedia 55598
- AC 95 SANDUR: margin TCPD 35522 vs Wikipedia 35532
- AC 108 MAYAKONDA: margin TCPD 33302 vs Wikipedia 33614
- AC 207 SULLIA: runner_up_votes TCPD 63037 vs Wikipedia 53037
- AC 207 SULLIA: margin TCPD 30874 vs Wikipedia 40874
- AC 208 MADIKERI: runner_up_votes TCPD 80477 vs Wikipedia 80466
- AC 208 MADIKERI: margin TCPD 4402 vs Wikipedia 4413
- AC 219 VARUNA: winner_votes TCPD 119816 vs Wikipedia 116856
- AC 219 VARUNA: runner_up_votes TCPD 73653 vs Wikipedia 70811
- AC 219 VARUNA: margin TCPD 46163 vs Wikipedia 46045
- AC 222 KOLLEGAL: margin TCPD 59519 vs Wikipedia 38481

## Electors, every AC (TCPD against IndiaVotes)

ac, ac_name, TCPD electors, IndiaVotes Voters, difference (TCPD less IndiaVotes):

- 1 NIPPANI: 225,798 / 226,653 / -855
- 2 CHIKKODI-SADALGA: 225,647 / 224,684 / +963
- 3 ATHANI: 239,660 / 229,191 / +10,469
- 4 KAGWAD: 196,936 / 195,981 / +955
- 5 KUDACHI: 194,655 / 193,550 / +1,105
- 6 RAYBAG: 214,381 / 211,452 / +2,929
- 7 HUKKERI: 209,095 / 208,196 / +899
- 8 ARABHAVI: 248,114 / 248,624 / -510
- 9 GOKAK: 257,006 / 256,452 / +554
- 10 YEMKANMARDI: 201,679 / 203,074 / -1,395
- 11 BELGAUM UTTAR: 251,097 / 251,567 / -470
- 12 BELGAUM DAKSHIN: 250,726 / 248,615 / +2,111
- 13 BELGAUM RURAL: 258,906 / 259,528 / -622
- 14 KHANAPUR: 212,727 / 214,446 / -1,719
- 15 KITTUR: 196,488 / 195,881 / +607
- 16 BAILHONGAL: 200,362 / 195,826 / +4,536
- 17 SAUNDATTI YELLAMMA: 201,129 / 199,845 / +1,284
- 18 RAMDURG: 204,527 / 203,871 / +656
- 19 MUDHOL: 206,191 / 201,304 / +4,887
- 20 TERDAL: 229,599 / 227,731 / +1,868
- 21 JAMKHANDI: 225,054 / 214,792 / +10,262
- 22 BILGI: 236,940 / 231,578 / +5,362
- 23 BADAMI: 231,559 / 220,420 / +11,139
- 24 BAGALKOT: 246,271 / 245,516 / +755
- 25 HUNGUND: 226,522 / 222,665 / +3,857
- 26 MUDDEBIHAL: 216,298 / 217,260 / -962
- 27 DEVAR HIPPARGI: 220,457 / 219,208 / +1,249
- 28 BASAVANA BAGEVADI: 212,423 / 210,076 / +2,347
- 29 BABALESHWAR: 228,904 / 217,487 / +11,417
- 30 BIJAPUR CITY: 283,019 / 281,633 / +1,386
- 31 NAGTHAN: 270,837 / 269,287 / +1,550
- 32 INDI: 242,699 / 242,891 / -192
- 33 SINDGI: 249,495 / 236,640 / +12,855
- 34 AFZALPUR: 229,228 / 228,150 / +1,078
- 35 JEVARGI: 241,216 / 239,886 / +1,330
- 36 SHORAPUR: 305,191 / 275,462 / +29,729
- 37 SHAHAPUR: 240,707 / 238,963 / +1,744
- 38 YADGIR: 240,201 / 237,418 / +2,783
- 39 GURMITKAL: 250,896 / 248,178 / +2,718
- 40 CHITTAPUR: 238,176 / 235,744 / +2,432
- 41 SEDAM: 228,479 / 225,658 / +2,821
- 42 CHINCHOLI: 205,566 / 203,585 / +1,981
- 43 GULBARGA RURAL: 266,643 / 257,716 / +8,927
- 44 GULBARGA DAKSHIN: 286,014 / 279,195 / +6,819
- 45 GULBARGA UTTAR: 309,474 / 306,993 / +2,481
- 46 ALAND: 268,514 / 241,716 / +26,798
- 47 BASAVAKALYAN: 248,962 / 246,576 / +2,386
- 48 HOMNABAD: 247,039 / 245,982 / +1,057
- 49 BIDAR SOUTH: 207,360 / 205,198 / +2,162
- 50 BIDAR: 228,837 / 228,018 / +819
- 51 BHALKI: 233,536 / 230,956 / +2,580
- 52 AURAD: 221,234 / 219,444 / +1,790
- 53 RAICHUR RURAL: 229,800 / 229,016 / +784
- 54 RAICHUR: 234,755 / 232,643 / +2,112
- 55 MANVI: 234,613 / 233,803 / +810
- 56 DEVADURGA: 236,811 / 233,488 / +3,323
- 57 LINGSUGUR: 258,475 / 255,619 / +2,856
- 58 SINDHANUR: 244,333 / 239,263 / +5,070
- 59 MASKI: 212,033 / 211,176 / +857
- 60 KUSHTAGI: 234,060 / 233,826 / +234
- 61 KANAKAGIRI: 225,454 / 224,059 / +1,395
- 62 GANGAWATI: 205,977 / 202,231 / +3,746
- 63 YELBURGA: 225,274 / 223,203 / +2,071
- 64 KOPPAL: 259,216 / 254,009 / +5,207
- 65 SHIRAHATTI: 231,634 / 226,985 / +4,649
- 66 GADAG: 225,294 / 222,775 / +2,519
- 67 RON: 235,056 / 232,487 / +2,569
- 68 NARGUND: 189,119 / 187,205 / +1,914
- 69 NAVALGUND: 210,305 / 207,230 / +3,075
- 70 KUNDGOL: 187,257 / 186,817 / +440
- 71 DHARWAD: 216,016 / 214,122 / +1,894
- 72 HUBLI-DHARWAD-EAST: 210,270 / 209,516 / +754
- 73 HUBLI-DHARWAD-CENTRAL: 250,080 / 249,332 / +748
- 74 HUBLI-DHARWAD- WEST: 264,486 / 263,226 / +1,260
- 75 KALGHATGI: 198,402 / 194,735 / +3,667
- 76 HALIYAL: 183,112 / 181,517 / +1,595
- 77 KARWAR: 231,983 / 219,544 / +12,439
- 78 KUMTA: 192,671 / 188,891 / +3,780
- 79 BHATKAL: 224,164 / 222,794 / +1,370
- 80 SIRSI: 208,086 / 200,753 / +7,333
- 81 YELLAPUR: 187,641 / 182,472 / +5,169
- 82 HANGAL: 215,549 / 211,923 / +3,626
- 83 SHIGGAON: 228,677 / 226,215 / +2,462
- 84 HAVERI: 236,762 / 233,300 / +3,462
- 85 BYADGI: 210,690 / 208,904 / +1,786
- 86 HIREKERUR: 187,887 / 185,978 / +1,909
- 87 RANIBENNUR: 240,075 / 237,219 / +2,856
- 88 HADAGALLI: 193,967 / 191,324 / +2,643
- 89 HAGARIBOMMANAHALLI: 233,011 / 230,020 / +2,991
- 90 VIJAYANAGARA: 252,389 / 249,879 / +2,510
- 91 KAMPLI: 215,426 / 214,444 / +982
- 92 SIRUGUPPA: 218,263 / 217,171 / +1,092
- 93 BELLARY: 240,068 / 238,312 / +1,756
- 94 BELLARY CITY: 261,510 / 259,191 / +2,319
- 95 SANDUR: 224,255 / 223,311 / +944
- 96 KUDLIGI: 206,102 / 203,788 / +2,314
- 97 MOLAKALMURU: 245,362 / 243,776 / +1,586
- 98 CHALLAKERE: 222,465 / 220,965 / +1,500
- 99 CHITRADURGA: 265,330 / 262,518 / +2,812
- 100 HIRIYUR: 245,962 / 243,604 / +2,358
- 101 HOSADURGA: 200,167 / 197,693 / +2,474
- 102 HOLALKERE: 237,130 / 235,338 / +1,792
- 103 JAGALUR: 195,189 / 193,017 / +2,172
- 104 HARAPANAHALLI: 223,739 / 217,156 / +6,583
- 105 HARIHAR: 209,596 / 207,571 / +2,025
- 106 DAVANAGERE NORTH: 244,739 / 241,240 / +3,499
- 107 DAVANAGERE SOUTH: 211,047 / 210,675 / +372
- 108 MAYAKONDA: 192,195 / 191,415 / +780
- 109 CHANNAGIRI: 201,553 / 199,509 / +2,044
- 110 HONNALI: 202,024 / 199,008 / +3,016
- 111 SHIMOGA RURAL: 217,758 / 212,452 / +5,306
- 112 BHADRAVATI: 218,655 / 212,354 / +6,301
- 113 SHIMOGA: 272,468 / 260,743 / +11,725
- 114 TIRTHAHALLI: 204,754 / 188,267 / +16,487
- 115 SHIKARIPURA: 201,924 / 198,880 / +3,044
- 116 SORAB: 198,447 / 195,339 / +3,108
- 117 SAGAR: 208,472 / 205,260 / +3,212
- 118 BYNDOOR: 238,544 / 235,713 / +2,831
- 119 KUNDAPURA: 212,150 / 209,590 / +2,560
- 120 UDUPI: 218,874 / 216,986 / +1,888
- 121 KAPU: 192,099 / 189,002 / +3,097
- 122 KARKAL: 192,919 / 190,611 / +2,308
- 123 SRINGERI: 174,790 / 170,578 / +4,212
- 124 MUDIGERE: 173,488 / 172,078 / +1,410
- 125 CHIKMAGALUR: 235,524 / 230,717 / +4,807
- 126 TARIKERE: 194,363 / 193,744 / +619
- 127 KADUR: 208,976 / 206,578 / +2,398
- 128 CHIKNAYAKANHALLI: 221,324 / 218,951 / +2,373
- 129 TIPTUR: 186,775 / 184,333 / +2,442
- 130 TURUVEKERE: 189,100 / 182,715 / +6,385
- 131 KUNIGAL: 199,790 / 198,791 / +999
- 132 TUMKUR CITY: 261,986 / 258,899 / +3,087
- 133 TUMKUR RURAL: 210,854 / 208,807 / +2,047
- 134 KORATAGERE: 208,377 / 204,675 / +3,702
- 135 GUBBI: 180,090 / 181,128 / -1,038
- 136 SIRA: 227,573 / 223,635 / +3,938
- 137 PAVAGADA: 191,500 / 193,090 / -1,590
- 138 MADHUGIRI: 194,281 / 193,576 / +705
- 139 GAURIBIDANUR: 209,957 / 210,457 / -500
- 140 BAGEPALLI: 203,059 / 201,026 / +2,033
- 141 CHIKKABALLAPUR: 212,678 / 209,827 / +2,851
- 142 SIDLAGHATTA: 205,305 / 203,553 / +1,752
- 143 CHINTAMANI: 225,547 / 225,418 / +129
- 144 SRINIVASPUR: 217,731 / 216,756 / +975
- 145 MULBAGAL: 218,713 / 216,625 / +2,088
- 146 KOLAR GOLD FIELD: 199,530 / 199,940 / -410
- 147 BANGARAPET: 210,633 / 205,254 / +5,379
- 148 KOLAR: 242,844 / 240,431 / +2,413
- 149 MALUR: 194,710 / 192,710 / +2,000
- 150 YELAHANKA: 438,429 / 439,005 / -576
- 151 K.R.PURA: 511,507 / 510,610 / +897
- 152 BYATARAYANAPURA: 519,919 / 508,676 / +11,243
- 153 YESHVANTHAPURA: 561,958 / 564,125 / -2,167
- 154 RAJARAJESHWARINAGAR: 488,201 / 485,735 / +2,466
- 155 DASARAHALLI: 457,817 / 457,110 / +707
- 156 MAHALAKSHMI LAYOUT: 293,277 / 292,001 / +1,276
- 157 MALLESHWARAM: 229,528 / 227,476 / +2,052
- 158 HEBBAL: 290,758 / 288,918 / +1,840
- 159 PULAKESHINAGAR: 238,856 / 239,052 / -196
- 160 SARVAGNANAGAR: 374,238 / 366,811 / +7,427
- 161 C.V. RAMAN NAGAR: 272,665 / 271,223 / +1,442
- 162 SHIVAJINAGAR: 195,171 / 194,060 / +1,111
- 163 SHANTI NAGAR: 220,817 / 220,830 / -13
- 164 GANDHI NAGAR: 231,510 / 231,424 / +86
- 165 RAJAJI NAGAR: 208,996 / 207,546 / +1,450
- 166 GOVINDRAJ NAGAR: 301,781 / 296,347 / +5,434
- 167 VIJAY NAGAR: 305,452 / 305,685 / -233
- 168 CHAMRAJPET: 232,818 / 229,875 / +2,943
- 169 CHICKPET: 221,773 / 221,197 / +576
- 170 BASAVANAGUDI: 234,913 / 233,598 / +1,315
- 171 PADMANABA NAGAR: 283,270 / 278,938 / +4,332
- 172 B.T.M LAYOUT: 275,139 / 275,022 / +117
- 173 JAYANAGAR: 208,178 / 210,064 / -1,886
- 174 MAHADEVAPURA: 607,951 / 607,135 / +816
- 175 BOMMANAHALLI: 434,418 / 452,738 / -18,320
- 176 BANGALORE SOUTH: 740,527 / 695,694 / +44,833
- 177 ANEKAL: 406,956 / 402,534 / +4,422
- 178 HOSAKOTE: 235,309 / 234,076 / +1,233
- 179 DEVANAHALLI: 225,711 / 212,190 / +13,521
- 180 DODDABALLAPUR: 215,817 / 214,238 / +1,579
- 181 NELAMANGALA: 218,838 / 217,368 / +1,470
- 182 MAGADI: 234,983 / 233,409 / +1,574
- 183 RAMANAGARAM: 217,819 / 216,067 / +1,752
- 184 KANAKAPURA: 225,536 / 224,982 / +554
- 185 CHANNAPATNA: 232,073 / 230,371 / +1,702
- 186 MALAVALLI: 252,755 / 248,554 / +4,201
- 187 MADDUR: 212,997 / 213,834 / -837
- 188 MELUKOTE: 202,225 / 200,177 / +2,048
- 189 MANDYA: 226,272 / 224,337 / +1,935
- 190 SHRIRANGAPATTANA: 214,668 / 213,205 / +1,463
- 191 NAGAMANGALA: 215,894 / 214,260 / +1,634
- 192 KRISHNARAJPET: 224,314 / 219,972 / +4,342
- 193 SHRAVANABELAGOLA: 207,573 / 205,239 / +2,334
- 194 ARSIKERE: 219,031 / 216,199 / +2,832
- 195 BELUR: 200,197 / 197,836 / +2,361
- 196 HASSAN: 232,483 / 228,423 / +4,060
- 197 HOLENARASIPUR: 221,929 / 220,501 / +1,428
- 198 ARKALGUD: 229,870 / 227,981 / +1,889
- 199 SAKLESHPUR: 207,837 / 205,871 / +1,966
- 200 BELTHANGADY: 233,920 / 228,940 / +4,980
- 201 MOODABIDRI: 208,542 / 205,094 / +3,448
- 202 MANGALORE CITY NORTH: 252,161 / 249,451 / +2,710
- 203 MANGALORE CITY SOUTH: 248,760 / 245,758 / +3,002
- 204 MANGALORE: 206,184 / 205,140 / +1,044
- 205 BANTVAL: 231,473 / 228,411 / +3,062
- 206 PUTTUR: 215,899 / 212,845 / +3,054
- 207 SULLIA: 208,680 / 206,208 / +2,472
- 208 MADIKERI: 235,331 / 232,789 / +2,542
- 209 VIRAJPET: 226,513 / 224,923 / +1,590
- 210 PERIYAPATNA: 195,694 / 195,624 / +70
- 211 KRISHNARAJANAGARA: 221,905 / 218,031 / +3,874
- 212 HUNSUR: 244,579 / 241,640 / +2,939
- 213 HEGGADADEVANKOTE: 228,392 / 225,845 / +2,547
- 214 NANJANGUD: 218,004 / 220,414 / -2,410
- 215 CHAMUNDESHWARI: 332,729 / 329,188 / +3,541
- 216 KRISHNARAJA: 253,323 / 250,406 / +2,917
- 217 CHAMARAJA: 246,425 / 246,266 / +159
- 218 NARASIMHARAJA: 291,521 / 288,726 / +2,795
- 219 VARUNA: 236,259 / 234,520 / +1,739
- 220 T.NARASIPUR: 205,987 / 204,850 / +1,137
- 221 HANUR: 225,401 / 221,614 / +3,787
- 222 KOLLEGAL: 217,162 / 216,624 / +538
- 223 CHAMARAJANAGAR: 209,766 / 209,506 / +260
- 224 GUNDLUPET: 216,484 / 213,869 / +2,615

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

# Maharashtra Legislative Assembly election 2024: results by constituency

File: `maharashtra_2024.csv`, 288 rows, one per AC, ACs 1 to 288. Compiled 2026-10-10.

## The Commission's own pages could not be read

Tried first, all from this sandbox on 2026-10-10:

- results.eci.gov.in: the 2022 and 2024 results pages are gone (`https://results.eci.gov.in/ResultAcGenNov2024/index.htm`, `.../ResultAcGenOct2024/index.htm` and their `candidateswise-*`/`Constituencywise*` pages answer 404; the root redirects to the October 2026 bye-elections).
- www.eci.gov.in statistical reports: every HTML page answers HTTP 406 (WAF). The reports index (`https://www.eci.gov.in/statistical-reports`, read once through Firecrawl) gives Maharashtra 2024 as `https://www.eci.gov.in/statistical-report/ae/2024/8`, Haryana 2024 as `https://www.eci.gov.in/statistical-report/ae/2024/6`, and Punjab, Uttarakhand and Goa 2022 as `https://old.eci.gov.in/files/file/14165-punjab-general-legislative-election-2022/`, `.../14169-uttarakhand-general-legislative-election-2022/`, `.../14168-goa-general-legislative-election-2022/`. The Maharashtra report page, rendered through Firecrawl, lists 10 Detailed Results and 11 AC Wise Number Of Electors as XLSX/PDF but exposes no file address (download is a script action). Guessed file paths under `https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/` on the pattern that serves Rajasthan 2023 (`rajasthan/2023_Including/Detailed_Results.xlsx`, which answered 200 as a control) all answered 406 for these states (`maharashtra/2024/...`, `Maharashtra/2024/...`, `haryana/2024/...`, `punjab/2022/...`, `uttarakhand/2022/...`, `goa/2022/...`, with several file-name variants). old.eci.gov.in and web.archive.org reset the connection. Firecrawl credits are low, so no further renders were attempted.
- No figure in the CSV is from the Commission directly. Replace with the Detailed Results and AC Wise Number Of Electors when they can be fetched.

## Sources used

1. **IndiaVotes** (states 'Election results sourced from the Election Commission of India'), state page https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ and one page per AC, `https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/<slug>/` (all 288 listed at the end), fetched with curl. Each page gives every candidate's votes and party code, NOTA, 'Voters' (`voters_eligible`) and the AC category (GEN/SC/ST).
2. **Wikipedia, results table** of https://en.wikipedia.org/wiki/2024_Maharashtra_Legislative_Assembly_election (AC number, name with (SC)/(ST), winner, runner-up, parties, votes, margin).
3. **Wikipedia, one article per AC** (all 288 listed at the end): infobox 'Constituency No.' and 'Reservation', and the 2024 election box ('Registered electors', candidate votes, 'Margin of victory'/'Majority', turnout).

## Which source each column came from

- `ac`: Wikipedia results table; agrees with the 'Constituency No.' of the AC's own Wikipedia article in 287 of 288 ACs (the rest print no number). IndiaVotes pages carry no AC number; each was matched to its AC by name, or where spellings differ by the winner's votes (listed below).
- `ac_name`: Wikipedia results table spelling, '(SC)'/'(ST)' removed. Not the Commission's spelling.
- `reserved`: majority of the readings of IndiaVotes' category, the Wikipedia results table and the Wikipedia AC article; each disagreement is listed below.
- `electors`: Wikipedia AC article 'Registered electors'. IndiaVotes 'Voters' is lower in all 288 ACs, by 4 to 3,332 (116,170 in all), and the gap is largest in Koregaon, Karad North, Man, Chandgad and Kagal and smallest in Mumbai, which is the pattern of service electors: IndiaVotes appears to give general electors only, so the Wikipedia figure was kept as the one matching 'general plus service'. This reading is inferred, not printed by either source.
- `winner`, `winner_votes`, `runner_up`, `runner_up_votes`, `total_votes`: IndiaVotes. Winner and runner-up are the two highest candidates; NOTA is never among them. `total_votes` is every candidate plus NOTA as IndiaVotes prints them (whether postal votes are inside each candidate's figure is not stated there).
- `winner_party`, `runner_up_party`: IndiaVotes party code, except where it prints an internal placeholder, where Wikipedia's abbreviation is used (listed below). Codes are IndiaVotes', not necessarily the Commission's (e.g. SHSUBT, NCPSP).
- `margin`: winner_votes less runner_up_votes. `unopposed`: no AC was uncontested.

## Checks

- ACs: 288 rows against 288 seats; numbers 1 to 288 each once: True.
- margin = winner_votes - runner_up_votes in 288 of 288 rows; every margin positive: True.
- Sum of electors: 97,141,289. The Commission's state total could not be read. IndiaVotes general electors sum to 97,025,119.
- Against the Wikipedia results table: winner votes agree in 286/288, runner-up votes in 286/288, margin in 287/288.
- Against the Wikipedia AC articles: margin agrees in 288/288; total votes (Wikipedia 'Turnout' count) agree in 286/288.
- Winner party agrees with the Wikipedia results table in 288/288 (treating IND/Ind, SHSUBT/SS(UBT), NCPSP/NCP-SP, UKKD/UKD, SAD(S)/SADS as the same party).
- Seats by winner party: BJP 132, SHS 57, NCP 41, SHSUBT 20, INC 16, NCPSP 10, SP 2, IND 2, JSS 2, RVSP 1, RSPS 1, AIMIM 1, CPI(M) 1, PWPI 1, RSVA 1.
- Reserved: general 234, SC 29, ST 25.

## Disagreements between sources, and what was kept

- AC 20 Muktainagar: margin IndiaVotes 23,904, Wikipedia results table 26,885, Wikipedia AC article margin 23,904. Kept IndiaVotes (23,904): the Wikipedia table's own winner and runner-up votes give a margin of 23,904, and the AC article's margin agrees with IndiaVotes.
- AC 38 Amravati: winner_votes IndiaVotes 60,087, Wikipedia results table 58,804. Kept IndiaVotes (60,087): the Wikipedia table's own winner and runner-up votes give a margin of 5,711, and the AC article's margin agrees with IndiaVotes.
- AC 38 Amravati: runner_up_votes IndiaVotes 54,674, Wikipedia results table 53,093. Kept IndiaVotes (54,674): the Wikipedia table's own winner and runner-up votes give a margin of 5,711, and the AC article's margin agrees with IndiaVotes.
- AC 283 Islampur: winner_votes IndiaVotes 109,879, Wikipedia results table 130,738. Kept IndiaVotes (109,879): the Wikipedia table's own winner and runner-up votes give a margin of 22,689, and the AC article's margin agrees with IndiaVotes.
- AC 283 Islampur: runner_up_votes IndiaVotes 96,852, Wikipedia results table 108,049. Kept IndiaVotes (96,852): the Wikipedia table's own winner and runner-up votes give a margin of 22,689, and the AC article's margin agrees with IndiaVotes.
- AC 7 Dhule City: runner_up_party: IndiaVotes prints the internal code 'PARTY-UNKNOWN-1920'; written as Wikipedia's 'AIMIM'.
- AC 12 Bhusawal: reserved readings IndiaVotes='', Wikipedia results table='SC', Wikipedia AC article='SC'; kept 'SC'.
- AC 37 Badnera: winner_party: IndiaVotes prints the internal code 'POUI_ABBR_RYSP_01'; written as Wikipedia's 'RVSP'.
- AC 40 Daryapur: runner_up_party: IndiaVotes prints the internal code 'POUI_ABBR_RYSP_01'; written as Wikipedia's 'RVSP'.
- AC 107 Aurangabad Central: runner_up_party: IndiaVotes prints the internal code 'PARTY-UNKNOWN-1920'; written as Wikipedia's 'AIMIM'.
- AC 109 Aurangabad East: runner_up_party: IndiaVotes prints the internal code 'PARTY-UNKNOWN-1920'; written as Wikipedia's 'AIMIM'.
- AC 114 Malegaon Central: winner_party: IndiaVotes prints the internal code 'PARTY-UNKNOWN-1920'; written as Wikipedia's 'AIMIM'.
- AC 114 Malegaon Central: runner_up_party: IndiaVotes prints the internal code 'POUI_ABBR_ISLAM_01'; written as Wikipedia's 'ISLAM'.
- AC 171 Mankhurd Shivaji Nagar: runner_up_party: IndiaVotes prints the internal code 'PARTY-UNKNOWN-1920'; written as Wikipedia's 'AIMIM'.
- AC 212 Parvati: reserved readings IndiaVotes='SC', Wikipedia results table='', Wikipedia AC article='None'; kept ''.
- AC 214 Pune Cantonment: reserved readings IndiaVotes='', Wikipedia results table='SC', Wikipedia AC article='SC'; kept 'SC'.
- AC 249 Solapur City Central: runner_up_party: IndiaVotes prints the internal code 'PARTY-UNKNOWN-1920'; written as Wikipedia's 'AIMIM'.
- AC 280 Shirol: winner_party: IndiaVotes prints the internal code 'POUI_ABBR_RSVA_18'; written as Wikipedia's 'RSVA'.
- Matching: AC 4 Navapur: matched to IndiaVotes Nawapur by winner votes, names differ.
- Matching: AC 23 Chikhali: matched to IndiaVotes Chikhli by winner votes, names differ.
- Matching: AC 73 Bramhapuri: matched to IndiaVotes Brahmapuri by winner votes, names differ.
- Matching: AC 118 Chandwad: matched to IndiaVotes Chandvad by winner votes, names differ.
- Matching: AC 202 Purandar: matched to IndiaVotes Purandhar by winner votes, names differ.
- Matching: AC 236 Ahmedpur: matched to IndiaVotes Ahmadpur by winner votes, names differ.
- Matching: AC 253 Sangola: matched to IndiaVotes Sangole by winner votes, names differ.
- Matching: AC 287 Tasgaon: matched to IndiaVotes Tasgaon - Kavathe Mahankal by winner votes, names differ.
- Party labels that differ only in abbreviation (IndiaVotes kept): AC 42 runner_up_party PJP / Wikipedia PHJSP; AC 118 runner_up_party PJP / Wikipedia PHJSP.
- Electors: see the column note above; the per-AC IndiaVotes and Wikipedia figures are both in `maharashtra_2024_electors_compare.csv`.

## Not covered

- Bye-elections held since the general election are not reflected.
- No Commission figure was read; party codes are IndiaVotes', AC names Wikipedia's.

## URLs

- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/akkalkuwa/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/shahada/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nandurbar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nawapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/sakri/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/dhule-rural/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/dhule-city/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/sindkheda-sindkheda-sinkheda/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/shirpur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/chopda/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/raver/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/bhusawal/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/jalgaon-city/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/jalgaon-rural/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/amalner/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/erandol/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/chalisgaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/pachora/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/jamner/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/muktainagar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/malkapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/buadhana-buldhana-buldhana/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/chikhli/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/sindkhed-raja/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/mehkar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/khamgaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/jalgaon-jamod/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/akot/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/balapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/akola-west/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/akola-east/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/murtijapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/risod/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/washim/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/karanja/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/dhamamgaon-railway/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/badnera/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/amravati/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/teosa/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/daryapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/melghat/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/achalpur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/morhsi-morshi-morshi/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/arvi/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/deoli/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/hinganghat/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/wardha/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/katol/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/saoner-savner-savner/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/hingna/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/umred/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nagpur-south-west/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nagpur-south/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nagpur-east/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nagpur-central/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nagpur-west/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nagpur-north/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kamthi/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ramtek/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/tumsar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/bhandara/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/sakoli/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/arjuni-morgaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/tirora/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/gondiya/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/amgaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/armori/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/gadchiroli/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/aheri/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/rajura/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/chandrapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ballarpur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/brahmapuri/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/chimur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/warora/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/wani/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ralegaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/yavatmal-yavatmal-yeotmal/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/digras/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/arni/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/pusad/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/umarkhed/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kinwat/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/hadgaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/bhokar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nanded-north/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nanded-south/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/loha/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/naigaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/deglur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/mukhed/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/basmath/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kalamnuri/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/hingoli/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/jintur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/parbhani/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/gangakhed/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/pathri/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/partur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ghansawangi/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/jalna/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/badnapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/bhokardan/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/sillod/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kannad/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/phulambri/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/aurangabad-central/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/aurangabad-west/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/aurangabad-east/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/paithan/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/gangapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/vaijapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nandgaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/malegaon-central/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/malegaon-outer/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/baglan/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kalwan/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/chandvad/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/yeola-yevla-yevla/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/sinnar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/niphad/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/dindori/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nashik-east/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nashik-central/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nashik-west/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/deolali-deolali-devlali/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/igatpuri/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/dahanu/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/vikramgad/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/palghar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/boisar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nalasopara/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/vasai/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/bhiwandi-rural/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/shahapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/bhiwandi-west/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/bhiwandi-east/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kalyan-west/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/murbad/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ambernath/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ulhas-nagar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kalyan-east/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/dombivali/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kalyan-rural/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/mira-bhayandar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ovala-majiwada/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kopri-pachpakhadi/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/thane/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/mumbra-kalwa/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/airoli/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/belapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/borivali/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/dahisar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/magathane/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/mulund/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/vikhroli/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/bhandup-west/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/jogeshwari-east/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/dindoshi/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kandivali-east/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/charkop/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/malad-west/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/goregaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/versova/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/andheri-west/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/andheri-east/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/vile-parle/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/chandivali/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ghatkopar-west/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ghatkopar-east/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/mankhurd-shivaji-nagar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/anushakti-nagar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/chembur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kurla/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kalina/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/vandre-east/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/vandre-west/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/dharavi/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/sion-koliwada/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/wadala/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/mahim/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/worli/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/shivadi/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/byculla/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/malabar-hill/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/mubadevi-mumbadevi-mumbadevi/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/colaba/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/panvel/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/karjat/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/uran/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/pen/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/alibag/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/shrivardhan/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/mahad/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/junnar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ambegaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/khed-alandi/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/shirur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/daund/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/indapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/baramati/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/purandhar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/bhor/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/maval-maval-mawal/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/chinchwad/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/pimpri/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/bhosari/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/vadgaol-sheri/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/shivajinagar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kothrud/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/khadakwasala/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/parvati-parvati-parwati/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/hadapsar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/puna-cantonment-pune-cantonment-pune-cantonment/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kasba-peth/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/akole/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/sangamner/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/shirdi/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kopargaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/shrirampur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nevasa/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/shevgaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/rahuri/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/parner/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ahmednagar-city/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/shrigonda/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/karjat-jamkhed/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/georai/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/majalgaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/beed/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ashti/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kaij/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/parli/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/latur-rural/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/latur-city/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ahmadpur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/udgir/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/nilanga/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/auea-ausa-ausa/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/umarga/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/tuljapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/osmanabad-osmanabad-osmanadbad/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/paranda/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/karmala/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/madha/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/barshi/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/mohol/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/solapur-city-north/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/solapur-city-central/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/akkalkot/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/solapur-south/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/pandharpur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/sangole/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/malshiras/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/phaltan/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/wai/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/koregaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/man/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/karad-north/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/karad-south/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/patan/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/satara/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/dapoli-dapoli-depoli/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/guhagar/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/chiplum-chiplun-chiplun/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ratnagiri/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/rajapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kankavli/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kudal/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/sawantwadi/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/chandgad/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/radhanagari/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kagal/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kolhapur-south/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/karvir/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/kolhapur-north/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/shahuwadi/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/hatkanangle/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/ichalkaranji/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/shirol/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/miraj/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/sangli/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/islampur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/shirala/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/palus-kadegaon/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/khanapur/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/tasgaon-kavathe-mahankal/
- https://www.indiavotes.com/vidhan-sabha/maharashtra/2024/jat/
- https://en.wikipedia.org/wiki/2024_Maharashtra_Legislative_Assembly_election
- https://en.wikipedia.org/wiki/Akkalkuwa_Assembly_constituency
- https://en.wikipedia.org/wiki/Shahada_Assembly_constituency
- https://en.wikipedia.org/wiki/Nandurbar_Assembly_constituency
- https://en.wikipedia.org/wiki/Navapur_Assembly_constituency
- https://en.wikipedia.org/wiki/Sakri_Assembly_constituency
- https://en.wikipedia.org/wiki/Dhule_Rural_Assembly_constituency
- https://en.wikipedia.org/wiki/Dhule_City_Assembly_constituency
- https://en.wikipedia.org/wiki/Sindkheda_Assembly_constituency
- https://en.wikipedia.org/wiki/Shirpur_Assembly_constituency
- https://en.wikipedia.org/wiki/Chopda_Assembly_constituency
- https://en.wikipedia.org/wiki/Raver_Assembly_constituency
- https://en.wikipedia.org/wiki/Bhusawal_Assembly_constituency
- https://en.wikipedia.org/wiki/Jalgaon_City_Assembly_constituency
- https://en.wikipedia.org/wiki/Jalgaon_Rural_Assembly_constituency
- https://en.wikipedia.org/wiki/Amalner_Assembly_constituency
- https://en.wikipedia.org/wiki/Erandol_Assembly_constituency
- https://en.wikipedia.org/wiki/Chalisgaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Pachora_Assembly_constituency
- https://en.wikipedia.org/wiki/Jamner_Assembly_constituency
- https://en.wikipedia.org/wiki/Muktainagar_Assembly_constituency
- https://en.wikipedia.org/wiki/Malkapur_Assembly_constituency
- https://en.wikipedia.org/wiki/Buldhana_Assembly_constituency
- https://en.wikipedia.org/wiki/Chikhali_Assembly_constituency
- https://en.wikipedia.org/wiki/Sindkhed_Raja_Assembly_constituency
- https://en.wikipedia.org/wiki/Mehkar_Assembly_constituency
- https://en.wikipedia.org/wiki/Khamgaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Jalgaon_(Jamod)_Assembly_constituency
- https://en.wikipedia.org/wiki/Akot_Assembly_constituency
- https://en.wikipedia.org/wiki/Balapur_Assembly_constituency
- https://en.wikipedia.org/wiki/Akola_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Akola_East_Assembly_constituency
- https://en.wikipedia.org/wiki/Murtizapur_Assembly_constituency
- https://en.wikipedia.org/wiki/Risod_Assembly_constituency
- https://en.wikipedia.org/wiki/Washim_Assembly_constituency
- https://en.wikipedia.org/wiki/Karanja_Assembly_constituency
- https://en.wikipedia.org/wiki/Dhamangaon_Railway_Assembly_constituency
- https://en.wikipedia.org/wiki/Badnera_Assembly_constituency
- https://en.wikipedia.org/wiki/Amravati_Assembly_constituency
- https://en.wikipedia.org/wiki/Teosa_Assembly_constituency
- https://en.wikipedia.org/wiki/Daryapur_Assembly_constituency
- https://en.wikipedia.org/wiki/Melghat_Assembly_constituency
- https://en.wikipedia.org/wiki/Achalpur_Assembly_constituency
- https://en.wikipedia.org/wiki/Morshi_Assembly_constituency
- https://en.wikipedia.org/wiki/Arvi_Assembly_constituency
- https://en.wikipedia.org/wiki/Deoli,_Maharashtra_Assembly_constituency
- https://en.wikipedia.org/wiki/Hinganghat_Assembly_constituency
- https://en.wikipedia.org/wiki/Wardha_Assembly_constituency
- https://en.wikipedia.org/wiki/Katol_Assembly_constituency
- https://en.wikipedia.org/wiki/Savner_Assembly_constituency
- https://en.wikipedia.org/wiki/Hingna_Assembly_constituency
- https://en.wikipedia.org/wiki/Umred_Assembly_constituency
- https://en.wikipedia.org/wiki/Nagpur_South_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Nagpur_South_Assembly_constituency
- https://en.wikipedia.org/wiki/Nagpur_East_Assembly_constituency
- https://en.wikipedia.org/wiki/Nagpur_Central_Assembly_constituency
- https://en.wikipedia.org/wiki/Nagpur_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Nagpur_North_Assembly_constituency
- https://en.wikipedia.org/wiki/Kamthi_Assembly_constituency
- https://en.wikipedia.org/wiki/Ramtek_Assembly_constituency
- https://en.wikipedia.org/wiki/Tumsar_Assembly_constituency
- https://en.wikipedia.org/wiki/Bhandara_Assembly_constituency
- https://en.wikipedia.org/wiki/Sakoli_Assembly_constituency
- https://en.wikipedia.org/wiki/Arjuni-Morgaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Tirora_Assembly_constituency
- https://en.wikipedia.org/wiki/Gondiya_Assembly_constituency
- https://en.wikipedia.org/wiki/Amgaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Armori_Assembly_constituency
- https://en.wikipedia.org/wiki/Gadchiroli_Assembly_constituency
- https://en.wikipedia.org/wiki/Aheri_Assembly_constituency
- https://en.wikipedia.org/wiki/Rajura_Assembly_constituency
- https://en.wikipedia.org/wiki/Chandrapur,_Maharashtra_Assembly_constituency
- https://en.wikipedia.org/wiki/Ballarpur_Assembly_constituency
- https://en.wikipedia.org/wiki/Bramhapuri_Assembly_constituency
- https://en.wikipedia.org/wiki/Chimur_Assembly_constituency
- https://en.wikipedia.org/wiki/Warora_Assembly_constituency
- https://en.wikipedia.org/wiki/Wani_Assembly_constituency
- https://en.wikipedia.org/wiki/Ralegaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Yavatmal_Assembly_constituency
- https://en.wikipedia.org/wiki/Digras_Assembly_constituency
- https://en.wikipedia.org/wiki/Arni_Assembly_constituency
- https://en.wikipedia.org/wiki/Pusad_Assembly_constituency
- https://en.wikipedia.org/wiki/Umarkhed_Assembly_constituency
- https://en.wikipedia.org/wiki/Kinwat_Assembly_constituency
- https://en.wikipedia.org/wiki/Hadgaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Bhokar_Assembly_constituency
- https://en.wikipedia.org/wiki/Nanded_North_Assembly_constituency
- https://en.wikipedia.org/wiki/Nanded_South_Assembly_constituency
- https://en.wikipedia.org/wiki/Loha_Assembly_constituency
- https://en.wikipedia.org/wiki/Naigaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Deglur_Assembly_constituency
- https://en.wikipedia.org/wiki/Mukhed_Assembly_constituency
- https://en.wikipedia.org/wiki/Basmath_Assembly_constituency
- https://en.wikipedia.org/wiki/Kalamnuri_Assembly_constituency
- https://en.wikipedia.org/wiki/Hingoli_Assembly_constituency
- https://en.wikipedia.org/wiki/Jintur_Assembly_constituency
- https://en.wikipedia.org/wiki/Parbhani_Assembly_constituency
- https://en.wikipedia.org/wiki/Gangakhed_Assembly_constituency
- https://en.wikipedia.org/wiki/Pathri_Assembly_constituency
- https://en.wikipedia.org/wiki/Partur_Assembly_constituency
- https://en.wikipedia.org/wiki/Ghansawangi_Assembly_constituency
- https://en.wikipedia.org/wiki/Jalna_Assembly_constituency
- https://en.wikipedia.org/wiki/Badnapur_Assembly_constituency
- https://en.wikipedia.org/wiki/Bhokardan_Assembly_constituency
- https://en.wikipedia.org/wiki/Sillod_Assembly_constituency
- https://en.wikipedia.org/wiki/Kannad_Assembly_constituency
- https://en.wikipedia.org/wiki/Phulambri_Assembly_constituency
- https://en.wikipedia.org/wiki/Aurangabad_Central_Assembly_constituency
- https://en.wikipedia.org/wiki/Aurangabad_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Aurangabad_East_Assembly_constituency
- https://en.wikipedia.org/wiki/Paithan_Assembly_constituency
- https://en.wikipedia.org/wiki/Gangapur,_Maharashtra_Assembly_constituency
- https://en.wikipedia.org/wiki/Vaijapur_Assembly_constituency
- https://en.wikipedia.org/wiki/Nandgaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Malegaon_Central_Assembly_constituency
- https://en.wikipedia.org/wiki/Malegaon_Outer_Assembly_constituency
- https://en.wikipedia.org/wiki/Baglan_Assembly_constituency
- https://en.wikipedia.org/wiki/Kalwan_Assembly_constituency
- https://en.wikipedia.org/wiki/Chandwad_Assembly_constituency
- https://en.wikipedia.org/wiki/Yevla_Assembly_constituency
- https://en.wikipedia.org/wiki/Sinnar_Assembly_constituency
- https://en.wikipedia.org/wiki/Niphad_Assembly_constituency
- https://en.wikipedia.org/wiki/Dindori,_Maharashtra_Assembly_constituency
- https://en.wikipedia.org/wiki/Nashik_East_Assembly_constituency
- https://en.wikipedia.org/wiki/Nashik_Central_Assembly_constituency
- https://en.wikipedia.org/wiki/Nashik_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Deolali_Assembly_constituency
- https://en.wikipedia.org/wiki/Igatpuri_Assembly_constituency
- https://en.wikipedia.org/wiki/Dahanu_Assembly_constituency
- https://en.wikipedia.org/wiki/Vikramgad_Assembly_constituency
- https://en.wikipedia.org/wiki/Palghar_Assembly_constituency
- https://en.wikipedia.org/wiki/Boisar_Assembly_constituency
- https://en.wikipedia.org/wiki/Nalasopara_Assembly_constituency
- https://en.wikipedia.org/wiki/Vasai_(Vidhan_Sabha)_Constituency
- https://en.wikipedia.org/wiki/Bhiwandi_Rural_Assembly_constituency
- https://en.wikipedia.org/wiki/Shahapur,_Maharashtra_Assembly_constituency
- https://en.wikipedia.org/wiki/Bhiwandi_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Bhiwandi_East_Assembly_constituency
- https://en.wikipedia.org/wiki/Kalyan_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Murbad_Assembly_constituency
- https://en.wikipedia.org/wiki/Ambernath_Assembly_constituency
- https://en.wikipedia.org/wiki/Ulhasnagar_Assembly_constituency
- https://en.wikipedia.org/wiki/Kalyan_East_Assembly_constituency
- https://en.wikipedia.org/wiki/Dombivali_Assembly_constituency
- https://en.wikipedia.org/wiki/Kalyan_Rural_Assembly_constituency
- https://en.wikipedia.org/wiki/Mira_Bhayandar_Assembly_constituency
- https://en.wikipedia.org/wiki/Ovala-Majiwada_Assembly_constituency
- https://en.wikipedia.org/wiki/Kopri-Pachpakhadi_Assembly_constituency
- https://en.wikipedia.org/wiki/Thane_Assembly_constituency
- https://en.wikipedia.org/wiki/Mumbra-Kalwa_Assembly_constituency
- https://en.wikipedia.org/wiki/Airoli_Assembly_constituency
- https://en.wikipedia.org/wiki/Belapur_Assembly_constituency
- https://en.wikipedia.org/wiki/Borivali_Assembly_constituency
- https://en.wikipedia.org/wiki/Dahisar_Assembly_constituency
- https://en.wikipedia.org/wiki/Magathane_Assembly_constituency
- https://en.wikipedia.org/wiki/Mulund_Assembly_constituency
- https://en.wikipedia.org/wiki/Vikhroli_Assembly_constituency
- https://en.wikipedia.org/wiki/Bhandup_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Jogeshwari_East_Assembly_constituency
- https://en.wikipedia.org/wiki/Dindoshi_Assembly_constituency
- https://en.wikipedia.org/wiki/Kandivali_East_Assembly_constituency
- https://en.wikipedia.org/wiki/Charkop_Assembly_constituency
- https://en.wikipedia.org/wiki/Malad_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Goregaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Versova_Assembly_constituency
- https://en.wikipedia.org/wiki/Andheri_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Andheri_East_Assembly_constituency
- https://en.wikipedia.org/wiki/Vile_Parle_Assembly_constituency
- https://en.wikipedia.org/wiki/Chandivali_Assembly_constituency
- https://en.wikipedia.org/wiki/Ghatkopar_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Ghatkopar_East_Assembly_constituency
- https://en.wikipedia.org/wiki/Mankhurd_Shivaji_Nagar_Assembly_constituency
- https://en.wikipedia.org/wiki/Anushakti_Nagar_Assembly_constituency
- https://en.wikipedia.org/wiki/Chembur_Assembly_constituency
- https://en.wikipedia.org/wiki/Kurla_Assembly_constituency
- https://en.wikipedia.org/wiki/Kalina_Assembly_constituency
- https://en.wikipedia.org/wiki/Vandre_East_Assembly_constituency
- https://en.wikipedia.org/wiki/Vandre_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Dharavi_Assembly_constituency
- https://en.wikipedia.org/wiki/Sion_Koliwada_Assembly_constituency
- https://en.wikipedia.org/wiki/Wadala_Assembly_constituency
- https://en.wikipedia.org/wiki/Mahim_Assembly_constituency
- https://en.wikipedia.org/wiki/Worli_Assembly_constituency
- https://en.wikipedia.org/wiki/Shivadi_Assembly_constituency
- https://en.wikipedia.org/wiki/Byculla_Assembly_constituency
- https://en.wikipedia.org/wiki/Malabar_Hill_Assembly_constituency
- https://en.wikipedia.org/wiki/Mumbadevi_Assembly_constituency
- https://en.wikipedia.org/wiki/Colaba_Assembly_constituency
- https://en.wikipedia.org/wiki/Panvel_Assembly_constituency
- https://en.wikipedia.org/wiki/Karjat_Assembly_constituency
- https://en.wikipedia.org/wiki/Uran_Assembly_constituency
- https://en.wikipedia.org/wiki/Pen_Assembly_constituency
- https://en.wikipedia.org/wiki/Alibag_Assembly_constituency
- https://en.wikipedia.org/wiki/Shrivardhan_Assembly_constituency
- https://en.wikipedia.org/wiki/Mahad_Assembly_constituency
- https://en.wikipedia.org/wiki/Junnar_Assembly_constituency
- https://en.wikipedia.org/wiki/Ambegaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Khed_Alandi_Assembly_constituency
- https://en.wikipedia.org/wiki/Shirur_Assembly_constituency
- https://en.wikipedia.org/wiki/Daund_Assembly_constituency
- https://en.wikipedia.org/wiki/Indapur_Assembly_constituency
- https://en.wikipedia.org/wiki/Baramati_Assembly_constituency
- https://en.wikipedia.org/wiki/Purandar_Assembly_constituency
- https://en.wikipedia.org/wiki/Bhor_Assembly_constituency
- https://en.wikipedia.org/wiki/Maval_Assembly_constituency
- https://en.wikipedia.org/wiki/Chinchwad_Assembly_constituency
- https://en.wikipedia.org/wiki/Pimpri_Assembly_constituency
- https://en.wikipedia.org/wiki/Bhosari_Assembly_constituency
- https://en.wikipedia.org/wiki/Vadgaon_Sheri_Assembly_constituency
- https://en.wikipedia.org/wiki/Shivajinagar,_Maharashtra_Assembly_constituency
- https://en.wikipedia.org/wiki/Kothrud_Assembly_constituency
- https://en.wikipedia.org/wiki/Khadakwasala_Assembly_constituency
- https://en.wikipedia.org/wiki/Parvati_Assembly_constituency
- https://en.wikipedia.org/wiki/Hadapsar_Assembly_constituency
- https://en.wikipedia.org/wiki/Pune_Cantonment_Assembly_constituency
- https://en.wikipedia.org/wiki/Kasba_Peth_Assembly_constituency
- https://en.wikipedia.org/wiki/Akole_Assembly_constituency
- https://en.wikipedia.org/wiki/Sangamner_Assembly_constituency
- https://en.wikipedia.org/wiki/Shirdi_Assembly_constituency
- https://en.wikipedia.org/wiki/Kopargaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Shrirampur_Assembly_constituency
- https://en.wikipedia.org/wiki/Nevasa_Assembly_constituency
- https://en.wikipedia.org/wiki/Shevgaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Rahuri_Assembly_constituency
- https://en.wikipedia.org/wiki/Parner_Assembly_constituency
- https://en.wikipedia.org/wiki/Ahmednagar_City_Assembly_constituency
- https://en.wikipedia.org/wiki/Shrigonda_Assembly_constituency
- https://en.wikipedia.org/wiki/Karjat_Jamkhed_Assembly_constituency
- https://en.wikipedia.org/wiki/Georai_Assembly_constituency
- https://en.wikipedia.org/wiki/Majalgaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Beed_Assembly_constituency
- https://en.wikipedia.org/wiki/Ashti_Assembly_constituency
- https://en.wikipedia.org/wiki/Kaij_Assembly_constituency
- https://en.wikipedia.org/wiki/Parli_Assembly_constituency
- https://en.wikipedia.org/wiki/Latur_Rural_Assembly_constituency
- https://en.wikipedia.org/wiki/Latur_City_Assembly_constituency
- https://en.wikipedia.org/wiki/Ahmedpur_Assembly_constituency
- https://en.wikipedia.org/wiki/Udgir_Assembly_constituency
- https://en.wikipedia.org/wiki/Nilanga_Assembly_constituency
- https://en.wikipedia.org/wiki/Ausa_Assembly_constituency
- https://en.wikipedia.org/wiki/Umarga_Assembly_constituency
- https://en.wikipedia.org/wiki/Tuljapur_Assembly_constituency
- https://en.wikipedia.org/wiki/Osmanabad_Assembly_constituency
- https://en.wikipedia.org/wiki/Paranda_Assembly_constituency
- https://en.wikipedia.org/wiki/Karmala_Assembly_constituency
- https://en.wikipedia.org/wiki/Madha_Assembly_constituency
- https://en.wikipedia.org/wiki/Barshi_Assembly_constituency
- https://en.wikipedia.org/wiki/Mohol_Assembly_constituency
- https://en.wikipedia.org/wiki/Solapur_City_North_Assembly_constituency
- https://en.wikipedia.org/wiki/Solapur_City_Central_Assembly_constituency
- https://en.wikipedia.org/wiki/Akkalkot_Assembly_constituency
- https://en.wikipedia.org/wiki/Solapur_South_Assembly_constituency
- https://en.wikipedia.org/wiki/Pandharpur_Assembly_constituency
- https://en.wikipedia.org/wiki/Sangola_Assembly_constituency
- https://en.wikipedia.org/wiki/Malshiras_Assembly_constituency
- https://en.wikipedia.org/wiki/Phaltan_(Vidhan_Sabha_Constituency)
- https://en.wikipedia.org/wiki/Wai_Assembly_constituency
- https://en.wikipedia.org/wiki/Koregaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Man_Assembly_constituency
- https://en.wikipedia.org/wiki/Karad_North_Assembly_constituency
- https://en.wikipedia.org/wiki/Karad_South_Assembly_constituency
- https://en.wikipedia.org/wiki/Patan,_Maharashtra_Assembly_constituency
- https://en.wikipedia.org/wiki/Satara_Assembly_constituency
- https://en.wikipedia.org/wiki/Dapoli_Assembly_constituency
- https://en.wikipedia.org/wiki/Guhagar_Assembly_constituency
- https://en.wikipedia.org/wiki/Chiplun_Assembly_constituency
- https://en.wikipedia.org/wiki/Ratnagiri_Assembly_constituency
- https://en.wikipedia.org/wiki/Rajapur_Assembly_constituency
- https://en.wikipedia.org/wiki/Kankavli_Assembly_constituency
- https://en.wikipedia.org/wiki/Kudal_Assembly_constituency
- https://en.wikipedia.org/wiki/Sawantwadi_Assembly_constituency
- https://en.wikipedia.org/wiki/Chandgad_Assembly_constituency
- https://en.wikipedia.org/wiki/Radhanagari_Assembly_constituency
- https://en.wikipedia.org/wiki/Kagal_Assembly_constituency
- https://en.wikipedia.org/wiki/Kolhapur_South_Assembly_constituency
- https://en.wikipedia.org/wiki/Karvir_Assembly_constituency
- https://en.wikipedia.org/wiki/Kolhapur_North_Assembly_constituency
- https://en.wikipedia.org/wiki/Shahuwadi_Assembly_constituency
- https://en.wikipedia.org/wiki/Hatkanangale_Assembly_constituency
- https://en.wikipedia.org/wiki/Ichalkaranji_Assembly_constituency
- https://en.wikipedia.org/wiki/Shirol_Assembly_constituency
- https://en.wikipedia.org/wiki/Miraj_Assembly_constituency
- https://en.wikipedia.org/wiki/Sangli_Assembly_constituency
- https://en.wikipedia.org/wiki/Islampur,_Maharashtra_Assembly_constituency
- https://en.wikipedia.org/wiki/Shirala_Assembly_constituency
- https://en.wikipedia.org/wiki/Palus-Kadegaon_Assembly_constituency
- https://en.wikipedia.org/wiki/Khanapur,_Maharashtra_Assembly_constituency
- https://en.wikipedia.org/wiki/Tasgaon-Kavathe_Mahankal_Assembly_constituency
- https://en.wikipedia.org/wiki/Jat_Assembly_constituency

---

# Odisha Legislative Assembly election, 2024: results by constituency

File: `odisha_2024.csv`, 147 rows, one per assembly constituency (AC), numbered as the Commission numbers them. The general election polled in four phases, 13 May to 1 June 2024, with the Lok Sabha; counted 4 June 2024. Retrieved 10 October 2026.

## The Commission's own pages could not be read

- The Commission's statistical report for this election is listed at https://www.eci.gov.in/statistical-report/ae/2024/4 (read through a Firecrawl render for Odisha, which shows 14 report files including "10-Detailed Results" and "11 - AC Wise Number Of Electors"). The files are served only through `https://www.eci.gov.in/eci-backend/public/api/election-result?category_id=N` and the encrypted `api/download` route, and both answered HTTP 406 ("Request was blocked due to suspicious behavior") from this sandbox, with curl and with a Firecrawl scrape. Guessed direct paths under `eci-backend/public/all_files/full-statistical-reports/` also answered 406, which is how that server answers a missing file.
- The results pages on results.eci.gov.in for 2024 (`AcResultGenJune2024`, `ResultAcGenNov2024`) now answer 404. Archived copies exist on the Wayback Machine, but web.archive.org could not be reached from here (connection reset) and WebFetch refuses that host.
- So every figure in the CSV comes from published compilations of the Commission's results, checked against each other. None was read from an ECI page directly, with the exceptions named below.

## Sources and URLs

1. **IndiaVotes** (compilation of ECI results). State page https://www.indiavotes.com/vidhan-sabha/orissa/2024/ and one page per AC, https://www.indiavotes.com/vidhan-sabha/orissa/2024/<slug>/ (147 pages, read from each page's embedded `iv-page-context` JSON: every candidate with party abbreviation and votes, NOTA, `voters_eligible`, `votes_polled`, `winning_margin`, AC category).
2. **Wikipedia, results by constituency**: https://en.wikipedia.org/wiki/2024_Odisha_Legislative_Assembly_election (section "Results by constituency", wikitext via `action=raw`): AC number, AC name, winner, runner-up, their parties and votes, margin.
3. **Wikipedia, list of constituencies**: https://en.wikipedia.org/wiki/List_of_constituencies_of_the_Odisha_Legislative_Assembly : AC number and reservation.
4. **Wikipedia AC articles**, one per AC, https://en.wikipedia.org/wiki/<AC>_Assembly_constituency (`action=raw`): the 2024 election box (candidates, votes) and the infobox `electors`, used only to break ties between 1 and 2.
5. **ECI statistical report 34 (Lok Sabha 2024, "Details of Assembly Segment of PC")** as compiled by OpenCity, https://data.opencity.in/dataset/85a345c6-78c0-4f57-adfc-236c726c5456/resource/881d1489-a8fc-46b1-b00d-d4824e08e797/download/142dc4e5-49e3-4412-a751-d712970b0dd5.csv , read from the copy already in the repository, `INDIA-DATA/data/india/raw/ls2024_ac_pc.csv` (column `electors_ac`). The Assembly and Lok Sabha polls here were simultaneous, on the same roll, so this is a check on electors.
6. **ECI statistical report 12 (Lok Sabha 2024, State-wise voters turnout)**, https://www.eci.gov.in/eci-backend/public/all_files/GE-2024-statistical-report/12-State-Wise-Voters-Turn-Out.pdf , as recorded in `INDIA-DATA/data/india/raw/adults_ls2024.csv` (`electors_2024` = 33,716,965). That file now answers 406 here too, so the figure is taken from the repository's record of it.
7. **Contributor's workbook** `06f59b0a-Odisha_Final.xlsx`, Sheet1 (AC name, Lok Sabha seat, electors, winner, runner-up, parties, votes, margin; Lok Sabha "Total" rows skipped). It lists ACs by Lok Sabha seat and carries no AC numbers; each row was matched to an AC by name, and every match was then confirmed by the winner's votes.

### Which source each column came from

| column | source |
|---|---|
| ac | Wikipedia results table and constituency list (they agree on every number) |
| ac_name | IndiaVotes spelling (closer to the Commission's than Wikipedia's, which uses native spellings such as Padamapur, Baragada); all-capital names put in title case. Not checked against the Commission's own spelling. |
| reserved | Wikipedia list of constituencies, whose counts equal the Delimitation Order's allocation; checked against the results table and IndiaVotes |
| electors | IndiaVotes `voters_eligible` |
| winner, runner_up | IndiaVotes candidate names (ECI-style transliteration) |
| winner_party, runner_up_party | IndiaVotes party abbreviation (ECI style), with `POUI_ABBR_JLKM_01` written as JLKM; checked against Wikipedia |
| winner_votes, runner_up_votes | IndiaVotes, checked against Wikipedia; disagreements decided as listed below |
| margin | computed, winner_votes - runner_up_votes |
| total_votes | computed from IndiaVotes: every candidate's votes plus NOTA (postal included) |
| unopposed | Wikipedia results table ("Elected unopposed") and IndiaVotes (one candidate, 0 votes) |

Runner-up is the second candidate by votes; NOTA is never a candidate in IndiaVotes' list and never a runner-up here.

## Checks

- **ACs**: 147 rows, numbered 1 to 147 once each, against the state's 147 seats. Passed.
- **Electors**: the CSV sums to 33,716,965. The Commission's Lok Sabha 2024 total for the state (source 6) is 33,716,965: equal. The Commission's Assembly report total was not read (see above).
- **Margin**: margin = winner_votes - runner_up_votes in 147 of 147 contested rows. The margin IndiaVotes prints (`winning_margin`) equals the written margin in 147 of 147.
- **Winner above runner-up**, margin > 0: 147 of 147.
- **total_votes** (candidates plus NOTA) equals IndiaVotes' own `votes_polled` in 147 of 147 contested ACs. It equals the turnout in the AC's Wikipedia election box in 145 of the 147 ACs whose box gives one; the others are AC 35 (box 196,131, CSV 196,081), AC 102 (box 194,113, CSV 184,113). Differences of exactly 10,000 are typing errors in the box; the others look like boxes that leave out postal votes. Kept IndiaVotes, whose candidate votes sum to its own total..
- **Second source**: winner party, runner-up party, winner votes and runner-up votes were compared between IndiaVotes and the Wikipedia results table in every contested AC; 143 of 147 agree on all four. Unopposed winners and their parties agree in every case.

## Disagreements and what was kept

| AC | field | IndiaVotes | Wikipedia table | tie-break | kept |
|---|---|---|---|---|---|
| 18 Rairakhol | runner-up votes | 56,756 | 56,436 | wikipedia ac article 56,756, contributor workbook 56,756 | indiavotes |
| 37 Basta | runner-up votes | 62,937 | written "62, 937" (a typing slip for the same number) | wikipedia ac article 62,937, contributor workbook 62,937 | indiavotes |
| 56 Hindol | runner-up votes | 85,968 | written "85.968" (a typing slip for the same number) | wikipedia ac article 85,968, contributor workbook 85,968 | indiavotes |
| 129 Surada | runner-up votes | 55,401 | 54,401 | wikipedia ac article 55,401, contributor workbook 55,401 | indiavotes |

Wikipedia's printed margin does not equal its own votes in these ACs (the CSV computes the margin from the votes kept):

- AC 18: printed 4,960, its votes give 5,280; IndiaVotes margin 4,960.
- AC 118: printed 4,536, its votes give 4,566; IndiaVotes margin 4,566.
- AC 129: printed 28,224, its votes give 29,224; IndiaVotes margin 28,224.

**Names and party labels.**

- AC 51 Dharamsala: IndiaVotes' winner name carries a suffix, "Himanshu Sekhar Sahoo F- late Ramesh Chandra Sahoo" (the father's name); written as Himanshu Sekhar Sahoo, as in Wikipedia and the workbook.

**Reservation.** Kept: the constituency list.

- AC 69 Titilagarh: results table blank, constituency list blank, IndiaVotes SC. Kept blank; the AC's own Wikipedia infobox agrees.
- AC 94 Salepur: results table blank, constituency list blank, IndiaVotes SC. Kept blank; the AC's own Wikipedia infobox agrees.
- AC 126 Khallikote: results table blank, constituency list SC, IndiaVotes blank. Kept SC; the AC's own Wikipedia infobox agrees.
- AC 127 Chhatrapur: results table blank, constituency list SC, IndiaVotes SC. Kept SC; the AC's own Wikipedia infobox agrees.

**Electors.**

- IndiaVotes equals the ECI report 34 segment figure in all 147 ACs (and the state sum equals the Commission's Lok Sabha total). The contributor's workbook differs in 147 of 147, always lower, by 578 to 10,731; its 147 AC rows sum to 33,236,360 (its Turnout_Reference sheet prints 33,236,360) against 33,716,965. It is probably a different roll or general electors without service voters; kept IndiaVotes. Every AC is listed in the workbook table below.
- AC 9 Sundargarh: the AC's Wikipedia infobox gives 230,729 against 237,029 in both IndiaVotes and report 34; kept 237,029.
- AC 70 Kantabanji: the AC's Wikipedia infobox gives 35,047 against 278,205 in both IndiaVotes and report 34; kept 278,205.

## The contributor's workbook against the Commission's figures

The workbook could be checked only against compilations of the Commission's results (IndiaVotes, Wikipedia, report 34), not against an ECI page. Winner party, runner-up party, winner votes and runner-up votes:

All four agree with the kept figures in every one of the 147 ACs. The workbook's margins equal its own winner minus runner-up votes in every row.

Electors, workbook against the kept figure, every AC (the workbook is lower in all 147):

| AC | name | workbook | kept | difference |
|---|---|---|---|---|
| 1 | Padampur | 268,744 | 270,450 | 1,706 |
| 2 | Bijepur | 239,696 | 241,753 | 2,057 |
| 3 | Bargarh | 214,549 | 217,952 | 3,403 |
| 4 | Attabira | 222,340 | 224,933 | 2,593 |
| 5 | Bhatli | 230,713 | 232,280 | 1,567 |
| 6 | Brajarajnagar | 214,434 | 217,251 | 2,817 |
| 7 | Jharsuguda | 224,702 | 229,274 | 4,572 |
| 8 | Talsara | 214,381 | 216,981 | 2,600 |
| 9 | Sundargarh | 234,477 | 237,029 | 2,552 |
| 10 | Biramitrapur | 241,303 | 244,417 | 3,114 |
| 11 | Raghunathpali | 179,480 | 183,207 | 3,727 |
| 12 | Rourkela | 209,710 | 215,294 | 5,584 |
| 13 | Rajgangapur | 249,334 | 253,571 | 4,237 |
| 14 | Bonai | 226,812 | 228,597 | 1,785 |
| 15 | Kuchinda | 220,516 | 222,709 | 2,193 |
| 16 | Rengali | 193,027 | 196,975 | 3,948 |
| 17 | Sambalpur | 199,459 | 206,279 | 6,820 |
| 18 | Rairakhol | 200,418 | 202,639 | 2,221 |
| 19 | Deogarh | 249,504 | 251,730 | 2,226 |
| 20 | Telkoi | 238,426 | 240,261 | 1,835 |
| 21 | Ghasipura | 228,399 | 231,781 | 3,382 |
| 22 | Anandapur | 233,203 | 235,679 | 2,476 |
| 23 | Patna | 211,738 | 214,433 | 2,695 |
| 24 | Keonjhar | 229,363 | 231,912 | 2,549 |
| 25 | Champua | 230,532 | 235,467 | 4,935 |
| 26 | Jashipur | 215,460 | 219,031 | 3,571 |
| 27 | Saraskana | 206,877 | 209,605 | 2,728 |
| 28 | Rairangpur | 225,749 | 230,824 | 5,075 |
| 29 | Bangriposi | 219,651 | 224,301 | 4,650 |
| 30 | Karanjia | 197,868 | 200,408 | 2,540 |
| 31 | Udala | 198,170 | 203,084 | 4,914 |
| 32 | Badasahi | 197,529 | 200,130 | 2,601 |
| 33 | Baripada | 220,961 | 225,354 | 4,393 |
| 34 | Morada | 230,777 | 234,075 | 3,298 |
| 35 | Jaleswar | 251,686 | 254,539 | 2,853 |
| 36 | Bhograi | 231,409 | 233,902 | 2,493 |
| 37 | Basta | 242,325 | 246,159 | 3,834 |
| 38 | Balasore | 225,525 | 229,852 | 4,327 |
| 39 | Remuna | 225,748 | 229,033 | 3,285 |
| 40 | Nilgiri | 213,360 | 216,428 | 3,068 |
| 41 | Soro | 224,490 | 228,076 | 3,586 |
| 42 | Simulia | 253,577 | 257,238 | 3,661 |
| 43 | Bhandaripokhari | 237,435 | 240,416 | 2,981 |
| 44 | Bhadrak | 267,167 | 274,332 | 7,165 |
| 45 | Basudevpur | 266,666 | 272,821 | 6,155 |
| 46 | Dhamnagar | 243,734 | 247,651 | 3,917 |
| 47 | Chandabali | 249,218 | 253,394 | 4,176 |
| 48 | Binjharpur | 227,095 | 229,680 | 2,585 |
| 49 | Bari | 224,359 | 227,157 | 2,798 |
| 50 | Barchana | 191,850 | 194,341 | 2,491 |
| 51 | Dharamsala | 229,849 | 232,166 | 2,317 |
| 52 | Jajpur | 241,535 | 244,613 | 3,078 |
| 53 | Korai | 207,283 | 209,605 | 2,322 |
| 54 | Sukinda | 208,269 | 211,032 | 2,763 |
| 55 | Dhenkanal | 267,317 | 271,942 | 4,625 |
| 56 | Hindol | 259,204 | 263,522 | 4,318 |
| 57 | Kamakhyanagar | 216,761 | 219,965 | 3,204 |
| 58 | Parjanga | 216,232 | 219,662 | 3,430 |
| 59 | Pallahara | 177,021 | 178,632 | 1,611 |
| 60 | Talcher | 159,974 | 164,354 | 4,380 |
| 61 | Angul | 211,080 | 215,625 | 4,545 |
| 62 | Chhendipada | 207,307 | 211,410 | 4,103 |
| 63 | Athamallik | 208,136 | 209,796 | 1,660 |
| 64 | Birmaharajpur | 214,782 | 216,088 | 1,306 |
| 65 | Sonepur | 253,893 | 256,007 | 2,114 |
| 66 | Loisingha | 243,160 | 245,851 | 2,691 |
| 67 | Patnagarh | 302,304 | 306,231 | 3,927 |
| 68 | Bolangir | 238,842 | 243,358 | 4,516 |
| 69 | Titilagarh | 254,114 | 257,804 | 3,690 |
| 70 | Kantabanji | 274,069 | 278,205 | 4,136 |
| 71 | Nawapara | 241,502 | 243,514 | 2,012 |
| 72 | Khariar | 251,053 | 253,164 | 2,111 |
| 73 | Umarkote | 195,711 | 196,646 | 935 |
| 74 | Jharigam | 216,256 | 217,126 | 870 |
| 75 | Nabarangpur | 232,821 | 234,183 | 1,362 |
| 76 | Dabugam | 204,388 | 204,966 | 578 |
| 77 | Lanjigarh | 228,557 | 230,367 | 1,810 |
| 78 | Junagarh | 244,768 | 246,605 | 1,837 |
| 79 | Dharmgarh | 259,898 | 261,881 | 1,983 |
| 80 | Bhawanipatna | 231,555 | 234,424 | 2,869 |
| 81 | Narla | 229,979 | 232,083 | 2,104 |
| 82 | Balliguda | 163,716 | 165,501 | 1,785 |
| 83 | G. Udayagiri | 206,406 | 208,617 | 2,211 |
| 84 | Phulbani | 198,839 | 200,205 | 1,366 |
| 85 | Kantamal | 167,838 | 169,070 | 1,232 |
| 86 | Boudh | 164,854 | 166,544 | 1,690 |
| 87 | Baramba | 244,560 | 247,960 | 3,400 |
| 88 | Banki | 216,520 | 219,513 | 2,993 |
| 89 | Athagarh | 211,490 | 214,063 | 2,573 |
| 90 | Barabati-Cuttack | 238,450 | 244,574 | 6,124 |
| 91 | Choudwar-Cuttack | 230,084 | 233,928 | 3,844 |
| 92 | Niali | 246,498 | 248,941 | 2,443 |
| 93 | Cuttack Sadar | 225,787 | 229,006 | 3,219 |
| 94 | Salepur | 245,881 | 249,033 | 3,152 |
| 95 | Mahanga | 269,044 | 271,535 | 2,491 |
| 96 | Patkura | 248,633 | 252,438 | 3,805 |
| 97 | Kendrapara | 226,103 | 230,413 | 4,310 |
| 98 | Aul | 271,285 | 275,973 | 4,688 |
| 99 | Rajanagar | 259,247 | 262,707 | 3,460 |
| 100 | Mahakalapada | 249,821 | 253,626 | 3,805 |
| 101 | Paradeep | 216,533 | 220,649 | 4,116 |
| 102 | Tirtol | 246,622 | 249,910 | 3,288 |
| 103 | Balikuda-Ersama | 267,980 | 270,641 | 2,661 |
| 104 | Jagatsinghpur | 217,522 | 220,988 | 3,466 |
| 105 | Kakatpur | 239,983 | 244,399 | 4,416 |
| 106 | Nimapara | 244,042 | 247,961 | 3,919 |
| 107 | Puri | 234,828 | 240,287 | 5,459 |
| 108 | Brahmagiri | 225,908 | 229,367 | 3,459 |
| 109 | Satyabadi | 211,656 | 215,326 | 3,670 |
| 110 | Pipili | 233,865 | 238,309 | 4,444 |
| 111 | Jayadev | 180,692 | 183,354 | 2,662 |
| 112 | Bhubaneswar Central (Madhya) | 213,223 | 219,233 | 6,010 |
| 113 | Bhubaneswar North (Uttar) | 275,141 | 285,872 | 10,731 |
| 114 | Ekamra-Bhubaneswar | 260,250 | 269,327 | 9,077 |
| 115 | Jatani | 241,579 | 247,101 | 5,522 |
| 116 | Begunia | 217,345 | 220,052 | 2,707 |
| 117 | Khurda | 246,424 | 250,080 | 3,656 |
| 118 | Chilika | 230,801 | 234,073 | 3,272 |
| 119 | Ranpur | 205,959 | 209,600 | 3,641 |
| 120 | Khandapada | 183,405 | 185,935 | 2,530 |
| 121 | Daspalla | 188,975 | 190,742 | 1,767 |
| 122 | Nayagarh | 218,938 | 222,736 | 3,798 |
| 123 | Bhanjanagar | 236,237 | 239,901 | 3,664 |
| 124 | Polasara | 245,919 | 249,263 | 3,344 |
| 125 | Kabisuryangar | 235,111 | 238,297 | 3,186 |
| 126 | Khallikote | 230,361 | 233,062 | 2,701 |
| 127 | Chhatrapur | 232,962 | 236,803 | 3,841 |
| 128 | Aska | 200,085 | 203,348 | 3,263 |
| 129 | Surada | 232,402 | 235,622 | 3,220 |
| 130 | Sanakhemundi | 227,770 | 231,373 | 3,603 |
| 131 | Hinjili | 229,734 | 232,439 | 2,705 |
| 132 | Gopalpur | 221,504 | 227,313 | 5,809 |
| 133 | Berhampur | 219,580 | 224,982 | 5,402 |
| 134 | Digapahandi | 222,087 | 225,979 | 3,892 |
| 135 | Chikiti | 212,264 | 216,271 | 4,007 |
| 136 | Mohana | 243,522 | 246,023 | 2,501 |
| 137 | Paralakhemundi | 215,706 | 217,857 | 2,151 |
| 138 | Gunupur | 221,495 | 224,055 | 2,560 |
| 139 | Bissam cuttack | 232,442 | 234,292 | 1,850 |
| 140 | Rayagada | 250,566 | 255,053 | 4,487 |
| 141 | Lakshmipur | 172,483 | 173,780 | 1,297 |
| 142 | Kotpad | 208,283 | 209,003 | 720 |
| 143 | Jeypore | 211,908 | 214,757 | 2,849 |
| 144 | Koraput | 190,341 | 192,486 | 2,145 |
| 145 | Pottangi | 186,076 | 187,219 | 1,143 |
| 146 | Malkangiri | 244,890 | 247,087 | 2,197 |
| 147 | Chitrakonda | 204,339 | 205,599 | 1,260 |

## What is missing

- The Commission's own Detailed Results and AC-wise electors files were not read; every row rests on two or more compilations that agree, or on the tie-breaks above.

---

# Puducherry 2026, Assembly results by AC

**Year used: 2026.** A general election to the Puducherry Legislative Assembly was held in 2026: ECI's results site carried "General Election to Assembly Constituencies: Trends & Results May-2026 / Puducherry ... Status Known For 30 out of 30 Constituencies" (archived copy below), and Wikipedia's article gives the poll as 9 April 2026. So the latest general election is 2026, not 2021. 30 elected ACs.

AC 9 Thattanchavady: N. Rangasamy won both AC 4 Mangalam and AC 9; Wikipedia records that he vacated AC 9 and a bye-election was held there on 6 October 2026. This file carries the general-election result; the bye-election is not reflected.

## What is incomplete, read this first

ECI's results pages (results.eci.gov.in/ResultAcGenMay2026/...) now answer 404, and its statistical report (https://www.eci.gov.in/statistical-report/ae/2026/25) exposes its files only through a script-driven download that answers 406 here. The archived copies on web.archive.org cannot be reached by curl or WebFetch from this sandbox; they were read through Firecrawl until its credits ran out, which happened after 19 of the 30 constituency pages and one of the two state-wise pages.

- ACs 1 to 19: every column except electors is from ECI's own constituency page.
- ACs 20, 21, 22, 23, 24, 26, 27, 28, 29: ac_name, winner, winner_party, runner_up, runner_up_party are from ECI's state-wise page, and ECI's margin there is checked against ours. winner_votes, runner_up_votes and total_votes are from IndiaVotes (a compilation of ECI's results), checked against Wikipedia.
- ACs 25 Thirunallar and 30 Yanam: no ECI page was read. ac_name from the CEO Puducherry roll page; winner, runner-up and their parties from Wikipedia; votes and total_votes from IndiaVotes. Names in these two rows are in Wikipedia's mixed case.
- **electors, all 30 rows, is not a Commission figure as printed.** It is IndiaVotes' "Voters" for each AC. Their sum is 9,50,311, which equals the total Wikipedia attributes to the Election Commission (4,46,361 men, 5,03,810 women, 140 third gender) from a press report of the final roll of 14 February 2026. Whether that figure includes service electors is not established. Replace this column when ECI's table 11 (AC Wise Number Of Electors) can be read.
- Still to fetch when possible: the archived ECI pages ConstituencywiseU0720.htm to ConstituencywiseU0730.htm and statewiseU072.htm (Wayback timestamps around 20260505012242 to 20260505012347), and the statistical report.

## Sources

ECI, archived by the Wayback Machine, read through Firecrawl:

- State-wise page 1 of 2 (20 ACs: winner, party, runner-up, party, margin, round, status): https://web.archive.org/web/20260505150318/https://results.eci.gov.in/ResultAcGenMay2026/statewiseU071.htm . Saved as dl/py/statewiseU071.tsv.
- Constituency pages (every candidate's EVM, postal and total votes, NOTA, and the Total row), ACs 1 to 19. Saved as dl/py/U07<ac>.md:
  - https://web.archive.org/web/20260505012241/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU0713.htm
  - https://web.archive.org/web/20260505012247/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU0719.htm
  - https://web.archive.org/web/20260505012250/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU0711.htm
  - https://web.archive.org/web/20260505012253/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU079.htm
  - https://web.archive.org/web/20260505012255/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU078.htm
  - https://web.archive.org/web/20260505012259/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU075.htm
  - https://web.archive.org/web/20260505012307/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU076.htm
  - https://web.archive.org/web/20260505012310/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU074.htm
  - https://web.archive.org/web/20260505012311/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU072.htm
  - https://web.archive.org/web/20260505012317/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU0715.htm
  - https://web.archive.org/web/20260505012318/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU0716.htm
  - https://web.archive.org/web/20260505012322/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU0710.htm
  - https://web.archive.org/web/20260505012328/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU0718.htm
  - https://web.archive.org/web/20260505012331/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU073.htm
  - https://web.archive.org/web/20260505012333/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU0712.htm
  - https://web.archive.org/web/20260505012333/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU0714.htm
  - https://web.archive.org/web/20260505012340/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU0717.htm
  - https://web.archive.org/web/20260505012346/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU077.htm
  - https://web.archive.org/web/20260505044129/https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseU071.htm

Compilations:

- IndiaVotes, https://www.indiavotes.com/vidhan-sabha/pondicherry/2026/ (state table: winner and runner-up votes, margin) and one page per AC, https://www.indiavotes.com/vidhan-sabha/pondicherry/2026/<slug>/ (Voters, all candidates' votes, NOTA).
- Wikipedia, "2026 Puducherry Legislative Assembly election", "By constituency" (https://en.wikipedia.org/w/index.php?title=2026_Puducherry_Legislative_Assembly_election&action=raw).

Other:

- CEO Puducherry, https://ceopuducherry.py.gov.in/ac_wise_electrol.php , for the (SC) marks on AC names (2, 3, 21, 22, 24) and the names of ACs 25 and 30. Its elector counts are the roll of 16 September 2026, after the election, and were not used.

## Columns

- reserved: SC for ACs 2, 3, 21, 22, 24 (CEO page; Wikipedia agrees).
- winner_party, runner_up_party: ECI's full party names as printed on the results pages (not abbreviations), "Independent" for independents.
- total_votes: ACs 1 to 19, the sum of every candidate and NOTA on ECI's page (equals its Total row). ACs 20 to 30, IndiaVotes' candidates' votes plus NOTA.
- unopposed: blank in every row.

## Checks

- 30 rows against 30 seats, ACs 1 to 30 once each.
- ACs 1 to 19: in each, candidates' EVM, postal and total votes sum to ECI's Total row; EVM + postal = total for every candidate; one NOTA row each.
- The IndiaVotes method for total_votes was tested on ACs 1 to 19, where it equals ECI's Total row in all 19.
- margin = winner_votes - runner_up_votes in all 30 rows; all positive; NOTA never first or second.
- ECI state-wise margin, winner and runner-up parties and names agree with our row in all 20 ACs on page 1 (including ACs 1 to 19 that are on it).
- Electors sum to 9,50,311 (see above; not a Commission table). total_votes sum to 8,66,139 (no state total was read to compare).
- Winners: All India N.R. Congress 12, DMK 5, BJP 4, Independent 3, TVK 2, INC 1, Latchiya Jananayaka Katchi 1, AIADMK 1, Neyam Makkal Kazhagam 1. AINRC 12, DMK 5, BJP 4, Independent 3, TVK 2 and INC 1 match the "Won In" counts on ECI's state-wise page.

## Disagreements

IndiaVotes agrees with every vote figure and margin taken from ECI (ACs 1 to 19) and with ECI's margin on page 1 of the state-wise table. Wikipedia:

- AC 27 Karaikal South: winner votes Wikipedia 12,453, IndiaVotes 12,543. ECI's state-wise margin is 5,862, which is 12,543 less the runner-up's 6,681, and is also Wikipedia's own margin. Kept 12,543.
- AC 8 Indira Nagar: runner-up S. Mourougane, ECI "Tamilaga Vettri Kazhagam"; Wikipedia gives the runner-up as "S. S. Rangan" of the DMK (the AC 4 runner-up's name). Kept ECI.
- ACs 9 and 10: Wikipedia's table rows for these two could not be parsed (its AC 9 row carries the 2026 bye-election). ECI's pages for both were read, and IndiaVotes agrees with them.

---

# Punjab Legislative Assembly election 2022: results by constituency

File: `punjab_2022.csv`, 117 rows, one per AC, ACs 1 to 117. Compiled 2026-10-10.

## The Commission's own pages could not be read

Tried first, all from this sandbox on 2026-10-10:

- results.eci.gov.in: the 2022 and 2024 results pages are gone (`https://results.eci.gov.in/ResultAcGenNov2024/index.htm`, `.../ResultAcGenOct2024/index.htm` and their `candidateswise-*`/`Constituencywise*` pages answer 404; the root redirects to the October 2026 bye-elections).
- www.eci.gov.in statistical reports: every HTML page answers HTTP 406 (WAF). The reports index (`https://www.eci.gov.in/statistical-reports`, read once through Firecrawl) gives Maharashtra 2024 as `https://www.eci.gov.in/statistical-report/ae/2024/8`, Haryana 2024 as `https://www.eci.gov.in/statistical-report/ae/2024/6`, and Punjab, Uttarakhand and Goa 2022 as `https://old.eci.gov.in/files/file/14165-punjab-general-legislative-election-2022/`, `.../14169-uttarakhand-general-legislative-election-2022/`, `.../14168-goa-general-legislative-election-2022/`. The Maharashtra report page, rendered through Firecrawl, lists 10 Detailed Results and 11 AC Wise Number Of Electors as XLSX/PDF but exposes no file address (download is a script action). Guessed file paths under `https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/` on the pattern that serves Rajasthan 2023 (`rajasthan/2023_Including/Detailed_Results.xlsx`, which answered 200 as a control) all answered 406 for these states (`maharashtra/2024/...`, `Maharashtra/2024/...`, `haryana/2024/...`, `punjab/2022/...`, `uttarakhand/2022/...`, `goa/2022/...`, with several file-name variants). old.eci.gov.in and web.archive.org reset the connection. Firecrawl credits are low, so no further renders were attempted.
- No figure in the CSV is from the Commission directly. Replace with the Detailed Results and AC Wise Number Of Electors when they can be fetched.

## Sources used

1. **IndiaVotes** (states 'Election results sourced from the Election Commission of India'), state page https://www.indiavotes.com/vidhan-sabha/punjab/2022/ and one page per AC, `https://www.indiavotes.com/vidhan-sabha/punjab/2022/<slug>/` (all 117 listed at the end), fetched with curl. Each page gives every candidate's votes and party code, NOTA, 'Voters' (`voters_eligible`) and the AC category (GEN/SC/ST).
2. **Wikipedia, results table** of https://en.wikipedia.org/wiki/2022_Punjab_Legislative_Assembly_election (AC number, name with (SC)/(ST), winner, runner-up, parties, votes, margin, turnout %).
3. **Wikipedia, one article per AC** (all 117 listed at the end): infobox 'Constituency No.' and 'Reservation', and the 2022 election box ('Registered electors', candidate votes, 'Margin of victory'/'Majority', turnout).

## Which source each column came from

- `ac`: Wikipedia results table; agrees with the 'Constituency No.' of the AC's own Wikipedia article in 117 of 117 ACs. IndiaVotes pages carry no AC number; each was matched to its AC by name, or where spellings differ by the winner's votes (listed below).
- `ac_name`: Wikipedia results table spelling, '(SC)'/'(ST)' removed. Not the Commission's spelling.
- `reserved`: majority of the readings of IndiaVotes' category, the Wikipedia results table and the Wikipedia AC article; each disagreement is listed below.
- `electors`: IndiaVotes 'Voters'. They sum to 2,16,08,701, which is the 'Registered voters' total printed in the Wikipedia results table; Wikipedia's infobox gives 2,14,99,804, apparently general electors only.
- `winner`, `winner_votes`, `runner_up`, `runner_up_votes`, `total_votes`: IndiaVotes. Winner and runner-up are the two highest candidates; NOTA is never among them. `total_votes` is every candidate plus NOTA as IndiaVotes prints them (whether postal votes are inside each candidate's figure is not stated there).
- `winner_party`, `runner_up_party`: IndiaVotes party code, except where it prints an internal placeholder, where Wikipedia's abbreviation is used (listed below). Codes are IndiaVotes', not necessarily the Commission's (e.g. SHSUBT, NCPSP).
- `margin`: winner_votes less runner_up_votes. `unopposed`: no AC was uncontested.

## Checks

- ACs: 117 rows against 117 seats; numbers 1 to 117 each once: True.
- margin = winner_votes - runner_up_votes in 117 of 117 rows; every margin positive: True.
- Sum of electors: 21,608,701. The Commission's state total could not be read. It equals the Wikipedia results table total of 21,608,701.
- Against the Wikipedia results table: winner votes agree in 117/117, runner-up votes in 117/117, margin in 117/117.
- Against the Wikipedia AC articles: margin agrees in 116/117; total votes (Wikipedia 'Turnout' count) agree in 76/78.
- Winner party agrees with the Wikipedia results table in 117/117 (treating IND/Ind, SHSUBT/SS(UBT), NCPSP/NCP-SP, UKKD/UKD, SAD(S)/SADS as the same party).
- Seats by winner party: AAP 92, INC 18, SAD 3, BJP 2, IND 1, BSP 1.
- Reserved: general 83, SC 34.
- Turnout recomputed as total_votes / electors agrees with the Wikipedia results table's turnout % within 0.01 point in 116 of 117 ACs. Exceptions (AC, name, Wikipedia %, recomputed %): 65 Ludhiana North 61.37 vs 61.38.

## Disagreements between sources, and what was kept

- AC 76 Firozpur City: margin IndiaVotes 19,569, Wikipedia results table 19,569, Wikipedia AC article 20,069. Kept IndiaVotes, which the results table supports.
- AC 100 Dirba: reserved readings IndiaVotes='', Wikipedia results table='SC', Wikipedia AC article='SC'; kept 'SC'.
- AC 102 Bhadaur: reserved readings IndiaVotes='SC', Wikipedia results table='', Wikipedia AC article='SC'; kept 'SC'.
- Matching: AC 24 Sri Khadoor Sahib: matched to IndiaVotes Khadoor Sahib by winner votes, names differ.
- Matching: AC 37 Jalandhar Cnt.: matched to IndiaVotes Jalandhar Cantt. by winner votes, names differ.
- Matching: AC 84 Gidderbaha: matched to IndiaVotes Giddar Baha by winner votes, names differ.
- Matching: AC 100 Dirba: matched to IndiaVotes Dirbha by winner votes, names differ.
- Party labels that differ only in abbreviation (IndiaVotes kept): AC 104 runner_up_party SAD(A) / Wikipedia SAD(M); AC 106 runner_up_party SAD(A) / Wikipedia SAD(M).
- Electors: the Wikipedia AC-article figures differ from IndiaVotes as described above; per-AC values in `punjab_2022_electors_compare.csv`.

## Not covered

- Bye-elections held since the general election are not reflected.
- No Commission figure was read; party codes are IndiaVotes', AC names Wikipedia's.

## URLs

- https://www.indiavotes.com/vidhan-sabha/punjab/2022/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/sujanpur/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/bhoa/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/pathankot/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/gurdaspur/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/dina-nagar/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/qadian/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/batala/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/sri-hargobindpur/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/fatehgarh-churian/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/dera-baba-nanak/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/ajnala/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/raja-sansi/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/majitha/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/jandiala/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/amritsar-north/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/amritsar-west/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/amritsar-central/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/amritsar-east/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/amritsar-south/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/attari/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/tarn-taran/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/khem-karan/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/patti/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/khadoor-sahib/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/baba-bakala/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/bholath/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/kapurthala/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/sultanpur-lodhi/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/phagwara/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/phillaur/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/nakodar/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/shahkot/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/kartarpur/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/jalandhar-west/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/jalandhar-central/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/jalandhar-north/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/jalandhar-cantt/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/adampur/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/mukerian/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/dasuya/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/urmar/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/sham-chaurasi/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/hoshiarpur/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/chabbewal/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/garhshankar/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/banga/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/nawan-shahr/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/balachaur/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/anandpur-sahib/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/rupnagar/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/chamkaur-sahib/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/kharar/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/s-a-s-nagar/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/bassi-pathana/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/fatehgarh-sahib/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/amloh/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/khanna/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/samrala/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/sahnewal/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/ludhiana-east/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/ludhiana-south/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/atam-nagar/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/ludhiana-central/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/ludhiana-west/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/ludhiana-north/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/gill/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/payal/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/dakha/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/raikot/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/jagraon/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/nihal-singh-wala/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/bhagha-purana/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/moga/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/dharamkot/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/zira/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/firozpur-city/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/firozpur-rural/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/guru-har-sahai/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/jalalabad/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/fazilka/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/abohar/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/balluana/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/lambi/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/giddar-baha/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/malout/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/muktsar/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/faridkot/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/kot-kapura/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/jaitu/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/rampura-phul/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/bhucho-mandi/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/bathinda-urban/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/bathinda-rural/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/talwandi-sabo/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/maur/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/mansa/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/sardulgarh/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/budhlada/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/lehra/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/dirbha/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/sunam/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/bhadaur/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/barnala/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/mehal-kalan/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/malerkotla/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/amargarh/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/dhuri/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/sangrur/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/nabha/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/patiala-rural/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/rajpura/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/dera-bassi/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/ghanaur/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/sanour/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/patiala/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/samana/
- https://www.indiavotes.com/vidhan-sabha/punjab/2022/shutrana/
- https://en.wikipedia.org/wiki/2022_Punjab_Legislative_Assembly_election
- https://en.wikipedia.org/wiki/Sujanpur,_Punjab_Assembly_constituency
- https://en.wikipedia.org/wiki/Bhoa_Assembly_constituency
- https://en.wikipedia.org/wiki/Pathankot_Assembly_constituency
- https://en.wikipedia.org/wiki/Gurudaspur_Assembly_constituency
- https://en.wikipedia.org/wiki/Dina_Nagar_Assembly_constituency
- https://en.wikipedia.org/wiki/Qadian_Assembly_constituency
- https://en.wikipedia.org/wiki/Batala_Assembly_constituency
- https://en.wikipedia.org/wiki/Sri_Hargobindpur_Assembly_constituency
- https://en.wikipedia.org/wiki/Fatehgarh_Churian_Assembly_constituency
- https://en.wikipedia.org/wiki/Dera_Baba_Nanak_Assembly_constituency
- https://en.wikipedia.org/wiki/Ajnala_Assembly_constituency
- https://en.wikipedia.org/wiki/Rajasansi_Assembly_constituency
- https://en.wikipedia.org/wiki/Majitha_Assembly_constituency
- https://en.wikipedia.org/wiki/Jandiala_Assembly_constituency
- https://en.wikipedia.org/wiki/Amritsar_North_Assembly_constituency
- https://en.wikipedia.org/wiki/Amritsar_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Amritsar_Central_Assembly_constituency
- https://en.wikipedia.org/wiki/Amritsar_East_Assembly_constituency
- https://en.wikipedia.org/wiki/Amritsar_South_Assembly_constituency
- https://en.wikipedia.org/wiki/Attari_Assembly_constituency
- https://en.wikipedia.org/wiki/Tarn_Taran_Assembly_constituency
- https://en.wikipedia.org/wiki/Khem_Karan_Assembly_constituency
- https://en.wikipedia.org/wiki/Patti,_Punjab_Assembly_constituency
- https://en.wikipedia.org/wiki/Khadoor_Sahib_Assembly_constituency
- https://en.wikipedia.org/wiki/Baba_Bakala_Assembly_constituency
- https://en.wikipedia.org/wiki/Bholath_Assembly_constituency
- https://en.wikipedia.org/wiki/Kapurthala_Assembly_constituency
- https://en.wikipedia.org/wiki/Sultanpur_Lodhi_Assembly_constituency
- https://en.wikipedia.org/wiki/Phagwara_Assembly_constituency
- https://en.wikipedia.org/wiki/Phillaur_Assembly_constituency
- https://en.wikipedia.org/wiki/Nakodar_Assembly_constituency
- https://en.wikipedia.org/wiki/Shahkot_Assembly_constituency
- https://en.wikipedia.org/wiki/Kartarpur_Assembly_constituency
- https://en.wikipedia.org/wiki/Jalandhar_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Jalandhar_Central_Assembly_constituency
- https://en.wikipedia.org/wiki/Jalandhar_North_Assembly_constituency
- https://en.wikipedia.org/wiki/Jalandhar_Cantonment_Assembly_constituency
- https://en.wikipedia.org/wiki/Adampur,_Punjab_Assembly_constituency
- https://en.wikipedia.org/wiki/Mukerian_Assembly_constituency
- https://en.wikipedia.org/wiki/Dasuya_Assembly_constituency
- https://en.wikipedia.org/wiki/Urmar_Assembly_constituency
- https://en.wikipedia.org/wiki/Sham_Chaurasi_Assembly_constituency
- https://en.wikipedia.org/wiki/Hoshiarpur_Assembly_constituency
- https://en.wikipedia.org/wiki/Chabbewal_Assembly_constituency
- https://en.wikipedia.org/wiki/Garhshankar_Assembly_constituency
- https://en.wikipedia.org/wiki/Banga_Assembly_constituency
- https://en.wikipedia.org/wiki/Nawan_Shahr_Assembly_constituency
- https://en.wikipedia.org/wiki/Balachaur_Assembly_constituency
- https://en.wikipedia.org/wiki/Anandpur_Sahib_Assembly_constituency
- https://en.wikipedia.org/wiki/Rupnagar_Assembly_constituency
- https://en.wikipedia.org/wiki/Chamkaur_Sahib_Assembly_constituency
- https://en.wikipedia.org/wiki/Kharar_Assembly_constituency
- https://en.wikipedia.org/wiki/Sahibzada_Ajit_Singh_Nagar_Assembly_constituency
- https://en.wikipedia.org/wiki/Bassi_Pathana_Assembly_constituency
- https://en.wikipedia.org/wiki/Fatehgarh_Sahib_Assembly_constituency
- https://en.wikipedia.org/wiki/Amloh_Assembly_constituency
- https://en.wikipedia.org/wiki/Khanna_Assembly_constituency
- https://en.wikipedia.org/wiki/Samrala_Assembly_constituency
- https://en.wikipedia.org/wiki/Sahnewal_Assembly_constituency
- https://en.wikipedia.org/wiki/Ludhiana_East_Assembly_constituency
- https://en.wikipedia.org/wiki/Ludhiana_South_Assembly_constituency
- https://en.wikipedia.org/wiki/Atam_Nagar_Assembly_constituency
- https://en.wikipedia.org/wiki/Ludhiana_Central_Assembly_constituency
- https://en.wikipedia.org/wiki/Ludhiana_West_Assembly_constituency
- https://en.wikipedia.org/wiki/Ludhiana_North_Assembly_constituency
- https://en.wikipedia.org/wiki/Gill_Assembly_constituency
- https://en.wikipedia.org/wiki/Payal_Assembly_constituency
- https://en.wikipedia.org/wiki/Dakha_Assembly_constituency
- https://en.wikipedia.org/wiki/Raikot_Assembly_constituency
- https://en.wikipedia.org/wiki/Jagraon_Assembly_constituency
- https://en.wikipedia.org/wiki/Nihal_Singh_Wala_Assembly_constituency
- https://en.wikipedia.org/wiki/Bhagha_Purana_Assembly_constituency
- https://en.wikipedia.org/wiki/Moga_Assembly_constituency
- https://en.wikipedia.org/wiki/Dharamkot_Assembly_constituency
- https://en.wikipedia.org/wiki/Zira_Assembly_constituency
- https://en.wikipedia.org/wiki/Firozpur_City_Assembly_constituency
- https://en.wikipedia.org/wiki/Firozpur_Rural_Assembly_constituency
- https://en.wikipedia.org/wiki/Guru_Har_Sahai_Assembly_constituency
- https://en.wikipedia.org/wiki/Jalalabad,_Punjab_Assembly_constituency
- https://en.wikipedia.org/wiki/Fazilka_Assembly_constituency
- https://en.wikipedia.org/wiki/Abohar_Assembly_constituency
- https://en.wikipedia.org/wiki/Balluana_Assembly_constituency
- https://en.wikipedia.org/wiki/Lambi_Assembly_constituency
- https://en.wikipedia.org/wiki/Gidderbaha_Assembly_constituency
- https://en.wikipedia.org/wiki/Malout_Assembly_constituency
- https://en.wikipedia.org/wiki/Muktsar_Assembly_constituency
- https://en.wikipedia.org/wiki/Faridkot_Assembly_constituency
- https://en.wikipedia.org/wiki/Kotkapura_Assembly_constituency
- https://en.wikipedia.org/wiki/Jaitu_Assembly_constituency
- https://en.wikipedia.org/wiki/Rampura_Phul_Assembly_constituency
- https://en.wikipedia.org/wiki/Bhucho_Mandi_Assembly_constituency
- https://en.wikipedia.org/wiki/Bathinda_Urban_Assembly_constituency
- https://en.wikipedia.org/wiki/Bathinda_Rural_Assembly_constituency
- https://en.wikipedia.org/wiki/Talwandi_Sabo_Assembly_constituency
- https://en.wikipedia.org/wiki/Maur_Assembly_constituency
- https://en.wikipedia.org/wiki/Mansa,_Punjab_Assembly_constituency
- https://en.wikipedia.org/wiki/Sardulgarh_Assembly_constituency
- https://en.wikipedia.org/wiki/Budhalada_Assembly_constituency
- https://en.wikipedia.org/wiki/Lehra_Assembly_constituency
- https://en.wikipedia.org/wiki/Dirba_Assembly_constituency
- https://en.wikipedia.org/wiki/Sunam_Assembly_constituency
- https://en.wikipedia.org/wiki/Bhadaur_Assembly_constituency
- https://en.wikipedia.org/wiki/Barnala_Assembly_constituency
- https://en.wikipedia.org/wiki/Mehal_Kalan_Assembly_constituency
- https://en.wikipedia.org/wiki/Malerkotla_Assembly_constituency
- https://en.wikipedia.org/wiki/Amargarh_Assembly_constituency
- https://en.wikipedia.org/wiki/Dhuri_Assembly_constituency
- https://en.wikipedia.org/wiki/Sangrur_Assembly_constituency
- https://en.wikipedia.org/wiki/Nabha_Assembly_constituency
- https://en.wikipedia.org/wiki/Patiala_Rural_Assembly_constituency
- https://en.wikipedia.org/wiki/Rajpura_Assembly_constituency
- https://en.wikipedia.org/wiki/Dera_Bassi_Assembly_constituency
- https://en.wikipedia.org/wiki/Ghanaur_Assembly_constituency
- https://en.wikipedia.org/wiki/Sanour_Assembly_constituency
- https://en.wikipedia.org/wiki/Patiala_Assembly_constituency
- https://en.wikipedia.org/wiki/Samana_Assembly_constituency
- https://en.wikipedia.org/wiki/Shutrana_Assembly_constituency

---

# Sikkim Legislative Assembly election, 2024: results by constituency

File: `sikkim_2024.csv`, 32 rows, one per assembly constituency (AC), numbered as the Commission numbers them. The general election polled 19 April 2024 with the Lok Sabha; counted 2 June 2024. Retrieved 10 October 2026.

## The Commission's own pages could not be read

- The Commission's statistical report for this election is listed at https://www.eci.gov.in/statistical-report/ae/2024/5 (read through a Firecrawl render for Odisha, which shows 14 report files including "10-Detailed Results" and "11 - AC Wise Number Of Electors"). The files are served only through `https://www.eci.gov.in/eci-backend/public/api/election-result?category_id=N` and the encrypted `api/download` route, and both answered HTTP 406 ("Request was blocked due to suspicious behavior") from this sandbox, with curl and with a Firecrawl scrape. Guessed direct paths under `eci-backend/public/all_files/full-statistical-reports/` also answered 406, which is how that server answers a missing file.
- The results pages on results.eci.gov.in for 2024 (`AcResultGenJune2024`, `ResultAcGenNov2024`) now answer 404. Archived copies exist on the Wayback Machine, but web.archive.org could not be reached from here (connection reset) and WebFetch refuses that host.
- So every figure in the CSV comes from published compilations of the Commission's results, checked against each other. None was read from an ECI page directly, with the exceptions named below.

## Sources and URLs

1. **IndiaVotes** (compilation of ECI results). State page https://www.indiavotes.com/vidhan-sabha/sikkim/2024/ and one page per AC, https://www.indiavotes.com/vidhan-sabha/sikkim/2024/<slug>/ (32 pages, read from each page's embedded `iv-page-context` JSON: every candidate with party abbreviation and votes, NOTA, `voters_eligible`, `votes_polled`, `winning_margin`, AC category).
2. **Wikipedia, results by constituency**: https://en.wikipedia.org/wiki/2024_Sikkim_Legislative_Assembly_election (section "Results by constituency", wikitext via `action=raw`): AC number, AC name, winner, runner-up, their parties and votes, margin.
3. **Wikipedia, list of constituencies**: https://en.wikipedia.org/wiki/List_of_constituencies_of_the_Sikkim_Legislative_Assembly : AC number and reservation.
4. **Wikipedia AC articles**, one per AC, https://en.wikipedia.org/wiki/<AC>_Assembly_constituency (`action=raw`): the 2024 election box (candidates, votes) and the infobox `electors`, used only to break ties between 1 and 2.
5. **ECI statistical report 34 (Lok Sabha 2024, "Details of Assembly Segment of PC")** as compiled by OpenCity, https://data.opencity.in/dataset/85a345c6-78c0-4f57-adfc-236c726c5456/resource/881d1489-a8fc-46b1-b00d-d4824e08e797/download/142dc4e5-49e3-4412-a751-d712970b0dd5.csv , read from the copy already in the repository, `INDIA-DATA/data/india/raw/ls2024_ac_pc.csv` (column `electors_ac`). The Assembly and Lok Sabha polls here were simultaneous, on the same roll, so this is a check on electors.
6. **ECI statistical report 12 (Lok Sabha 2024, State-wise voters turnout)**, https://www.eci.gov.in/eci-backend/public/all_files/GE-2024-statistical-report/12-State-Wise-Voters-Turn-Out.pdf , as recorded in `INDIA-DATA/data/india/raw/adults_ls2024.csv` (`electors_2024` = 466,643). That file now answers 406 here too, so the figure is taken from the repository's record of it.

### Which source each column came from

| column | source |
|---|---|
| ac | Wikipedia results table and constituency list (they agree on every number) |
| ac_name | IndiaVotes spelling (closer to the Commission's than Wikipedia's, which uses native spellings such as Padamapur, Baragada); all-capital names put in title case. Not checked against the Commission's own spelling. |
| reserved | Wikipedia list of constituencies, whose counts equal the Delimitation Order's allocation; checked against the results table and IndiaVotes |
| electors | IndiaVotes `voters_eligible` |
| winner, runner_up | IndiaVotes candidate names (ECI-style transliteration) |
| winner_party, runner_up_party | IndiaVotes party abbreviation (ECI style), with `POUI_ABBR_JLKM_01` written as JLKM; checked against Wikipedia |
| winner_votes, runner_up_votes | IndiaVotes, checked against Wikipedia; disagreements decided as listed below |
| margin | computed, winner_votes - runner_up_votes |
| total_votes | computed from IndiaVotes: every candidate's votes plus NOTA (postal included) |
| unopposed | Wikipedia results table ("Elected unopposed") and IndiaVotes (one candidate, 0 votes) |

Runner-up is the second candidate by votes; NOTA is never a candidate in IndiaVotes' list and never a runner-up here.

## Checks

- **ACs**: 32 rows, numbered 1 to 32 once each, against the state's 32 seats. Passed.
- **Electors**: the CSV sums to 466,643. The Commission's Lok Sabha 2024 total for the state (source 6) is 466,643: equal. The Commission's Assembly report total was not read (see above).
- **Margin**: margin = winner_votes - runner_up_votes in 32 of 32 contested rows. The margin IndiaVotes prints (`winning_margin`) equals the written margin in 32 of 32.
- **Winner above runner-up**, margin > 0: 32 of 32.
- **total_votes** (candidates plus NOTA) equals IndiaVotes' own `votes_polled` in 32 of 32 contested ACs. It equals the turnout in the AC's Wikipedia election box in 30 of the 32 ACs whose box gives one; the others are AC 19 (box 15,639, CSV 15,640), AC 20 (box 15,557, CSV 14,731). Differences of exactly 10,000 are typing errors in the box; the others look like boxes that leave out postal votes. Kept IndiaVotes, whose candidate votes sum to its own total..
- **Second source**: winner party, runner-up party, winner votes and runner-up votes were compared between IndiaVotes and the Wikipedia results table in every contested AC; 32 of 32 agree on all four. Unopposed winners and their parties agree in every case.

## Disagreements and what was kept

No disagreement on winner, runner-up, parties or votes.

Wikipedia's printed margin does not equal its own votes in these ACs (the CSV computes the margin from the votes kept):

- AC 28: printed 4,089, its votes give 2,568; IndiaVotes margin 2,568.

**Names and party labels.**

- AC 7: the runner-up is "Dr. A D Subba" in IndiaVotes and Akar Dhoj Limbu in the Wikipedia table, same party and votes. Kept IndiaVotes' name.

**Reservation in Sikkim.** The brief allows only SC, ST or blank. Twelve ACs are reserved for Bhutia-Lepcha (BL) and AC 32 Sangha is reserved for the monasteries (Sangha electors only); these are written blank in `reserved`. BL seats per the constituency list: 1, 5, 6, 9, 16, 21, 23, 24, 27, 29, 30, 31. The results table marks only 10 of them BL. The 2 SC seats are 8 Salghari-Zoom and 18 West Pendam per the list.

**Electors.**

IndiaVotes against report 34, every AC where they differ:

| AC | IndiaVotes | report 34 | Wikipedia infobox | kept |
|---|---|---|---|---|
| 1 Yoksam-tashiding | 15,524 | 15,942 | - | 15,524 (indiavotes) |
| 2 Yangthang | 14,121 | 14,379 | 12,952 | 14,121 (indiavotes) |
| 5 Rinchenpong | 16,024 | 16,137 | 14,756 | 16,024 (indiavotes) |
| 6 Daramdin | 16,404 | 16,473 | 15,269 | 16,404 (indiavotes) |
| 7 Soreong-chakung | 16,740 | 16,758 | 15,589 | 16,740 (indiavotes) |
| 9 Barfung | 15,980 | 16,187 | - | 15,980 (indiavotes) |
| 10 Poklok-kamrang | 16,870 | 16,874 | - | 16,870 (indiavotes) |
| 11 Namchi-singhithang | 13,251 | 13,342 | 12,689 | 13,251 (indiavotes) |
| 12 Melli | 16,029 | 16,051 | 15,479 | 16,029 (indiavotes) |
| 13 Namthang-rateypani | 16,455 | 16,542 | 15,451 | 16,455 (indiavotes) |
| 14 Temi-namphing | 15,465 | 15,513 | 14,225 | 15,465 (indiavotes) |
| 15 Rangang-yangang | 15,261 | 15,354 | - | 15,261 (indiavotes) |
| 16 Tumen-lingi | 16,767 | 17,087 | - | 16,767 (indiavotes) |
| 17 Khamdong-singtam | 14,428 | 14,523 | 13,067 | 14,428 (indiavotes) |
| 19 Rhenock | 18,356 | 18,371 | - | 18,356 (indiavotes) |
| 20 Chujachen | 18,749 | 18,786 | - | 18,749 (indiavotes) |
| 21 Gnathang-machong | 12,965 | 13,158 | - | 12,965 (indiavotes) |
| 22 Namcheybung | 16,397 | 16,484 | - | 16,397 (indiavotes) |
| 23 Shyari | 16,196 | 16,332 | - | 16,196 (indiavotes) |
| 24 Martam-rumtek | 17,844 | 18,206 | - | 17,844 (indiavotes) |
| 29 Kabi lungchuk | 13,209 | 14,029 | 12,661 | 13,209 (indiavotes) |
| 30 Djongu | 10,523 | 10,865 | 9,595 | 10,523 (indiavotes) |
| 31 Lachen mangan | 8,404 | 8,643 | 7,867 | 8,404 (indiavotes) |

- In 3 further ACs the only disagreement is the Wikipedia AC infobox, which is lower than IndiaVotes in 3 of them and higher in 0, while IndiaVotes and report 34 agree; kept IndiaVotes. ACs: 3, 4, 8.
- Why IndiaVotes is kept in Sikkim: the 32 IndiaVotes figures sum to 4,66,643, exactly the Commission's Lok Sabha total, while report 34's 31 segment figures (Sangha is not a segment) also sum to 4,66,643. Report 34 counts the Sangha electors inside the territorial segments; the Assembly roll counts them in AC 32. The Assembly figures are therefore IndiaVotes'.

## Not in scope

The 2024 bye-elections in Soreng-Chakung (AC 7) and Namchi-Singhithang (AC 11), held after Prem Singh Tamang and Krishna Kumari Rai vacated them, are not in the CSV; the rows are the general election. Wikipedia AC articles carry the bye-election boxes under the same 2024 heading, and those were set aside by matching the general-election votes.

## What is missing

- The Commission's own Detailed Results and AC-wise electors files were not read; every row rests on two or more compilations that agree, or on the tie-breaks above.

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

# Uttarakhand Legislative Assembly election 2022: results by constituency

File: `uttarakhand_2022.csv`, 70 rows, one per AC, ACs 1 to 70. Compiled 2026-10-10.

## The Commission's own pages could not be read

Tried first, all from this sandbox on 2026-10-10:

- results.eci.gov.in: the 2022 and 2024 results pages are gone (`https://results.eci.gov.in/ResultAcGenNov2024/index.htm`, `.../ResultAcGenOct2024/index.htm` and their `candidateswise-*`/`Constituencywise*` pages answer 404; the root redirects to the October 2026 bye-elections).
- www.eci.gov.in statistical reports: every HTML page answers HTTP 406 (WAF). The reports index (`https://www.eci.gov.in/statistical-reports`, read once through Firecrawl) gives Maharashtra 2024 as `https://www.eci.gov.in/statistical-report/ae/2024/8`, Haryana 2024 as `https://www.eci.gov.in/statistical-report/ae/2024/6`, and Punjab, Uttarakhand and Goa 2022 as `https://old.eci.gov.in/files/file/14165-punjab-general-legislative-election-2022/`, `.../14169-uttarakhand-general-legislative-election-2022/`, `.../14168-goa-general-legislative-election-2022/`. The Maharashtra report page, rendered through Firecrawl, lists 10 Detailed Results and 11 AC Wise Number Of Electors as XLSX/PDF but exposes no file address (download is a script action). Guessed file paths under `https://www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/` on the pattern that serves Rajasthan 2023 (`rajasthan/2023_Including/Detailed_Results.xlsx`, which answered 200 as a control) all answered 406 for these states (`maharashtra/2024/...`, `Maharashtra/2024/...`, `haryana/2024/...`, `punjab/2022/...`, `uttarakhand/2022/...`, `goa/2022/...`, with several file-name variants). old.eci.gov.in and web.archive.org reset the connection. Firecrawl credits are low, so no further renders were attempted.
- No figure in the CSV is from the Commission directly. Replace with the Detailed Results and AC Wise Number Of Electors when they can be fetched.

## Sources used

1. **IndiaVotes** (states 'Election results sourced from the Election Commission of India'), state page https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/ and one page per AC, `https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/<slug>/` (all 70 listed at the end), fetched with curl. Each page gives every candidate's votes and party code, NOTA, 'Voters' (`voters_eligible`) and the AC category (GEN/SC/ST).
2. **Wikipedia, results table** of https://en.wikipedia.org/wiki/2022_Uttarakhand_Legislative_Assembly_election (AC number, name with (SC)/(ST), winner, runner-up, parties, votes, margin, turnout %).
3. **Wikipedia, one article per AC** (all 70 listed at the end): infobox 'Constituency No.' and 'Reservation', and the 2022 election box ('Registered electors', candidate votes, 'Margin of victory'/'Majority', turnout).

## Which source each column came from

- `ac`: Wikipedia results table; agrees with the 'Constituency No.' of the AC's own Wikipedia article in 70 of 70 ACs. IndiaVotes pages carry no AC number; each was matched to its AC by name, or where spellings differ by the winner's votes (listed below).
- `ac_name`: Wikipedia results table spelling, '(SC)'/'(ST)' removed. Not the Commission's spelling.
- `reserved`: majority of the readings of IndiaVotes' category, the Wikipedia results table and the Wikipedia AC article; each disagreement is listed below.
- `electors`: Wikipedia AC article 'Registered electors'. IndiaVotes 'Voters' cannot be used: it is 0 in ACs 34 to 70, and in ACs 1 to 33 it carries the electors of ACs 38 to 70 (shifted by 37). Those 33 misfiled values agree with Wikipedia's ACs 38 to 70 within 0 to 11 (Wikipedia never lower), which is the only second reading available; ACs 1 to 37 have one source only.
- `winner`, `winner_votes`, `runner_up`, `runner_up_votes`, `total_votes`: IndiaVotes. Winner and runner-up are the two highest candidates; NOTA is never among them. `total_votes` is every candidate plus NOTA as IndiaVotes prints them (whether postal votes are inside each candidate's figure is not stated there).
- `winner_party`, `runner_up_party`: IndiaVotes party code, except where it prints an internal placeholder, where Wikipedia's abbreviation is used (listed below). Codes are IndiaVotes', not necessarily the Commission's (e.g. SHSUBT, NCPSP).
- `margin`: winner_votes less runner_up_votes. `unopposed`: no AC was uncontested.

## Checks

- ACs: 70 rows against 70 seats; numbers 1 to 70 each once: True.
- margin = winner_votes - runner_up_votes in 70 of 70 rows; every margin positive: True.
- Sum of electors: 8,266,644. The Commission's state total could not be read.
- Against the Wikipedia results table: winner votes agree in 69/70, runner-up votes in 68/70, margin in 64/70.
- Against the Wikipedia AC articles: margin agrees in 70/70; total votes (Wikipedia 'Turnout' count) agree in 69/70.
- Winner party agrees with the Wikipedia results table in 70/70 (treating IND/Ind, SHSUBT/SS(UBT), NCPSP/NCP-SP, UKKD/UKD, SAD(S)/SADS as the same party).
- Seats by winner party: BJP 47, INC 19, IND 2, BSP 2.
- Reserved: general 55, SC 13, ST 2.
- Turnout recomputed as total_votes / electors agrees with the Wikipedia results table's turnout % within 0.01 point in 3 of 70 ACs. Exceptions (AC, name, Wikipedia %, recomputed %): 1 Purola 69.4 vs 69.26; 2 Yamunotri 68.12 vs 67.75; 3 Gangotri 68.01 vs 67.47; 4 Badrinath 65.65 vs 65.09; 5 Tharali 60.34 vs 59.65; 6 Karanprayag 61.04 vs 60.19; 7 Kedarnath 66.43 vs 65.28; 8 Rudraprayag 60.34 vs 59.89; 9 Ghansali 50.38 vs 50.18; 10 Deoprayag 54.94 vs 54.71; 11 Narendranagar 62.18 vs 61.99; 12 Pratapnagar 49.99 vs 49.81; 13 Tehri 55.03 vs 54.93; 14 Dhanaulti 65.89 vs 65.48; 15 Chakrata 68.24 vs 68.57; 16 Vikasnagar 75.74 vs 75.46; 17 Sahaspur 72.98 vs 72.7; 18 Dharampur 57.35 vs 57.22; 19 Raipur 61.33 vs 61.36; 20 Rajpur Road 57.75 vs 57.73; 21 Dehradun Cantonment 56.89 vs 56.72; 22 Mussoorie 60.01 vs 59.66; 23 Doiwala 68.06 vs 67.85; 24 Rishikesh 62.21 vs 62.09; 25 Haridwar 64.89 vs 64.23; 26 BHEL Ranipur 69.08 vs 69.32; 27 Jwalapur 79.35 vs 79.3; 29 Jhabrera 78.42 vs 78.4; 30 Piran Kaliyar 77.44 vs 77.47; 31 Roorkee 63.1 vs 63.05; 32 Khanpur 76.85 vs 76.65; 33 Manglaur 75.95 vs 75.58; 35 Haridwar Rural 81.94 vs 81.95; 36 Yamkeshwar 53.94 vs 52.99; 37 Pauri 51.82 vs 51.44; 38 Srinagar 59.71 vs 59.4; 39 Chaubattakhal 45.33 vs 44.86; 40 Lansdowne 48.12 vs 47.38; 41 Kotdwar 65.92 vs 65.46; 42 Dharchula 62.74 vs 62.03; 43 Didihat 64.01 vs 62.58; 44 Pithoragarh 62.15 vs 61.49; 45 Gangolihat 55.39 vs 54.88; 46 Kapkot 63.71 vs 62.94; 47 Bageshwar 62.4 vs 61.96; 48 Dwarahat 52.72 vs 52.2; 49 Salt 45.92 vs 46.05; 50 Ranikhet 51.8 vs 51.9; 51 Someshwar 56.92 vs 56.63; 52 Almora 59.19 vs 59.42; 53 Jageshwar 56.07 vs 55.91; 54 Lohaghat 58.96 vs 58.56; 55 Champawat 66.8 vs 66.46; 56 Lalkuan 72.56 vs 71.61; 57 Bhimtal 65.44 vs 65.29; 58 Nainital 55.25 vs 54.98; 59 Haldwani 65.65 vs 65.71; 60 Kaladhungi 68.25 vs 68.31; 61 Ramnagar 69.15 vs 67.8; 62 Jaspur 74.39 vs 73.53; 63 Kashipur 64.26 vs 63.95; 64 Bajpur 72.04 vs 71.96; 65 Gadarpur 75.64 vs 75.59; 66 Rudrapur 68.24 vs 68.83; 67 Kichha 71.66 vs 71.57; 68 Sitarganj 78.64 vs 78.56; 70 Khatima 76.63 vs 75.57. The results table's turnout is higher than the recomputed one in most ACs (by up to about 1.4 points), which is what a denominator of general electors alone would give; the electors kept here are the larger Wikipedia AC-article figures, read as general plus service. Not resolved without the Commission's table.

## Disagreements between sources, and what was kept

- AC 12 Pratapnagar: margin IndiaVotes 2,341, Wikipedia results table 2,340, Wikipedia AC article margin 2,341. Kept IndiaVotes (2,341): the Wikipedia table's own winner and runner-up votes give a margin of 2,341, and the AC article's margin agrees with IndiaVotes.
- AC 16 Vikasnagar: margin IndiaVotes 5,193, Wikipedia results table 4,563, Wikipedia AC article margin 5,193. Kept IndiaVotes (5,193): the Wikipedia table's own winner and runner-up votes give a margin of 5,193, and the AC article's margin agrees with IndiaVotes.
- AC 24 Rishikesh: winner_votes IndiaVotes 52,460, Wikipedia results table 52,125. Kept IndiaVotes (52,460): the Wikipedia table's own winner and runner-up votes give a margin of 18,722, and the AC article's margin agrees with IndiaVotes.
- AC 29 Jhabrera: runner_up_votes IndiaVotes 31,436, Wikipedia results table 31,346. Kept IndiaVotes (31,436): the Wikipedia table's own winner and runner-up votes give a margin of 8,306, and the AC article's margin agrees with IndiaVotes.
- AC 29 Jhabrera: margin IndiaVotes 8,216, Wikipedia results table 8,036, Wikipedia AC article margin 8,216. Kept IndiaVotes (8,216): the Wikipedia table's own winner and runner-up votes give a margin of 8,306, and the AC article's margin agrees with IndiaVotes.
- AC 43 Didihat: runner_up_votes IndiaVotes 17,368, Wikipedia results table 14,298. Kept IndiaVotes (17,368): the Wikipedia table's own winner and runner-up votes give a margin of 6,296, and the AC article's margin agrees with IndiaVotes.
- AC 55 Champawat: margin IndiaVotes 5,304, Wikipedia results table 5,403, Wikipedia AC article margin 5,304. Kept IndiaVotes (5,304): the Wikipedia table's own winner and runner-up votes give a margin of 5,304, and the AC article's margin agrees with IndiaVotes.
- AC 57 Bhimtal: margin IndiaVotes 9,844, Wikipedia results table 9,444, Wikipedia AC article margin 9,844. Kept IndiaVotes (9,844): the Wikipedia table's own winner and runner-up votes give a margin of 9,844, and the AC article's margin agrees with IndiaVotes.
- AC 66 Rudrapur: margin IndiaVotes 19,750, Wikipedia results table 19,850, Wikipedia AC article margin 19,750. Kept IndiaVotes (19,750): the Wikipedia table's own winner and runner-up votes give a margin of 19,750, and the AC article's margin agrees with IndiaVotes.
- AC 5 Tharali: reserved readings IndiaVotes='SC', Wikipedia results table='SC', Wikipedia AC article='None'; kept 'SC'.
- AC 13 Tehri: runner_up_party: IndiaVotes prints the internal code 'UTTARAKHANDJ'; written as Wikipedia's 'UJP'.
- Matching: AC 2 Yamunotri: matched to IndiaVotes Yamunotr by winner votes, names differ.
- Matching: AC 14 Dhanaulti: matched to IndiaVotes Dhanolti by winner votes, names differ.
- Matching: AC 21 Dehradun Cantonment: matched to IndiaVotes Dehraduncant. by winner votes, names differ.
- Matching: AC 23 Doiwala: matched to IndiaVotes Doiwwala by winner votes, names differ.
- Matching: AC 26 BHEL Ranipur: matched to IndiaVotes Bhelranif'Ur by winner votes, names differ.
- Matching: AC 33 Manglaur: matched to IndiaVotes Manglor by winner votes, names differ.
- Matching: AC 36 Yamkeshwar: matched to IndiaVotes Yamakeshwar by winner votes, names differ.
- Matching: AC 38 Srinagar: matched to IndiaVotes Shrinagar by winner votes, names differ.
- Matching: AC 39 Chaubattakhal: matched to IndiaVotes Chaubatakhal by winner votes, names differ.
- Matching: AC 47 Bageshwar: matched to IndiaVotes Bageshwwar by winner votes, names differ.
- Matching: AC 56 Lalkuan: matched to IndiaVotes Lalkuwan by winner votes, names differ.
- Matching: AC 64 Bajpur: matched to IndiaVotes Bazpur (SC) by winner votes, names differ.
- Matching: AC 69 Nanakmatta: matched to IndiaVotes Nanakmata (ST) by winner votes, names differ.
- Electors: see the column note above; the per-AC IndiaVotes and Wikipedia figures are both in `uttarakhand_2022_electors_compare.csv`.

## Not covered

- Bye-elections held since the general election are not reflected (for example Champawat, May 2022, won by Pushkar Singh Dhami; this file keeps the February 2022 result).
- No Commission figure was read; party codes are IndiaVotes', AC names Wikipedia's.

## URLs

- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/purola/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/yamunotri/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/gangotri/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/badrinath/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/tharali/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/karanprayag/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/kedarnath/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/rudraprayag/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/ghanshali/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/deoprayag/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/narendranagar/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/pratapnagar/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/tehri/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/dhanolti/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/chakrata/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/vikasnagar/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/sahaspur/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/dharampur/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/raipur/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/rajpur-road/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/dehradun-cantt/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/mussoorie/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/doiwala/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/rishikesh/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/hardwar/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/bhel-ranipur/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/jwalapur/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/bhagwanpur/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/jhabrera/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/pirankaliyar/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/roorkee/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/khanpur/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/manglore/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/laksar-lhaksar/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/hardwar-rural/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/yamakeshwar/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/pauri/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/srinagar/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/chaubattakhal/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/lansdowne/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/kotdwar/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/dharchula/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/didihat/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/pithoragarh/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/gangolihat/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/kapkote/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/bageshwar/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/dwarahat/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/salt/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/ranikhet/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/someshwar/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/almora/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/jageshwar/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/lohaghat/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/champawat/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/lalkuwa/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/bhimtal/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/nainital/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/haldwani/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/kaladhungi/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/ramnagar/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/jaspur/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/kashipur/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/bajpur/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/gadarpur/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/rudrapur/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/kichha/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/sitarganj/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/nanak-matta/
- https://www.indiavotes.com/vidhan-sabha/uttarakhand/2022/khatima/
- https://en.wikipedia.org/wiki/2022_Uttarakhand_Legislative_Assembly_election
- https://en.wikipedia.org/wiki/Purola_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Yamunotri_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Gangotri_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Badrinath_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Tharali_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Karnaprayag_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Kedarnath_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Rudraprayag_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Ghansali_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Devprayag_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Narendranagar_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Pratapnagar_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Tehri_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Dhanaulti_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Chakrata_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Vikasnagar_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Sahaspur_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Dharampur_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Raipur_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Rajpur_Road_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Dehradun_Cantonment_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Mussoorie_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Doiwala_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Rishikesh_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Haridwar_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/BHEL_Ranipur_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Jwalapur_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Bhagwanpur_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Jhabrera_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Piran_Kaliyar_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Roorkee_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Khanpur_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Manglaur_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Laksar_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Haridwar_Rural_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Yamkeshwar_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Pauri_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Srinagar_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Chaubattakhal_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Lansdowne_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Kotdwar_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Dharchula_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Didihat_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Pithoragarh_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Gangolihat_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Kapkot_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Bageshwar_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Dwarahat_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Salt_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Ranikhet_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Someshwar_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Almora_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Jageshwar_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Lohaghat_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Champawat_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Lalkuan_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Bhimtal_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Nainital_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Haldwani_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Kaladhungi_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Ramnagar_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Jaspur_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Kashipur,_Uttarakhand_Assembly_constituency
- https://en.wikipedia.org/wiki/Bajpur_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Gadarpur_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Rudrapur_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Kichha_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Sitarganj_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Nanakmatta_(Uttarakhand_Assembly_constituency)
- https://en.wikipedia.org/wiki/Khatima_(Uttarakhand_Assembly_constituency)


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
