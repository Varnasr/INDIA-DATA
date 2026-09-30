#!/usr/bin/env python3
"""Hyderabad against the rest of Telangana, from the state's draft-roll figures.

    python3 scripts/build_telangana.py          # writes data/hyderabad/telangana.json
    python3 scripts/build_telangana.py --check  # fails if it is stale

Sources: data/hyderabad/raw/telangana_districts.csv (all 33 districts) and
hyderabad_district_acs.csv (the 15 seats of Hyderabad district): electors on
the roll before the revision, on the draft roll of 17 August 2026, and the
names left off it, as the Chief Electoral Officer published them. Totals only;
no split by reason is published below the district.
"""
import csv
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(ROOT, 'data', 'hyderabad', 'raw')
OUT = os.path.join(ROOT, 'data', 'hyderabad', 'telangana.json')
OLD_CITY = ['Charminar', 'Yakutpura', 'Malakpet', 'Chandrayangutta', 'Bahadurpura']
STATE = {'electors_pre': 33826448, 'removed': 7339235}  # the state's published totals


def rows(name):
    out = []
    for x in csv.DictReader(open(os.path.join(RAW, name), encoding='utf-8')):
        for k in ('electors_pre', 'electors_draft', 'removed'):
            x[k] = int(x[k])
        assert x['electors_pre'] - x['electors_draft'] == x['removed'], x
        x['rate'] = round(100 * x['removed'] / x['electors_pre'], 2)
        out.append(x)
    return out


def group(xs):
    pre, rem = sum(x['electors_pre'] for x in xs), sum(x['removed'] for x in xs)
    return {'seats': len(xs), 'electors_pre': pre, 'removed': rem, 'rate': round(100 * rem / pre, 2)}


def build():
    D = rows('telangana_districts.csv')
    assert len(D) == 33
    assert sum(x['electors_pre'] for x in D) == STATE['electors_pre'] and sum(x['removed'] for x in D) == STATE['removed'], 'districts add to the state'
    A = rows('hyderabad_district_acs.csv')
    assert len(A) == 15
    hyd = next(x for x in D if x['district'] == 'Hyderabad')
    assert sum(x['electors_pre'] for x in A) == hyd['electors_pre'] and sum(x['removed'] for x in A) == hyd['removed'], 'seats add to the district'
    for x in A:
        x['ac'] = int(x['ac'])
        x['old_city'] = x['name'] in OLD_CITY
    assert sum(x['old_city'] for x in A) == 5
    # Our own lists hold every elector of the Old City seats; two exports are
    # complete and must agree with the state's figures exactly.
    S = json.load(open(os.path.join(ROOT, 'data', 'hyderabad', 'summary.json'), encoding='utf-8'))
    own = {a['name']: a for a in S['acs']}
    for n in ('Charminar', 'Yakutpura'):
        a = next(x for x in A if x['name'] == n)
        assert (own[n]['electors'], own[n]['deleted']) == (a['electors_pre'], a['removed']), n
    rest = [x for x in D if x['district'] != 'Hyderabad']
    return {
        'state': group(D), 'hyderabad': group([hyd]), 'rest_of_state': group(rest),
        'old_city': group([x for x in A if x['old_city']]), 'other_hyderabad': group([x for x in A if not x['old_city']]),
        'districts': [{k: x[k] for k in ('district', 'electors_pre', 'electors_draft', 'removed', 'rate')} for x in D],
        'seats': [{k: x[k] for k in ('ac', 'name', 'electors_pre', 'electors_draft', 'removed', 'rate', 'old_city')} for x in A],
        'source': A[0]['source_url'],
    }


def main():
    j = json.dumps(build(), ensure_ascii=False, indent=1) + '\n'
    if '--check' in sys.argv:
        if not os.path.exists(OUT) or open(OUT, encoding='utf-8').read() != j:
            sys.exit('stale: data/hyderabad/telangana.json (run scripts/build_telangana.py)')
        print('PASS: data/hyderabad/telangana.json is current')
        return
    open(OUT, 'w', encoding='utf-8').write(j)
    d = json.loads(j)
    print({k: d[k]['rate'] for k in ('state', 'hyderabad', 'rest_of_state', 'old_city', 'other_hyderabad')})


if __name__ == '__main__':
    main()
