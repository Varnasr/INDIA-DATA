# Madhya Pradesh sources

**No primary document could be read.** The CEO, Madhya Pradesh
(ceoelection.mp.gov.in) lists three SIR press notes on its home page and its
Press Note page: "Press Note : Madhya Pradesh SIR : Key finding Enumeration
Phase" (`/SIR2003/PressnoteMP23122025.pdf`), its Hindi version
(`/SIR2003/Pressnote-Hindi.pdf`), and the final-publication note of 21.02.2026
(`/SIR2003/PRESS%20NOTE.pdf`). On 2026-10-06 all three return HTTP 404 (read
through Firecrawl, live fetch; plain curl to the site is refused from the
sandbox). The Wayback Machine has not archived them. Every figure here is
therefore a newspaper's report of the CEO's figures, `primary=false`.
The draft note evidently carried a district table by reason: NDTV reports
"district-wise data" from it. Only fragments of that table were found.

## Files

- `state.csv`: state figures. Roll before, draft and names left off by sex,
  and the five reasons, are from Dainik Jagran (23.12.2025), which prints the
  CEO's table. Final roll figures from ETV Bharat and Dainik Bhaskar
  (21.02.2026).
- `district_draft_press.csv`: the only district figures found: four districts
  in full or nearly (Bhopal, Indore, Jabalpur, Gwalior; Jagran) and two single
  cells (Burhanpur duplicates, Alirajpur absent; NDTV). Not a table; never sum
  it.
- `ac_press.csv`: scattered constituency figures from Dainik Bhaskar
  (21.02.2026): names left off at the draft in 11 ACs, and applications to add
  names after the draft in 20 ACs. AC numbers are left blank rather than
  guessed.
- `sources/press_extracts.md`: the figures as each article printed them.

## Checks (run 2026-10-06)

- By sex, roll before: 2,93,91,548 + 2,80,13,362 + 1,233 = 5,74,06,143. Pass.
- By sex, draft: 2,74,82,233 + 2,56,48,831 + 919 = 5,31,31,983. Pass.
- By sex, left off: 19,09,315 + 23,64,531 + 314 = 42,74,160. Pass; and each
  equals roll before less draft for that sex. Pass.
- Roll before less draft = 42,74,160. Pass.
- **Reasons: 8,46,184 + 8,42,677 + 22,78,393 + 2,76,961 + 29,927 = 42,74,142,
  18 short of 42,74,160.** Fail by 18, recorded as printed.
- Roll before less final = 34,25,078; final less draft = 8,49,082. Both match
  the printed figures. Pass.
- Districts: Bhopal's four reasons sum to 4,36,126; India Today (Facebook post)
  gives 4,38,875 deleted in Bhopal, which would leave 2,749 for "other". Not
  verifiable.

## Discrepancies with data/india/raw

- `states.csv` has the reasons in lakh (deceased 8.46, absent or shifted
  31.51, duplicate 2.77). Exact: dead 8,46,184; absent 8,42,677 plus shifted
  22,78,393 plus other 29,927 = 31,50,997; duplicate 2,76,961.
- `gender.csv` has men removed 19,08,541 and women 23,63,850 with a roll share
  of 48.59% from a sex ratio. Jagran prints men 19,09,315, women 23,64,531,
  third gender 314; women's share of the roll before was 48.80% exactly, and
  of the names left off 55.32%.
- `notices.csv` has a no-mapping count of 8,46,184 from NDTV. That number is
  exactly the count of dead electors. Jagran gives 8,65,832 electors with
  incomplete forms to be served notices, and its headline calls them
  unmapped. The 8,46,184 is probably a misreading in NDTV's copy; 8,65,832 is
  the better figure, still press.

## What was looked for and not found

- The CEO's draft and final press notes (404, not archived).
- Any full district or AC table of the roll before, the draft, the names left
  off by reason, or the final roll.
- Gross additions and deletions after the draft; final roll by sex in numbers
  (only shares). Applications to add names are reported (9,89,991), admissions
  are not.
- Notices issued, hearings, deletions after notice.
- Dainik Jagran's district figures for Jabalpur differ from a Jabalpur
  Collector's Facebook post (51,004 dead, 75,895 absent, 1,18,303 shifted),
  probably of a different date; the post was seen only as a search excerpt and
  is not used.
