#!/usr/bin/env python3
"""Bihar: the final roll of 30 September 2025, seat by seat.

    python3 scripts/build_bihar_final.py          # writes data/bihar/final.json
    python3 scripts/build_bihar_final.py --check  # fails if it is stale

Source: data/bihar/raw/final_roll_format4b.csv, the Election Commission's
Format 4B return for the final roll as the Chief Electoral Officer, Bihar
published it: for every seat and by sex, the draft roll, the names added
on claims and removed on objections after it, the reason for each of those
removals, and the final roll.

The roll before the revision is published only as a state total, so a
seat's roll before is taken here as its draft roll plus the names on its
phase 1 deletion list. The net fall in a seat is that less its final roll:
the names removed at the draft, less the net rise from draft to final.
"""
import csv
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(ROOT, 'data', 'bihar', 'raw', 'final_roll_format4b.csv')
ACS = os.path.join(ROOT, 'data', 'bihar', 'constituencies.json')
OUT = os.path.join(ROOT, 'data', 'bihar', 'final.json')
# The Chief Electoral Officer's press note of 30 September 2025.
PRESS = {'before': 78969844, 'draft': 72405756, 'added': 2153343, 'removed_after': 366742, 'final': 74192357}
SOURCE = 'http://ceoelection.bihar.gov.in/format_1to8.html'


def build():
    raw = list(csv.DictReader(open(RAW, encoding='utf-8')))
    for r in raw:
        for k in r:
            if k != 'ac_name':
                r[k] = int(r[k])
    acs = {a['ac']: a for a in json.load(open(ACS, encoding='utf-8'))}
    assert sorted(r['ac_number'] for r in raw) == sorted(acs) and len(raw) == 243, 'one row for each of the 243 seats'
    seats = []
    for r in raw:
        a = acs[r['ac_number']]
        assert r['electors_draft'] + r['added_after_draft'] - r['removed_after_draft'] == r['electors_final'], r['ac_number']
        assert r['men_final'] + r['women_final'] + r['third_gender_final'] == r['electors_final'], r['ac_number']
        assert r['removed_expired'] + r['removed_shifted'] + r['removed_repeated'] + r['removed_reason_unstated'] == r['removed_after_draft'], r['ac_number']
        net_after = r['electors_final'] - r['electors_draft']
        s = {'ac': a['ac'], 'name': a['name'], 'district': a['district'], 'draft': r['electors_draft'],
             'added': r['added_after_draft'], 'added_f': r['added_women'], 'added_m': r['added_men'],
             'removed_after': r['removed_after_draft'], 'removed_after_f': r['removed_women'], 'removed_after_m': r['removed_men'],
             'r_expired': r['removed_expired'], 'r_shifted': r['removed_shifted'], 'r_repeated': r['removed_repeated'], 'r_unstated': r['removed_reason_unstated'],
             'final': r['electors_final'], 'final_f': r['women_final'], 'final_m': r['men_final'],
             'p1': a['p1'], 'before': r['electors_draft'] + a['p1'], 'net_after': net_after, 'net_fall': a['p1'] - net_after,
             'made_up_pct': round(100 * net_after / a['p1'], 1),
             'margin2025': a['margin2025'], 'al2025': a['al2025'], 'win2025': a['win2025'], 'total': a['total']}
        s['net_fall_pct'] = round(100 * s['net_fall'] / s['before'], 4)
        seats.append(s)
    t = {k: sum(s[k] for s in seats) for k in ('draft', 'added', 'added_f', 'added_m', 'removed_after', 'removed_after_f', 'removed_after_m',
                                              'r_expired', 'r_shifted', 'r_repeated', 'r_unstated', 'final', 'final_f', 'final_m', 'p1', 'before', 'net_after', 'net_fall')}
    for k, v in (('draft', 'draft'), ('added', 'added'), ('removed_after', 'removed_after'), ('final', 'final')):
        assert t[k] == PRESS[v], (k, t[k], PRESS[v])
    # The lists fall a few thousand short of the press note's count at the draft.
    assert abs(t['before'] - PRESS['before']) < 0.001 * PRESS['before'], t['before']
    t['before_press'] = PRESS['before']
    t['net_fall_press'] = PRESS['before'] - PRESS['final']
    t['made_up_pct'] = round(100 * t['net_after'] / t['p1'], 1)
    p1f = sum(a['p1_f'] for a in acs.values())
    p1m = sum(a['p1_m'] for a in acs.values())
    t['women_share_p1'] = round(100 * p1f / (p1f + p1m), 4)
    t['women_share_added'] = round(100 * t['added_f'] / (t['added_f'] + t['added_m']), 4)
    t['women_share_removed_after'] = round(100 * t['removed_after_f'] / (t['removed_after_f'] + t['removed_after_m']), 4)
    t['women_share_final'] = round(100 * t['final_f'] / t['final'], 4)
    draft_f = sum(r['draft_women'] for r in raw)
    t['women_share_draft'] = round(100 * draft_f / t['draft'], 4)
    t['women_share_before'] = round(100 * (draft_f + p1f) / t['before'], 4)
    m = [s for s in seats if s['margin2025']]
    als = sorted({s['al2025'] for s in m})
    over = {'seats': len(m),
            'total': sum(1 for s in m if s['total'] > s['margin2025']),
            'net': sum(1 for s in m if s['net_fall'] > s['margin2025']),
            'net_by_alliance': {al: sum(1 for s in m if s['al2025'] == al and s['net_fall'] > s['margin2025']) for al in als},
            'won_by_alliance': {al: sum(1 for s in m if s['al2025'] == al) for al in als},
            'fell_every_seat': all(s['net_fall'] > 0 for s in seats)}
    mu = sorted(s['made_up_pct'] for s in seats)
    over['made_up_median'] = mu[len(mu) // 2]
    return {'as_of': '2025-09-30', 'source': SOURCE, 'totals': t, 'margin': over, 'seats': seats}


def main():
    j = json.dumps(build(), ensure_ascii=False, indent=1) + '\n'
    if '--check' in sys.argv:
        if not os.path.exists(OUT) or open(OUT, encoding='utf-8').read() != j:
            sys.exit('stale: data/bihar/final.json (run scripts/build_bihar_final.py)')
        print('PASS: data/bihar/final.json is current')
        return
    open(OUT, 'w', encoding='utf-8').write(j)
    d = json.loads(j)
    print(json.dumps(d['totals']), json.dumps(d['margin']))


if __name__ == '__main__':
    main()
