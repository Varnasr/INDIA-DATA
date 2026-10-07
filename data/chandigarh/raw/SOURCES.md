# Chandigarh sources

ceochandigarh.gov.in refused every connection from the sandbox (curl reset; Firecrawl failed
with a tunnel error and timed out). Nothing was read from it directly.

## Documents (in `sources/`)

- `ceo_x_post_20260805.json`: CEO Chandigarh X post of 05/08/2026,
  https://x.com/ceochandigarh/status/2085033322586226809 , read through api.fxtwitter.com.
  Primary: roll before 516427, draft 450282, 1780 BLAs.
- `indianewscalling_20260922_official_release_extract.txt`: the UT's release of 22/09/2026
  reproduced verbatim, https://www.indianewscalling.com/news/190303-final-electoral-roll-for-chandigarh-parliamentary-constituency-published.aspx
  (final 460209). Press reproduction, primary=false.
- `hindustantimes_20260923_final_roll_extract.txt`:
  https://www.hindustantimes.com/cities/chandigarh-news/chandigarh-just-2-rise-in-voters-after-clearing-discrepancies-in-sir-101790106180996.html .
  Reports the UT statement: roll before by sex, the five reasons, mapping, notices, hearings,
  claims and objections, additions, deletions, the final by sex, service electors.
- `indianexpress_draft_wards_extract.txt`, `tribune_draft_wards_extract.txt`: reports of a
  ward-wise chart shared by the Chandigarh MP, comparing the 2024 Lok Sabha roll with the draft.
  The Tribune calls it a chart "of the Election Commission"; the chart itself was not found.

## Files

- `state.csv`.
- `ward_change_2024_to_draft_press_partial.csv`: the only figures below the UT that were found.
  Press, primary=false, and partial: 17 of 35 municipal wards, with the fall from the 2024 Lok
  Sabha roll to the draft as a percentage and, for six wards, as a count. This is not the SIR's
  names left off (66145); it is the change over two years (2,09,523 in all), which the papers
  report alongside. Use with care, or not at all.

## Checks

- Roll before by sex 263724 + 252677 + 26 = 516427: OK.
- Roll before less draft 516427 - 450282 = 66145: OK.
- Reasons 12567 + 43725 + 3535 + 2590 + 3728 = 66145: OK.
- Mapped 167406 + 213415 = 380821; + unmapped 69461 = 450282 (draft): OK.
- Notices (Tribune, 28/07/2026) 69461 + 68353 = 137814: OK. HT's rounded 69500 + 68700 = 138200,
  reported as "1,38,000".
- Draft + 15117 - 5190 = 460209 (final): OK. Final by sex 234516 + 225671 + 22 = 460209: OK.
- 2024 roll 659805 - draft 450282 = 209523, 31.76%: OK against the press figures.

## Gaps

- The draft by sex was not found in a source that could be read. data/india/raw/gender.csv
  carries women removed 31971 and men 34169 from the PTI story on ThePrint, which refused curl
  (browser check). If those are right the draft is men 229555, women 220706, third gender 21;
  not recorded here.
- No table by ward, sector, polling station or ERO area from the CEO. Chandigarh has no assembly
  constituencies; the roll is one parliamentary constituency.
- The 4644 marked ineligible at hearings are part of the 5190 removed after the draft; the rest
  (546) are not split by route in what was read.
