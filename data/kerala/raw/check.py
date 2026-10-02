"""Assertions for the Kerala raw tables. Run: python3 data/kerala/raw/check.py

Published totals below are copied from the CEO Kerala PDFs named in
SOURCES.md (state row and every DISTRICT TOTAL row)."""
import csv
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUBLISHED = {
 "draft_roll_ac.csv": {
  "state": [
   12383341,
   13058731,
   280,
   25442352
  ],
  "districts": {
   "KASARAGOD": [
    503118,
    518217,
    10,
    1021345
   ],
   "KANNUR": [
    956081,
    1058517,
    10,
    2014608
   ],
   "WAYANAD": [
    296036,
    308449,
    2,
    604487
   ],
   "KOZHIKODE": [
    1204786,
    1267841,
    41,
    2472668
   ],
   "MALAPPURAM": [
    1635245,
    1603165,
    42,
    3238452
   ],
   "PALAKKAD": [
    1053676,
    1087582,
    18,
    2141276
   ],
   "THRISSUR": [
    1162170,
    1240241,
    21,
    2402432
   ],
   "ERNAKULAM": [
    1139053,
    1191571,
    19,
    2330643
   ],
   "IDUKKI": [
    384323,
    392051,
    7,
    776381
   ],
   "KOTTAYAM": [
    707341,
    742386,
    13,
    1449740
   ],
   "ALAPPUZHA": [
    779007,
    837538,
    16,
    1616561
   ],
   "PATHANAMTHITTA": [
    453812,
    495814,
    6,
    949632
   ],
   "KOLLM": [
    946604,
    1037263,
    18,
    1983885
   ],
   "THIRUVANANTHAPURAM": [
    1162089,
    1278096,
    57,
    2440242
   ]
  }
 },
 "final_roll_ac.csv": {
  "state": [
   13126048,
   13827319,
   277,
   26953644
  ],
  "districts": {
   "KASARAGOD": [
    540698,
    555530,
    13,
    1096241
   ],
   "KANNUR": [
    1041897,
    1118589,
    11,
    2160497
   ],
   "WAYANAD": [
    313257,
    327688,
    2,
    640947
   ],
   "KOZHIKODE": [
    1298343,
    1359102,
    33,
    2657478
   ],
   "MALAPPURAM": [
    1810627,
    1805303,
    40,
    3615970
   ],
   "PALAKKAD": [
    1105398,
    1147655,
    20,
    2253073
   ],
   "THRISSUR": [
    1218432,
    1294470,
    19,
    2512921
   ],
   "ERNAKULAM": [
    1202881,
    1266891,
    22,
    2469794
   ],
   "IDUKKI": [
    394705,
    404541,
    8,
    799254
   ],
   "KOTTAYAM": [
    730005,
    768805,
    14,
    1498824
   ],
   "ALAPPUZHA": [
    805899,
    864933,
    15,
    1670847
   ],
   "PATHANAMTHITTA": [
    466546,
    508251,
    5,
    974802
   ],
   "KOLLM": [
    992443,
    1084207,
    21,
    2076671
   ],
   "THIRUVANANTHAPURAM": [
    1204917,
    1321354,
    54,
    2526325
   ]
  }
 },

 "roll_before_ac.csv": {
  "state": [
   13441490,
   14369092,
   360,
   27810942
  ],
  "districts": {
   "KASARAGOD": [
    526098,
    550525,
    11,
    1076634
   ],
   "KANNUR": [
    1001233,
    1112114,
    12,
    2113359
   ],
   "WAYANAD": [
    313676,
    328520,
    4,
    642200
   ],
   "KOZHIKODE": [
    1285257,
    1372255,
    49,
    2657561
   ],
   "MALAPPURAM": [
    1700629,
    1700907,
    41,
    3401577
   ],
   "PALAKKAD": [
    1133985,
    1188571,
    23,
    2322579
   ],
   "THRISSUR": [
    1277491,
    1397098,
    36,
    2674625
   ],
   "ERNAKULAM": [
    1283008,
    1355070,
    28,
    2638106
   ],
   "IDUKKI": [
    438998,
    455108,
    6,
    894112
   ],
   "KOTTAYAM": [
    778510,
    827002,
    16,
    1605528
   ],
   "ALAPPUZHA": [
    838664,
    915485,
    15,
    1754164
   ],
   "PATHANAMTHITTA": [
    498291,
    554171,
    6,
    1052468
   ],
   "KOLLM": [
    1017994,
    1122362,
    20,
    2140376
   ],
   "THIRUVANANTHAPURAM": [
    1347656,
    1489904,
    93,
    2837653
   ]
  }
 },
 "election_roll_ac.csv": {
  "state": [
   13220811,
   13921868,
   273,
   27142952
  ],
  "districts": {
   "KASARAGOD": [
    544543,
    559063,
    12,
    1103618
   ],
   "KANNUR": [
    1052014,
    1124959,
    11,
    2176984
   ],
   "WAYANAD": [
    314584,
    329038,
    3,
    643625
   ],
   "KOZHIKODE": [
    1304604,
    1364182,
    31,
    2668817
   ],
   "MALAPPURAM": [
    1819198,
    1812974,
    38,
    3632210
   ],
   "PALAKKAD": [
    1112616,
    1156085,
    20,
    2268721
   ],
   "THRISSUR": [
    1228118,
    1304580,
    17,
    2532715
   ],
   "ERNAKULAM": [
    1218709,
    1285112,
    27,
    2503848
   ],
   "IDUKKI": [
    397586,
    407833,
    8,
    805427
   ],
   "KOTTAYAM": [
    735989,
    775578,
    13,
    1511580
   ],
   "ALAPPUZHA": [
    811641,
    871041,
    15,
    1682697
   ],
   "PATHANAMTHITTA": [
    469184,
    510955,
    5,
    980144
   ],
   "KOLLM": [
    998167,
    1089804,
    21,
    2087992
   ],
   "THIRUVANANTHAPURAM": [
    1213858,
    1330664,
    52,
    2544574
   ]
  }
 }
}


