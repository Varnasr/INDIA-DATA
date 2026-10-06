# Gujarat raw tables: sources

All files written 2026-10-06. Aggregates only: no list of individual electors
was opened, downloaded or counted. `check_raw.py` in this folder asserts
everything listed under "Checks" below and prints ok or FAIL for each; all 30
pass.

## The Chief Electoral Officer's site could not be reached

ceo.gujarat.gov.in gives no connection to plain curl from here. An earlier
look through Firecrawl found no SIR document on it (its What's New list stops
at July 2026 bye-election circulars). The SIR tables below are known only as
images of the CEO office's spreadsheet printouts, carried by DeshGujarat and
hosted on X's media CDN (so presumably posted by @CEOGujarat; the original
post was not found). **They are the CEO's tables as published in the press,
not files from the CEO's site**: say so on every page.

## ac.csv and district_printed_totals.csv

The names left off the draft roll, by reason, for all 182 ACs, with each AC's
roll before the revision and its draft roll.

- Source: "Assembly Constituency wise Elector Details : Draft Roll - 2026",
  4 pages ("Page 1 of 4" to "Page 4 of 4"), embedded in DeshGujarat, 20 Dec
  2025, "Gujarat Electoral Roll Revision: Assembly-wise Data on Voter
  Deletions and Total Electors",
  https://deshgujarat.com/2025/12/20/gujarat-electoral-roll-revision-assembly-wise-data-on-voter-deletions-and-total-electors/
  - page 1 (ACs 1 to 59, Kachchh to Ahmedabad): https://pbs.twimg.com/media/G8nJee5aAAAak2e?format=jpg&name=large
  - page 2 (ACs 60 to 114, Surendranagar to Anand): https://pbs.twimg.com/media/G8nJek2a8AASw0X?format=jpg&name=large
  - page 3 (ACs 115 to 172, Kheda to Tapi): https://pbs.twimg.com/media/G8nJek6bQAABC4d?format=jpg&name=large
  - page 4 (ACs 173 to 182, Dangs to Valsad, and "Total of State"): https://pbs.twimg.com/media/G8nJeejbMAArz-U?format=jpg&name=large
  - Each is 1241 x 1755; `name=orig` and `name=4096x4096` return the same
    size. sha256 prefixes: 353804aaa12802b7, 9d99e42a8650282f,
    54e80d83d8d21ff0, d7e214d4edf790ee.
- Columns in the image: Sr. No. (district), Name of District, No. & Name of
  Assembly Constituency, "Elector w.r.t 01-10-2025", Death,
  Untraceable/Absent, Permanently Shifted, Already Enrolled, Other, Total, "SIR
  Draft Roll - 2026 Electors". After each district a bold "Total of District"
  row; after the last, "Total of State".
- `ac.csv` columns: ac, ac_name (as printed, with (SC)/(ST)), district (as
  printed), before (the roll w.r.t. 01-10-2025), death, untraceable_absent,
  shifted (Permanently Shifted), already_enrolled, other, total, draft. Rows
  are in AC order. **The printout lists them in district order, so AC 33
  Prantij comes under Sabarkantha after 29 Khedbrahma, ACs 30 to 32 under
  Arvalli, and 137 to 139 under Chhota Udepur after Vadodara's 147.** The
  district column follows the printout.
