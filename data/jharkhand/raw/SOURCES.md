# Jharkhand sources

**Nothing below the state level was found from the Chief Electoral Officer.**
The CEO's site (ceo.jharkhand.gov.in, including the SIR page at
`/SIRASD2026/SIRJharkhand.aspx`) refused the sandbox with plain curl
(connection reset) and timed out twice through Firecrawl on 2026-10-06, so no
press note, bulletin or district table could be read from it. Every figure here
is the CEO's as reported in the press, and is marked primary=false.

## Files

- `state.csv`: the state figures, each with its source.
- `district_press_partial.csv`: two districts' provisional count of electors
  marked dead, as officials gave it to the Hindustan Times at 8 pm on
  29 July 2026, before the draft. Not a table; two rows of a press report.
- `district_claims_lastday_partial.csv`: the five districts with the most
  Form 6 and Form 8 applications on the last day of claims (30 September 2026),
  from the CEO's SIR bulletin as reported by the Times of India. Not a full
  table, and a single day's intake only.
- `sources/`: the text of each article, extracted from the page HTML.

## Sources

| file in sources/ | document | date | how read | gives |
|---|---|---|---|---|
| etvbharat_2026-08-05_draft.txt | ETV Bharat, "43.61 lakh names removed..." https://www.etvbharat.com/en/state/over-43-lakh-voters-names-deleted-as-ec-publishes-draft-electoral-rolls-in-jharkhand-after-sir-enn26080506218 | 5 Aug 2026 | curl | roll before, draft, left off, four reasons exact, polling stations |
| thehindu_2026-08-05_draft.txt | The Hindu, "Jharkhand SIR: Over 43 lakh voters deleted..." https://www.thehindu.com/news/national/jharkhand/jharkhand-sir-over-43-lakh-voters-deleted-in-draft-electoral-rolls/article71310282.ece | 5 Aug 2026 | curl | roll before, draft, left off, reasons in lakh |
| (search excerpt only) | NDTV (PTI), https://www.ndtv.com/india-news/over-43-lakh-names-deleted-from-jharkhand-draft-voter-rolls-after-revision-11869880 | 5 Aug 2026 | Firecrawl search excerpt | shifted 15.92 lakh, absent 14.50 lakh, dead 7.63 lakh, duplicate 4.38 lakh |
| hindustantimes_2026-07-30_enumeration.txt | Hindustan Times, https://www.hindustantimes.com/india-news/jharkhand-sir-4-37m-may-be-dropped-in-draft-rolls-over-7-lakh-dead-voters-recorded-101785460949162.html | 30 Jul 2026 | curl | dead 763,930 (before the draft), Ranchi and Dhanbad dead |
| toi_2026-08-06_notices.txt | Times of India (Ranchi), notices to 63,24,116 | 6 Aug 2026 | curl | no mapping, logical discrepancy, demographic similar entries |
| toi_2026-10-01_claims_bulletin.txt | Times of India (Ranchi), "officials rush to resolve 11.8 lakh claims", citing the CEO's SIR bulletin | 1 Oct 2026 | curl | Forms 6, 6A, 7, 8 received to 30 Sep; last-day district intake |
| pioneer_2026-09-29_claims.txt | The Pioneer (PTI), "claims and objections deadline ends on September 30" | 29 Sep 2026 | curl | Forms to 28 Sep (rounded), draft by sex (rounded, third gender 260) |

## Checks

- roll_before less draft equals left_off: 2,64,63,236 − 2,21,01,249 =
  43,61,987. **Passes exactly.**
- Reasons: ETV Bharat prints four exact figures (dead 7,63,903, absent
  14,50,810, duplicate 4,38,596, foreign or other 1,16,484), which sum to
  27,69,793. The fifth reason, permanently shifted, is not printed exactly in
  anything read. Left off less the four gives 15,92,194, which matches NDTV's
  "15.92 lakh" to the rounding. It is in `state.csv` as `shifted_derived`, not
  as a printed figure. The row in `data/india/raw/states.csv` (dead 763000,
  shifted_absent_other 3042000, duplicate 438000, split "short") can now be
  made exact: dead 763,903; shifted, absent and other 15,92,194 + 14,50,810 +
  1,16,484 = 31,59,488; duplicate 4,38,596; total 43,61,987 (complete, with
  shifted derived).
- Dead: ETV Bharat 7,63,903 at the draft; Hindustan Times 7,63,930 on
  30 July, before the draft. Recorded as a discrepancy of 27, not resolved.
- Notices: 14,03,205 + 45,55,227 + 3,65,684 = 63,24,116. **Passes.**
- Forms to 30 September: 6,92,597 + 112 + 13,443 + 4,73,609 = 11,79,761.
  **Passes.**
- Draft by sex is rounded (1.12 crore and 1.08 crore); 1.12 + 1.08 = 2.20
  crore against 2,21,01,249, consistent with rounding only.

## Not found

- No district or assembly constituency table of the roll before, the draft or
  the names left off, from the CEO or in the press.
- No split of the names left off by sex.
- The final roll (due 19 October 2026) is not yet out.
- Claims and objections admitted (as opposed to received), and notices by
  district.
