"""Assertions over the Uttar Pradesh raw tables in this folder.

Run from anywhere: python3 data/uttarpradesh/raw/check.py
Checks every CSV that exists; tables not yet collected are reported as missing.
"""
import csv
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
N_AC = 403
N_DISTRICT = 75
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)
    return cond


def load(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        print(f"MISSING {name}")
        return None
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# results_2022.csv -----------------------------------------------------------
rows = load("results_2022.csv")
if rows is not None:
    acs = [int(r["ac"]) for r in rows]
    check(len(rows) == N_AC, f"results_2022: {len(rows)} rows, expected {N_AC}")
    check(sorted(acs) == list(range(1, N_AC + 1)), "results_2022: ACs are not exactly 1..403")
    check(len({r["district"] for r in rows}) == N_DISTRICT, "results_2022: district count is not 75")
    margin_printed_differs = []
    share_inconsistent = []
    for r in rows:
        wv, rv = int(r["winner_votes"]), int(r["runner_up_votes"])
        check(wv > rv, f"results_2022 AC {r['ac']}: winner not ahead of runner-up")
        check(int(r["margin"]) == wv - rv, f"results_2022 AC {r['ac']}: margin != winner - runner-up")
        check(float(r["winner_pct"]) > float(r["runner_up_pct"]), f"results_2022 AC {r['ac']}: winner share not ahead")
        if int(r["margin_printed"]) != wv - rv:
            margin_printed_differs.append(int(r["ac"]))
        # Votes over vote share implies the AC's total valid votes; winner and
        # runner-up must imply the same total within rounding of the shares
        # (two decimals), else one of the vote figures is wrong.
        tw = wv / float(r["winner_pct"]) * 100
        tr = rv / float(r["runner_up_pct"]) * 100
        tol = tw * 0.005 / float(r["runner_up_pct"]) + tw * 0.005 / float(r["winner_pct"]) + 2
        if abs(tw - tr) > tol:
            share_inconsistent.append(int(r["ac"]))
    seats = Counter(r["winner_party"] for r in rows)
    declared = {"BJP": 255, "SP": 111, "AD(S)": 12, "RLD": 8, "SBSP": 6,
                "NISHAD": 6, "INC": 2, "JD(L)": 2, "BSP": 1}
    check(dict(seats) == declared, f"results_2022: seat tally {dict(seats)} != declared {declared}")
    check(share_inconsistent == [], f"results_2022: votes and shares disagree in ACs {share_inconsistent}")
    print(f"results_2022: {len(rows)} rows; seats {dict(seats)}")
    print(f"results_2022: printed margin differs from winner - runner-up in {len(margin_printed_differs)} ACs: {margin_printed_differs}")
    print(f"results_2022: votes consistent with vote shares in all ACs except {share_inconsistent}")


# SIR tables -------------------------------------------------------------------
def check_ac_table(name, parts, total="total"):
    rows = load(name)
    if rows is None:
        return
    acs = [int(r["ac"]) for r in rows]
    check(sorted(acs) == list(range(1, N_AC + 1)), f"{name}: ACs are not exactly 1..403")
    for r in rows:
        s = sum(int(r[p] or 0) for p in parts)
        check(s == int(r[total]), f"{name} AC {r['ac']}: parts {s} != total {r[total]}")
    print(f"{name}: {len(rows)} rows; " + ", ".join(f"{c} {sum(int(r[c] or 0) for r in rows):,}" for c in parts + [total]))


check_ac_table("asd_ac.csv", ["dead", "shifted_absent", "multiple", "others"])
check_ac_table("draft_roll_ac.csv", ["men", "women", "third"])
check_ac_table("final_roll_ac.csv", ["men", "women", "third"])

# asd_district.csv -------------------------------------------------------------
# The CEO's district table of the draft roll, transcribed from a photograph.
# Every row has to add up two independent ways, and the columns have to equal
# the State row printed on the same sheet, or a digit was misread.
STATE_ROW = {"roll_before": 154430092, "draft": 125556025, "dead": 4623796,
             "untraceable_absent": 7952190, "shifted": 12977472,
             "multiple": 2547207, "others": 773402, "total": 28874067}
REASONS = ["dead", "untraceable_absent", "shifted", "multiple", "others"]
dist = load("asd_district.csv")
if dist is not None:
    check(len(dist) == N_DISTRICT, f"asd_district: {len(dist)} rows, expected {N_DISTRICT}")
    check(sorted(int(r["sno"]) for r in dist) == list(range(1, N_DISTRICT + 1)), "asd_district: sno not 1..75")
    for r in dist:
        v = {k: int(r[k]) for k in STATE_ROW}
        check(v["roll_before"] - v["draft"] == v["total"],
              f"asd_district {r['district']}: before - draft != total")
        check(sum(v[k] for k in REASONS) == v["total"],
              f"asd_district {r['district']}: reasons do not sum to total")
    for k, want in STATE_ROW.items():
        got = sum(int(r[k]) for r in dist)
        check(got == want, f"asd_district: column {k} sums to {got}, State row {want}")
    names = {r["district"] for r in dist}
    if results_districts := ({r["district"] for r in rows} if rows is not None else None):
        alias = {"Kheri": "Lakhimpur Kheri"}
        mapped = {alias.get(n, n) for n in names}
        check(mapped == results_districts, f"asd_district: districts differ from results_2022: {sorted(mapped ^ results_districts)}")
    print(f"asd_district: {len(dist)} rows; " + ", ".join(f"{k} {sum(int(r[k]) for r in dist):,}" for k in STATE_ROW))

# sir_state_summary.csv --------------------------------------------------------
summ = load("sir_state_summary.csv")
if summ is not None:
    val = {}
    for r in summ:
        t = int(r["total"])
        if r["men"]:
            parts = int(r["men"]) + int(r["women"]) + int(r["third"])
            check(parts == t, f"sir_state_summary {r['item']}: men + women + third {parts} != total {t}")
        if r["item"] in val:
            check(val[r["item"]] == t, f"sir_state_summary {r['item']}: sources disagree")
        val[r["item"]] = t
    check(val["roll_before"] - val["draft"] == val["removed_at_draft"], "summary: before - draft != removed")
    check(val["forms_collected"] == val["draft"], "summary: forms collected != draft")
    check(sum(val["removed_" + k] for k in ["dead", "untraceable_absent", "shifted", "multiple", "others"])
          == val["removed_at_draft"], "summary: reasons do not sum to removed")
    check(val["final"] - val["draft"] == val["net_rise_draft_to_final"], "summary: final - draft != net rise")
    if dist is not None:
        check(val["removed_at_draft"] == STATE_ROW["total"], "summary and district table disagree")
    after = sum(val[k] for k in val if k.startswith("removed_after_draft_"))
    print(f"sir_state_summary: {len(summ)} rows; removed at draft {val['removed_at_draft']:,}; "
          f"after draft {val['removed_after_draft']:,}, of which itemised exactly {after:,} "
          f"(remainder {val['removed_after_draft'] - after:,} reported as 3.28 lakh shifted)")

if fails:
    print("\nFAILED:")
    for m in fails:
        print("  " + m)
    sys.exit(1)
print("\nPASS")
