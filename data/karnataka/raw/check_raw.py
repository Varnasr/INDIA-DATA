"""Assertions over the Karnataka raw tables. Run from anywhere:

    python3 data/karnataka/raw/check_raw.py

Published totals are written out below, each with the table it comes from,
so a table that stops adding up to its own source fails here.
"""
import csv
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
passed = []


def load(name):
    with open(os.path.join(HERE, name), newline="") as f:
        return list(csv.DictReader(f))


def ints(row, *cols):
    return [int(row[c]) for c in cols]


def check(cond, msg):
    assert cond, msg
    passed.append(msg)


def colsum(rows, col):
    return sum(int(r[col]) for r in rows)


# ---- asd_district.csv: press note of 24.08.2026, Annexures 1 and 2 ----
asd = load("asd_district.csv")
check(len(asd) == 34 and len({r["district"] for r in asd}) == 34,
      "asd_district: 34 election districts, each once")
for r in asd:
    ab, sh, de, du, ot, tot = ints(r, "absent", "shifted", "dead", "duplicate", "other", "total")
    assert ab + sh + de + du + ot == tot, r["district"]
    assert int(r["digitised"]) + tot == int(r["electors_before"]), r["district"]
check(True, "asd_district: absent+shifted+dead+duplicate+other = total in every row")
check(True, "asd_district: digitised + total = electors_before (roll of 16.06.2026) in every row")
STATE_ASD = {  # 'Karnataka State' rows of Annexures 1 and 2, and page 2 of the note
    "electors_before": 55432314, "absent": 1517042, "shifted": 6545679,
    "dead": 1639864, "duplicate": 709870, "other": 383884,
    "total": 10796339, "digitised": 44635975,
}
for col, val in STATE_ASD.items():
    assert colsum(asd, col) == val, (col, colsum(asd, col), val)
check(True, "asd_district: every column sums to the published state row "
            "(55,432,314 before; 10,796,339 removed; 44,635,975 digitised)")

# ---- draft_roll_district.csv: Annexures 5 (general) and 10 (service) ----
dr = load("draft_roll_district.csv")
check(len(dr) == 34, "draft_roll_district: 34 rows")
NO_SERVICE_ROW = {"YADGIR", "VIJAYANAGARA"}  # absent from Annexure-10
for r in dr:
    m, w, t, g = ints(r, "men", "women", "third", "general_total")
    assert m + w + t == g, r["district"]
    if r["district"] in NO_SERVICE_ROW:
        assert r["service_men"] == r["service_women"] == r["service_total"] == r["total"] == ""
        continue
    sm, sw, st, tot = ints(r, "service_men", "service_women", "service_total", "total")
    assert sm + sw == st and g + st == tot, r["district"]
check(True, "draft_roll_district: men+women+third = general_total in all 34 rows; "
            "service men+women = service_total and general+service = total in the 32 listed")
check({r["district"] for r in dr if r["service_total"] == ""} == NO_SERVICE_ROW,
      "draft_roll_district: service cells blank only for Yadgir and Vijayanagara")
dig = {r["district"]: int(r["digitised"]) for r in asd}
check(all(int(r["general_total"]) == dig[r["district"]] for r in dr),
      "draft_roll_district: general electors equal Annexure-1's digitised forms in all 34 districts")
for col, val in {"men": 22159240, "women": 22473864, "third": 2871,
                 "general_total": 44635975}.items():
    assert colsum(dr, col) == val, (col, colsum(dr, col), val)
check(True, "draft_roll_district: general electors sum to the published state totals "
            "(22,159,240 men, 22,473,864 women, 2,871 third gender, 44,635,975)")
listed = [r for r in dr if r["district"] not in NO_SERVICE_ROW]
STATE_SERVICE = {"service_men": 42487, "service_women": 1689, "service_total": 44176}
resid = {c: v - colsum(listed, c) for c, v in STATE_SERVICE.items()}
check(resid == {"service_men": 460, "service_women": 7, "service_total": 467},
      "draft_roll_district: the 32 listed service rows fall short of the published "
      "state row (42,487 / 1,689 / 44,176) by exactly 460 / 7 / 467, the two unlisted districts")

# ---- roll_20260925_district.csv: press note of 25.09.2026, Annexure-1 ----
r25 = load("roll_20260925_district.csv")
check(len(r25) == 34, "roll_20260925_district: 34 rows")
check(all(sum(ints(r, "men", "women", "third")) == int(r["total"]) for r in r25),
      "roll_20260925_district: men+women+third = total in every row")
for col, val in {"men": 22255071, "women": 22586136, "third": 2873, "total": 44844080}.items():
    assert colsum(r25, col) == val, (col, colsum(r25, col), val)
check(True, "roll_20260925_district: columns sum to the published state row (44,844,080)")
check({r["district"] for r in r25} == {r["district"] for r in asd} == {r["district"] for r in dr},
      "all three SIR tables name the same 34 districts")

# ---- the press note of 09.10.2026, Annexures 1 to 3 ----
r09 = load("roll_20261009_district.csv")
check(len(r09) == 34 and all(sum(ints(r, "men", "women", "third")) == int(r["total"]) for r in r09),
      "roll_20261009_district: 34 rows, men+women+third = total in every row")
