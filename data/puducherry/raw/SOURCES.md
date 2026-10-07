# Puducherry sources

ceopuducherry.py.gov.in answers plain HTTPS, but its press-release archive now holds only
September 2026 items; the SIR press notes are no longer listed. The CEO's own X account
(@ceopuducherry) carries the final-roll press release as images; they were fetched through
api.fxtwitter.com (post JSON) and pbs.twimg.com (images) on 2026-10-06 and read by eye.

## Documents (in `sources/`)

- `ceo_press_release_final_20260214_p1.jpg`, `_p2.jpg`, `_annexure.jpg`: CEO Puducherry press
  release No. E.1-5/SIR-2026 of 14/02/2026, posted at https://x.com/ceopuducherry/status/2022544949041074407 .
  Primary (the CEO's own document). Page 1: roll on 27/10/2025, names removed in the draft, the
  draft by sex, additions and deletions after the draft by sex and route, the final by sex.
  Page 2: final by region. Annexure: final by AC and sex.
- `ceo_x_post_20251216.json`: CEO X post of 16/12/2025 (press briefing); text only, image is a
  photograph of the briefing. Prints shifted 80615 and duplicate 2100, and "Lowest: Mahe - 898".
- `ceo_ac_wise_electoral_statistics_20260916.html`: https://ceopuducherry.py.gov.in/ac_wise_electrol.php
  as fetched on 2026-10-06 (AC-wise electors as on 16/09/2026).
- `deccanherald_20251216_extract.txt`, `indianexpress_20251217_extract.txt`,
  `thehindu_20251216_extract.txt`, `hindustantimes_20251216_extract.txt`: article text from the
  draft-day reports (curl), quoting the CEO's statement of 16/12/2025.

## Files

- `ac_final_20260214.csv`: final roll of 14/02/2026 by AC, region and district, by sex,
  transcribed by eye from the annexure image. Primary.
- `printed_totals_final_20260214.csv`: the region, district and state totals the release prints.
- `district_left_off_draft_press.csv`: names left off the draft by district and reason, from the
  press (primary=false). Deccan Herald gives two groups, labelled "Puducherry" and "Mahe and
  Yanam"; Indian Express gives the same totals as Puducherry district 85531 and Karaikal 17936,
  and The Hindu gives the draft as 7.66 lakh in Puducherry district and 1.51 lakh in Karaikal.
  The labels in both papers are muddled (Indian Express also attaches the second group's reasons
  to "Mahe and Yanam"). The file takes the second group as Karaikal district, which is what the
  Indian Express total says and what the draft sizes support; Mahe and Yanam are part of
  Puducherry district. `draft_rounded` is The Hindu's rounded figure.
- `ac_roll_20260916.csv`: AC-wise electors on 16/09/2026 (after supplements; not the SIR final),
  parsed from the CEO page.
- `state.csv`.

## Checks

- Roll before less draft: 1021578 - 918111 = 103467: OK.
- Reasons as reported by three papers 20798 + 80645 + 2024 = 103467: OK. The CEO's X post
  (20798 + 80615 + 2100 = 103513) is 46 over; not used.
- Draft by sex 431301 + 486673 + 137 = 918111: OK.
- Walk to the final: 918111 + 41492 + 1227 + 0 - 858 - 15761 = 944211: OK; for men
  (431301 + 19474 + 366 - 6 - 482 - 7058 = 443595), women (486673 + 22012 + 861 + 4 - 376 - 8697
  = 500477) and third gender (137 + 6 + 0 + 2 - 0 - 6 = 139): OK.
- Additions 41492 + 1227 = 42719 and deletions 858 + 15761 = 16619, as para 3 prints: OK.
- Final AC table: men + women + TG = total in all 30 rows; ACs sum to every printed region total
  (Puducherry 721296, Karaikal 155515, Mahe 29736, Yanam 37664), both district totals
  (788696, 155515) and the state (443595 / 500477 / 139 / 944211): OK.
- District split of the draft removals: each row's reasons add to its total, and the two rows sum
  to the state totals for every reason: OK.
- 16/09/2026 AC table: rows by sex OK; sums to the printed district and UT totals: OK.

## Below the state: what was looked for

- No CEO table of the roll before, the draft or the names left off by AC or district was found.
  The draft-roll page (draftelectrol_rolls.php) leads to part-wise roll PDFs of named electors
  and the ASD page (voters2025) is a search of named electors; neither was used.
- Press (Hindustan Times, 16/12/2025): most uncollectable forms in Ozhukarai (6139), fewest in
  Bahour (1651). The Hindu and the CEO's X post name Kamaraj Nagar, Raj Bhavan and Karaikal North
  and South as highest and Mahe (898) or Mahe and Bahour as lowest. These disagree with each
  other and are not tabulated.
- No count of notices or hearings was found. The New Indian Express (17/12/2025) quotes the CEO:
  about 71,500 people not linked to an earlier SIR were included in the draft and would need a
  document.
- The note in data/india/raw/final.csv that the 1227 were "marked as shifted outside the union
  territory" does not match the primary release: row 3 is Form 8 from electors who shifted in
  **from** other states, an addition, and the walk adds up with it.
