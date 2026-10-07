# Andaman and Nicobar Islands sources

The CEO's sites (ceo.andamannicobar.gov.in, ceoandaman.nic.in) refused the sandbox. The CEO's
final-roll statement of 21/02/2026 is read from its reproduction on the front page of The Daily
Telegrams (the Andaman and Nicobar Administration's daily, "Source: CEO, A&N Islands"), posted
as an image by the Administration's X account (@Andaman_Admin) and fetched through
api.fxtwitter.com and pbs.twimg.com on 2026-10-06. Read by eye from crops enlarged 2.5 times.
Counted as primary=false (a reproduction), though it is the government's own newspaper.

## Documents (in `sources/`)

- `daily_telegrams_20260222_front_page_ceo_final.jpg`: https://x.com/Andaman_Admin/status/2025442063752511792 .
  The draft by sex, Forms 6/6A, 8 and 7 admitted by sex, the final by sex, the final by district
  and by tehsil.
- `andaman_admin_x_post_20260222.json`: post text.
- `hindustantimes_20251223_extract.txt` (https://www.hindustantimes.com/india-news/nearly-21-voters-may-get-deleted-after-sir-in-andaman-nicobar-101766517677944.html):
  names left off the draft by district and tehsil group, from the CEO's data.
- `thenewsmill_ani_20251223_extract.txt` (ANI), `nicobartimes_20251223_extract.txt`,
  `business_standard_pti_20260221_extract.txt`: the reasons, the 25407 unmapped, the 411 booths,
  and the final statement as reported.

## Files

- `tehsil_final_20260221.csv`: final roll by tehsil and sex (nine tehsils in three districts).
- `district_final_printed_20260221.csv`: the district subtotals as printed.
- `district_left_off_draft_press.csv`: names left off the draft by district and tehsil group
  (press, primary=false). Only totals; no reasons or sex below the UT.
- `state.csv`.

## Checks

- Roll before less draft 310404 - 246390 = 64014: OK. Nicobar Times prints 3,10,444 forms
  distributed, 40 more; every other source and the arithmetic give 310404.
- Reasons 9191 + 51906 + 2917 = 64014: OK.
- Draft by sex 124911 + 121476 + 3 = 246390: OK.
- Districts left off 51801 + 8717 + 3496 = 64014: OK; South Andaman 44502 + 7299 = 51801 and
  Nicobar 1401 + 2095 = 3496: OK.
- Additions 14427 + 2474 + 18 = 16919 and deletions 72 + 5197 = 5269: OK.
- Walk 246390 + 16919 - 5269 = 258040: OK; men 124911 + 6940 + 1170 + 7 - 1 - 44 - 2568 = 130415
  and women 121476 + 7487 + 1304 + 11 + 1 - 28 - 2629 = 127622: OK; third gender 3 throughout.
- Tehsil table: every row adds by sex; tehsils sum to each printed district subtotal and to the
  grand total 130415 / 127622 / 3 / 258040: OK.

## Gaps

- No district or tehsil table of the roll before or the draft, and no reasons below the UT.
- Notices: only the 25407 unmapped at the draft (already in data/india/raw/notices/notices.csv);
  no logical-discrepancy count and no count of names deleted after notices separately from the
  5197 "deletion due to shifting within and outside state + SIR verification".
