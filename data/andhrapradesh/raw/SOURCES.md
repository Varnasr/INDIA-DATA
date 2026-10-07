# Andhra Pradesh sources

Collected 2026-10-06. The Chief Electoral Officer's site (ceoandhra.nic.in)
refused the sandbox (connection reset, one retry), and ceo.ap.gov.in was
refused by the egress proxy. The CEO's own press note of 31 July 2026 and its
district statement were read instead from the images the CEO posted on X,
which are the CEO's documents as issued.

## The documents

- **CEO Andhra Pradesh, press note "Andhra Pradesh Special Intensive Revision
  (SIR): Key Findings of Enumeration Phase (15th June - 24th July 2026)",
  dated 31.07.2026** (memo number ending 610/Elecs.B/A1/2026; the start of
  the number is cut off in the image). Five pages, posted as images by the
  CEO's account @CEOAndhra on 31 July 2026 at 11:19 IST:
  https://x.com/CEOAndhra/status/2083150543489491157
  Images downloaded at full size from pbs.twimg.com on 2026-10-06 and saved in
  `sources/`:
  - `ceo_ap_press_note_20260731_p1_p2.jpg` (pages 1 and 2, edges cropped in the
    CEO's own collage): the chart of the roll before the revision and the
    three reasons, in lakh; 4,16,27,694 electors on 24 July, 3,71,38,182 who
    submitted forms; 28 districts, 175 EROs, 1,079 AEROs, 46,397 BLOs; the
    table of BLAs by party (total 1,27,868).
  - `ceo_ap_press_note_20260731_p3_p4.jpg` (pages 3 and 4): polling stations
    rationalised from 46,397 to 50,328; the schedule after the draft; that
    booth-wise ASDD lists were displayed and put on the CEO's and DEOs'
    websites.
  - `ceo_ap_press_note_20260731_p5.jpg` (page 5): notices, no deletion without
    notice, appeals.
  - `ceo_ap_district_statement_20260731.jpg`: "Statement showing the electors
    existed Pre-SIR, Total number of Absent / Shifted / Dead / Duplicate
    electors (EFs uncollectable), electors in the draft electoral roll
    published on 31.07.2026", one row per district for all 28 districts, each
    block by male, female and third gender, plus service electors in the
    draft roll by sex. This is the table behind `district_draft.csv`.
  - How read: transcribed by eye from the image (1080x803, upscaled 3x in
    crops for reading). Primary: yes, the CEO's own document.
- **The same press note as reported**: The News Minute, 31 July 2026,
  https://www.thenewsminute.com/andhra-pradesh/andhra-sir-draft-roll-removes-nearly-45-lakh-names-found-absent-dead-or-duplicate
  (read with Firecrawl). Gives the same state figures and embeds the CEO's
  post, which is how the images were found.
- **Notices after the draft**: ETV Bharat, 24 September 2026,
  https://www.etvbharat.com/en/state/andhra-pradesh-sir-over-1-lakh-voters-ineligible-enn26092402945
  (already in `data/india/raw/notices/notices.csv`; not reopened). Press,
  interim.
- **Schedule moved**: ECI press note ECI/PN/121/2026 of 30.09.2026,
  https://www.eci.gov.in/eci/public/api/document?id=17539 , and the PIB copy;
  already read for `data/india/process.json`. Final roll due 16 October 2026.

## Files

- `district_draft.csv`: the district statement, 28 rows, no total row.
  Columns: `before_*` and `roll_before` (pre-SIR electors), `left_off_*` and
  `left_off` (ASDD / enumeration forms uncollectable), `draft_*` and `draft`
  (electors in the draft roll), `service_draft_*` and `service_draft` (service
  electors in the draft roll, men and women; the table has no third-gender
  column for them). District names as printed.
- `state.csv`: state figures with their source, including the grand total row
  of the statement.

## Checks run (all on the transcription, 2026-10-06)

- Every row: men + women + third gender = total, for the roll before, the
  names left off and the draft: 28 of 28 rows, all three blocks, pass.
- Every row: service men + service women = service total: 28 of 28 pass.
- Every row and each sex: roll before minus left off = draft: 28 of 28 rows,
  men, women, third gender and total, pass.
- Every column sums to the printed Grand Total: all 15 numeric columns pass
  with 0 difference (roll before 4,16,27,694; left off 44,89,512; draft
  3,71,38,182; service 64,502).
- The press note's state figures agree with the statement: 4,16,27,694 before
  and 3,71,38,182 who submitted forms equal the grand totals; 4,16,27,694 less
  3,71,38,182 = 44,89,512.
- The three reasons are in lakh, rounded: 15.22 + 22.30 + 7.37 = 44.89 lakh,
  which matches 44,89,512 at that rounding. No exact count by reason was
  found, and no split by reason below the state.
- Whether "Electors in Draft Roll" includes the service electors is not
  stated. The identity before less left off equals the draft holds exactly
  without them, so the service electors look to be counted apart.
- Notices (press, interim, 24 September): 44,00,225 verified + 28,619 pending
  = 44,28,844, which is 400 more than the 44,28,444 notices reported. Recorded
  as printed; not reconciled.

## Differences from `data/india/raw/states.csv`

The All India row carries the press figures in lakh: electors before
4,16,00,000 (rounded), removed 44,89,512, dead 15,22,000, shifted/absent/other
22,30,000, duplicate 7,37,000, flagged `rounded` and `press`. The primary
gives the roll before exactly as 4,16,27,694. The reasons are still rounded in
the primary itself.

## What was looked for and not found

- An AC-wise table of the roll before, the draft or the names left off. The
  press note says booth-wise ASDD lists were put on the CEO's and DEOs'
  websites; those are lists of named electors and were not opened. The CEO
  site itself could not be reached.
- Reasons by district or by sex.
- The final roll (due 16 October 2026) and claims and objections admitted.
- A split of the notices between the no-mapping list and the logical
  discrepancy list, by district or for the state.
