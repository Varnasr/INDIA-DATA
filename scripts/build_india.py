#!/usr/bin/env python3
"""All India: the reasons recorded for SIR removals, state by state.

    python3 scripts/build_india.py          # writes data/india/states.json and states.csv
    python3 scripts/build_india.py --check  # fails if either is stale

Source: data/india/raw/states.csv, one row per state or union territory,
curated from the Chief Electoral Officers' draft-roll figures (their press
notes where they could be read, press reports of them otherwise) and, for
Bihar, from the phase 1 deletion lists on this site.

The figures are those at the draft roll: the names left off it at the end of
enumeration, with the reason entered for each. The reasons are folded into
the three that every state reports: dead, shifted or absent (with "others"
where a state reported it), and enrolled more than once. Names removed after
the draft, at hearings and on objections, carry no reason in any state and
are kept apart.
"""
import csv
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(ROOT, 'data', 'india', 'raw', 'states.csv')
OUT_J = os.path.join(ROOT, 'data', 'india', 'states.json')
OUT_C = os.path.join(ROOT, 'data', 'india', 'states.csv')
R = ['dead', 'shifted_absent_other', 'duplicate']
INT = ['electors_before', 'removed', 'removed_after_draft'] + R


def load():
    rows = []
    for x in csv.DictReader(open(RAW, encoding='utf-8')):
        for k in INT:
            x[k] = int(x[k]) if x[k] else None
        rows.append(x)
    return rows


def build():
    rows = load()
    names = [x['state'] for x in rows]
    assert len(names) == len(set(names)) == 32, 'one row for each of the 32 states and union territories'
    for x in rows:
        split = x['split']
        cats = [x[k] for k in R]
        if split in ('complete', 'short'):
            assert all(c is not None for c in cats), x['state']
            s = sum(cats)
            gap = x['removed'] - s
            # A complete split may miss by rounding (lakh figures), never by more than 0.5%.
            if split == 'complete':
                assert abs(gap) <= 0.005 * x['removed'], (x['state'], gap)
            else:
                assert gap > 0, x['state']
            x['unsplit'] = max(gap, 0)
            x['shares'] = {k: round(100 * x[k] / s, 2) for k in R}
        else:
            assert all(c is None for c in cats), x['state']
            x['unsplit'] = x['removed']
            x['shares'] = None
        x['per_100'] = round(100 * x['removed'] / x['electors_before'], 2) if x['removed'] and x['electors_before'] else None
    has = [x for x in rows if x['removed'] is not None]

    def total(xs):
        t = {'states': len(xs), 'removed': sum(x['removed'] for x in xs)}
        for k in R:
            t[k] = sum(x[k] or 0 for x in xs)
        t['unsplit'] = t['removed'] - sum(t[k] for k in R)
        split = sum(t[k] for k in R)
        t['shares'] = {k: round(100 * t[k] / split, 2) for k in R}
        wb = [x for x in xs if x['electors_before']]
        t['per_100'] = round(100 * sum(x['removed'] for x in wb) / sum(x['electors_before'] for x in wb), 2)
        return t

    out = {
        'as_of': '2026-09-30',
        'reasons': R,
        'total': total(has),
        'by_phase': {p: total([x for x in has if x['phase'] == p]) for p in ('1', '2', '3')},
        'pending': [x['state'] for x in rows if x['removed'] is None],
        'after_draft': {'states': sum(1 for x in rows if x['removed_after_draft'] is not None),
                        'removed': sum(x['removed_after_draft'] or 0 for x in rows)},
        'states': rows,
    }
    return out


def dump_csv(d):
    import io
    cols = ['state', 'phase', 'draft_date', 'electors_before', 'removed', 'per_100', 'dead', 'shifted_absent_other', 'duplicate', 'unsplit',
            'split', 'figures', 'source', 'source_url', 'removed_after_draft', 'final_date', 'note']
    b = io.StringIO()
    w = csv.DictWriter(b, fieldnames=cols, extrasaction='ignore', lineterminator='\n')
    w.writeheader()
    for x in d['states']:
        w.writerow({k: ('' if x.get(k) is None else x[k]) for k in cols})
    return b.getvalue()


def main():
    d = build()
    j = json.dumps(d, ensure_ascii=False, indent=1) + '\n'
    c = dump_csv(d)
    if '--check' in sys.argv:
        stale = [p for p, s in ((OUT_J, j), (OUT_C, c)) if not os.path.exists(p) or open(p, encoding='utf-8').read() != s]
        if stale:
            sys.exit('stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale) + ' (run scripts/build_india.py)')
        print('PASS: data/india is current')
        return
    open(OUT_J, 'w', encoding='utf-8').write(j)
    open(OUT_C, 'w', encoding='utf-8').write(c)
    t = d['total']
    print('%d states, %s removed, dead %.1f%%, shifted/absent/other %.1f%%, duplicate %.1f%%, not split %s'
          % (t['states'], t['removed'], t['shares']['dead'], t['shares']['shifted_absent_other'], t['shares']['duplicate'], t['unsplit']))


if __name__ == '__main__':
    main()
