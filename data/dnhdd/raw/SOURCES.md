# Dadra and Nagar Haveli and Daman and Diu sources

ceodaman.nic.in fails TLS verification from the sandbox (incomplete certificate chain); one
Firecrawl scrape of its home page found no SIR document listed. The Dadra and Nagar Haveli
district site (dnh.gov.in, S3WaaS) answers plain HTTPS and carries the ERO's draft press note.
The Daman and Diu district sites refused the sandbox.

## Documents (in `sources/`)

- `ero_dnh_press_note_draft_20260710.pdf`: press note No. ADM/Election/SIR-2026/2026/215 of
  10/07/2026 by the Electoral Registration Officer, 2-Dadra and Nagar Haveli PC,
  https://cdn.s3waas.gov.in/s35878a7ab84fb43402106c575658472fa/uploads/2026/07/17839213888692.pdf .
  Scanned; read by eye. Roll on 04/06/2026 291672, forms collected 205998, and a chart: deceased
  5581 (1.91%), permanently shifted 13118 (4.50%), untraceable/absent 64473 (22.10%), duplicate
  2084 (0.71%), EF collected 70.63%. Primary.
- `ero_dnh_form5_notice_20260710.pdf`: Form 5 notice of the draft for the same PC. No figures.
- `timesofindia_draft_extract.txt`: https://timesofindia.indiatimes.com/india/30-deletions-in-daman-diu-sir-draft-roll/articleshow/132323298.cms ,
  the UT's shares from the CEO's statement.
- `deccanherald_final_extract.txt`: https://www.deccanherald.com/india/sir-dadra-nagar-haveli-and-daman-diu-sees-3088-voter-drop-highest-among-4-final-rolls-no-transgender-voter-named-in-list-4147035 ,
  the UT's roll before, draft and final, the final by sex.

## Files

- `pc_draft_20260710.csv`: the one sub-UT row found, 2-Dadra and Nagar Haveli PC. `other` is
  blank because the chart shows none.
- `state.csv`.

## Checks

- UT roll before less draft 428036 - 301142 = 126894, 29.65%; TOI's shares (22.5 + 4.6 + 1.7 +
  0.6 + 0.2 = 29.6) agree within rounding.
- Final by sex 145809 + 150024 + 0 = 295833: OK. Draft less final 5309; fall from the roll
  before 132203, 30.89% (DH prints 30.88).
- DNH PC: 291672 - 205998 = 85674 left off; the four reasons on the chart sum to 85256, **418
  short**, presumably the "others" the chart does not show. Recorded as printed. The chart's
  percentages match the counts over 291672.
- Daman and Diu PC by subtraction (not a source): roll before 136364, draft 95144, left off 41220.
  Not written to a CSV.

## Gaps

- No press note or table for 1-Daman and Diu PC; no district table (Dadra and Nagar Haveli, Daman,
  Diu).
- No final roll by PC or district, no additions or deletions after the draft, no notices.
- UT reasons are known only as shares of the roll (TOI); counts were not found.
