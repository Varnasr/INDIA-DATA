#!/usr/bin/env python3
"""Integrity checks for the Bihar electoral datasets.

This dashboard makes political claims about electoral roll deletions. Nothing in
the repository checked the data those claims rest on, and three of the columns
they depend on do not survive contact with published election results. The
findings are written up in DATA_INTEGRITY.md; this script is what keeps them
from being quietly forgotten or quietly reintroduced.

Two kinds of check:

  STRUCTURAL   invariants that must hold. Bihar has 243 assembly constituencies
               and 38 districts; ac_number runs 1..243 exactly once; derived
               columns recompute from their inputs. These pass, and a change
               that breaks one is a new defect.

  KNOWN DEFECT conditions that are currently WRONG and are pinned here so the
               state is explicit. Each asserts the defect is still exactly as
               documented. If you repair the data, the corresponding check fails
               and tells you to update DATA_INTEGRITY.md and delete it. That is
               the intended way for these to die.

Run:  python3 scripts/check_data.py
"""
import csv
import statistics as st
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEL = ROOT / "data" / "ac_deletions_change_2020_2024.csv"

failures = []
notes = []


def check(name, fn, kind="STRUCTURAL"):
    try:
        note = fn()
        print(f"  ok    [{kind}] {name}" + (f" ({note})" if note else ""))
    except AssertionError as e:
        failures.append(name)
        print(f"  FAIL  [{kind}] {name}\n        {e}")


def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


rows = load(DEL)

# --------------------------------------------------------------------------
# Structural
# --------------------------------------------------------------------------

def _count():
    assert len(rows) == 243, f"Bihar has 243 assembly constituencies, found {len(rows)}"
    return "243 ACs"
check("one row per assembly constituency", _count)


def _acnum():
    nums = sorted(int(r["ac_number"]) for r in rows)
    assert nums == list(range(1, 244)), "ac_number is not exactly 1..243 with no gaps or repeats"
check("ac_number covers 1..243 exactly once", _acnum)


def _names():
    """ac_name is NOT a key, and joining on it silently merges two constituencies.

    Bihar has two Kalyanpur constituencies (16, Purvi Champaran; 131, Samastipur,
    SC-reserved) and two Pipra constituencies (17 and 42). These are genuinely
    distinct seats that happen to share a name, verified against the Wikipedia
    constituency pages and the Bihar CEO's own Form 20 for AC 131. Any join or
    lookup in this repository must use ac_number.
    """
    dupes = sorted(n for n, c in Counter(r["ac_name"] for r in rows).items() if c > 1)
    assert dupes == ["Kalyanpur", "Pipra"], (
        f"the set of duplicate constituency names changed: {dupes}. Confirm against "
        f"the ECI list before treating either as an error; two Bihar seats really do "
        f"share each of these names."
    )
    return "Kalyanpur and Pipra are each two real seats; join on ac_number, not name"
check("duplicate constituency names are the two known legitimate pairs", _names)


def _derived_2024():
    bad = []
    for r in rows:
        want = int(r["deletions_2024"]) / int(r["booths_2024"])
        if abs(want - float(r["del_per_booth_2024"])) > 1e-6:
            bad.append(r["ac_name"])
    assert not bad, f"del_per_booth_2024 does not equal deletions/booths for: {bad[:5]}"
    return "recomputes exactly"
check("del_per_booth_2024 is consistent with its inputs", _derived_2024)


def _no_negative():
    bad = [r["ac_name"] for r in rows if int(r["deletions_2024"]) < 0 or int(r["booths_2024"]) <= 0]
    assert not bad, f"non-positive booths or negative deletions: {bad[:5]}"
check("booth counts positive and deletions non-negative", _no_negative)


def _sir_total():
    total = sum(int(r["deletions_2024"]) for r in rows)
    assert 6_000_000 <= total <= 7_000_000, (
        f"total 'deletions_2024' is {total:,}; it had been ~6.56M, consistent with the "
        f"reported Bihar SIR figure of roughly 65 lakh"
    )
    return f"{total:,}"
check("2024 deletions total stays near the reported SIR figure", _sir_total)


# --------------------------------------------------------------------------
# Known defects. See DATA_INTEGRITY.md. Each of these SHOULD eventually fail.
# --------------------------------------------------------------------------

