"""Uttar Pradesh: the names left off the SIR draft roll, by district and
reason, and the state's roll from before the revision to the final roll.

Reads data/uttarpradesh/raw (see SOURCES.md there) and writes
data/uttarpradesh/summary.json, districts.json and districts.csv.

    python3 scripts/build_uttarpradesh.py           # write
    python3 scripts/build_uttarpradesh.py --check   # fail if the output is stale

The district table is the Chief Electoral Officer's handout of 6 January 2026,
known only from a photograph published by India TV and transcribed by eye.
Every row is held by two identities (roll before less draft = total, and the
five reasons add up to the total), and every column adds up to the handout's
printed State row, so a misread digit fails the build. No table by assembly
constituency could be reached, so there is no constituency page.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'uttarpradesh', 'raw')
OUT = os.path.join(ROOT, 'data', 'uttarpradesh')
CHECK = '--check' in sys.argv
R = ('dead', 'untraceable_absent', 'shifted', 'multiple', 'others')
# the handout's printed State row
STATE = {'roll_before': 154430092, 'draft': 125556025, 'dead': 4623796, 'untraceable_absent': 7952190,
         'shifted': 12977472, 'multiple': 2547207, 'others': 773402, 'total': 28874067}


def build():
    rows = list(csv.DictReader(open(os.path.join(RAW, 'asd_district.csv'), encoding='utf-8')))
    assert [int(r['sno']) for r in rows] == list(range(1, 76)), '75 districts, numbered 1 to 75'
    D = []
    for r in rows:
        v = {k: int(r[k]) for k in ('roll_before', 'draft', 'total') + R}
        assert v['roll_before'] - v['draft'] == v['total'] == sum(v[k] for k in R), r['district']
        d = {'district': r['district'].strip(), **v, 'per_100': round(100 * v['total'] / v['roll_before'], 2)}
        for k in R:
            d[k + '_pct'] = round(100 * v[k] / v['total'], 2)
        D.append(d)
    for k, t in STATE.items():
        assert sum(d[k] for d in D) == t, 'column %s does not add up to the State row' % k
    S = {(r['item'], r['date']): r for r in csv.DictReader(open(os.path.join(RAW, 'sir_state_summary.csv'), encoding='utf-8'))}
    get = lambda item: [r for (i, _), r in S.items() if i == item][0]
    dr, fn, nr = get('draft'), get('final'), get('net_rise_draft_to_final')
    assert int(dr['total']) == STATE['draft'] and int(dr['men']) + int(dr['women']) + int(dr['third']) == STATE['draft']
    assert int(fn['total']) - int(dr['total']) == int(nr['total']), 'final less draft equals the net rise'
    ra = get('removed_after_draft')
    f6, f7 = get('form6_2026-01-06_to_2026-03-06'), get('form7_2026-01-06_to_2026-03-06')
    T = STATE['total']
    D.sort(key=lambda d: -d['per_100'])
    summary = {
        'roll_before': STATE['roll_before'], 'draft': STATE['draft'], 'left_off': T, 'per_100': round(100 * T / STATE['roll_before'], 2),
        'reasons': {k: STATE[k] for k in R}, 'shares': {k: round(100 * STATE[k] / T, 2) for k in R},
        'final': int(fn['total']), 'final_date': '2026-04-10', 'net_rise': int(nr['total']), 'made_up_pct': round(100 * int(nr['total']) / T, 2),
        'removed_after': int(ra['total']), 'removed_after_kind': ra['kind'],
        'draft_women_pct': round(100 * int(dr['women']) / STATE['draft'], 2), 'final_women_pct': round(100 * int(fn['women']) / int(fn['total']), 2),
        'rise_women_pct': round(100 * int(nr['women']) / int(nr['total']), 2),
        'form6': int(f6['total']), 'form6_women_pct': round(100 * int(f6['women']) / int(f6['total']), 2),
        'form7': int(f7['total']), 'form7_women_pct': round(100 * int(f7['women']) / int(f7['total']), 2), 'forms_kind': f6['kind'],
        'districts': len(D), 'top': [{'district': d['district'], 'per_100': d['per_100'], 'total': d['total']} for d in D[:5]],
        'low': [{'district': d['district'], 'per_100': d['per_100']} for d in D[-3:]],
        'most_names': max(D, key=lambda d: d['total'])['district'],
        'over_20': sum(d['per_100'] >= 20 for d in D),
    }
    out = {'summary.json': json.dumps(summary, ensure_ascii=False, indent=1) + '\n',
           'districts.json': json.dumps(D, ensure_ascii=False, separators=(',', ':')) + '\n'}
    buf = io.StringIO(); w = csv.writer(buf, lineterminator='\n')
    cols = ['district', 'roll_before', 'draft', 'total', 'per_100'] + list(R) + [k + '_pct' for k in R]
    w.writerow(['district', 'roll_27_oct_2025', 'draft_roll_6_jan_2026', 'left_off', 'left_off_per_100'] + list(R) + [k + '_pct_of_left_off' for k in R])
    for d in D:
        w.writerow([d[c] for c in cols])
    out['districts.csv'] = buf.getvalue()
    stale = []
    for name, text in out.items():
        path = os.path.join(OUT, name)
        old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
        if old != text:
            stale.append(name)
            if not CHECK:
                open(path, 'w', encoding='utf-8').write(text)
    return summary, stale


if __name__ == '__main__':
    s, stale = build()
    if CHECK:
        if stale:
            sys.exit('STALE, run python3 scripts/build_uttarpradesh.py: ' + ', '.join(stale))
        print('OK: data/uttarpradesh matches its raw tables')
    else:
        print(json.dumps(s, indent=0)[:2500])
