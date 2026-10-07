# Arunachal Pradesh sources

Searched on 2026-10-06: ceoarunachal.nic.in (home page, press releases, the
`/sir-2026` page), the Arunachal DIPR press releases, two web searches for
district and constituency figures. **The CEO has published no table below the
state.** Its SIR page links the notification, the draft roll, the ASDD list
(named, by part; not opened, not linked here) and the statutory Form 9/10/11
lists (named). What exists below the state is what District Election Officers
told their district meetings on draft day (21 July 2026), relayed by the
DIPR and the press, for five of the 26 election districts. Nothing below the
state for the final roll, notices or hearings.

## Documents

- **CEO Arunachal Pradesh, press note No. EN/OP/SIR-01/2026, 22 September 2026.**
  https://ceoarunachal.nic.in/componenthelper/getcomponentfile/68
  Scanned, five pages numbered "of 5" (the file holds four). Downloaded with
  curl; read from the PDF's OCR text layer and checked against renderings of
  pages 1 and 3 (the OCR misreads several figures and their order, for example
  the final total as "6,96,025"; the page reads 6,96,026). Primary.
  `sources/ceo_press_note_EN-OP-SIR-01-2026_20260922.pdf`.
- **DIPR Arunachal Pradesh, "Draft Electoral Roll-2026 Published in Papum Pare;
  Political Parties Assure Full Cooperation", 22 July 2026.**
  https://arunachalipr.gov.in/post/draft-electoral-roll-2026-published-in-papum-pare-political-parties-assure-full-cooperation
  Fetched with curl; text in `sources/dipr_papum_pare_draft_20260722.txt`.
  Figures presented by the ERO of 13-Itanagar at the DEO's meeting.
  State government information department: primary=false.
- **Echo of Arunachal, "Draft E-Rolls published across Arunachal; claims and
  objections open till August 20", 21 July 2026 ("with inputs from DIPROs").**
  http://echoofarunachal.in/news_details.php?nid=38296
  Fetched with curl; text in `sources/echo_of_arunachal_draft_districts_20260721.txt`.
  Press: Tawang, Tirap, Lohit (Tezu), West Siang. primary=false.
- **The Arunachal Times, "Draft electoral rolls for Arunachal published, over
  1.69 lakh names deleted", 22 July 2026**, reporting the CEO's draft-day
  release (same state figures; staffing counts).
  https://arunachaltimes.in/article/draft-electoral-rolls-for-arunachal-published-over-1-69-lakh-names-deleted
  Text in `sources/arunachal_times_draft_20260722.txt`. primary=false.

## Files

- `state.csv`: the state figures from the CEO's press note of 22 September 2026
  (roll on 2 June 2026, five reasons, draft, mapping, notices, found
  ineligible, claims and objections, final), plus three staffing counts from
  the press.
- `ac_draft_papum_pare.csv`: the three constituencies of Papum Pare district
  (13-Itanagar, 14-Doimukh, 15-Sagalee): roll before, draft, the fall, and the
  draft by sex. From the DIPR release. Not primary.
- `district_draft_partial.csv`: five districts, each with whatever its DEO
  gave: Papum Pare (whole), Tawang (draft by sex and 3,023 left off; no roll
  before), Tirap (roll before, forms collected, left off), West Siang (roll
  before, forms digitised, five reasons; no total left off printed), and
  Lohit's single constituency 44-Tezu (draft general electors by sex and 254
  service voters). Blank where nothing was given. Not primary.

## Checks

Passed:
- Roll before by sex: 4,35,414 + 4,52,089 + 2 = 8,87,505.
- Draft by sex: 3,53,965 + 3,64,079 + 2 = 7,18,046. Final by sex: 3,43,709 +
  3,52,315 + 2 = 6,96,026.
- Reasons: 54,678 + 78,980 + 25,573 + 4,947 + 5,281 = 1,69,459 = 8,87,505 -
  7,18,046.
- Mapped 6,32,871 + unmapped 85,175 = 7,18,046.
- Notices: 85,175 + 1,33,413 = 2,18,588.
- Final: 7,18,046 + 8,803 - 28,899 - 1,924 = 6,96,026 (the note gives 1,924
  deleted and 28,899 found ineligible separately; together 30,823).
- Gender ratios recomputed: 1029 (draft), 1025 (final), as printed.
- Papum Pare: each AC's roll before less draft equals its printed fall
  (41,575, 6,039, 1,814); each AC's men + women equals its draft; the three ACs
  sum to the district's 1,02,810 before, 53,382 draft, 49,428 fall, 24,717 men,
  28,665 women.
- Tirap: 40,041 - 34,177 = 5,864, as printed. Tawang: 12,227 + 13,285 = 25,512.
  Tezu: 8,255 + 8,573 = 16,828; + 254 service = 17,082, as printed.

Failed, recorded and not corrected:
- **West Siang: 42,546 - 36,254 = 6,292, but the five reasons printed add to
  6,492** (3,992 shifted + 1,243 dead + 974 absent + 173 duplicate + 110
  other), 200 more. Either a reason or a total is misprinted in the press copy.

Not checkable: the five districts cannot be summed to the state (21 districts
are missing).
