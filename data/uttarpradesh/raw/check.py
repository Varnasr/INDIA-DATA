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

if fails:
    print("\nFAILED:")
    for m in fails:
        print("  " + m)
    sys.exit(1)
print("\nPASS")
