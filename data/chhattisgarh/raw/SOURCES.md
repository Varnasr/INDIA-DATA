# Chhattisgarh sources

Both documents are press notes of the Chief Electoral Officer, Chhattisgarh.
The CEO site (ceochhattisgarh.nic.in) refused plain curl from the sandbox
(connection reset, twice); both PDFs were read through Firecrawl's PDF parser
on 2026-10-06. Transcriptions are in `sources/`.

- **Press Release 23.12.2025, "Chhattisgarh SIR: Key Findings of Enumeration
  Phase From 04.11.2025 to 18.12.2025"** (English, 6 pages).
  https://ceochhattisgarh.nic.in/assets/pdf%20files/SIRDraftpressnote_en.pdf
  (Hindi version: .../SIRDraftpressnote_hi.pdf, not read.)
  Electors as on 27.10.2025: 2,12,30,737. Forms collected (the draft):
  1,84,95,920. Death 6,42,234; Shifted/Absent 19,13,540 (the note's footnote
  folds in electors not found, enrolled elsewhere, forms not returned by
  18.12.2025, and the unwilling); Enrolled at multiple places 1,79,043.
  State figures only.
- **Press note 21.02.2026, final publication** (Hindi, 5 pages).
  https://ceochhattisgarh.nic.in/assets/pdf%20files/PN21.02.2026FinalPublicationofERollChhattisgarh.pdf
  Final roll 1,87,30,914; net rise after the draft 2,34,994; and a table of
  all 33 districts: draft, additions, deletions, net addition, per cent net
  change, final.

## Files

- `final_district.csv`: the 21.02.2026 district table, 33 rows, no total row.
  Columns as printed: `draft`, `added` (Addition), `removed` (Deletion),
  `net_added`, `net_change_pct`, `final`. District names as printed.
- `state.csv`: the state figures from both notes.
- `sources/ceo_cg_draft_pressnote_20251223.md`,
  `sources/ceo_cg_final_pressnote_20260221.md`: transcriptions of the figures.
  The PDFs themselves could not be saved (plain download refused).

## Checks (run 2026-10-06, all pass)

- Draft note: 1,84,95,920 + 6,42,234 + 19,13,540 + 1,79,043 = 2,12,30,737,
  the printed roll before. Roll before less draft = 27,34,817 = the three
  reasons together.
- Final table: the 33 rows sum to the printed total in every column
  (draft 18,495,920; addition 343,801; deletion 108,807; net 234,994;
  final 18,730,914).
- In every row, draft + addition - deletion = final, and addition - deletion
  = net addition.
- In every row the printed per cent net change equals net/draft to two places.
- State: draft 18,495,920 + 343,801 - 108,807 = 18,730,914, the final roll.

## What was looked for and not found

- No table of the roll before or of the names left off (by reason) below the
  state, by district or by AC. The CEO's SIR page
  (https://ceochhattisgarh.nic.in/both/SIR.html) links only the named ASD list
  search (not used) and the ECI press note.
- No split by sex of the roll before, the draft, the names left off, or the
  final roll.
- No count of notices (no-mapping or logical discrepancy), hearings or
  deletions after notice. The draft note says only "more than 98% mapping".
- `data/india/raw/final.csv` describes Chhattisgarh as "net only, additions
  and removals after the draft were not published". The CEO's 21.02.2026 note
  does publish them: 3,43,801 added and 1,08,807 removed, by district.
- A Facebook post of a news page claims 3.66 lakh more names were removed
  after claims and objections. That conflicts with the CEO's 1,08,807 and is
  not used.