def _booths_copied():
    same = sum(1 for r in rows if r["booths_2020"] == r["booths_2024"])
    assert same == 243, (
        f"booths_2020 now differs from booths_2024 in {243 - same} rows. If the 2020 "
        f"booth counts have been sourced, delete this check and finding 1 in "
        f"DATA_INTEGRITY.md, and recompute del_per_booth_2020, delta_del_per_booth, "
        f"pct_change_del_per_booth and quartile_2020, which were all derived from the "
        f"wrong denominator."
    )
    return "still a verbatim copy in all 243 rows, as documented"
check("DEFECT 1: booths_2020 is a copy of booths_2024", _booths_copied, "KNOWN DEFECT")


def _deletions_2020_implausible():
    total = sum(int(r["deletions_2020"]) for r in rows)
    assert total > 30_000_000, (
        f"deletions_2020 now totals {total:,}, no longer the implausible 39.2M. If this "
        f"column has been sourced or corrected, delete this check and finding 2 in "
        f"DATA_INTEGRITY.md."
    )
    return f"{total:,}, still ~54% of Bihar's electorate, as documented"
check("DEFECT 2: deletions_2020 remains implausibly large", _deletions_2020_implausible,
      "KNOWN DEFECT")


def _party_2024_unreconciled():
    """BJP and JD(U) each won 12 of Bihar's 40 Lok Sabha seats in 2024.

    At roughly six assembly segments per parliamentary seat that is about 72
    segments each. RJD won 4 and LJP(RV) 5. BSP and independents won none.
    """
    c = Counter(r["party_2024"] for r in rows)
    assert c.get("JD(U)", 0) < 40 or c.get("BSP", 0) > 20, (
        "party_2024 now reconciles with the 2024 Lok Sabha result. Delete this check "
        "and finding 3 in DATA_INTEGRITY.md, and recheck every claim that groups by "
        "alliance_2024_ls."
    )
    return (f"JD(U)={c.get('JD(U)', 0)} (expect ~72), BSP={c.get('BSP', 0)} (expect 0), "
            f"RJD={c.get('RJD', 0)} (expect ~24)")
check("DEFECT 3: party_2024 does not match the 2024 Lok Sabha result",
      _party_2024_unreconciled, "KNOWN DEFECT")


def _alliance_coverage():
    c = Counter(r["alliance_2024_ls"] for r in rows)
    classified = c.get("NDA", 0) + c.get("INDIA", 0)
    assert classified < 200, (
        f"alliance_2024_ls now classifies {classified} of 243 ACs. Delete this check "
        f"and finding 4 in DATA_INTEGRITY.md."
    )
    return f"{classified} of 243 classified NDA or INDIA, as documented"
check("DEFECT 4: alliance_2024_ls leaves most constituencies unclassified",
      _alliance_coverage, "KNOWN DEFECT")


def _comparison_not_robust():
    """The dashboard's headline political claim flips with the labelling year."""
    def mean_for(col, label):
        v = [float(r["del_per_booth_2024"]) for r in rows if r[col] == label]
        return st.mean(v) if v else float("nan")
    nda24, ind24 = mean_for("alliance_2024_ls", "NDA"), mean_for("alliance_2024_ls", "INDIA")
    nda20, ind20 = mean_for("alliance_2020_vs", "NDA"), mean_for("alliance_2020_vs", "INDIA")
    flips = (nda24 < ind24) != (nda20 < ind20)
    assert flips, (
        "the NDA/INDIA comparison no longer reverses between the 2020 and 2024 "
        "labellings. Delete this check and finding 5 in DATA_INTEGRITY.md."
    )
    return (f"2024 labels NDA {nda24:.1f} vs INDIA {ind24:.1f}; "
            f"2020 labels NDA {nda20:.1f} vs INDIA {ind20:.1f}")
check("DEFECT 5: the NDA/INDIA comparison reverses with the labelling year",
      _comparison_not_robust, "KNOWN DEFECT")


# --------------------------------------------------------------------------

print()
if failures:
    print(f"FAIL - {len(failures)} check(s) failed: {', '.join(failures)}")
    print("If a KNOWN DEFECT check failed, the data was repaired: update "
          "DATA_INTEGRITY.md and remove the check.")
    sys.exit(1)
print("PASS - structural invariants hold; 5 documented defects unchanged")
