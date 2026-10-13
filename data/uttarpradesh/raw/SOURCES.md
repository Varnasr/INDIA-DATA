# Uttar Pradesh raw tables: sources

All files fetched 2026-10-03. Aggregates only: no list of individual electors
was opened, downloaded or counted. `check.py` in this folder asserts everything
listed under "Assertions passed" below.

## The Chief Electoral Officer's site could not be reached

ceouttarpradesh.nic.in serves Indian networks only, as far as can be told from
here. Every attempt failed:

- `https://ceouttarpradesh.nic.in/`, `/SIR.aspx`, `/default.aspx`,
  `/171_AC_Statistics_English.aspx`: curl through the sandbox proxy, connection
  reset (the proxy logs `ws_closed_mid_exchange` for ceouttarpradesh.nic.in:443).
- `http://ceouttarpradesh.nic.in/` and `http://www.ceouttarpradesh.nic.in/`:
  HTTP 503.
- Firecrawl, default, stealth, enhanced and basic proxies, with and without
  country IN: `ERR_TUNNEL_CONNECTION_FAILED`, or 503 from cache
  (`/rollpdf/rollpdf.aspx`, cached 2026-09-16).
- Wayback Machine (through Firecrawl; web.archive.org is blocked to curl here):
  the CDX index of ceouttarpradesh.nic.in holds two captures after
  2025-10-01, both 302 redirects of `171_AC_Statistics_English.aspx` and
  `266_AC_Statistics_English.aspx`, and nothing for the SIR.

So no constituency table of any kind was read: not the roll before the
revision, not the draft roll, not the names left off, not the final roll. The
CEO's press note of 06.01.2026 (below) says booth-wise copies of the draft were
uploaded to the site; whether the CEO also published AC-wise statistics could
not be checked. **`asd_ac.csv`, `draft_roll_ac.csv` and `final_roll_ac.csv`,
which `check.py` expects, do not exist.**

Other places tried for AC figures:

- eci.gov.in: `/sir/`, `/sir/f3/`, `/sir/f3/S24/` and
  `voters.eci.gov.in/download-eroll?stateCode=U01` answer **406** (AppTrana
  "Request was blocked due to suspicious behavior"). The ECI press-release list
  (`/issue-details-page/press-releases`) renders through Firecrawl; its API
  (`/api/get-file`) takes encrypted parameters and a secret header and was not
  pursued. The backend download links (`eci-backend/public/api/download?url=…`)
  do work with curl.
- District sites (gorakhpur.nic.in, lucknow.nic.in, maharajganj.nic.in,
  amroha.nic.in, unnao.nic.in, lalitpur.nic.in) publish the draft roll, the
  ASD lists and the uncollectable-forms lists **by AC and part, with names**.
  These are lists of individual electors. **Not opened.** AC totals could in
  principle be counted from them; that was not done.
- A secondary compilation of the fall from the 27.10.2025 roll to the final
  roll for all 403 ACs exists at
  https://click2public.com/up-sir-2026-voter-roll-changes-across-403-assembly-constituencies/
  (a political consultancy; no source document named; its headline "total cut
  1.47 crore" does not match the state's own 2.04 crore). Read, **not used**.

## asd_district.csv

The names left off the draft roll, by reason, for all 75 districts, with each
district's roll of 27.10.2025 and draft roll.

- Source: a photograph, published by India TV on 06.01.2026, of a two-page
  table headed "Uttar Pradesh Special Intensive Revision 2026, Status of
  Electors in Draft Roll as on 06-01-2026", columns "Total Electors as on
  27-10-2025", "Total Electors as on 05-01-2026", and "Uncollectable Forms
  Reason": Death, Untraceable/Absent, Permanently Shifted, Already Enrolled,
  Others, Total, each with a percentage, plus a "State-" row. File:
  https://getapi.indiatvnews.com/doc/pu.pdf (2 pages, one JPEG each, 1240 x
  1653), linked from
  https://www.indiatvnews.com/uttar-pradesh/up-sir-draft-voter-list-top-three-districts-where-maximum-number-of-voters-have-been-removed-2026-01-06-1024693.
  The layout and the State row match the CEO's press note of the same day, so
  this is taken to be the CEO's handout. **It is a photograph carried by the
  press, not a file from the CEO's site**: flag it so.
- Transcribed by eye from the images (upscaled); the percentage columns were
  not transcribed. On the second page (districts 42 to 75) the paper is curled,
  so the right-hand columns drift by up to a row against the names; values
  were assigned in column order and every row is held by the checks below.
