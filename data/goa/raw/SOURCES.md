# Goa sources

All CEO documents were downloaded from ceogoa.nic.in with plain HTTPS (curl, browser user agent) on 2026-10-06.

## Documents (in `sources/`)

- `ceo_goa_press_note_final_20260221.pdf`: CEO Goa press note of 21/02/2026 on the final roll,
  https://ceogoa.nic.in/PDF/SIR2026/press-note-Final-publication.pdf . Text PDF, read with pymupdf.
  Roll on 27/10/2025 by sex, the five reasons for forms not returned, the draft by sex, mapping
  (self, progeny, unmapped), the five logical-discrepancy categories, claims and objections,
  additions, deletions on forms and after notices, and the final roll by sex.
- `ceo_goa_press_note_draft_20251216.pdf`: CEO press note of 16/12/2025, "Key Findings of
  Enumeration Phase", https://ceogoa.nic.in/PDF/SIR2026/SIR_PNN14.pdf . Scanned; pages rendered
  to PNG and read by eye. Chart: EF collected 1084992; deceased 25574; shifted/absent 72471;
  enrolled at multiple places 1997.
- `ceo_goa_press_note_20251213.pdf`: CEO press note of 13/12/2025, https://ceogoa.nic.in/PDF/SIR2026/SIR_PNN12.pdf .
  An earlier count, before the draft: 1084956 collected, 100078 uncollectable (dead 25574,
  absent 29750, shifted 40473, already enrolled 2008, other 2273); 182855 not mapped.
  Kept for the record; state.csv uses the later figures.
- `ceo_goa_daily_bulletin_20260120.pdf`: CEO daily bulletin of 20/01/2026 (claims and objections
  to 19/01/2026), https://ceogoa.nic.in/PDF/SIR2026/SIR_DB35.pdf . Text PDF.
- `ceo_goa_state_profile_20261006.html`: the CEO's State Profile page as fetched on 2026-10-06,
  https://ceogoa.nic.in/appln/UIL/StateProfile.aspx .

## Files

- `state.csv`: state figures with their source.
- `ac_roll_20260701.csv`: AC-wise general electors by sex "as on 1st July 2026 (qualifying date)",
  from the State Profile page, parsed from the HTML. This is the roll after the SIR and after
  supplements 2 and 3. It is **not** the SIR final roll of 21/02/2026, and the page shows no
  AC figures for any earlier date. Goa now has three districts (North Goa, South Goa, and
  Kushavati, ACs 36 to 40), as the page prints them.

## Checks

- Roll before by sex 573853 + 611168 + 13 = 1185034: OK.
- Draft by sex 523304 + 561679 + 9 = 1084992: OK. Final by sex 511436 + 546121 + 9 = 1057566: OK.
- Roll before less draft = 100042 = forms not returned: OK.
- Reasons 25574 + 29729 + 40469 + 1997 + 2273 = 100042: OK.
- Mapped 489629 + 412960 = 902589; mapped + unmapped 182403 = 1084992 (draft): OK.
- Logical-discrepancy categories 3348 + 41116 + 7197 + 3830 + 3432 = 58923: OK.
- Deletions after the draft 3812 + 35780 = 39592: OK. Draft + 12166 - 39592 = 1057566 (final): OK.
- By sex, the names left off are men 50549, women 49489, third gender 4 (roll before less draft).
- AC table, 1 July 2026: men + women + third gender = total in all 40 rows; the ACs sum to each
  printed district total (North Goa 503782, South Goa 422600, Kushavati 145624) for every column,
  and to the state 1072006 / 518333 / 553664 / 9, which the page also prints: OK.
- The 13/12/2025 note's reasons (25574 + 29750 + 40473 + 2008 + 2273 = 100078) add to its own total;
  they differ from the final counts by 36 (absent -21, shifted -4, duplicate -11).

## Below the state: what was looked for

- No district or AC table of the roll before, the draft, the names left off or the final roll was
  found on ceogoa.nic.in (press notes 03/11/2025 to 21/02/2026, daily bulletins, SIR 2026 page,
  draft and final roll pages, Format 9-11B page, Form Status Count page).
- The draft and final roll pages and the Format 9/10/11 pages are lists of named electors and
  applicants; they were not opened beyond the page listing and nothing from them is used.
- Press (Indian Express, 17/12/2025, from the CEO's data): North Goa 44639 and South Goa 55403
  names left off the draft (sum 100042). Times of India (17/12/2025): Vasco had the most
  deletions, then Cortalim, Fatorda, Santa Cruz, Taleigao, Margao and Panaji; Sanguem the fewest,
  then Sanquelim, Bicholim, Mandrem, Priol, Poriem and Mayem; South Goa 10764 more than North
  Goa (consistent with 55403 - 44639 = 10764). These are press figures and are recorded here only.
- The Wayback Machine could not be reached from the sandbox, so earlier versions of the State
  Profile page (which may have carried AC figures for 21/02/2026) could not be checked.
