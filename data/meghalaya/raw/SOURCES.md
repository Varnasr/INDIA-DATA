# Meghalaya: sources and checks

Read on 2026-10-06. Primary throughout: the Election Department, Government of Meghalaya
(the office of the Chief Electoral Officer), whose numbered press notes EL.63/2026/nn are
posted at https://meghalaya.gov.in/meghalaya/sites/default/files/press_release/EL_63_2026_nn.pdf,
and the PIB release of the same note.

## Files

| file | what it holds | source | how read |
|---|---|---|---|
| `ac.csv` | per AC (all 60): BLOs, electors before the revision, names left off (Total ASDD) and its five reasons (death, untraceable, shifted, EF refused, duplicate), electors mapped as self, as progeny and with no mapping; `draft` is computed as roll_before - left_off and equals self + progeny + no mapping in every AC | "SIR Status Report as on 05-08-2026", pages 6 to 8 of press note No.EL.63/2026/29 of 5 August 2026, https://meghalaya.gov.in/meghalaya/sites/default/files/press_release/EL_63_2026_29.pdf (`sources/ceo_press_note_EL63_2026_29_draft_20260805.pdf`) | curl, PDF tables extracted with pymupdf `find_tables`; percentage columns read but not written (they are recomputable) |
| `district_printed.csv` | the 12 printed district subtotal rows of the same table, kept to check the AC rows against | same | same |
| `state.csv` | state figures: roll before, the five reasons, draft by sex, mapping; notices (no mapping, discrepancy), cases completed, ineligible so far and electors parked for the final roll as on 1 October; Forms 6, 7 and 8 received | EL.63/2026/29 (above) and the PIB release https://www.pib.gov.in/PressReleasePage.aspx?PRID=2295108 of 5 August 2026 (`sources/pib_2295108_20260805.txt`, text extracted); EL.63/2026/37 of 5 August ("Key Findings of Enumeration Phase", https://ceomeghalaya.nic.in/press-notes/pn_draft_pub_5_8_2026.pdf, `sources/ceo_press_note_EL63_2026_37_key_findings_20260805.pdf`); EL.63/2026/87 of 1 October 2026 (`sources/ceo_press_note_EL63_2026_87.pdf`) | curl, PDF text |

Also saved, read for the state figures over time: EL.63/2026/25 (30 July), 45 (11 Aug),
50 (18 Aug), 56 (25 Aug), 62 (1 Sept), 70 (8 Sept), 76 (15 Sept), 83 (29 Sept). Several are
scans with an OCR text layer, read from that layer; no figure from them is in a CSV except
through `state.csv`, whose values were also found in EL.63/2026/87 or EL.63/2026/29.

District names in `ac.csv` are written out in full from the table's abbreviations
("EAST JAINTIA" is East Jaintia Hills, "SOUTH WEST" South West Khasi Hills, "SOUTH WEST
GARO" South West Garo Hills, "EASTERN WEST" Eastern West Khasi Hills). The AC-to-district
assignment was compared by eye with the CEO's "Information on Assembly Constituencies within Districts"
(https://ceomeghalaya.nic.in/epic-per-status/epic-per-status.pdf), read but not saved, and agrees.

## What is not published

- **No split by sex of the names left off**, at any level. Draft by sex is a state figure only.
- **The final roll is not out.** It was due 7 October 2026; ECI Press Note ECI/PN/121/2026 of
  30 September moved it to 26 October 2026 (stated in EL.63/2026/87).
- Notices, hearings and ineligible cases are state totals; EL.63/2026/83 says a district-wise
  review was held but prints no district table.
- Notice counts moved: the discrepancy list was 4,28,858 (total 6,51,644) in the notes of
  11, 18 and 25 August and 1 September, and 4,28,949 (total 6,51,735) from 8 September.
  The 1 October figures are in `state.csv`; 1,194 found ineligible is interim.
- On 25 August hearings were suspended by the District Magistrate in 14 of the 17 East Khasi
  Hills ACs (all but 26 Shella, 27 Pynursla, 28 Sohra), per EL.63/2026/56.

## Checks run

- PASS: ac: ACs of each of the 12 districts sum to the printed district total, all 12 count columns
- PASS: ac: 60 ACs sum to the printed Grand Total in all 12 count columns
- PASS: district_printed: 12 district totals sum to the printed Grand Total
- PASS: Grand Total equals the press note: 23,49,645 before, 1,80,402 left off, 81,490 dead, 45,011 untraceable/absent, 42,532 shifted, 4,668 refused/other, 6,701 duplicate
- PASS: ac: five reasons sum to Total ASDD in every AC (failing [])
- PASS: district_printed: five reasons sum to Total ASDD in every district
- PASS: ac: self + progeny + no mapping = roll before - ASDD (the draft) in every AC
- PASS: state: sum of AC drafts = 21,69,243 (press note draft) (2169243)
- PASS: ac: printed percentages agree with counts / Total Electors to printed precision (6 of 240 differ by 0.05; each is a value like 32.845 printed 32.9, i.e. rounded to 2 dp then to 1 dp; counts unaffected) ([(20, 'pct_self', '32.9', 32.845), (25, 'pct_self', '34.9', 34.849), (35, 'pct_progeny', '50.6', 50.547), (50, 'pct_progeny', '41.7', 41.645), (50, 'pct_no_mapping', '11.7', 11.649), (54, 'pct_self', '38.7', 38.646)])
- PASS: Note: Total BLO column sums to 3,637, the post-rationalisation polling stations (the AC table on epic-per-status.pdf gives pre-rationalisation stations)
- PASS: state: roll before - draft = left off
- PASS: state: reasons sum to left off
- PASS: state: draft by sex sums to draft
- PASS: state: self + progeny + no mapping = draft (the note says "out of the total 23,49,645" but the three sum to the draft)
- PASS: state: notices no mapping + discrepancy = total (1 Oct figures)
- PASS: state: Form 6 + 7 + 8 shifting + 8 correction = 23,259
- PASS: Note: 30 July note EL.63/2026/25 gave interim figures that differ slightly: ASDD 1,80,404, EF not returned 45,013, self 7,75,337, progeny 11,69,670, no mapping 2,24,234; the 5 August figures are kept

## Constituency to district (`ac_district.csv`, 13 October 2026)

The constituency table names no district. Each constituency's district is taken from
Wikipedia's list of constituencies of the Meghalaya Legislative Assembly, which cites the
Chief Electoral Officer's constituency map. `build_states.py` accepts the map only because
every district's constituencies add up exactly to the district table here in the roll before,
the names left off, each reason and the draft. Ri Bhoi is spelt Ri-Bhoi to match that table.