for col, val in {"men": 22403422, "women": 22755113, "third": 2858, "total": 45161393}.items():
    assert colsum(r09, col) == val, (col, colsum(r09, col), val)
check({r["district"] for r in r09} == {r["district"] for r in r25},
      "roll_20261009_district: columns sum to the published state row (45,161,393), same 34 districts")
nt = load("notices_20261009_district.csv")
check(all(int(r["notices_delivered"]) + int(r["notices_undelivered"]) == int(r["notices_generated"])
          and int(r["hearings_held"]) + int(r["hearings_pending"]) == int(r["notices_delivered"]) for r in nt),
      "notices_20261009_district: delivered + undelivered = generated, held + pending = delivered, every row")
for col, val in {"notices_generated": 4382315, "notices_delivered": 4373745, "notices_undelivered": 8570,
                 "hearings_held": 4088099, "hearings_pending": 285646, "polling_stations": 60923}.items():
    assert colsum(nt, col) == val, (col, colsum(nt, col), val)
fm = load("forms_20260616_20261008_district.csv")
check(all(sum(ints(r, "form6", "form6a", "form7", "form8")) == int(r["all_forms"]) for r in fm),
      "forms_20260616_20261008_district: the four forms add to the row total")
for col, val in {"form6": 952497, "form6a": 4712, "form7": 110654, "form8": 1234352, "all_forms": 2302215}.items():
    assert colsum(fm, col) == val, (col, colsum(fm, col), val)
check(True, "notices and forms: columns sum to the published state rows")

# ---- results_2023.csv and results_2023_candidates.csv ----
res = load("results_2023.csv")
cand = load("results_2023_candidates.csv")
check(sorted(int(r["ac"]) for r in res) == list(range(1, 225)),
      "results_2023: ACs 1 to 224, each once")
by_ac = {}
for c in cand:
    by_ac.setdefault(c["ac"], []).append(c)
check(len(by_ac) == 224, "results_2023_candidates: 224 ACs")
for r in res:
    cs = by_ac[r["ac"]]
    pos = [int(c["position"]) for c in cs]
    assert pos == list(range(1, len(cs) + 1)), r["ac"]
    assert sum(c["party"] == "None of the Above" for c in cs) == 1, r["ac"]
    assert sum(int(c["votes"]) for c in cs) == int(r["valid_votes"]), r["ac"]
    w, ru, m = ints(r, "winner_votes", "runner_up_votes", "margin")
    assert w - ru == m and m >= 0, r["ac"]
    assert (cs[0]["candidate"], cs[0]["party"], int(cs[0]["votes"])) == (r["winner"], r["winner_party"], w)
    assert (cs[1]["candidate"], cs[1]["party"], int(cs[1]["votes"])) == (r["runner_up"], r["runner_up_party"], ru)
    assert cs[0]["party"] != "None of the Above" and cs[1]["party"] != "None of the Above", r["ac"]
check(True, "results_2023: positions run 1..n, one NOTA row per AC, "
            "candidate votes (NOTA included) sum to valid_votes in every AC")
check(True, "results_2023: margin = winner_votes - runner_up_votes, and winner and "
            "runner-up agree with positions 1 and 2 of the candidate file, in every AC")
tally = Counter(r["winner_party"] for r in res)
DECLARED = {"INC": 135, "BJP": 66, "JD(S)": 19, "IND": 2,
            "Kalyana Rajya Pragathi Paksha": 1, "Sarvodaya Karnataka Paksha": 1}
check(dict(tally) == DECLARED, "results_2023: winners by party equal the declared result "
                               "(INC 135, BJP 66, JD(S) 19, IND 2, KRPP 1, SKP 1)")

# Form 20 'Total Votes Polled' rows (CEO Karnataka, via the OpenCity mirror):
# every candidate's total, in ballot order, read from the final result sheet.
FORM20 = {
    150: ([77428, 44491, 1597, 141538, 940, 2944, 142, 115, 358, 112, 191, 139,
           183, 193, 181, 362, 560, 335, 271, 489], 2238),   # text layer
    165: ([4081, 701, 50564, 58624, 281, 38, 93, 1213, 83, 85, 54, 42, 111,
           128, 144, 129, 54, 62], 1700),                     # scanned, read by eye
    176: ([2585, 775, 196220, 146521, 24612, 4360, 417, 856, 183, 271, 217,
           409, 394, 286], 4006),                             # scanned, read by eye
}
for ac, (votes, nota) in FORM20.items():
    cs = by_ac[str(ac)]
    mine = sorted(int(c["votes"]) for c in cs if c["party"] != "None of the Above")
    assert mine == sorted(votes), ac
    assert [int(c["votes"]) for c in cs if c["party"] == "None of the Above"] == [nota], ac
check(True, "results_2023_candidates: every candidate's votes and NOTA equal the CEO "
            "Form 20 final result sheet in ACs 150, 165 and 176")

for p in passed:
    print("ok  ", p)
print(f"{len(passed)} checks passed")
