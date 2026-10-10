"""What goes with the removal rate, district by district: the rank correlation
between each district's rate and its circumstances, state by state.

Writes data/india/factors.json and data/india/factors.csv.

    python3 scripts/build_factors.py           # write
    python3 scripts/build_factors.py --check   # fail if the output is stale

- The rates are the district rows the state pages already use, read through
  build_cities.rows(), each state in its own measure (see build_urban.py).
- Survey factors are from NFHS-5 (2019-21), district fact sheets, taken from
  a published compilation of the fact sheets
  (data/india/raw/nfhs5_districts_phase1.csv, sources in
  data/india/raw/FACTORS_SOURCES.md). It holds the seven states whose fact
  sheets came out in the survey's first phase and that have a district table
  here. Bihar's values are checked against the state's own compendium in
  data/bihar/raw/nfhs5_districts.csv and the build fails on any difference.
- The unit for the survey factors is the survey's district. A district made
  after the survey is counted under the one it was made from (ALIAS), and
  districts sharing a survey district are added together.
- Census factors (urban share and density, 2011) are read on the 2011
  districts of build_urban.build(), the units of the rural and urban page,
  so the two pages cannot disagree.
- Each correlation is a rank correlation within one state. It is reported
  with the size a correlation must reach before chance becomes an unlikely
  explanation, 1.96 / sqrt(n - 1), which for 14 districts is 0.54.
"""
import csv
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_cities import rows  # noqa: E402
from build_urban import build as build_urban, spearman  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'india', 'raw')
OUT = os.path.join(ROOT, 'data', 'india')
CHECK = '--check' in sys.argv

SURVEY_STATES = [('Bihar', 'roll_2025'), ('Gujarat', 'left_off'), ('Karnataka', 'left_off'), ('Maharashtra', 'left_off'),
                 ('Telangana', 'left_off'), ('West Bengal', 'fall'), ('Kerala', 'fall')]
# key, NFHS-5 indicator number, label, source
FACTORS = [
    ('women_literate', '14.', 'Women who can read', 'nfhs'),
    ('women_10yr', '15.', 'Women with ten or more years of school', 'nfhs'),
    ('married_18', '16.', 'Women aged 20 to 24 married before 18', 'nfhs'),
    ('clean_fuel', '10.', 'Households cooking with clean fuel', 'nfhs'),
    ('sanitation', '9.', 'People in homes with improved sanitation', 'nfhs'),
    ('death_reg', '6.', 'Deaths in the last three years that were registered', 'nfhs'),
    ('sex_ratio', '3.', 'Women per 1,000 men', 'nfhs'),
    ('urban_pct', None, 'Share of people living in towns, 2011', 'census'),
    ('density', None, 'People per square kilometre, 2011', 'census'),
]
# today's district: the survey district it lies in (made after the survey, or spelt differently)
ALIAS = {
    'Bihar': {'Kaimur': 'Kaimur (Bhabua)', 'West Champaran': 'Pashchim Champaran', 'East Champaran': 'Purba Champaran',
              'Purnea': 'Purnia'},
    'Gujarat': {'Arvalli': 'Aravali', 'Chhota Udepur': 'Chhota Udaipur', 'Dangs': 'The Dangs'},
    'Karnataka': {'B.B.M.P (South)': 'Bangalore', 'B.B.M.P (Central)': 'Bangalore', 'B.B.M.P (North)': 'Bangalore',
                  'Bangalore Urban': 'Bangalore', 'Davangere': 'Davanagere', 'Vijayanagara': 'Bellary',
                  'Ramanagaram': 'Ramanagara', 'Chikkaballapur': 'Chikkaballapura', 'Chikkmagalur': 'Chikmagalur',
                  'Chamarajnagar': 'Chamarajanagar'},
    'Maharashtra': {'Mumbai City': 'Mumbai', 'Raigad': 'Raigarh', 'Gondia': 'Gondiya', 'Amaravati': 'Amravati',
                    'Beed': 'Bid', 'Buldhana': 'Buldana'},
    'Telangana': {'Kumaram Bheem Asifabad': 'Komaram Bheem Asifabad', 'Jagtial': 'Jagitial', 'Rangareddy': 'Ranga Reddy',
                  'Medchal Malkajgiri': 'Medchal-Malkajgiri', 'Yadadri Bhongiri': 'Yadadri Bhuvanagiri',
                  'Jangaon': 'Jangoan', 'Warangal': 'Warangal Rural', 'Hanumakonda': 'Warangal Urban',
                  'Jayashankar Bhupalpalle': 'Jayashankar Bhupalapally', 'Bhadradri': 'Bhadradri Kothagudem',
                  'Mulugu': 'Jayashankar Bhupalapally', 'Narayanpet': 'Mahabubnagar', 'Mahbubnagar': 'Mahabubnagar'},
    'West Bengal': {'Kolkata North': 'Kolkata', 'Kolkata South': 'Kolkata', 'Paschim Bardhaman': 'Paschim Barddhaman',
                    'Purba Bardhaman': 'Purba Barddhaman', 'North 24 Parganas': 'North Twenty Four Parganas',
                    'South 24 Parganas': 'South Twenty Four Parganas', 'Howrah': 'Haora', 'Malda': 'Maldah',
                    'Alipurduar': 'Jalpaiguri', 'Hooghly': 'Hugli', 'Kalimpong': 'Darjeeling', 'Coochbehar': 'Koch Bihar',
                    'Purulia': 'Puruliya', 'Jhargram': 'Paschim Medinipur', 'Purbo Medinipur': 'Purba Medinipur'},
}