def rows(name):
    return list(csv.DictReader(open(HERE / name, newline="")))


def check_roll(name):
    r = rows(name)
    assert [int(x["ac"]) for x in r] == list(range(1, 141)), name
    for x in r:
        assert int(x["men"]) + int(x["women"]) + int(x["third"]) == int(x["total"]), (name, x["ac"])
    cols = ("men", "women", "third", "total")
    assert [sum(int(x[c]) for x in r) for c in cols] == PUBLISHED[name]["state"], name
    dist = defaultdict(lambda: [0, 0, 0, 0])
    for x in r:
        for i, c in enumerate(cols):
            dist[x["district"]][i] += int(x[c])
    assert dict(dist) == PUBLISHED[name]["districts"], name
    print(f"{name}: 140 ACs, row sums, {len(dist)} district totals and state total "
          f"{PUBLISHED[name]['state'][3]:,} all agree")
    return r


draft = check_roll("draft_roll_ac.csv")
final = check_roll("final_roll_ac.csv")
before = check_roll("roll_before_ac.csv")
election = check_roll("election_roll_ac.csv")
assert all(int(f["total"]) > int(d["total"]) for d, f in zip(draft, final))
print("final roll larger than draft in all 140 ACs")

res = rows("results_2026.csv")
cand = rows("results_2026_candidates.csv")
assert [int(x["ac"]) for x in res] == list(range(1, 141))
by_ac = defaultdict(list)
for c in cand:
    by_ac[int(c["ac"])].append(c)
    assert int(c["evm_votes"]) + int(c["postal_votes"]) == int(c["total_votes"]), c
for x in res:
    ac = int(x["ac"])
    cs = by_ac[ac]
    assert sum(int(c["total_votes"]) for c in cs) == int(x["total_votes"]), ac
    assert sum(int(c["postal_votes"]) for c in cs) == int(x["postal_votes"]), ac
    nota = [c for c in cs if c["party"] == "None of the Above"]
    assert len(nota) == 1 and int(nota[0]["total_votes"]) == int(x["nota_votes"]), ac
    nn = sorted((c for c in cs if c["party"] != "None of the Above"), key=lambda c: -int(c["total_votes"]))
    assert nn[0]["candidate"] == x["winner"] and int(nn[0]["total_votes"]) == int(x["winner_votes"]), ac
    assert nn[1]["candidate"] == x["runner_up"] and int(nn[1]["total_votes"]) == int(x["runner_up_votes"]), ac
    assert int(x["margin"]) == int(x["winner_votes"]) - int(x["runner_up_votes"]) > 0, ac
print(f"results_2026.csv: 140 ACs, {len(cand)} candidate rows; candidate votes sum to each AC total, "
      "EVM + postal = total, one NOTA per AC, winner and runner-up are the top two, margin = difference")
print("  winners:", dict(Counter(x["winner_party"] for x in res).most_common()))
tv = sum(int(x["total_votes"]) for x in res)
fr = sum(int(x["total"]) for x in final)
print(f"  total votes {tv:,} = {tv / fr:.1%} of the final SIR roll")

# AC names: the new tables spell every AC as draft_roll_ac.csv does except these.
NAME_DIFFS = {
 "roll_before_ac.csv": {8: "TALIPARMBA", 42: "VALIKKUNNU"},
 "election_roll_ac.csv": {61: "CHELACKARA", 83: "THRIPKAKARA"},
}
for name, tab in (("roll_before_ac.csv", before), ("election_roll_ac.csv", election)):
    got = {int(x["ac"]): x["ac_name"] for x in tab if x["ac_name"] != draft[int(x["ac"]) - 1]["ac_name"]}
    assert got == NAME_DIFFS[name], (name, got)
    assert all(x["district"] == d["district"] for x, d in zip(tab, draft)), name
print("AC names agree with the draft except the spellings listed in SOURCES.md")

tot = lambda t: [int(x["total"]) for x in t]
assert all(b > d for b, d in zip(tot(before), tot(draft)))
assert sum(tot(before)) - sum(tot(draft)) == 2368590
print("roll of 06.01.2025 larger than the draft in all 140 ACs, by 2,368,590 statewide")
assert sum(tot(before)) == 27850855 - 39913
print("roll of 06.01.2025 is 39,913 below the 2,78,50,855 frozen for the revision (press)")
assert all(e > f for e, f in zip(tot(election), tot(final)))
assert sum(tot(election)) - sum(tot(final)) == 189308
print("election roll of 23.03.2026 larger than the final SIR roll in all 140 ACs, by 189,308")
assert sum(int(x["total_votes"]) for x in res) <= sum(tot(election))
print(f"  total votes {tv:,} = {tv / sum(tot(election)):.1%} of the election roll")
