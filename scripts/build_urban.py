"""Rural, mixed and urban districts: how many names each kind of district lost,
state by state, from the district tables the state pages already use.

Writes data/india/urban.json and data/india/urban.csv.

    python3 scripts/build_urban.py           # write
    python3 scripts/build_urban.py --check   # fail if the output is stale

- Urban share is the share of a district's people living in towns at the 2011
  Census (table A-01, data/india/raw/census2011_a01_districts.csv). It is the
  last count by district. A district is rural under 20 per cent, mixed from 20
  to 50, urban above 50. The mixed band is where peri-urban and small-town
  districts fall.
- Many districts were made after 2011. data/india/raw/district_2011_parent.csv
  names the 2011 district or districts each of today's was made from, with its
  source (data/india/raw/URBAN_SOURCES.md). Each of today's districts is
  counted under the 2011 district it was mostly made from, the first parent
  listed, and the districts sharing a parent are added together. So a "unit"
  here is a 2011 district, and its urban share is that district's in 2011.
- Each state is read in its own measure and never ranked against another:
  names left off the draft per 100 on the roll before (Karnataka, Maharashtra,
  Tamil Nadu, Uttar Pradesh, Gujarat, Telangana), both phases per 100 on the
  2025 roll (Bihar), and the fall in the roll (West Bengal, Kerala). The rows
  come from build_cities.rows(), so this page and the cities page cannot
  disagree.
- Left out, and the page says why: Delhi (one unit, almost wholly urban),
  Rajasthan (a change over two years, across a split of districts) and
  Uttarakhand (counts after the draft only).
"""
import csv
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_cities import rows  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'india', 'raw')
OUT = os.path.join(ROOT, 'data', 'india')
CHECK = '--check' in sys.argv

STATES = [('Uttar Pradesh', 'left_off'), ('Maharashtra', 'left_off'), ('Tamil Nadu', 'left_off'), ('Gujarat', 'left_off'),
          ('Karnataka', 'left_off'), ('Telangana', 'left_off'), ('Bihar', 'roll_2025'),
          ('West Bengal', 'fall'), ('Kerala', 'fall')]
CENSUS_STATE = {'Telangana': 'Andhra Pradesh'}
BANDS = [('rural', 0, 20), ('mixed', 20, 50), ('urban', 50, 101)]


def band(u):
    return next(b for b, lo, hi in BANDS if lo <= u < hi)


def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return round(num / den, 4)