def chance(n):
    return round(1.96 / (n - 1) ** 0.5, 4)


def pearson(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
    return round(num / den, 4)


def read_nfhs():
    nf = {}
    for r in csv.DictReader(open(os.path.join(RAW, 'nfhs5_districts_phase1.csv'), encoding='utf-8')):
        num = r['indicator'].split(' ')[0]
        if r['nfhs5'] == '':
            continue
        nf.setdefault((r['state'], r['district']), {})[num] = float(r['nfhs5'])
    # Bihar against the state's own compendium
    own = {}
    for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'bihar', 'raw', 'nfhs5_districts.csv'), encoding='utf-8')):
        if r['indicator'].startswith('NFHS-5'):
            own[(r['district'], r['indicator'].split(': ', 1)[1].split(' ')[0])] = float(r['value'])
    seen = 0
    for (st, d), v in nf.items():
        if st != 'Bihar':
            continue
        name = 'Kaimur' if d == 'Kaimur (Bhabua)' else d
        for num, x in v.items():
            if (name, num) in own:
                seen += 1
                if own[(name, num)] != x:
                    raise SystemExit('FAIL - Bihar %s %s: compilation %s, compendium %s' % (d, num, x, own[(name, num)]))
    if seen < 140:
        raise SystemExit('FAIL - only %d Bihar values checked against the compendium' % seen)
    return nf, seen


def correl(us, key):
    pts = [(u[key], u['per_100']) for u in us if u.get(key) is not None]
    n = len(pts)
    if n < 8:
        return None
    a, b = [p[0] for p in pts], [p[1] for p in pts]
    rho = spearman(a, b)
    return dict(n=n, rho=rho, r=pearson(a, b), chance=chance(n), clear=abs(rho) >= chance(n))


