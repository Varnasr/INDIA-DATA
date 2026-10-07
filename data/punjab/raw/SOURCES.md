# Punjab sources

**Nothing below the state level was found from the Chief Electoral Officer.**
ceopunjab.gov.in and ceopunjab.nic.in reset the connection to curl on
2026-10-06. Firecrawl credits were low and the site was not scraped. Every
figure here is the CEO's as reported in the press (primary=false).

## Files

- `state.csv`: the state figures, each with its source.
- `district_press_partial.csv`: the five districts with the most uncollectable
  forms, in lakh, from The Tribune on the day of the draft. A Facebook post
  seen only as a search excerpt gives Amritsar 2,42,751 and Jalandhar
  1,84,997 exactly; those are in `left_off_exact_unverified` and were not read
  in full.
- `ac_discrepancy_pending_partial.csv`: the five constituencies with the most
  logical-discrepancy cases still pending on 22 September 2026, from
  "data available with the CEO" as reported by the Hindustan Times.
- `sources/`: the text of each article.

## Sources

| file in sources/ | document | date | how read | gives |
|---|---|---|---|---|
| newindianexpress_2026-08-04_enumeration.txt | New Indian Express, "20.66 lakh Punjab voters dropped..." | 4 Aug 2026 | curl | roll before (9 Jun), forms, left off, four reasons |
| toi_2026-08-04_enumeration.txt | Times of India, "Punjab SIR identifies over 20 lakh ineligible voters" | 4 Aug 2026 | curl | same figures; 12.80 lakh unmapped |
| toi_2026-08-13_draft.txt | Times of India, "20.6L names deleted in Punjab SIR draft" | 13 Aug 2026 | curl | the same reasons at the draft |
| tribune_2026-08-13_draft.txt | The Tribune, "20.66 lakh Punjab voters struck..." | 13 Aug 2026 | curl | five districts in lakh; draft "around 1.93 crore" |
| hindustantimes_2026-08-13_draft.txt | Hindustan Times, draft published | 13 Aug 2026 | curl | dates; final 12 Oct |
| hindustantimes_2026-09-23_discrepancy.txt | Hindustan Times, "Punjab clears 99% of logical discrepancy cases" | 23 Sep 2026 | curl | 22.69 lakh flagged, 22.41 lakh cleared; five ACs pending |

## Checks

- roll_before less forms equals left_off: 2,14,61,043 − 1,93,94,408 =
  20,66,635. **Passes exactly.**
- Reasons: 9,44,131 + 5,74,568 + 4,12,715 + 1,19,145 = 20,50,559, which is
  **16,076 short of 20,66,635**. Every source gives the same four figures and
  none names a fifth reason. Recorded as a shortfall, as states.csv already
  does.
- Shares: 20,66,635 / 2,14,61,043 = 9.63%, as printed.
- Districts: the five named districts in lakh sum to 11.33 lakh of 20.67; no
  check against a total is possible.

## Not found

- The exact draft roll count of 13 August 2026 (the press gives 1.93 and 1.94
  crore), the draft by sex, and any split of the names left off by sex.
- Any district or constituency table from the CEO.
- Claims and objections received or admitted; an exact count of unmapped
  notices (only "around 12.80 lakh").
- The final roll (due 12 October 2026) is not out.