- `district_printed_totals.csv`: every "Total of District" row as printed
  (level `district`, the district's Sr. No., name, the page it is on) and the
  "Total of State" row (level `state`).
- Transcribed by eye from the images, which are clean typeset printouts, not
  photographs. Every row and every subtotal passed every check on the first
  transcription; no digit had to be re-read, and none was uncertain.
- No split by sex or age, at any level. No final roll by AC.

## district.csv

- Source: "District wise Electors Details : Draft Roll - 2026", "Page 1 of 1",
  the first image in the same DeshGujarat article:
  https://pbs.twimg.com/media/G8nJa5absAE8W9_?format=jpg&name=large
  (sha256 prefix 4fd3d166350f9549). 33 districts, the same columns as the AC
  table, and a "Total of State" row identical to the AC table's.
- Transcribed separately from the AC table's district subtotals, so the check
  that they agree is a check of two transcriptions as well as of two printed
  tables.
- The article text gives the same state figures: 5,08,43,436 registered,
  4,34,70,109 forms received, 73,73,327 deleted (18,07,278 dead, 9,69,662
  untraceable or absent, 40,25,553 permanently shifted, 3,81,470 already
  enrolled, 1,89,364 other).

## final_district.csv

- Source: "District wise Addition / Deletion / Net Change : Final Roll -
  2026", embedded in DeshGujarat, 17 Feb 2026, "Final electoral roll for
  Gujarat published with 4.40 crore voters; district-wise data here",
  https://deshgujarat.com/2026/02/17/final-electoral-roll-for-gujarat-published-with-4-40-crore-voters-district-wise-data-here/
  image https://pbs.twimg.com/media/HBWTdgebcAMs1CR?format=jpg&name=medium
  (894 x 1107, the largest size served; sha256 prefix 547f44885b4c3e48).
- 34 districts: **Vav-Tharad is separate from Banaskantha** here, while the
  draft tables have 33. Columns: sno, district, draft ("Draft Roll - 2026
  Electors"), addition, deletion, net ("Net Addition"), pct ("% of Net
  Change", as printed), final ("Final Roll - 2026 Electors"). State row
  4,34,70,109 | 9,56,121 | 3,95,555 | 5,60,566 | 1.29 | 4,40,30,725. The
  article text gives the same draft and final and "approximately 5.60 lakh"
  net.
- These are **gross** additions and deletions after the draft.
  `data/india/raw/final.csv` holds Gujarat as `net only`; this table can
  replace that (not changed here: that file is outside this folder).
- **The table is inconsistent as printed, by 50 electors.** Net = addition -
  deletion in every row, and every column sums exactly to the printed state
  row, but in seven districts the printed final exceeds draft + net:
  Banaskantha by 1, Ahmedabad 25, Rajkot 1, Panchmahal 5, Dahod 6, Surat 5,
  Navsari 7. Those sum to 50, which is exactly the gap in the printed state
  row (4,34,70,109 + 5,60,566 = 4,40,30,675 against a printed 4,40,30,725).
  Each of the seven rows was re-read from a 2x enlargement; the digits are as
  printed. Kept as printed. The likeliest reading is that the final column
  carries 50 entries the addition column does not (late additions, or a
  different cut-off), but the table does not say. Use the printed final for
  the final roll and addition - deletion for the change; do not force them to
  agree.
- Vav-Tharad's draft (8,02,018) equals the draft of ACs 7 Vav, 8 Tharad and
  14 Deodar exactly, and Banaskantha's (16,03,307) the other six. No table
  names Vav-Tharad's ACs; that assignment is inferred from the exact sum (no
  other combination of Banaskantha ACs comes within 500). Treat it as
  inferred if a page relies on it.
- Nothing below the district: no final roll by AC, and no split by sex.

## results_2022.csv

The general election to the Gujarat Legislative Assembly, 1 and 5 December
2022, results 8 December 2022.

- **Not a primary source.** ECI's results pages
  (https://results.eci.gov.in/ResultAcGenDec2022/ and its
  `partywiseresult-S06.htm`, `ConstituencywiseS061.htm`) now answer 404. The
  ECI statistical report could not be reached: guessed paths under
  `www.eci.gov.in/eci-backend/public/all_files/full-statistical-reports/gujarat/...`
  (the pattern that serves Rajasthan 2023) answer 406, as do
  `/statistical-report/ae/2022` and `/gujarat-legislative-election-2022`;
  old.eci.gov.in, ceo.gujarat.gov.in, web.archive.org and
  lokdhaba.ashoka.edu.in reset the connection; OpenCity holds no Gujarat
  election dataset.
- Used instead: **IndiaVotes** ("Election results sourced from the Election
  Commission of India"), one page per AC,
  `https://www.indiavotes.com/vidhan-sabha/gujarat/2022/<slug>/` (slug in the
  `source_slug` column; the state page
  https://www.indiavotes.com/vidhan-sabha/gujarat/2022/ lists all 182),
  fetched with curl on 2026-10-06. Each page gives the electors ("Voters"),
  every candidate's votes and party (ECI abbreviations), and NOTA. Not
  Firecrawl.
- Columns: ac, ac_name (the SIR table's spelling, for joins; IndiaVotes
  spells some differently, e.g. Ellis Bridge, Dehgam, Devgadh Baria, Lunavada,
  Nijhar, Sayajiganj), winner, winner_party, winner_votes, runner_up,
  runner_up_party, runner_up_votes, margin (winner_votes - runner_up_votes),
  electors (IndiaVotes "Voters"), votes_total (all candidates plus NOTA),
  nota_votes, source_slug. Winner and runner-up are the two highest
  candidates; NOTA is not a candidate and is never runner-up.
- **Cross-checked against English Wikipedia**, "2022 Gujarat Legislative
  Assembly election", section "Results by constituency",
  https://en.wikipedia.org/w/index.php?title=2022_Gujarat_Legislative_Assembly_election&action=raw
  (fetched 2026-10-06), matched to the IndiaVotes pages by AC number:
  - the margin agrees in **all 182** ACs, and the winner's and runner-up's
    party in all 182;
  - the winner's and runner-up's votes agree in 167. In the other 15
    (39, 40, 52, 86, 98, 110, 123, 126, 128, 142, 143, 146, 168, 171, 181)
    one of Wikipedia's vote figures differs by a slipped digit (Rajula
    runner-up 63,019 against 68,019; Kaprada winner 90,399 against 90,999),
    and in every one IndiaVotes' votes give Wikipedia's own printed margin,
    so the error is in Wikipedia's vote column;
  - Wikipedia's vote shares (of all votes including NOTA) agree with
    IndiaVotes' votes over votes_total to 0.02 points for both winner and
    runner-up in 172 ACs. In the other 10 (3, 53, 115, 123, 132, 135, 150,
    156, 163, 164) one share differs by a slipped digit (Savli 57.40 against
    58.40, Jambusar 51.74 against 55.74) and the other agrees.
  - Seats: BJP 156, INC 17, AAP 5, IND 3, SP 1, the declared result.
  - Party vote totals summed from IndiaVotes equal Wikipedia's state table for
    NCP (76,949), SP (92,215), independents (11,74,108) and NOTA (5,01,202);
    INC is 86,83,966 against 86,83,969. Wikipedia's BJP (2,18,78,194) and AAP
    (2,33,671) figures are plainly wrong and were not used.
- **Not reconciled:** electors sum to 4,91,34,009 against 4,91,63,277
  "registered voters" in Wikipedia's state table (29,268 apart, perhaps
  service electors), and votes_total to 3,18,27,563 against 3,18,79,194
  "votes cast" there (51,631 apart, perhaps rejected postal ballots). Whether
  IndiaVotes' electors include service voters is not stated. The
  electors and votes_total columns therefore carry IndiaVotes' definition
  and are not certified against the ECI's own; margins, winners and
  runners-up are, through the two independent agreements above.
- Closest seats: 6 Rapar (577), 90 Somnath (922), 17 Chanasma (1,404).

## Joining to DataMeet's assembly constituency map

AC numbers here are the 2008 delimitation's, 1 to 182, the numbering of both
the SIR printout and the 2022 result. DataMeet's `India_AC.dbf`
(github.com/datameet/maps, `assembly-constituencies/`) was read for Gujarat on
2026-10-06 (attributes only; nothing was written to `data/geo`):

- 172 Gujarat shapes: 162 distinct AC_NO, and 10 with AC_NO 0 and no name
  (four in Kachchh and one each in Jamnagar and Bhavnagar district, which look
  like creek and coast polygons, plus one in Ahmadabad, one in Bharuch and two
  in Surat).
- **20 ACs have no shape of their own**: 45 to 56 (Naranpura to Asarwa,
  Ahmedabad city) and 160 to 167 (Surat North to Surat West, Surat city). They
  appear to be merged into the unnumbered Ahmadabad and Surat polygons. A map
  by AC from this file would leave both cities blank or need them drawn as one
  block each, or a different boundary source.
- Names agree with this folder's for all 162 numbered shapes once (SC)/(ST)
  and punctuation are ignored, except 77, which DataMeet calls "Jamnagar" and
  the CEO "Jamnagar Rural", and 137, truncated to "Chhota Udaipur (ST" in
  DataMeet. Join on the number, never the name: Jetpur (74 Rajkot, 138 Chhota
  Udepur), Kalol (38 Gandhinagar, 127 Panchmahal), Mahuva (99 Bhavnagar, 170
  Surat), Mandvi (2 Kachchh, 157 Surat) and Mangrol (89 Junagadh, 156 Surat)
  are each two seats.

## Checks (check_raw.py)

All pass:

- ac.csv: 182 rows numbered 1 to 182, 33 districts, nothing negative; in
  every AC the five reasons sum to the total **and** before - total = draft
  (two independent identities, so a misread digit in any of the eight numbers
  fails at least one).
- Each district's ACs sum to its printed "Total of District" row in every
  column; the 33 printed district totals sum to the printed "Total of State";
  the 182 ACs sum to it too: 5,08,43,436 before, 18,07,278 death, 9,69,662
  untraceable/absent, 40,25,553 shifted, 3,81,470 already enrolled, 1,89,364
  other, 73,73,327 total, 4,34,70,109 draft.
- district.csv: 33 districts; the same two identities in every row; equal,
  district by district and in order, to the printed subtotals of the AC table;
  columns sum to the state row.
- final_district.csv: 34 districts; net = addition - deletion in every row;
  draft + addition - deletion = final in every row except the seven recorded
  above, with exactly those gaps (any other gap fails); the printed % equals
  net / draft; columns sum to the printed state row; the printed state row is
  off by exactly those 50; the 34-district draft equals the 33-district draft
  once Banaskantha and Vav-Tharad are added; Vav-Tharad equals ACs 7, 8 and 14.
- results_2022.csv: 182 ACs numbered 1 to 182; margin = winner - runner-up > 0
  everywhere; NOTA never runner-up; votes_total covers winner, runner-up and
  NOTA and is below electors everywhere; seats by party equal the declared
  result; ac_name equals ac.csv's.

Two checks were fault-injected on a copy of the folder: one digit changed in
an AC's death count (three checks failed) and one in a district's additions
in the final table (three failed).

## Not found

- Any split by sex or age of the names left off, at any level, or of the
  draft or final roll.
- The final roll by AC.
- Claims and objections (Forms 6, 7, 8) by district or AC, and notices.

## Not done

- Nothing outside data/gujarat/raw/ was changed. `data/india/raw/states.csv`
  (electors_before rounded to 50800000; the exact figure is 5,08,43,436) and
  `data/india/raw/final.csv` (Gujarat `net only`; gross 9,56,121 added and
  3,95,555 deleted are now known) can be updated from these tables.
- No individual-elector list was opened.