def build():
    nf, checked = read_nfhs()
    states, units_out = [], []
    for state, measure in SURVEY_STATES:
        al = ALIAS.get(state, {})
        units = {}
        for d in rows(state):
            name = al.get(d['district'], d['district'])
            v = nf.get((state, name))
            if v is None:
                raise SystemExit('FAIL - %s: no survey district for %s (%s)' % (state, d['district'], name))
            u = units.setdefault(name, dict(state=state, unit=name, districts=[], before=0, removed=0,
                                             **{k: v.get(num) for k, num, _, src in FACTORS if src == 'nfhs'}))
            u['districts'].append(d['district'])
            u['before'] += d['before']
            u['removed'] += d['removed']
        survey = {d for (s, d) in nf if s == state}
        if set(units) != survey:
            raise SystemExit('FAIL - %s: survey districts with no rows: %s' % (state, sorted(survey - set(units))))
        us = sorted(units.values(), key=lambda u: u['unit'])
        for u in us:
            u['per_100'] = round(100 * u['removed'] / u['before'], 4)
            u['measure'] = measure
        tb, tm = sum(u['before'] for u in us), sum(u['removed'] for u in us)
        if tb != sum(r['before'] for r in rows(state)) or tm != sum(r['removed'] for r in rows(state)):
            raise SystemExit('FAIL - %s: units do not add up to the state' % state)
        states.append(dict(state=state, measure=measure, units=len(us), districts=len(rows(state)),
                           per_100=round(100 * tm / tb, 4), chance=chance(len(us)),
                           # how closely schooling and clean fuel move together across the districts
                           school_fuel=spearman([u['women_10yr'] for u in us], [u['clean_fuel'] for u in us]),
                           survey={k: correl(us, k) for k, num, _, src in FACTORS if src == 'nfhs'}))
        units_out.extend(us)

    # census factors on the 2011 districts of the rural and urban page
    density = {}
    for r in csv.DictReader(open(os.path.join(RAW, 'census2011_a01_districts.csv'), encoding='utf-8')):
        density[r['census_code']] = float(r['density']) if r['density'] else None
    urb = build_urban()
    census = []
    for s in urb['states']:
        us = [dict(u, density=density.get(u['census_code'])) for u in urb['units'] if u['state'] == s['state']]
        census.append(dict(state=s['state'], measure=s['measure'], units=len(us), chance=chance(len(us)),
                           census={k: correl(us, k) for k, num, _, src in FACTORS if src == 'census'}))
        if census[-1]['census']['urban_pct']['rho'] != s['rho'] and census[-1]['census']['urban_pct']['n'] == s['units']:
            raise SystemExit('FAIL - %s: urban share does not match the rural and urban page' % s['state'])

    sv = [k for k, num, _, src in FACTORS if src == 'nfhs']
    clear = {k: [s['state'] for s in states if s['survey'][k] and s['survey'][k]['clear']] for k in sv}
    summary = dict(survey_states=len(states), survey_units=len(units_out), census_states=len(census),
                   bihar_checked=checked, clear=clear,
                   lit_negative=sum(1 for s in states if s['survey']['women_literate']['rho'] < 0),
                   lit_positive=sum(1 for s in states if s['survey']['women_literate']['rho'] > 0))
    return dict(summary=summary, factors=[dict(key=k, nfhs=num, label=l, source=src) for k, num, l, src in FACTORS],
                states=states, census=census, units=units_out)


def as_csv(d):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    keys = [f['key'] for f in d['factors'] if f['source'] == 'nfhs']
    w.writerow(['state', 'measure', 'nfhs5_district', 'districts_today', 'roll_before', 'count', 'per_100'] + keys)
    for u in d['units']:
        w.writerow([u['state'], u['measure'], u['unit'], '; '.join(u['districts']), u['before'], u['removed'], u['per_100']]
                   + ['' if u[k] is None else u[k] for k in keys])
    return buf.getvalue()


def main():
    d = build()
    files = {os.path.join(OUT, 'factors.json'): json.dumps(d, ensure_ascii=False, indent=1) + '\n',
             os.path.join(OUT, 'factors.csv'): as_csv(d)}
    stale = [p for p, t in files.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != t]
    if CHECK:
        if stale:
            raise SystemExit('FAIL - stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale))
        print('OK: district factors up to date')
        return
    for p, t in files.items():
        open(p, 'w', encoding='utf-8').write(t)
    print(json.dumps(d['summary']))
    for s in d['states']:
        print('%-12s n=%2d chance %.2f  ' % (s['state'], s['units'], s['chance'])
              + '  '.join('%s %+.2f%s' % (k[:8], v['rho'], '*' if v['clear'] else '') for k, v in s['survey'].items() if v))
    for s in d['census']:
        print('%-13s n=%2d chance %.2f  ' % (s['state'], s['units'], s['chance'])
              + '  '.join('%s %+.2f%s' % (k, v['rho'], '*' if v['clear'] else '') for k, v in s['census'].items() if v))


if __name__ == '__main__':
    main()
