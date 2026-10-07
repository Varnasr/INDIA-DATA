# Mizoram: sources and checks

Read on 2026-10-06. Primary throughout: the Chief Electoral Officer, Mizoram's press
notes, listed at https://ceo.mizoram.gov.in/show-all-data/press-release. Each note is
issued in Mizo and in English; the Mizo draft note carries the district table and the
reasons, the English one does not.

## Files

| file | what it holds | source | how read |
|---|---|---|---|
| `district_draft.csv` | draft roll of 4 July 2026 per district (11), men and women (no third-gender column printed) | Press note No. H.11018/2/2024-CEO of 4 July 2026 (Mizo), para 13, https://ceo.mizoram.gov.in/storage/press-releases/July_2026/01KWPBBZRST6PJEWCKV628GVGK.pdf (`sources/ceo_press_note_draft_20260704_mizo.pdf`) | curl, PDF text; every row matched against the text by script |
| `district_final.csv` | final roll of 7 September 2026 per district by sex | Press note No. H.11011/06/2026-CEO of 7 September 2026, English https://ceo.mizoram.gov.in/storage/press-releases/September_2026/01M1XFVV4G2XCZA15M3W40KESR.pdf and Mizo https://ceo.mizoram.gov.in/storage/press-releases/September_2026/01M1XFX40J7CMCPHFAGZ1JWX2X.pdf (`sources/ceo_press_note_final_20260907_*.pdf`) | curl, PDF text; every row matched in both |
| `draft_age.csv` | draft roll by age band (state) | 4 July Mizo note, para 14 | PDF text |
| `state.csv` | roll before, names left off and five reasons, draft by sex, service electors, additions and deletions after the draft, final by sex, the AC with most forms not collected | 4 July notes (Mizo above; English https://ceo.mizoram.gov.in/storage/press-releases/July_2026/01KWPBE4VP2HKAZT95503YKFK2.pdf, `sources/ceo_press_note_draft_20260704_english.pdf`) and the 7 September notes | PDF text |

## What is not published

- **Nothing below the state for the names left off.** No district or AC table of the 46,162,
  its reasons, or its sex. The only sub-state figure is the AC with the most forms not
  collected: 19-Aizawl South II, 2,351 (8.23%).
- **No roll before by district**, so district rates of removal cannot be computed. The
  district comparison available is draft against final, which is the change after the draft
  (additions and deletions together).
- No AC tables. The 7 September note gives single AC facts only (largest, smallest, largest
  rise, largest fall, sex ratio).
- **No notice counts** (no mapping or discrepancy) found in any Mizoram note, and no hearing
  counts.
- A Government of Mizoram DIPR post for Aizawl district ("Uncollectible: 20,269", with an
  Annexure-I of reasons) refused the sandbox and Firecrawl (403); not read, not used.

## Checks run

- PASS: district_draft transcription matches the PDF text of the 4 July Mizo press note, row by row
- PASS: district_draft: men + women = total in every district (the table prints no third-gender column)
- PASS: district_draft: districts sum to printed state total 3,99,025 / 4,29,881 / 8,28,906 ((399025, 429881, 828906))
- PASS: district_final transcription matches the PDF text of both 7 September press notes (English and Mizo), row by row
- PASS: district_final: men + women + third gender = total
- PASS: district_final: districts sum to printed state total 4,03,179 / 4,32,689 / 1 / 8,35,869 ((403179, 432689, 1, 835869))
- PASS: Sum over districts of (final - draft) = net rise 6,963 (39,243 added - 32,280 deleted) (6963)
- PASS: Note: districts whose final roll is below the draft ([('Kolasib', -1397), ('Lunglei', -1636), ('Khawzawl', -20)])
- PASS: draft_age: eight age bands sum to printed total 8,28,906 (828906)
- PASS: state: roll before - draft = left off (8,75,068 - 8,28,906 = 46,162) (46162)
- FAIL: state: five reasons sum to left off 46,162 (reasons sum to 46163, which equals the 4 July printed 46,163 but is 1 more than 46,162 (FAILS by 1; printed numbers kept))
- PASS: state: English 4 July note chart: shifted/absent 22,311 = untraceable 8,333 + shifted 13,978 (others 309 shown nowhere in the chart)
- PASS: state: draft men + women = draft (no third-gender figure printed for the draft)
- PASS: state: draft + added - removed = final
- PASS: state: final by sex sums to final
- PASS: Note: 7 Sept note says 35-West Tuipui went from 16,477 to 14,677 (-1,800) but also that its final roll is 14,667, the lowest; 16,477 - 1,800 = 14,677; the two printed finals differ by 10

The one failure: the 4 July note's five reasons (21,295 + 8,333 + 13,978 + 2,248 + 309)
sum to 46,163, and the note prints that total, but 8,75,068 - 8,28,906 = 46,162, which is
the figure the 7 September note gives. Both are kept as printed; `left_off` is 46,162.