def build():
    census = {}
    for r in csv.DictReader(open(os.path.join(RAW, 'census2011_a01_districts.csv'), encoding='utf-8')):
        census[(r['state'], r['district'].lower())] = r
    parents = {}
    for r in csv.DictReader(open(os.path.join(RAW, 'district_2011_parent.csv'), encoding='utf-8')):
        parents[(r['state'], r['district'])] = [p.strip() for p in r['district_2011'].split(';')]

    states, units_out = [], []
    for state, measure in STATES:
        cs = CENSUS_STATE.get(state, state)
        units = {}
        for d in rows(state):
            ps = parents.get((state, d['district']))
            if not ps:
                raise SystemExit('FAIL - %s: no 2011 parent for %s' % (state, d['district']))
            p = ps[0]
            c = census.get((cs, p.lower()))
            if not c:
                raise SystemExit('FAIL - %s: %s is not a 2011 district of %s' % (state, p, cs))
            u = units.setdefault(p, dict(state=state, unit=c['district'], census_code=c['census_code'], districts=[],
                                         urban_pct=float(c['urban_pct']), before=0, removed=0))
            u['districts'].append(d['district'])
            u['before'] += d['before']
            u['removed'] += d['removed']
        us = sorted(units.values(), key=lambda u: u['urban_pct'])
        tb, tm = sum(u['before'] for u in us), sum(u['removed'] for u in us)
        st_rows = rows(state)
        if tb != sum(r['before'] for r in st_rows) or tm != sum(r['removed'] for r in st_rows):
            raise SystemExit('FAIL - %s: units do not add up to the state' % state)
        for u in us:
            u['band'] = band(u['urban_pct'])
            u['per_100'] = round(100 * u['removed'] / u['before'], 4)
            u['measure'] = measure
        st_100 = 100 * tm / tb
        bands = []
        for b, lo, hi in BANDS:
            g = [u for u in us if u['band'] == b]
            if not g:
                bands.append(dict(band=b, units=0, per_100=None, times_state=None, share_of_roll=0, share_of_removed=0))
                continue
            bb, bm = sum(u['before'] for u in g), sum(u['removed'] for u in g)
            bands.append(dict(band=b, units=len(g), before=bb, removed=bm, per_100=round(100 * bm / bb, 4),
                              times_state=round(100 * bm / bb / st_100, 4),
                              share_of_roll=round(100 * bb / tb, 1), share_of_removed=round(100 * bm / tm, 1)))
        by = {b['band']: b for b in bands}
        r_, m_, u_ = by['rural']['per_100'], by['mixed']['per_100'], by['urban']['per_100']
        # the same order without the cities: only the units under 50 per cent urban
        low = [u for u in us if u['band'] != 'urban']
        states.append(dict(state=state, measure=measure, units=len(us), districts=len(st_rows), per_100=round(st_100, 4),
                           rho=spearman([u['urban_pct'] for u in us], [u['per_100'] for u in us]),
                           rho_no_urban=spearman([u['urban_pct'] for u in low], [u['per_100'] for u in low]), bands=bands,
                           urban_over_rural=round(u_ / r_, 4) if r_ and u_ else None,
                           mixed_over_rural=round(m_ / r_, 4) if r_ and m_ else None))
        units_out.extend(us)

    for u in units_out:
        if not 0 < u['per_100'] < 100:
            raise SystemExit('FAIL - %s, %s: a rate outside 0 to 100' % (u['state'], u['unit']))
    both = [s for s in states if s['urban_over_rural'] is not None]
    summary = dict(states=len(states), units=len(units_out), districts=sum(s['districts'] for s in states),
                   with_both=len(both), urban_higher=sum(1 for s in both if s['urban_over_rural'] > 1),
                   rho_positive=sum(1 for s in states if s['rho'] > 0), rho_02=sum(1 for s in states if s['rho'] >= 0.2),
                   mixed_higher=sum(1 for s in states if s['mixed_over_rural'] and s['mixed_over_rural'] > 1),
                   rho_no_urban_02=sum(1 for s in states if s['rho_no_urban'] >= 0.2),
                   no_urban=[s['state'] for s in states if not any(b['band'] == 'urban' and b['units'] for b in s['bands'])],
                   no_rural=[s['state'] for s in states if not any(b['band'] == 'rural' and b['units'] for b in s['bands'])])
    return dict(summary=summary, bands=[dict(band=b, lo=lo, hi=min(hi, 100)) for b, lo, hi in BANDS], states=states, units=units_out)


def as_csv(d):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['state', 'measure', 'district_2011', 'census_code', 'districts_today', 'urban_pct_2011', 'band', 'roll_before', 'count', 'per_100'])
    for u in d['units']:
        w.writerow([u['state'], u['measure'], u['unit'], u['census_code'], '; '.join(u['districts']), u['urban_pct'], u['band'],
                    u['before'], u['removed'], u['per_100']])
    return buf.getvalue()


def main():
    d = build()
    files = {os.path.join(OUT, 'urban.json'): json.dumps(d, ensure_ascii=False, indent=1) + '\n',
             os.path.join(OUT, 'urban.csv'): as_csv(d),
             os.path.join(OUT, 'district_2011_parent.csv'): open(os.path.join(RAW, 'district_2011_parent.csv'), encoding='utf-8').read()}
    stale = [p for p, t in files.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != t]
    if CHECK:
        if stale:
            raise SystemExit('FAIL - stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale))
        print('OK: rural and urban table up to date')
        return
    for p, t in files.items():
        open(p, 'w', encoding='utf-8').write(t)
    print(json.dumps(d['summary']))
    for s in d['states']:
        print('%-14s %-9s units %2d  state %5.2f  rho %5.2f  ' % (s['state'], s['measure'], s['units'], s['per_100'], s['rho'])
              + '  '.join('%s %s:%s (%s%%roll)' % (b['band'], b['units'], b['per_100'], b['share_of_roll']) for b in s['bands']))


if __name__ == '__main__':
    main()
