"""Assertions over the Maharashtra raw tables. Run from anywhere:

    python3 data/maharashtra/raw/check_raw.py

Published totals are written out below, each with the place in the CEO's press
note of 31.08.2026 it comes from, so a table that stops adding up to its own
source fails here. Every check prints ok or FAIL; the script exits 1 on any FAIL.
"""
import csv
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
results = []


def load(name):
    with open(os.path.join(HERE, name), newline="") as f:
        return list(csv.DictReader(f))


def check(cond, msg):
    results.append((bool(cond), msg))


def colsum(rows, col):
    return sum(int(r[col]) for r in rows)


# Published state figures: page 1 of the note and the Total rows of the annexures.
BEFORE = 97854049        # "9,78,54,049"
DRAFT = 77165562         # "7,71,65,562", also Annexure-1 Total
DRAFT_MEN = 39589905     # "3,95,89,905"
DRAFT_WOMEN = 37572570   # "3,75,72,570"
DRAFT_THIRD = 3087       # "3,087"
LEFT_OFF = 20688487      # "2,06,88,487", also Annexure-2 Total

# ---- state.csv ----
state = {r["measure"]: r["value"] for r in load("state.csv")}
check(int(state["before"]) == BEFORE and int(state["draft"]) == DRAFT
      and int(state["left_off"]) == LEFT_OFF,
      "state: before, draft and left_off as printed on page 1")
check(int(state["draft_men"]) == DRAFT_MEN and int(state["draft_women"]) == DRAFT_WOMEN
      and int(state["draft_third_gender"]) == DRAFT_THIRD,
      "state: draft by sex as printed on page 1")
check(DRAFT_MEN + DRAFT_WOMEN + DRAFT_THIRD == DRAFT,
      "state: draft men + women + third gender = draft (77,165,562)")
check(DRAFT + LEFT_OFF == BEFORE,
      "state: draft + left off = roll before (97,854,049)")
check(round(100 * DRAFT / BEFORE, 2) == float(state["draft_pct_of_before"])
      and round(100 * LEFT_OFF / BEFORE, 2) == float(state["left_off_pct_of_before"]),
      "state: the printed 78.86% and 21.14% follow from the counts")
check(int(state["polling_stations_before"]) + int(state["polling_stations_added"])
      - int(state["polling_stations_deleted"]) == int(state["polling_stations_after"]),
      "state: polling stations 100,253 + 394 - 431 = 100,216")

# ---- district_draft.csv: Annexure-1 ----
draft = load("district_draft.csv")
names = [r["district"] for r in draft]
check(len(draft) == 36 and len(set(names)) == 36,
      "district_draft: 36 districts, each once")
check([int(r["sr"]) for r in draft] == list(range(1, 37)),
      "district_draft: serial numbers 1 to 36 in the CEO's order")
bad = [r["district"] for r in draft
       if int(r["men"]) + int(r["women"]) + int(r["third_gender"]) != int(r["total"])]
check(not bad, "district_draft: men + women + third gender = total in every district"
      + (f" (fails: {bad})" if bad else ""))
check(colsum(draft, "total") == DRAFT,
      f"district_draft: totals sum to 7,71,65,562 (got {colsum(draft, 'total'):,})")
check(colsum(draft, "men") == DRAFT_MEN and colsum(draft, "women") == DRAFT_WOMEN
      and colsum(draft, "third_gender") == DRAFT_THIRD,
      "district_draft: men, women and third gender sum to the state figures "
      f"(got {colsum(draft, 'men'):,} / {colsum(draft, 'women'):,} / "
      f"{colsum(draft, 'third_gender'):,})")

# ---- district_uncollectable.csv: Annexure-2 ----
unc = load("district_uncollectable.csv")
check(len(unc) == 36 and len({r["district"] for r in unc}) == 36,
      "district_uncollectable: 36 districts, each once")
check([r["district"] for r in unc] == names,
      "district_uncollectable: the same 36 names, in the same order, as Annexure-1")
check(colsum(unc, "uncollectable") == LEFT_OFF,
      f"district_uncollectable: sums to 2,06,88,487 (got {colsum(unc, 'uncollectable'):,})")
before = {r["district"]: int(r["total"]) for r in draft}
for r in unc:
    before[r["district"]] = before.get(r["district"], 0) + int(r["uncollectable"])
check(sum(before.values()) == BEFORE,
      "draft + uncollectable sums to 9,78,54,049, so the roll before by district "
      f"is derived as draft + uncollectable (got {sum(before.values()):,})")

# ---- ac_district.csv ----
acs = load("ac_district.csv")
nums = [int(r["ac"]) for r in acs]
check(sorted(nums) == list(range(1, 289)),
      "ac_district: ACs 1 to 288, each once")
check(all(r["district"] in set(names) for r in acs),
      "ac_district: every AC mapped to one of the 36 press-note districts, spelt the same")
per = Counter(r["district"] for r in acs)
check(set(per) == set(names) and min(per.values()) >= 1,
      "ac_district: every district has at least one AC "
      f"(fewest: {min(per.values())}, most: {max(per.values())})")
check(per["Palghar"] == 6 and per["Thane"] == 18,
      "ac_district: Palghar 6 ACs (128-133) and Thane 18, as ECI lists them")

fails = 0
for ok, msg in results:
    print("ok  " if ok else "FAIL", msg)
    fails += not ok
print(f"{len(results) - fails} of {len(results)} checks passed")
sys.exit(1 if fails else 0)