- Columns: sno (the table's own S. No., 1 to 75), district (as the table spells
  it), roll_before, draft, dead, untraceable_absent, shifted, multiple (the
  table's "Already Enrolled"), others, total, source.
- Assertions passed: 75 rows, sno 1 to 75; in every row roll_before - draft =
  total, **and** dead + untraceable_absent + shifted + multiple + others =
  total (two independent identities, so a misread digit in any of the eight
  numbers fails at least one); every column sums exactly to the printed State
  row: 15,44,30,092 before, 12,55,56,025 draft, 46,23,796 dead, 79,52,190
  untraceable/absent, 1,29,77,472 shifted, 25,47,207 already enrolled,
  7,73,402 others, 2,88,74,067 total. The 75 names equal the districts of
  `results_2022.csv` once "Kheri" is read as "Lakhimpur Kheri".
- No split by sex or age. The draft column is dated 05-01-2026 in the header;
  its state total equals the published draft of 06.01.2026.
- The press note's "shifted/absent 2.17 crore" (14.06%) is untraceable/absent
  plus permanently shifted plus others: 2,17,03,064, which is 14.05% of the
  roll. Without "others" it would be 2.09 crore. The press note's footnote
  describes the bucket as electors not found, shifted, or whose forms were not
  returned by 26.12.2025, which is where "others" belongs.
  The pie in the press note: 46.23 lakh dead, 2.17 crore shifted/absent,
  25.47 lakh multiple. 46.23 + 209.30 + 25.47 + 7.73 = 288.74 lakh.

## sir_state_summary.csv

State totals. Columns: item, date, men, women, third, total, kind
(`primary` or `press`), source. Several items carry two or three sources;
the check requires them to agree.

Primary:

- ECI daily bulletin, 11.12.2025 (PIB, release 2202423),
  https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2202423 (the
  `PressReleaseDetail` URL renders empty without JavaScript; the iframe URL
  works with curl). Electors as on 27.10.2025: 15,44,30,092. Same figure in ECI
  bulletin No. ECI/SIR/DB/1/2025 of 12.11.2025,
  https://eci.gov.in/eci-backend/public/api/download?url=LMAhAK6sOPBp%2FNFF0iRfXbEB1EVSLT41NNLRjYNJJP1KivrUxbfqkDatmHy12e%2FzOS%2BIOmr%2FtOeSK8w38bI0zVpeBXSsnQZZ9%2F7T4x79iAaxz3pCCbxjKAdMEF%2FhNLcRMWx%2BzZqaZugBnaOJXu4MPg%3D%3D
- CEO press note No. 08/CEO-6, 06.01.2026, Hindi, 4 pages,
  https://getapi.indiatvnews.com/doc/up-draft-er-hindi.pdf (the CEO's
  letterhead; mirrored by India TV, the CEO's own copy unreachable). Text in a
  Kruti Dev font; page 1 read from a rendering. 15,44,30,092 on the roll of
  27.10.2025, of whom 12,55,56,025 returned forms by 26.12.2025; dead 46.23
  lakh (2.99%), shifted/absent 2.17 crore (14.06%), multiple 25.47 lakh
  (1.65%), all rounded; 15,78,483 Form 6 received to date. It gives the claims
  period as 06.01 to 06.02.2026 and the final roll as 06.03.2026; both were
  later extended.
- CEO UP's own Instagram account (ceo_up), post of 13.04.2026,
  https://www.instagram.com/p/DXEa2dkEuo7/ (read from the page's meta
  description with curl; Firecrawl refuses Instagram). Draft of 06.01.2026 by
  sex: 6,88,43,159 men, 5,67,08,747 women, 4,119 third gender, 12,55,56,025;
  18-19 year olds 3,33,981. Final of 10.04.2026: 7,30,71,061 men, 6,09,09,525
  women, 4,206 third gender, 13,39,84,792; 18-19 year olds 17,63,360. Net rise
  84,28,767 (42,27,902 men, 42,00,778 women, 87 third gender). Schedule as
  carried out: claims 06.01 to 06.03.2026, notices and hearings to 27.03.2026,
  final 10.04.2026.
- The district handout above, State row: the five reasons and 2,88,74,067.

Press (state totals only):

- The New Indian Express, 10.04.2026,
  https://www.newindianexpress.com/india/2026/Apr/11/up-final-voter-list-at-1339-crore-after-revision-over-2-crore-names-deleted,
  quoting the CEO: 8,15,996 removed between 06.01 and 10.04.2026, of which
  3,50,026 for not answering notices, "3.28 lakh" shifted, 79,076 multiple,
  55,865 dead, 2,069 under age or not citizens. Notices to 3.26 crore. The
  itemised exact figures leave 3,28,960 for "shifted", which matches 3.28 lakh.
  Same 8,15,996 in the Times of India and Zee News.
