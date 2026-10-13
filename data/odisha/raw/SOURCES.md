# Odisha sources

Collected 2026-10-06. **No table below the state was obtained.** Every figure
here is the Chief Electoral Officer's as reported by the press; nothing in
this folder is read from a CEO or ECI document directly.

## What was tried

- **ceoodisha.nic.in** (the CEO's site). Plain curl over HTTPS: connection
  reset; over HTTP: 503. Firecrawl, three attempts on
  `https://ceoodisha.nic.in/` and `https://ceoodisha.nic.in/en/eroll-analysis/`
  (basic, auto and stealth proxy, location India): tunnel connection failed
  or timed out every time. The Wayback Machine refused the sandbox (429, then
  egress policy).
- A Firecrawl search restricted to ceoodisha.nic.in found the page that very
  likely holds what is wanted: **"Eroll analysis - CEO Odisha",
  https://ceoodisha.nic.in/en/eroll-analysis/**, whose indexed snippet reads
  "Constituency-wise Information on Inclusion and Deletions in Current
  Electoral Rolls Over Previous Roll ... Electoral Roll Analysis (DRAFT 2026
  Pub.Dt. 05.07.2026)". It could not be opened from here. **This is the first
  place to look from an Indian network**: it should give the draft roll and
  the deletions by AC.
- Hindustan Times (7 July 2026) says district-wise data on the deletions was
  "released by the Election Commission of India on July 6". That release was
  not found: the ECI site's document listing goes through an encoded API, and
  a targeted search turned up nothing.
- The CEO's posts on X for the draft (5 July 2026,
  https://x.com/OdishaCeo/status/2073676372468523030) and the final roll
  (21 September 2026, https://x.com/OdishaCeo/status/2102016953267392810)
  were opened through X's public embed service: both carry only photographs
  of the press conference, no table.

## Files

- `state.csv`: the state figures, each with the outlet that reported it.
  Primary: no. The figures are the CEO's as reported.
- `district_ac_press_partial.csv`: **not a table.** The eleven districts and
  six ACs whose counts of names left off the draft were printed in the press,
  with the printed percentage where given. Kept so the numbers can be checked
  against the CEO's table when it is found. Do not build a page from it.
- `sources/ht_20260707_excerpt.md`, `sources/toi_20260706_excerpt.md`,
  `sources/etv_20260921_excerpt.md`: the passages the figures are taken from,
  aggregates only.

Documents:

- ETV Bharat, 21 September 2026, "Over 20 Lakh Voter Names Deleted After
  Completion Of SIR In Odisha",
  https://www.etvbharat.com/en/state/over-20-lakh-voter-names-deleted-after-completion-of-sir-in-odisha-enn26092107667
  (Firecrawl). The fullest account of the CEO's press conference: the roll of
  17 May 2026 and the final roll by sex, the five reasons, mapping, notices,
  claims and the removals after the draft.
- The Hindu, 21 September 2026,
  https://www.thehindu.com/news/national/odisha/odishas-final-electoral-roll-has-316-crore-voters-1766-lakh-names-struck-off/article71491775.ece
  (excerpt in a Firecrawl search result). Draft 3,13,87,034; four of the
  reasons; 24,070 ineligible after hearing and 20,707 on Form 7; final
  3,16,32,754.
- The New Indian Express, 22 September 2026 (the source already on the All
  India row and in `notices.csv`; not reopened).
- Hindustan Times, 7 July 2026,
  https://www.hindustantimes.com/india-news/ganjam-cuttack-among-districts-with-most-odisha-sir-deletions-101783387962814.html
  (Firecrawl). Ten district counts and six AC counts of names left off; its
  percentages are on the roll of 1 January 2025, not the roll before.
- Times of India, 6 July 2026,
  https://timesofindia.indiatimes.com/city/bhubaneswar/draft-electoral-roll-ganjam-tops-deletions-malkangiri-sees-sharpest-decline-at-10-25/articleshow/132217485.cms
  (Firecrawl). Ganjam and Malkangiri before and draft in lakh, Malkangiri's
  47,355, and percentages on the pre-revision roll from the CEO's draft.

## Checks run

- Reasons: 1,99,249 absent + 8,08,205 shifted + 8,32,544 dead + 1,58,118
  duplicate + 14,441 other = 20,12,557, the total. Pass, 0 difference.
- Roll before by sex: 1,68,85,283 + 1,65,11,223 + 3,085 = 3,33,99,591. Pass.
- Roll before less draft: 3,33,99,591 - 3,13,87,034 = 20,12,557. Pass.
- Final by sex: 1,61,30,319 + 1,54,99,661 + 2,774 = 3,16,32,754. Pass.
- Draft + added - removed after the draft: 3,13,87,034 + 2,90,497 - 44,777 =
  3,16,32,754. Pass.
- Removed after the draft: 24,070 + 20,707 = 44,777 (The Hindu, TNIE). Pass.
  ETV Bharat prints 20,708 on Form 7, which makes 44,778, one over. Recorded,
  not resolved.
- Notices: TNIE 12,98,779 + 45,37,613 = 58,36,392; ETV Bharat 12,98,779 +
  45,37,547 = 58,36,326. Each adds up on its own; the two differ by 66 in the
  discrepancy list. Both kept in `state.csv`.
- Mapping: 1,35,64,839 self + 1,65,23,415 descendants = 3,00,88,254. Pass.
  3,00,88,254 mapped + 12,98,779 unmapped = 3,13,87,033, one short of the
  draft of 3,13,87,034. Recorded as printed.
- District and AC press figures: no total to check against, since only 11 of
  30 districts and 6 of 147 ACs were printed. Ganjam's 2,07,624 and
  Malkangiri's 47,355 agree with TOI's lakh figures (29.99 - 27.92 = 2.07;
  4.62 - 4.15 = 0.47).
- The draft by sex was not found in any source read today. The All India
  gender row (women 11,46,140, men 8,66,107 removed) is attributed to the CEO
  through ETV Bharat, but the ETV article read today gives the roll before and
  the final roll by sex, not the draft. Those two numbers imply a draft of
  1,60,19,176 men, 1,53,65,083 women and 2,775 third gender, which sums to
  the draft exactly; their source should be re-found before it is used.

## Differences from `data/india/raw/states.csv`

None in the state figures. The row's shifted, absent or other (10,21,895) is
1,99,249 + 8,08,205 + 14,441, as its note says.

## What was looked for and not found

- The CEO's AC-wise "Electoral Roll Analysis (DRAFT 2026 Pub.Dt.
  05.07.2026)" and any district-wise table of the roll before, the draft and
  the names left off (see above).
- The ECI's district-wise release of 6 July 2026.
- Any split of the names left off by reason or by sex below the state.
- The final roll by district or AC, and claims and objections by district.
- Notices by district.

## od_district_rolls.csv, od_ac_rolls.csv, od_ac_after_draft.csv (added 2026-10-13)

The Chief Electoral Officer's own statutory formats for the draft roll of
05.07.2026 and the final roll of 21.09.2026, from
https://ceoodisha.nic.in/en/eroll-analysis/ (primary). Read from the PDFs'
text layer through Firecrawl, since the site resets plain curl.

- Format 1B (final): all 147 ACs and 30 districts, the 2024 roll, the
  January 2025 roll, the draft and the final roll, each by sex. Every AC adds
  to its district and every district to the grand total in every column, and
  every printed sex ratio agrees. One slip was corrected: Loisingha women on
  the 2025 roll read as 121,144; the sex ratio and the district total give
  122,144.
- Format 4B (final): draft to final for every AC, claims admitted and
  deletions by sex, Form 6 and Form 7 lodged, deletions by reason. Draft plus
  added less removed equals final in every row on totals, and the columns add
  to 2,90,497 added and 44,777 removed. By sex the identity misses by small
  amounts in both directions in 119 ACs (men +101, women -84 for the state),
  so only totals are used. The three reasons add to 28,229 of the 44,777.
- Not published: the 20,12,557 names left off at the draft, by AC or district.
  The draft Format 4B gives them only as a state footnote.
