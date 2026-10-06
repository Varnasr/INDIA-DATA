"""Assertions over the Gujarat raw tables in this folder.

Run from anywhere: python3 data/gujarat/raw/check_raw.py
Prints ok or FAIL for every check and exits 1 if any check fails.

The SIR tables were transcribed by eye from images of the Chief Electoral
Officer's printouts (see SOURCES.md). Every AC row is held by two identities
and every column by a printed subtotal, so a misread digit fails at least one
check below.
"""
import csv
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
COLS = ['before', 'death', 'untraceable_absent', 'shifted', 'already_enrolled', 'other', 'total', 'draft']
REASONS = COLS[1:6]
# "Total of State" row, printed identically in the AC table (page 4) and the district table
STATE = dict(zip(COLS, [50843436, 1807278, 969662, 4025553, 381470, 189364, 7373327, 43470109]))
# "Total of State" row of the final-roll table (17 Feb 2026)
FINAL_STATE = {'draft': 43470109, 'addition': 956121, 'deletion': 395555, 'net': 560566, 'final': 44030725}
# The final-roll table is inconsistent as printed: in these seven districts the
# printed final exceeds draft + addition - deletion by these amounts (the net
# column itself equals addition - deletion everywhere). They sum to 50, which is
# exactly the gap in the printed state row (43,470,109 + 560,566 = 44,030,675
# against a printed 44,030,725). Kept as printed; any other gap fails.
FINAL_PRINTED_GAP = {'Banaskantha': 1, 'Ahmedabad': 25, 'Rajkot': 1, 'Panchmahal': 5,
                     'Dahod': 6, 'Surat': 5, 'Navsari': 7}
DECLARED_2022 = {'BJP': 156, 'INC': 17, 'AAP': 5, 'IND': 3, 'SP': 1}

results = []


def check(cond, msg, detail=''):
    results.append(bool(cond))
    print(('ok    ' if cond else 'FAIL  ') + msg + ('' if cond or not detail else '  [' + str(detail) + ']'))
    return cond