- The Hindu (PTI), 07.03.2026,
  https://www.thehindu.com/news/national/uttar-pradesh/uttar-pradesh-sir-forms-including-names-deletion-in-claims-objections-period/article70715531.ece,
  quoting the CEO's press conference of 07.03.2026: Form 6 in the claims
  period 70,69,810 (34,96,911 men, 35,72,603 women, 296 third gender); Form 6
  since 27.10.2025 86,69,073; Form 7 in the claims period 2,68,682 and since
  27.10.2025 3,18,140. **For Form 7 the split by sex is of the electors whose
  deletion was sought**, not of the applicants. Also reported there and not
  tabulated: notices to 3.26 crore (1.4 crore unmapped to the 2003 roll, 2.02
  crore logical discrepancies), Form 8 22,55,473.

Assertions passed: men + women + third = total for every row that has them;
repeated items agree across sources; roll before - draft = 2,88,74,067 =
removed; forms collected = draft; the five reasons sum to the removed; final -
draft = net rise; the removed equal the district table's State row.

What this means for `data/india/raw/states.csv`: the Uttar Pradesh row
(2.89 crore; 46.23 lakh dead; 2.17 crore shifted and absent; 25.47 lakh
duplicates; source Times of India, flagged rounded and press) can be replaced
by exact primary figures: 2,88,74,067; dead 46,23,796; shifted, absent or other
2,17,03,064 (79,52,190 + 1,29,77,472 + 7,73,402); enrolled more than once
25,47,207. The sum is exact, so the split is complete. Not changed here: that
file is outside this folder.

## press_ceo.csv

The Chief Electoral Officer's figures as the press carried them, one row each,
with the verbatim sentence they come from. Fetched 2026-10-13.

- Hindustan Times, 18.01.2026 (CEO Navdeep Rinwa):
  https://www.hindustantimes.com/cities/lucknow-news/155-million-vs-13-4-million-names-of-more-women-than-men-deleted-in-uttar-pradesh-draft-electoral-rolls-101768679003877.html
  Names left off by sex, rounded (1.55 crore women, 1.34 crore men); women per
  1,000 men on the roll (877 in 2025, 824 on the draft); women over 25 at their
  father's address (71.18 lakh checked, 42.15 lakh left off, 29.4 lakh kept,
  which add to 71.55 lakh, so the parts and the total disagree by 37,000);
  urban and rural rolls before and at the draft (4.16 and 2.99 crore urban,
  11.28 and 9.56 crore rural); notices 3.26 crore (1.04 crore not linked to
  2003, 2.22 crore with discrepancies, which add up); 493 EROs and 8,751 AEROs
  for the hearings.
- **A misprint, kept out.** The report prints the rural fall as "1.27 crore".
  Its own rolls give 1.72 crore, and 1.72 is 15.23% of 11.28, the percentage
  it prints beside it, so 1.27 is a transposition. The build uses the
  difference of the rolls.
- The Hindu, 07.03.2026, hearings held for about 2.80 crore by that date.

So "No split by sex of the names left off" below is no longer true for the
state. Below the state there is still none.

`scripts/build_uttarpradesh.py` reads these and writes `analysis.json`: the
split by sex and area, the notices per officer (an average over the 66 days
from 21.01 to 27.03.2026, never a hearing's length), the removals after the
draft by reason (3,28,960 shifted is what the itemised figures leave of
8,15,996), the district names left off spread over each constituency by its
2022 electors (`data/india/raw/assembly/uttarpradesh_2022.csv`, the ECI's
statistical report) against its 2022 margin, written to `seats.csv`, and the
district circumstances read from the factors and urban pages' own files.

## Not found

- Any table by assembly constituency (roll before, draft, ASD, final). See
  above.
- The roll of 27.10.2025 by sex, at any level.
- The names left off by sex below the state, or by age at any level. The
  state split by sex is the CEO's rounded figure in the press (above).
- The final roll by district or AC. The New Indian Express names only the five
  districts and five ACs with the largest rise after the draft (Prayagraj
  3,29,421; Sahibabad 82,898, and so on); not tabulated.
- Claims and objections by district or AC.

## Not done

- Nothing outside data/uttarpradesh/raw/ was changed.
- No individual-elector list was opened, including the district ASD, draft
  and uncollectable-forms lists.
- `results_2022.csv` was not touched. Its existing assertion that votes agree
  with vote shares fails in 32 ACs; that failure predates this work.
