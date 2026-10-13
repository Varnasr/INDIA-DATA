# Manipur: sources and checks

Read on 2026-10-06. Every table below is the Chief Electoral Officer, Manipur's own,
from ceomanipur.nic.in. All are primary. The SIR page (https://ceomanipur.nic.in/sir.aspx)
links the four tables and the press notes.

## Files

| file | what it holds | source | how read |
|---|---|---|---|
| `ac_roll_before.csv` | electors per AC before the revision (the electors to be enumerated), with the AC's district, 60 rows | "Total Numbers of Electors to be Enumerated: District-wise Assembly Constituencies and Total Electors", an HTML table on https://ceomanipur.nic.in/sir.aspx; district subtotals and a grand total of 20,93,076 printed in it. Saved as `sources/ceo_sir_page_electors_to_be_enumerated.txt` (the table text only; the page also links a search of the named list of electors left off, so the page itself is not saved) | curl, HTML parsed |
| `ac_final.csv` | final roll of 06-09-2026 per AC by sex, with district and PC | "AC Wise Elector Count - Final Publication 2026", https://ceomanipur.nic.in/Documents/SIR/AC%20Wise%20Elector%20Count%20Final%20Publication%202026.pdf (`sources/ceo_ac_wise_elector_count_final_2026.pdf`) | curl, PDF text layer (pymupdf) |
| `district_final.csv` | final roll per district by sex | "District Wise Elector Count - Final Publication 2026", https://ceomanipur.nic.in/Documents/SIR/District%20Wise%20Elector%20Count%20Final%20Publication%202026.pdf (`sources/ceo_district_wise_elector_count_final_2026.pdf`) | curl, PDF text layer |
| `district_elector_population.csv` | the CEO's projected population by sex beside the final roll by sex, and the elector-population ratio, per district | "SIR Elector-Population Ration, Final Electoral Roll 2026", https://ceomanipur.nic.in/Documents/SIR/SIR%20Elector%20Population%20Data%202026.pdf (`sources/ceo_sir_elector_population_data_2026.pdf`). The table does not say what year or source its population is | curl, PDF text layer |
| `state.csv` | state figures: roll before by sex, the five reasons, draft by sex, mapping, notices, ineligible after hearing, claims, additions and deletions after the draft, final by sex, service electors | Press note No. e-Roll-101/6/2025-ELEC-ED of 6 September 2026, https://ceomanipur.nic.in/Documents/PressNote/2026-2027/PRESS%20NOTE%20SIR%20FINAL%20EROLL%202026.pdf (`sources/ceo_press_note_final_20260906.pdf`); press note of 5 July 2026 (draft), https://ceomanipur.nic.in/Documents/PressNote/2026-2027/SIR%20Draft%20Publication%20Press%20Release%202026.pdf (`sources/ceo_press_note_draft_20260705.pdf`) | curl; the 6 September note is a scan with no text layer, rendered to PNG and read by eye; the 5 July note has a text layer, and its figures are a chart whose legend was read by eye |

Also saved, not transcribed: `sources/ceo_sir_gender_ratio_final_2026.pdf` ("SIR Gender
Ratio: Final Elector Roll, 2026", https://ceomanipur.nic.in/Documents/SIR/SIR%20Gender%20Ratio%20Final%20Elector%20Roll%202026.pdf),
which repeats the district final roll by sex with women per 1,000 men; it is used only as a check.

## What is not published

- **No table of the names left off below the state.** The 1,58,677 and its five reasons
  (absent 34,740, shifted 72,473, dead 43,000, duplicate 7,394, others 1,070) are state
  figures only. The CEO's "ASDD" service is a search of the named lists by AC and part and
  was not opened.
- **No draft roll by AC or district.** So the AC-level comparison available is roll before
  (ac_roll_before) against final (ac_final), which mixes the draft removals with the
  additions and deletions after it. It must not be called the removals.
- No AC or district split of notices, hearings, or the 56,871 added and 30,650 deleted after the draft.
- The roll before is by sex only for the state (10,10,317 men, 10,82,459 women, 300 third gender).
- The date of the roll before: the press note says "as on 18-05-2026 i.e. prior to draft
  publication"; the SIR page table carries no date, but sums to the same 20,93,076.

## Checks run

- PASS: ac_roll_before: 60 ACs sum to printed grand total 20,93,076 (sum 2093076, printed 2093076)
- PASS: ac_roll_before: Imphal West ACs sum to printed district total (sum 390196, printed 390196)
- PASS: ac_roll_before: Imphal East ACs sum to printed district total (sum 331602, printed 331602)
- PASS: ac_roll_before: Bishnupur ACs sum to printed district total (sum 188054, printed 188054)
- PASS: ac_roll_before: Thoubal ACs sum to printed district total (sum 209628, printed 209628)
- PASS: ac_roll_before: Chandel ACs sum to printed district total (sum 44745, printed 44745)
- PASS: ac_roll_before: Ukhrul ACs sum to printed district total (sum 97571, printed 97571)
- PASS: ac_roll_before: Senapati ACs sum to printed district total (sum 150097, printed 150097)
- PASS: ac_roll_before: Tamenglong ACs sum to printed district total (sum 79196, printed 79196)
- PASS: ac_roll_before: Churachandpur ACs sum to printed district total (sum 193418, printed 193418)
- PASS: ac_roll_before: Jiribam ACs sum to printed district total (sum 32171, printed 32171)
- PASS: ac_roll_before: Kangpokpi ACs sum to printed district total (sum 110290, printed 110290)
- PASS: ac_roll_before: Kakching ACs sum to printed district total (sum 119260, printed 119260)
- PASS: ac_roll_before: Tengnoupal ACs sum to printed district total (sum 45139, printed 45139)
- PASS: ac_roll_before: Kamjong ACs sum to printed district total (sum 36207, printed 36207)
- PASS: ac_roll_before: Noney ACs sum to printed district total (sum 30166, printed 30166)
- PASS: ac_roll_before: Pherzawl ACs sum to printed district total (sum 35336, printed 35336)
- PASS: ac_final: men + women + third gender = total in every AC (failing ACs [])
- PASS: ac_final: men column sums to printed total (sum 953350, printed 953350)
- PASS: ac_final: women column sums to printed total (sum 1006962, printed 1006962)
- PASS: ac_final: third_gender column sums to printed total (sum 308, printed 308)
- PASS: ac_final: final column sums to printed total (sum 1960620, printed 1960620)
- PASS: ac_final: printed total equals press note final roll 19,60,620 (9,53,350 / 10,06,962 / 308) ([953350, 1006962, 308, 1960620])
- PASS: AC names agree between the roll-before table and the final table (one spelling differs: 39 Sugnu in the roll-before table, Sugnoo in the final table; same AC number and district, kept as printed) (differs: [(39, 'Sugnu', 'Sugnoo')])
- PASS: District of each AC agrees between the two tables (differs: [])
- PASS: Sum over ACs of (roll before - final) = 20,93,076 - 19,60,620 = 1,32,456 (132456)
- PASS: State: 1,58,677 left off - 56,871 added + 30,650 deleted: 20,93,076 - 1,58,677 + 56,871 - 30,650 = 19,60,620 (1960620)
- PASS: Note (not a failure test): ACs whose final roll exceeds the roll before (5 ACs: [(26, 'Bishenpur', 273), (30, 'Lilong', 36), (35, 'Khangabok', 107), (38, 'Hiyanglam', 158), (39, 'Sugnoo', 819)])
- PASS: district_final: men sums to printed total (sum 953350, printed 953350)
- PASS: district_final: women sums to printed total (sum 1006962, printed 1006962)
- PASS: district_final: third_gender sums to printed total (sum 308, printed 308)
- PASS: district_final: final sums to printed total (sum 1960620, printed 1960620)
- PASS: district_final equals the AC final table aggregated by district (all 16, all four columns)
- PASS: district_final: men + women + third gender = total
- PASS: district_elector_population: population by sex sums to total in every district
- PASS: district_elector_population: population column sums to printed 37,71,168 (3771168 vs 3771168)
- PASS: district_elector_population: elector columns equal district_final
- PASS: district_elector_population: printed EP ratio = electors / population x 100 (to 2 dp)
- PASS: gender ratio table (16 districts): sex counts equal district_final and ratio = women per 1,000 men (16 rows; [])
- PASS: state: roll before by sex sums to total (2093076)
- PASS: state: roll before - draft = left off (158677)
- PASS: state: five reasons sum to left off (158677)
- PASS: state: draft by sex sums to draft (1934399)
- PASS: state: self + progeny + unmapped = draft (1934399)
- PASS: state: no-mapping + discrepancy notices = total notices (1221833)
- PASS: state: draft + added - removed = final (1960620)
- PASS: state: final by sex sums to final
- PASS: Note: the press note printed sex split of the left-off is not given; implied by subtraction (roll before - draft) men 69,871, women 88,799, third gender 7 (men 69871, women 88799, tg 7)

The one name difference (39 Sugnu / Sugnoo) is kept as each table prints it; join on `ac_no`.
Five ACs end with more electors than they had before the revision (Bishenpur, Lilong,
Khangabok, Hiyanglam, Sugnoo); the tables give no reason, and additions after the draft
include new electors.

## Constituency to district (`ac_district.csv`, 13 October 2026)

The district of each constituency is the Chief Electoral Officer's own, from the table of the
final publication 2026 (`ac_final.csv`), and it agrees with the table of electors to be
enumerated in all 60. `build_states.py` checks that every district's constituencies add up
exactly to the district table in the final roll, men, women and third gender.