def load(name):
    with open(os.path.join(HERE, name), newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def ints(r, cols):
    return {c: int(r[c]) for c in cols}


# ac.csv -----------------------------------------------------------------------
ac = load('ac.csv')
check(len(ac) == 182 and sorted(int(r['ac']) for r in ac) == list(range(1, 183)),
      'ac.csv: 182 rows, ACs numbered 1 to 182')
bad_reason = [r['ac'] for r in ac if sum(int(r[k]) for k in REASONS) != int(r['total'])]
check(not bad_reason, 'ac.csv: in every AC the five reasons sum to the total', bad_reason)
bad_draft = [r['ac'] for r in ac if int(r['before']) - int(r['total']) != int(r['draft'])]
check(not bad_draft, 'ac.csv: in every AC before - total = draft', bad_draft)
check(all(int(r[c]) >= 0 for r in ac for c in COLS), 'ac.csv: no negative figures')
check(len({r['district'] for r in ac}) == 33, 'ac.csv: 33 districts')

# district_printed_totals.csv ------------------------------------------------------
pt = load('district_printed_totals.csv')
pd = [r for r in pt if r['level'] == 'district']
ps = [r for r in pt if r['level'] == 'state']
check(len(pd) == 33 and len(ps) == 1, 'district_printed_totals.csv: 33 "Total of District" rows and one "Total of State"')
sums = defaultdict(lambda: Counter())
for r in ac:
    for c in COLS:
        sums[r['district']][c] += int(r[c])
bad_sub = []
for r in pd:
    for c in COLS:
        if sums[r['district']][c] != int(r[c]):
            bad_sub.append((r['district'], c, sums[r['district']][c] - int(r[c])))
check(not bad_sub, 'each district\'s ACs sum to its printed "Total of District" row, in every column', bad_sub)
col_pd = {c: sum(int(r[c]) for r in pd) for c in COLS}
check(col_pd == STATE, 'the 33 printed district totals sum to the printed "Total of State" row', col_pd)
check(ints(ps[0], COLS) == STATE, 'the printed "Total of State" row is 5,08,43,436 | 18,07,278 | 9,69,662 | '
      '40,25,553 | 3,81,470 | 1,89,364 | 73,73,327 | 4,34,70,109')
col_ac = {c: sum(int(r[c]) for r in ac) for c in COLS}
check(col_ac == STATE, 'the 182 AC rows sum to the state total in every column', col_ac)

# district.csv ---------------------------------------------------------------------
dist = load('district.csv')
check(len(dist) == 33 and [int(r['sno']) for r in dist] == list(range(1, 34)), 'district.csv: 33 districts, numbered 1 to 33')
check(all(sum(int(r[k]) for k in REASONS) == int(r['total']) and int(r['before']) - int(r['total']) == int(r['draft'])
          for r in dist), 'district.csv: in every district the reasons sum to the total and before - total = draft')
pmap = {r['district']: ints(r, COLS) for r in pd}
bad_eq = [r['district'] for r in dist if pmap.get(r['district']) != ints(r, COLS)]
check(not bad_eq, 'the printed district totals in the AC table equal district.csv, district by district', bad_eq)
check([r['district'] for r in dist] == [r['district'] for r in pd], 'district.csv and the AC table list the districts in the same order')
check({c: sum(int(r[c]) for r in dist) for c in COLS} == STATE, 'district.csv: every column sums to the state total')

# final_district.csv -----------------------------------------------------------------
fin = load('final_district.csv')
FC = ['draft', 'addition', 'deletion', 'net', 'final']
check(len(fin) == 34 and [int(r['sno']) for r in fin] == list(range(1, 35)), 'final_district.csv: 34 districts, numbered 1 to 34')
check(all(int(r['addition']) - int(r['deletion']) == int(r['net']) for r in fin),
      'final_district.csv: net = addition - deletion in every district')
gaps = {r['district']: int(r['final']) - (int(r['draft']) + int(r['addition']) - int(r['deletion'])) for r in fin}
gaps = {k: v for k, v in gaps.items() if v}
check(gaps == FINAL_PRINTED_GAP,
      'final_district.csv: draft + addition - deletion = final, except the 7 districts printed inconsistently (recorded)', gaps)
check(all(abs(round(100 * int(r['net']) / int(r['draft']), 2) - float(r['pct'])) < 0.006 for r in fin),
      'final_district.csv: the printed % net change equals net / draft')
check({c: sum(int(r[c]) for r in fin) for c in FC} == FINAL_STATE,
      'final_district.csv: columns sum to the printed state row 4,34,70,109 | 9,56,121 | 3,95,555 | 5,60,566 | 4,40,30,725')
check(FINAL_STATE['draft'] + FINAL_STATE['net'] + sum(FINAL_PRINTED_GAP.values()) == FINAL_STATE['final'],
      'the printed state row is off by exactly the 50 of the seven district gaps')
fd = {r['district']: int(r['draft']) for r in fin}
dd = {r['district']: int(r['draft']) for r in dist}
merged = dict(fd)
merged['Banaskantha'] = merged.pop('Banaskantha') + merged.pop('Vav-Tharad')
check(merged == dd, 'the 34-district draft equals the 33-district draft once Banaskantha and Vav-Tharad are added together')
# Vav-Tharad was carved out of Banaskantha. No table names its ACs; the draft
# of 7 Vav, 8 Tharad and 14 Deodar adds to its 8,02,018 exactly, and no other
# set of Banaskantha ACs comes within 500 (see SOURCES.md).
vav_tharad = sum(int(r['draft']) for r in ac if r['ac'] in ('7', '8', '14'))
check(vav_tharad == fd['Vav-Tharad'],
      'Vav-Tharad\'s draft (8,02,018) equals the draft of ACs 7 Vav, 8 Tharad and 14 Deodar', (vav_tharad, fd['Vav-Tharad']))

# results_2022.csv -------------------------------------------------------------------
res = load('results_2022.csv')
check(len(res) == 182 and sorted(int(r['ac']) for r in res) == list(range(1, 183)), 'results_2022.csv: 182 ACs, numbered 1 to 182')
check(all(int(r['margin']) == int(r['winner_votes']) - int(r['runner_up_votes']) > 0 for r in res),
      'results_2022.csv: margin = winner_votes - runner_up_votes > 0 in every AC')
check(all('NOTA' not in (r['runner_up'] + r['runner_up_party']).upper() for r in res), 'results_2022.csv: NOTA is never the runner-up')
check(all(int(r['runner_up_votes']) > 0 and int(r['votes_total']) >= int(r['winner_votes']) + int(r['runner_up_votes']) + int(r['nota_votes'])
          for r in res), 'results_2022.csv: votes_total covers winner, runner-up and NOTA in every AC')
check(all(int(r['votes_total']) < int(r['electors']) for r in res), 'results_2022.csv: votes_total below electors in every AC')
seats = dict(Counter(r['winner_party'] for r in res))
check(seats == DECLARED_2022, 'results_2022.csv: seats by party equal the declared result (BJP 156, INC 17, AAP 5, IND 3, SP 1)', seats)
names = {r['ac']: r['ac_name'] for r in ac}
check(all(names[r['ac']] == r['ac_name'] for r in res), 'results_2022.csv: ac_name equals the name in ac.csv')

n_fail = results.count(False)
print(f'\n{len(results) - n_fail} ok, {n_fail} failed')
sys.exit(1 if n_fail else 0)
