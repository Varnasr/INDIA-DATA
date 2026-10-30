# Haryana sources

**Nothing below the state level was found from the Chief Electoral Officer,
apart from scattered district figures for claims after the draft.** The CEO's
site (ceoharyana.gov.in) was read with curl on 2026-10-06. Its server sends an
incomplete certificate chain, so the GlobalSign intermediate named in the
certificate's own AIA field was fetched from GlobalSign and added to the CA
bundle; verification stayed on. The "SIR 2026" page (`/WebCMS/Start/1985`)
carries the Commission's press note of 14.05.2026, a revised schedule, a link
to the draft roll on voters.eci.gov.in, and an "ASDD list" page, which was not
opened because it lists named electors. It carries no statistics. The state
government's press releases (prms.prharyana.gov.in) quote the CEO and are
counted as primary; they reset the connection on most attempts, and three were
read.

## Files

- `state.csv`: the state figures, each with its source.
- `district_claims_partial.csv`: the districts the release of 1 October 2026
  names as highest or lowest for Form 6, Form 7 and Form 8 received. Primary
  (state government release quoting the Additional CEO), but only the named
  districts; blanks are figures the release does not give.
- `district_uncollectable_provisional.csv`: uncollectable forms in five
  districts and the percentage in three, as of 15 July 2026, mid-enumeration,
  from Dainik Jagran quoting the CEO. Rounded to thousands from lakh. Press,
  provisional, and not the draft.
- `sources/`: text of the releases and articles; the ECI letter and
  notification of 29.08.2026 revising the schedule (PDF, from ceoharyana.gov.in).

## Sources

| file in sources/ | document | date | how read | gives |
|---|---|---|---|---|
| hindustantimes_2026-07-25_enumeration.txt | Hindustan Times, "16% voters found absent, shifted or dead during SIR: Haryana CEO" https://www.hindustantimes.com/cities/chandigarh-news/16-voters-found-absent-shifted-or-dead-during-sir-haryana-ceo-101785002164991.html | 25 Jul 2026 | curl | roll before, forms digitised, five reasons exact |
| toi_2026-07-31_draft.txt | Times of India, "16.4% deleted in Haryana draft roll" | 31 Jul 2026 | curl | draft-day shares in lakh |
| prharyana_release_2951_2026-06-18.txt | Haryana govt release 2951 | 18 Jun 2026 | curl | 2,06,55,929 electors, 20,629 BLOs |
| prharyana_release_3846_2026-08-05.txt | Haryana govt release 3846 | 5 Aug 2026 | curl | notices required and prepared |
| prharyana_release_8134_2026-10-01.txt | Haryana govt release 8134 | 1 Oct 2026 | curl | Forms 6, 7, 8 received; notices, hearings; named districts |
| jagran_2026-07-16_enumeration_hi.txt | Dainik Jagran (Hindi) | 16 Jul 2026 | curl | provisional uncollectable by district |
| eci_revised_schedule_2026-08-29.pdf | ECI letter and notification No.23/2025-ERS (Vol.II), 29.08.2026 | 29 Aug 2026 | curl, pymupdf text | claims to 30.09, notices to 28.10, final 06.11.2026 |
| (search excerpt only) | prharyana.gov.in/en/press-notes-295, "SIR-2026: 19.35 Lakh Notices Issued" | Aug 2026 | Firecrawl search excerpt; the page itself reset curl three times and timed out in Firecrawl | 18,56,138 and 26,31,312 in two notice categories (labels not read) |

## Checks

- roll_before less forms digitised equals left_off: 2,06,55,929 −
  1,72,71,361 = 33,84,568. **Passes exactly.**
- Reasons sum to left_off: 9,36,646 + 13,75,278 + 7,66,205 + 2,04,916 +
  1,01,523 = 33,84,568. **Passes exactly.** This is a complete exact split,
  where `data/india/raw/states.csv` now carries a rounded one (dead 766000,
  shifted_absent_other 2413000, duplicate 204000, from Deccan Herald). The
  exact fold is: dead 7,66,205; shifted, absent and other 24,13,447;
  duplicate 2,04,916.
- **Unresolved:** states.csv gives removed 33,83,302 at the draft (Deccan
  Herald), 1,266 fewer than the 33,84,568 at the end of enumeration. The
  draft-day count itself (which would be 1,72,72,627 on that figure) was not
  found in anything read here. Not reconciled.
- Notices on 1 October: hearings completed 40,56,716 + pending 4,34,975 =
  44,91,691 issued. **Passes.**
- Notice categories from the search excerpt: 18,56,138 + 26,31,312 =
  44,87,450, against 44,86,035 required by 31 July and 44,91,691 issued by
  1 October. Not used; recorded only.
- District claims: only named districts, so no sum can be checked against the
  state total.

## Not found

- No district or constituency table of the roll before, the draft or the
  names left off from the CEO; the ASDD list exists only as named lists.
- No split of the names left off by sex; no draft by sex.
- The final roll is not out. It was due on 6 November 2026 and is now due on 30 November
  2026, with notices decided by 20 November, per the Haryana Public Relations release of
  30 October 2026 from the Jhajjar District Election Officer
  (https://prms.prharyana.gov.in/press-release/10167).
