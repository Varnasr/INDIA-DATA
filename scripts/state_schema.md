# `data/<slug>/raw/normal.json`: one state's figures in one shape

`scripts/build_states.py` reads this file for every state in `STATES` and
writes `data/<slug>/summary.json` and `data/<slug>/tables.csv`. One page
script, `assets/statepage.js`, draws every such state from its summary, so
the shape below is the whole contract. The build fails on any field it does
not know, on any identity below that does not hold, and on any figure without
a source.

```json
{
  "state": "Chhattisgarh",
  "slug": "chhattisgarh",
  "ut": false,
  "revision": "sir",
  "dates": {"roll_before": "2025-10-27", "draft": "2025-12-23", "final": "2026-02-21"},
  "figures": {
    "roll_before": {"v": 21230737, "src": "s1"},
    "draft":       {"v": 18495920, "src": "s1"},
    "removed":     {"v": 2734817,  "src": "s1"}
  },
  "reasons_complete": true,
  "tables": [
    {"id": "districts", "title": "Every district, from the draft to the final roll",
     "level": "district", "kind": "after", "src": "s2", "partial": false,
     "rows": [{"name": "Surguja", "draft": 598492, "added": 4992, "removed": 1174, "final": 602310}]}
  ],
  "sources": [
    {"id": "s1", "title": "CEO Chhattisgarh, press release of 23 December 2025",
     "url": "https://...", "date": "2025-12-23", "primary": true}
  ],
  "notes": ["Plain sentences for the method page."],
  "cannot_show": ["Plain sentences on what the published figures cannot show."]
}
```

## Fields

- `article`: `"the"` for a name read with the article ("the Andaman and
  Nicobar Islands"). Leave it out otherwise.
- `revision`: `"sir"`, or `"no_draft"` when no draft roll has been published.
- `dates`: any of `roll_before` (the date the roll before the revision refers
  to), `draft`, `final`, as `YYYY-MM-DD`, and `notices`, the date by which
  the `notices` count had been sent (leave it out when the count is of
  notices still to be sent). Leave out what is not known.
- `figures`: each `{"v": integer, "src": source id}`. Add `"press": true` when
  the figure reached us through a newspaper or broadcaster rather than an
  official document, and `"rounded": true` when it was printed in lakh. Keys,
  all optional:
  - `roll_before`, `draft`, `removed` (the names left off the draft),
  - reasons: `dead`, `shifted_absent_other`, `duplicate` (the three every
    state reported; put absent, shifted and other together in the middle one),
  - after the draft: `added_after`, `removed_after`, `net_after`, `final`,
  - by sex: `men_before`, `women_before`, `third_before`, and the same with
    `_draft`, `_removed`, `_final`,
  - `notices` (electors kept on the draft but sent a notice).
- `reasons_complete`: true when the three reasons were published as exact
  counts that add to `removed`.
- `tables`: any district, constituency or other table that was published.
  `level` is `district`, `region`, `ac`, `pc`, `island`, `tehsil` or `ward`.
  `removed_label` heads the `removed` column of a `left_off` table when it
  holds something other than the names left off the draft. `kind` says
  what the rows hold:
  - `left_off`: rows carry `before`, `draft` and `removed` (any two give the
    third), and optionally `dead`, `shifted_absent_other`, `duplicate`;
  - `after`: rows carry `draft`, `added`, `removed`, `final` (or `net`);
  - `draft`: rows carry `draft`, and optionally `men`, `women`;
  - `final`: rows carry `final`, and optionally `draft`, `men`, `women`;
  - `fall`: rows carry an earlier roll `before` and `draft` or `final`, where
    the earlier roll is not the roll the revision started from. Say which
    roll in `title`.
  `partial: true` when the table covers only some rows (press extracts). A
  full table must add up to the state figure in every column it shares with
  `figures`; a partial one is checked row by row only.
  Add `"press": true` to a table that came through the press.
- `sources`: every document used, `primary: true` only for a document of the
  Election Commission, a Chief Electoral Officer or a District Election
  Officer read from that office or a faithful copy of it.
- `notes`, `cannot_show`: whole plain sentences, the site's writing rules
  (no em dashes, no sentence hinged on a colon or strung on semicolons, no
  "X, not Y"). Never name a person on a list, never link a list of names.

## Identities the build checks

- `roll_before - draft = removed` when all three are given.
- The three reasons add to `removed` when `reasons_complete`, and to no more
  than `removed` otherwise.
- `added_after - removed_after = net_after`, `draft + net_after = final`.
- For each of before, draft, removed and final, men + women + third = the
  total, when all are given.
- Every row of an `after` table: `draft + added - removed = final`.
- Every row of a `left_off` table: `before - draft = removed`.
- A table that is not `partial` adds up to the state figure in each column it
  shares with `figures`.
