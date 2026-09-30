#!/usr/bin/env python3
"""The downloadable tables for Bihar and Hyderabad, written from the published JSON.

    python3 scripts/build_downloads.py          # writes the CSVs
    python3 scripts/build_downloads.py --check  # fails if any is stale

Counts only; every column is an aggregate the pages already show.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
J = lambda *p: json.load(open(os.path.join(ROOT, 'data', *p), encoding='utf-8'))


def table(rows, cols):
    b = io.StringIO()
    w = csv.writer(b, lineterminator='\n')
    w.writerow([c for c, _ in cols])
    for r in rows:
        w.writerow(['' if f(r) is None else f(r) for _, f in cols])
    return b.getvalue()


def outputs():
    A = J('bihar', 'constituencies.json')
    ac = table(A, [(k, (lambda k: lambda r: r[k])(k)) for k in [
        'ac', 'name', 'district', 'pc', 'reserved', 'border', 'electorate_2025', 'booths', 'p1', 'p2', 'total', 'per_100',
        't_f', 't_m', 'r_dead', 'r_shifted', 'r_absent', 'r_enrolled', 'hindu', 'muslim', 'unknown',
        'win2020', 'al2020', 'margin2020', 'seg2024', 'al2024', 'win2025', 'al2025', 'margin2025', 'votes2025']])
    D = J('bihar', 'districts.json')
    RS = {d['district']: d for d in J('bihar', 'reasons.json')['districts']}
    ID = {d['district']: d for d in J('bihar', 'identity.json')['districts']}
    dist = table(D, [('district', lambda r: r['district']), ('constituencies', lambda r: r['acs']), ('removed', lambda r: r['deleted']),
                     ('per_100', lambda r: r['per_100']), ('border', lambda r: r['border'])] +
                 [(k, (lambda k: lambda r: RS[r['district']][k])(k)) for k in ('dead', 'shifted', 'absent', 'already_enrolled')] +
                 [('women_pct_removed', lambda r: ID[r['district']]['female_share_deleted']),
                  ('muslim_pct_removed_low', lambda r: ID[r['district']]['muslim_share_deleted_low']),
                  ('muslim_pct_removed_high', lambda r: ID[r['district']]['muslim_share_deleted_high'])])
    H = J('hyderabad', 'summary.json')
    reasons = H['reasons']
    hac = table(H['acs'], [('constituency', lambda r: r['name']), ('electors', lambda r: r['electors']), ('struck_off', lambda r: r['deleted']),
                           ('pct_struck_off', lambda r: r['rate']), ('summoned_to_hearing', lambda r: r['hearing']),
                           ('pct_summoned', lambda r: r['hearing_rate'])] +
                [(k.lower().replace('/', '_').replace(' ', '_'), (lambda k: lambda r: r['reasons'][k])(k)) for k in reasons] +
                [('women_pct_struck_off', lambda r: r['female_rate']), ('men_pct_struck_off', lambda r: r['male_rate']),
                 ('margin_2023', lambda r: r['e2023']['margin'])])
    P = J('hyderabad', 'parts.json')
    parts = table([dict(zip(P['fields'], r)) for r in P['rows']], [(k, (lambda k: lambda r: r[k])(k)) for k in P['fields']])
    return {
        os.path.join(ROOT, 'data', 'bihar', 'constituencies.csv'): ac,
        os.path.join(ROOT, 'data', 'bihar', 'districts.csv'): dist,
        os.path.join(ROOT, 'data', 'hyderabad', 'constituencies.csv'): hac,
        os.path.join(ROOT, 'data', 'hyderabad', 'parts.csv'): parts,
    }


def main():
    out = outputs()
    if '--check' in sys.argv:
        stale = [p for p, s in out.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != s]
        if stale:
            sys.exit('stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale) + ' (run scripts/build_downloads.py)')
        print('PASS: downloads are current')
        return
    for p, s in out.items():
        open(p, 'w', encoding='utf-8').write(s)
        print('wrote', os.path.relpath(p, ROOT))


if __name__ == '__main__':
    main()
