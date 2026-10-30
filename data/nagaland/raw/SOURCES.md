# Nagaland: sources and checks

Read on 2026-10-06. The draft was published on 20 September 2026; the final roll was due
22 November 2026. The Free Press Journal, carrying ANI, reported on 30 October 2026 that the
Commission moved it on 29 October to 30 November 2026, with notices to be decided by
25 November
(https://www.freepressjournal.in/mumbai/ec-extends-sir-deadline-in-maharashtra-4-other-states-final-rolls-on-nov-30-delhis-on-dec-22).
The News Minute and Business Today of 30 October report the same final date.

## Files

| file | what it holds | source | primary | how read |
|---|---|---|---|---|
| `state.csv` | roll before (13,57,208), forms collected, dead, absent/shifted/others (one category), duplicate, draft roll general and service electors by sex as printed | Press note No. ELE/REV-15/2026 of 20 September 2026, "Nagaland Special Intensive Revision (SIR): Key findings of Enumeration phase", https://ceo.nagaland.gov.in/media/sir2026/PressNoteSIR20092026.pdf (`sources/ceo_press_note_ELE_REV-15_2026_20260920.pdf`) | yes | curl (the CEO site resets some connections from the sandbox), scanned PDF with OCR layer, the table on page 4 read from the rendered image |
| `district_status_20260913.csv` | per election district (17): total electors (the roll before), forms distributed, digitised, submitted online, and uncollectable, as of 13 September 2026 18:00, one day before house visits ended | "SIR Status Report as on 13-09-2026 18:00:00", Office of the Chief Electoral Officer, Nagaland. Seen only as an image posted by the CEO on X (@NAGALANDCEO) and carried by The Morung Express, 13 September 2026, https://morungexpress.com/sir-in-nagaland-157-lakh-efs-uncollectable-with-house-visits-ending-sept-14 (image `sources/ceo_sir_status_report_20260913_via_morung_express.png`, article text `sources/morung_express_20260913.txt`) | **no**: a CEO table, but seen only in the press | image transcribed by eye at 1.5x zoom; every row checked against the printed percentage columns |

`sources/morung_express_20260920.txt` (https://www.morungexpress.com/around-158-lakh-electors-fall-under-asdd-categories-in-nagaland-sir)
says in so many words that the CEO "has not released district wise figures for the final
draft roll".

## Reading the district table

The table is **interim**: 1,57,451 uncollectable on 13 September against 1,57,752 left off
at the draft. Its rows are uncollectable forms, not removals, and carry no reasons. Use them
as the nearest district measure the state has published, and say both things wherever they
appear.

## The draft by sex does not add up, as printed

The draft table prints general electors as 6,73,864 men, 6,83,344 women, 0 third gender,
total 11,99,456. The men and women sum to 13,57,208, the roll **before** the revision, not
to the draft. Each by-sex column then adds the service electors correctly (6,73,864 + 6,883 =
6,80,747; 6,83,344 + 118 = 6,83,462), so the total row inherits the error: 6,80,747 + 6,83,462
= 13,64,209 against a printed 12,06,457. The figures are kept as printed, with `_printed` in
the item name, and should not be used as the draft by sex. The Morung Express (20 September)
repeats them as the draft by sex.

## What is not published

- No district or AC table of the names left off at the draft, its reasons, or its sex.
- The three reasons are dead 28,944, absent/permanently shifted/others 1,23,749 (one
  category) and duplicate 5,059; the note prints no total, so `left_off` (1,57,752) is
  computed as roll before less forms collected and equals the three.
- Notices: only a press figure (about five lakh expected, The New Indian Express,
  21 September 2026), already in `data/india/raw/notices/notices.csv`. No CEO count found.

## Checks run

- PASS: district_status_20260913: 17 districts sum to the printed Total row in all five columns ((1357208, 1357208, 1198989, 969, 157451) vs (1357208, 1357208, 1198989, 969, 157451))
- PASS: district_status_20260913: digitized + uncollectable = total electors (holds exactly in 12 of 17 districts; in 5 a remainder of forms is neither digitized nor uncollectable, 768 state-wide, which reads as forms still pending on 13 Sept; no district goes negative) (remainders [('Phek', 264), ('Zunheboto', 65), ('Mon', 12), ('Noklak', 48), ('Shamator', 379)]; state 768)
- PASS: district_status_20260913: printed uncollectable % = uncollectable / total electors
- PASS: district_status_20260913: printed digitized % = digitized / total electors
- PASS: Interim vs final: uncollectable 1,57,451 on 13 Sept against 1,57,752 left off at the draft (difference 301); district rows are interim and cannot be checked against the final count
- PASS: state: dead + absent/shifted/other + duplicate = roll before - EFs collected (1,57,752) (157752)
- FAIL: state: draft general men + women + TG = draft general 11,99,456 (FAILS: 6,73,864 + 6,83,344 = 1357208, which is the pre-SIR roll 13,57,208, not the draft; printed numbers kept)
- FAIL: state: draft total men + women = 12,06,457 (FAILS: 1364209 (inherits the error above))
- PASS: state: general + service = total, by column (men 6,73,864 + 6,883 = 6,80,747; women 6,83,344 + 118 = 6,83,462; total 11,99,456 + 7,001 = 12,06,457)
- PASS: state: service men + women = service total
- PASS: state: printed percentages 88.38 / 2.13 / 9.12 / 0.37 of 13,57,208 ([88.38, 2.13, 9.12, 0.37])
