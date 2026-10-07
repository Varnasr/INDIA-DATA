# Lakshadweep sources

All documents from ceolakshadweep.gov.in with plain HTTPS (curl, browser user agent, one or two
retries after connection resets) on 2026-10-06. Scanned PDFs rendered to PNG and read by eye.

## Documents (in `sources/`)

- `ceo_press_note_draft_20251216.pdf`: CEO press note F.No.16/10/2025-ELE/SIR of 16/12/2025,
  publication of the draft roll. Page 2: "Details of electors", island by island: forms printed
  and distributed (the roll on 27/10/2025), dead, permanently shifted, already enrolled,
  untraceable/absent, refused to sign, no-mapping cases, total, and electors in the draft.
  URL: https://ceolakshadweep.gov.in/Users/download_pdf_draft_roll_2024/UHJlc3MgTm90ZS0gUHVibGljYXRpb24gb2YgRHJhZnQgRWxlY3RvcmFsIFJvbGwgKDEpLnBkZg==
- `ceo_press_release_20251212.pdf`: CEO press release of 12/12/2025, "Details of electors as per
  ECINET as on 12.12.2025", the same table without the no-mapping column, with polling stations
  per island. URL: .../MTc2NTUzOTI0NF80ZjExYzQ1NjAyMjgyYjliZDliMy5wZGY=
- `ceo_press_note_final_20260214.pdf`: CEO press note of 14/02/2026 on the final roll: draft by
  sex, Forms 6/6A, 7 and 8 admitted by sex, the final by sex.
  URL: .../UHJlc3MgTm90ZSAtIFNJUiAyMDI2IEZpbmFsIFJvbGwgUHVibGljYXRpb24gYW5kIGRpc3RyaWJ1dGlvbi5wZGY=
- `deo_press_note_claims_20260101.pdf`: DEO press note of 01/01/2026, claims and objections
  16/12/2025 to 31/12/2025 by form. URL: .../cHJlc3Mgbm90ZSAtIGRpc3RyaWJ1dGlvbiBvZiBzdGF0dXRvcnkgZm9ybXMucGRm
- Not saved (7.7 MB): "Pres Note Key findings of the Enumeration Phase in Lakshadweep (Updated)",
  16/12/2025, .../UHJlcyBOb3RlICBLZXkgZmluZGluZ3Mgb2YgdGhlIEVudW1lcmF0aW9uIFBoYXNlIGluIExha3NoYWR3ZWVwIChVcGRhdGVkKS5wZGY= .
  Chart only: EF collected 56384, deceased 705, shifted/absent/others 252, multiple places 472.

## Files

- `island_draft_20251216.csv`: one row per island (the UT has one district and one parliamentary
  constituency; islands are the only unit below it). Columns from the 16/12/2025 table; polling
  stations from the 12/12/2025 table. `no_mapping` is a separate column in the source and is not
  part of `left_off`.
- `island_printed_totals.csv`: the printed total rows of both tables.
- `state.csv`.

## Checks

- Every island: roll before less draft equals the printed total, and dead + shifted + already
  enrolled + absent + refused equals it too: OK in all 10 rows. Adding the no-mapping column
  would break every row but Bitra, so it is not counted in the total.
- Columns sum to the printed totals: 57813, 705, 210, 472, 41, 1, 267, 1429, 56384; polling
  stations 64: OK.
- The 12/12/2025 table prints Kalpeni "already enrolled" as 6; the 16/12/2025 table prints 16.
  16 is the value that makes Kalpeni's row and the printed column total (472) add up. The CSV
  uses the 16/12/2025 value.
- Draft by sex 28574 + 27810 = 56384; final 29222 + 28385 = 57607: OK.
- Draft + 1269 + 1 - 47 = 57607: OK; men 28574 + 672 + 1 - 25 = 29222 and women
  27810 + 597 - 22 = 28385: OK.
- DEO claims 16 to 31 December: 401 + 6 + 269 + 2003 + 1 + 0 = 2680: OK.

## Gaps

- No count of notices or hearings for the 267 no-mapping cases, and no final roll by island.
- No split of the names left off by sex.
