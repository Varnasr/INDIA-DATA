"""Checks the hand transcription of the Chief Electoral Officer's
constituency table (PN 63/2026, pages 3 and 4) against itself.

Every constituency must satisfy draft + claims admitted - objections admitted
= final, for men, women and third gender separately; claims and objections
must add to their printed totals; the constituencies of each district must add
to the district total the table prints; and the districts to the state total.
A misread digit breaks at least one of these.

    python3 data/uttarakhand/raw/check_raw.py
"""
import csv
import os
import sys

RAW = os.path.dirname(os.path.abspath(__file__))
K = ['draft_men', 'draft_women', 'draft_tg', 'claims_men', 'claims_women', 'claims_tg', 'claims_total',
     'objections_men', 'objections_women', 'objections_tg', 'objections_total', 'final_men', 'final_women', 'final_tg']


def main():
    A = list(csv.DictReader(open(os.path.join(RAW, 'ac.csv'), encoding='utf-8')))
    T = {r['district']: {k: int(r[k]) for k in K} for r in csv.DictReader(open(os.path.join(RAW, 'district_printed.csv'), encoding='utf-8'))}
    S = {r['measure']: int(r['value']) for r in csv.DictReader(open(os.path.join(RAW, 'state.csv'), encoding='utf-8'))}
    bad = []
    assert [int(a['ac']) for a in A] == list(range(1, 71)), 'constituencies 1 to 70, in order'
    for a in A:
        v = {k: int(a[k]) for k in K}
        for s in ('men', 'women', 'tg'):
            if v['draft_' + s] + v['claims_' + s] - v['objections_' + s] != v['final_' + s]:
                bad.append('%s %s: draft + claims - objections != final' % (a['ac'], s))
        for f in ('claims', 'objections'):
            if v[f + '_men'] + v[f + '_women'] + v[f + '_tg'] != v[f + '_total']:
                bad.append('%s %s total' % (a['ac'], f))
    dists = [d for d in T if d != 'State']
    assert len(dists) == 13 and set(dists) == {a['district'] for a in A}
    for d in dists:
        for k in K:
            if sum(int(a[k]) for a in A if a['district'] == d) != T[d][k]:
                bad.append('%s %s: constituencies do not add to the printed district total' % (d, k))
    for k in K:
        if sum(T[d][k] for d in dists) != T['State'][k] or sum(int(a[k]) for a in A) != T['State'][k]:
            bad.append('state %s' % k)
    st = T['State']
    want = {'draft_men': S['draft_men'], 'draft_women': S['draft_women'], 'draft_tg': S['draft_third_gender'],
            'claims_total': S['claims_admitted'], 'objections_total': S['objections_admitted'],
            'final_men': S['final_men'], 'final_women': S['final_women'], 'final_tg': S['final_third_gender']}
    for k, v in want.items():
        if st[k] != v:
            bad.append('state %s: table %d, press note %d' % (k, st[k], v))
    if st['draft_men'] + st['draft_women'] + st['draft_tg'] != S['draft'] or st['final_men'] + st['final_women'] + st['final_tg'] != S['final']:
        bad.append('state draft or final does not equal the press note')
    if S['roll_before'] - S['draft'] != S['left_off'] or S['dead'] + S['absent_or_shifted'] + S['other'] + S['duplicate'] != S['left_off']:
        bad.append('the reasons do not add to the names left off')
    if S['draft'] + S['claims_admitted'] - S['objections_admitted'] != S['final']:
        bad.append('draft + claims - objections != final, for the state')
    if bad:
        print('FAIL: ' + '; '.join(bad))
        sys.exit(1)
    print('OK: 70 constituencies, 13 districts and the state agree, row by row and with the press notes')


if __name__ == '__main__':
    main()
