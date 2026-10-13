# Tamil Nadu raw tables: sources

All files fetched 2026-10-01. One row per assembly constituency (AC 1 to 234)
unless stated. Aggregates only: no list of individual electors was opened or
stored.

## asd_ac.csv

Absent, shifted and dead electors (the names removed at the draft roll), by AC.

- Source: https://www.elections.tn.gov.in/ACwise_ASD.aspx ("AC wise Absent /
  Shifted /Dead Electors - SIR 2026"), via Firecrawl (country IN).
- Columns: district, ac, ac_name, dead, shifted_absent, multiple, total.
  `dead` is the page's "Deceased", `shifted_absent` its "Shifted/ Absent",
  `multiple` its "Enrolled at multiple places". District appears on the first
  AC of each block on the page and is carried down. Per-district Total rows
  are dropped.
- Assertions passed: 234 rows; ACs 1 to 234 each once; total = dead +
  shifted_absent + multiple in every row; all 38 district Total rows equal the
  sum of their ACs; column sums equal the GRAND TOTAL row, 2,694,672 dead,
  6,644,881 shifted/absent, 398,278 multiple, 9,737,831 total.
- Odd: the page lists districts out of AC order (Ariyalur, Tiruppur and the
  newer districts come at the end). AC names are spelt as the page spells
  them, and four differ from the roll tables: 11 "Dr.Radhakrish Nagar"
  (truncated), 45 "Kilvaithikuppam", 169 "Nanilam", 227 "guneri" (truncated
  Nanguneri). Not corrected. The page footer says "Last Updated : Jan 07,
  2025", which is a stale template line.
- Draft roll total (54,376,756) plus these removals (9,737,831) is 64,114,587,
  the implied roll before the revision.

## draft_roll_ac.csv

Electors by sex on the draft roll of 19.12.2025.

- Source: https://www.elections.tn.gov.in/ACwise_Gendercount_19122025.aspx
  ("AC wise Electors as per Draft Roll (19/12/2025)"), linked from
  https://www.elections.tn.gov.in/SIR_2026.aspx. Via Firecrawl.
- Columns: ac, ac_name, district, men, women, third, total.
- Assertions passed: 234 rows, ACs 1 to 234 once each; total = men + women +
  third in every row; column sums equal the page's Total row, 26,663,233 men,
  27,706,332 women, 7,191 third gender, 54,376,756 total. (This page carries
  no per-district totals.)

## final_roll_ac.csv

Electors by sex on the final roll of 23.02.2026.

- Source: https://www.elections.tn.gov.in/ACwise_Gendercount_23022026.aspx
  ("AC wise Electors as per Final Roll (23/02/2026)"). Via Firecrawl.
- Same columns. `<br>` inside two names (140, 141) replaced by a space.
- Assertions passed: 234 rows; row sums; all 38 district Total rows equal the
  sum of their ACs; column sums equal the Grand Total row, 27,738,925 men,
  28,960,838 women, 7,617 third gender, 56,707,380 total.
- AC names and districts are identical to the draft roll table in every row.
  The final roll is larger than the draft in every one of the 234 ACs.
- Not fetched: the SIR page also links a later table,
  https://www.elections.tn.gov.in/ACwise_Gendercount_07042026.aspx (roll of
  07.04.2026, presumably the roll the election was held on), and
  ASD_19122025.aspx, Districtwise_Gendercount_* and Age_Cohort_07042026.aspx.

## results_2026.csv and results_2026_candidates.csv

Assembly election, results declared May 2026.

- Source: https://results.eci.gov.in/ResultAcGenMay2026/ConstituencywiseS22{ac}.htm
  for ac 1 to 234 (every candidate's EVM, postal and total votes, NOTA, Total
  row), and the statewise pages statewiseS221.htm to statewiseS2212.htm
  (winner, runner-up, party, margin, status). Fetched directly with curl
  (results.eci.gov.in answered plain requests from the sandbox).
- results_2026.csv columns: ac, ac_name (as ECI spells it, upper case),
  winner, winner_party, winner_votes, runner_up, runner_up_party,
  runner_up_votes, margin, total_votes (all candidates including NOTA,
  postal included), nota_votes, postal_votes. Winner and runner-up are the two
  highest non-NOTA candidates on the constituency page.
- results_2026_candidates.csv: every row of every constituency table (4,257
  rows including NOTA), columns ac, ac_name, candidate, party, evm_votes,
  postal_votes, total_votes.
- Assertions passed: 234 rows; status "Result Declared" in all 234; in every
  AC the candidate totals sum to the page's Total row, EVM + postal = total for
  every candidate and for the Total row, exactly one NOTA row; winner,
  winner party, runner-up, runner-up party and margin from the constituency
  page equal the statewise page in all 234 (after collapsing repeated
  spaces); margin = winner_votes - runner_up_votes in every row. Winners by
  party: TVK 108, DMK 59, AIADMK 47, INC 5, PMK 4, IUML 2, CPI 2, VCK 2,
  CPI(M) 2, BJP 1, DMDK 1, AMMK 1. State total votes polled 49,324,121.
