"""Uttarakhand: what happened to the roll after the SIR draft, in each of
the 70 assembly constituencies, and the names left off the draft for the
state as a whole.

Reads data/uttarakhand/raw (see SOURCES.md there; check_raw.py there checks
the transcription) and writes data/uttarakhand/summary.json,
constituencies.json, districts.json and the two CSVs.

    python3 scripts/build_uttarakhand.py           # write
    python3 scripts/build_uttarakhand.py --check   # fail if the output is stale

- The constituency figures are the Chief Electoral Officer's table published
  with the final roll (PN 63/2026, 3 October 2026): the draft roll, claims
  admitted (Form 6, 6A and Form 8 transfers in), objections admitted (Form 7
  and Form 8 transfers out) and the final roll, each by sex.
- The names left off the draft and their four reasons are for the state only
  (PN 36/2026, 14 July 2026). No table of the roll before the revision by
  constituency or district was published, so nothing below the state is
  measured against it.
- Rates after the draft are per 1,000 electors on the draft roll, because
  claims and objections are a few per cent of a constituency's roll.
- PLAINS is the four districts with the plains of the state, Dehradun,
  Haridwar, Nainital and Udham Singh Nagar. Dehradun and Nainital also take in
  hill constituencies, so the split is by district and is said to be.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'uttarakhand', 'raw')
OUT = os.path.join(ROOT, 'data', 'uttarakhand')
CHECK = '--check' in sys.argv
PLAINS = ['Dehradun', 'Haridwar', 'Nainital', 'Udham Singh Nagar']


def rd(name):
    return list(csv.DictReader(open(os.path.join(RAW, name), encoding='utf-8')))


def r1(x):
    return round(x, 1)


def block(rows):
    """Totals and rates for any set of constituencies."""
    t = {}
    for k in ('draft', 'draft_women', 'claims', 'claims_women', 'objections', 'objections_women', 'final', 'final_women'):
        t[k] = sum(r[k] for r in rows)
    t['net'] = t['final'] - t['draft']
    t['claims_per_1000'] = r1(1000 * t['claims'] / t['draft'])
    t['objections_per_1000'] = r1(1000 * t['objections'] / t['draft'])
    t['net_per_1000'] = r1(1000 * t['net'] / t['draft'])
    t['women_draft_pct'] = r1(100 * t['draft_women'] / t['draft'])
    t['women_claims_pct'] = r1(100 * t['claims_women'] / t['claims']) if t['claims'] else None
    t['women_objections_pct'] = r1(100 * t['objections_women'] / t['objections']) if t['objections'] else None
    t['women_final_pct'] = r1(100 * t['final_women'] / t['final'])
    return t


def main():
    st = {r['measure']: int(r['value']) for r in rd('state.csv')}
    rows = []
    for a in rd('ac.csv'):
        g = lambda k: int(a[k])
        r = {'ac': g('ac'), 'name': a['name'], 'district': a['district'],
             'draft': g('draft_men') + g('draft_women') + g('draft_tg'), 'draft_women': g('draft_women'),
             'claims': g('claims_total'), 'claims_women': g('claims_women'),
             'objections': g('objections_total'), 'objections_women': g('objections_women'),
             'final': g('final_men') + g('final_women') + g('final_tg'), 'final_women': g('final_women')}
        assert r['draft'] + r['claims'] - r['objections'] == r['final'], r['ac']
        r.update({k: v for k, v in block([r]).items() if k not in r})
        r['plains'] = r['district'] in PLAINS
        # how far women's share of the names removed after the draft
        # stands above their share of the draft roll, in points
        r['women_objections_gap'] = r1(r['women_objections_pct'] - r['women_draft_pct'])
        rows.append(r)
    assert len(rows) == 70
    S = block(rows)
    assert S['draft'] == st['draft'] and S['final'] == st['final']
    assert S['claims'] == st['claims_admitted'] and S['objections'] == st['objections_admitted']
    assert st['roll_before'] - st['draft'] == st['left_off'] == st['dead'] + st['absent_or_shifted'] + st['other'] + st['duplicate']

    D = {}
    for r in rows:
        D.setdefault(r['district'], []).append(r)
    dist = []
    for d, rs in D.items():
        b = block(rs)
        b.update({'district': d, 'acs': len(rs), 'plains': d in PLAINS})
        dist.append(b)
    dist.sort(key=lambda d: -d['objections_per_1000'])
    for r in rows:
        r['objections_vs_district'] = r1(r['objections_per_1000'] - [d for d in dist if d['district'] == r['district']][0]['objections_per_1000'])

    pl, hi = block([r for r in rows if r['plains']]), block([r for r in rows if not r['plains']])
    by_obj = sorted(rows, key=lambda r: -r['objections_per_1000'])
    by_gap = sorted(rows, key=lambda r: -r['women_objections_gap'])
    lost = [r for r in rows if r['net'] < 0]
    summ = {
        'roll_before': st['roll_before'], 'draft': st['draft'], 'left_off': st['left_off'],
        'per_100': r1(100 * st['left_off'] / st['roll_before']),
        'reasons': {k: st[k] for k in ('absent_or_shifted', 'dead', 'duplicate', 'other')},
        'shares': {k: r1(100 * st[k] / st['left_off']) for k in ('absent_or_shifted', 'dead', 'duplicate', 'other')},
        'claims': S['claims'], 'objections': S['objections'], 'final': S['final'], 'net': S['net'],
        'claims_per_1000': S['claims_per_1000'], 'objections_per_1000': S['objections_per_1000'], 'net_per_1000': S['net_per_1000'],
        # the net rise after the draft counts first-time electors too, so it is
        # the most that could have been put back, as a share of those left off
        'made_up_pct': r1(100 * S['net'] / st['left_off']),
        'final_vs_before': st['final'] - st['roll_before'], 'final_vs_before_per_100': r1(100 * (st['final'] - st['roll_before']) / st['roll_before']),
        'women_draft_pct': S['women_draft_pct'], 'women_claims_pct': S['women_claims_pct'],
        'women_objections_pct': S['women_objections_pct'], 'women_final_pct': S['women_final_pct'],
        'acs': 70, 'acs_lost': len(lost), 'acs_women_over': sum(r['women_objections_gap'] > 0 for r in rows),
        'acs_women_over_10': sum(r['women_objections_gap'] >= 10 for r in rows),
        'obj_max': by_obj[0]['name'], 'obj_max_v': by_obj[0]['objections_per_1000'],
        'obj_min': by_obj[-1]['name'], 'obj_min_v': by_obj[-1]['objections_per_1000'],
        'gap_max': by_gap[0]['name'], 'gap_max_pct': by_gap[0]['women_objections_pct'], 'gap_max_n': by_gap[0]['objections'],
        'plains': {'districts': PLAINS, 'acs': sum(r['plains'] for r in rows),
                   'draft_pct': r1(100 * pl['draft'] / S['draft']), 'claims_pct': r1(100 * pl['claims'] / S['claims']),
                   'objections_pct': r1(100 * pl['objections'] / S['objections']),
                   'objections_per_1000': pl['objections_per_1000'], 'claims_per_1000': pl['claims_per_1000'], 'net_per_1000': pl['net_per_1000']},
        'hills': {'acs': sum(not r['plains'] for r in rows), 'objections_per_1000': hi['objections_per_1000'],
                  'claims_per_1000': hi['claims_per_1000'], 'net_per_1000': hi['net_per_1000']},
        'electors_18_19': st['electors_18_19'], 'electors_80_plus': st['electors_80_plus'],
    }
    rows.sort(key=lambda r: r['ac'])
    files = {}
    files['summary.json'] = json.dumps(summ, ensure_ascii=False, indent=1) + '\n'
    files['constituencies.json'] = json.dumps(rows, ensure_ascii=False, indent=0) + '\n'
    files['districts.json'] = json.dumps(dist, ensure_ascii=False, indent=0) + '\n'
    acc = ['ac', 'name', 'district', 'draft', 'claims', 'objections', 'final', 'net', 'claims_per_1000', 'objections_per_1000', 'net_per_1000',
           'women_draft_pct', 'women_claims_pct', 'women_objections_pct', 'women_objections_gap']
    dcc = ['district', 'acs', 'draft', 'claims', 'objections', 'final', 'net', 'claims_per_1000', 'objections_per_1000', 'net_per_1000',
           'women_draft_pct', 'women_objections_pct']
    for name, data, cols in (('constituencies.csv', rows, acc), ('districts.csv', dist, dcc)):
        b = io.StringIO(); w = csv.writer(b, lineterminator='\n'); w.writerow(cols)
        for r in data:
            w.writerow([r[c] for c in cols])
        files[name] = b.getvalue()
    if CHECK:
        stale = [k for k, t in files.items() if not os.path.exists(os.path.join(OUT, k)) or open(os.path.join(OUT, k), encoding='utf-8').read() != t]
        assert not stale, 'stale: ' + ', '.join(stale)
        print('OK: data/uttarakhand matches its raw tables')
        return
    for k, t in files.items():
        open(os.path.join(OUT, k), 'w', encoding='utf-8').write(t)
    print('wrote data/uttarakhand: %d left off (%.1f per 100); after the draft +%d -%d, net %+d; %d of 70 seats ended below their draft' % (
        summ['left_off'], summ['per_100'], summ['claims'], summ['objections'], summ['net'], summ['acs_lost']))


if __name__ == '__main__':
    main()