- Missing: electors are not shown on these pages, so there is no electors
  column. Total votes are 87.0% of the 23.02.2026 final roll statewide (70.8%
  to 95.7% by AC); the 07.04.2026 roll was not fetched. ECI's disclaimer says
  the page is as filled by Returning Officers and the final figures are in
  Form 20.
- Odd: three ECI names differ in spelling from the CEO roll tables: 39
  SHOLINGUR (Sholinghur), 50 TIRUPPATTUR (Tirupattur), 178 GANDHARVAKOTTAI
  (Gandarvakkottai). Same AC numbers, not renamed.

## results_2021.csv

Assembly election of April 2021, for which party held each seat before the
revision.

- Source: TCPD Lok Dhaba candidate-level file for Tamil Nadu 2021 (built from
  the ECI statistical report), as mirrored by OpenCity:
  https://data.opencity.in/dataset/74f05dff-eac3-4e2b-80cd-3382e9c190d5/resource/5ca1808c-4b8a-4fa6-957e-409e690f509d/download/b89dceb3-b295-4d9b-af6d-b71d2a86ee49.csv
  (dataset page https://data.opencity.in/dataset/tamil-nadu-assembly-elections-2021).
  The ECI 2021 results pages (results.eci.gov.in/Result2021/...) return 404,
  and old.eci.gov.in and the CEO Form 20 page reset the connection, so the
  ECI file itself was not reached.
- Columns: ac, ac_name (CEO roll spelling), ac_name_source (TCPD spelling),
  winner, winner_party, winner_votes, runner_up, runner_up_party,
  runner_up_votes, margin, valid_votes, electors. Party codes are TCPD's:
  ADMK = AIADMK, CPM = CPI(M).
- Assertions passed: 234 rows, one poll per AC (no bye-elections in the
  file); positions 1 and 2 present in every AC; margin = winner_votes -
  runner_up_votes in every row and equal to the file's own Margin column;
  candidate votes sum to Valid_Votes in every AC. Winners by party: DMK 133,
  ADMK 66, INC 18, PMK 5, VCK 4, BJP 4, CPI 2, CPM 2, which is the declared
  2021 result.
- Cross-check against Wikipedia's results table
  (https://en.wikipedia.org/wiki/2021_Tamil_Nadu_Legislative_Assembly_election):
  winner party agrees in all 234 apart from labels (CPI(M) for CPM; AC 96
  Tiruchengodu, where Wikipedia shows KMDK for a candidate who won on the DMK
  symbol). Margins differ in 10 ACs: 20, 37, 39, 68, 112, 116, 132, 136, 147,
  159, 206. In five of those (39, 68, 112, 116, 136) Wikipedia's margin does
  not equal its own winner minus runner-up votes, so the error is on that
  side; the TCPD figures are kept. Runner-up party also differs at AC 186
  (TCPD CPI, Wikipedia CPI(M)); not resolved.
- The CEO page https://www.elections.tn.gov.in/TNLA2021_MLA.aspx was read but
  not used as the source: it is the list of sitting MLAs at some later date,
  not the 2021 result. It shows AC 233 Vilavancode as "Vaccant", AC 98 Erode
  (East) with the 2023 bye-election winner, and its page title says 2016.

## Not done

- No district-level or age-cohort tables were taken.
- Nothing in the repository outside data/tamilnadu/raw/ was changed.

## Two more rolls by constituency and sex (added 2026-10-13)

- `election_roll_20260406_ac.csv`: the roll of 06.04.2026, the roll the 2026
  election was held on, from https://www.elections.tn.gov.in/ACwise_Gendercount_07042026.aspx
  (CEO). 234 rows; men, women and third gender add to the total in every row;
  the 38 district rows and the grand total agree; the grand total is
  5,73,43,291, the figure of the CEO's Press Note 16. It leaves out service
  electors. It is larger than the final roll of 23.02.2026 in every seat
  (6,35,911 in all). Turnout on the pages is votes over this roll.
- `roll_20250106_ac.csv`: the final roll of 06.01.2025 (Special Summary
  Revision 2025), from https://www.elections.tn.gov.in/ACwise_Gendercount_06012025.aspx
  (CEO). 234 rows with SC and ST seats marked (44 and 2); every row adds up;
  the district rows and grand total agree (3,11,74,027 men, 3,24,29,803 women,
  9,120 third gender, 6,36,12,950). It is 5,01,637 smaller than the roll of
  27.10.2025, so the fall from it to the draft is never called the names
  removed. The build asserts that no seat's men or women rose from it to the
  draft.

Both were fetched through Firecrawl from an Indian address on 2026-10-13 and
parsed by a script that checks every identity above before writing.
