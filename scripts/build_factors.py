"""What goes with the removal rate, district by district: the rank correlation
between each district's rate and its circumstances, state by state.

Writes data/india/factors.json and data/india/factors.csv.

    python3 scripts/build_factors.py           # write
    python3 scripts/build_factors.py --check   # fail if the output is stale

- The rates are the district rows the state pages already use, read through
  build_cities.rows(), each state in its own measure (see build_urban.py).
- Survey factors are from NFHS-5 (2019-21), read from the district fact sheets
  in each state's Compendium of Fact Sheets (IIPS and the Ministry of Health)
  into data/india/raw/nfhs5_districts.csv, with the page each value is on
  (sources in data/india/raw/FACTORS_SOURCES.md). Twelve states. Bihar's
  values are checked against data/bihar/raw/nfhs5_districts.csv, read earlier
  from the same compendium, and the build fails on any difference.
- Rates come from build_cities.rows() for the states it covers, and for
  Rajasthan (the fall in the roll from 2023 to the final roll of 2026),
  Uttarakhand (names left off, from the CEO's table of the draft) and Delhi (names left off, on
  the 11 districts of the 2025 roll, which are the survey's) from their own
  files (ROWS).
- Income per head is read from each state's own district table (INCOME), on
  that table's districts, in its own year and prices. Only ranks inside a
  state are used, so the year and prices do not matter to the result.
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
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_cities import rows  # noqa: E402
from build_urban import build as build_urban, spearman  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'india', 'raw')
OUT = os.path.join(ROOT, 'data', 'india')
CHECK = '--check' in sys.argv

SURVEY_STATES = [('Bihar', 'roll_2025'), ('Gujarat', 'left_off'), ('Karnataka', 'left_off'), ('Maharashtra', 'left_off'),
                 ('Telangana', 'left_off'), ('Tamil Nadu', 'left_off'), ('Uttar Pradesh', 'left_off'),
                 ('Delhi', 'left_off'), ('West Bengal', 'fall'), ('Kerala', 'fall'), ('Rajasthan', 'change_2023'),
                 ('Uttarakhand', 'left_off'), ('Andhra Pradesh', 'left_off'), ('Meghalaya', 'left_off'),
                 ('Manipur', 'fall'), ('Odisha', 'fall'), ('Assam', 'fall_after_draft'),
                 ('Chhattisgarh', 'rise_after_draft'), ('Mizoram', 'rise_after_draft')]
# for these, today's districts against the survey's are in raw/nfhs5_alias, each row with its parents and source
ALIAS_FILES = {'Andhra Pradesh': 'andhrapradesh', 'Assam': 'assam', 'Chhattisgarh': 'chhattisgarh', 'Manipur': 'manipur',
               'Meghalaya': 'meghalaya', 'Mizoram': 'mizoram', 'Odisha': 'odisha'}
NFHS_STATE = {'Delhi': 'NCT Delhi'}  # as the compendium names it
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
    'Tamil Nadu': {'Chengalpattu': 'Kancheepuram', 'Ranipet': 'Vellore', 'Tirupathur': 'Vellore',
                   'Tenkasi': 'Tirunelveli', 'Thoothukudi': 'Thoothukkudi', 'Mayiladuthurai': 'Nagapattinam',
                   'Kallakurichi': 'Viluppuram'},
    'Uttar Pradesh': {'Sant Kabir Nagar': 'Sant Kabeer Nagar', 'Ayodhya': 'Faizabad',
                      'Bhadohi': 'Sant Ravidas Nagar (Bhadohi)', 'Shrawasti': 'Shravasti', 'Raebareli': 'Rae Bareli',
                      'Hathras': 'Mahamaya Nagar', 'Kasganj': 'Kanshiram Nagar', 'Amroha': 'Jyotiba Phule Nagar'},
    'Rajasthan': {'Salumber': 'Udaipur', 'Chittorgarh': 'Chittaurgarh', 'Khairthal-Tijara': 'Alwar',
                  'Jhunjhunu': 'Jhunjhunun', 'Deedwanna-Kuchaman': 'Nagaur', 'Beawar': 'Ajmer', 'Jalore': 'Jalor',
                  'Kotputali-Behror': 'Jaipur', 'Balotara': 'Barmer', 'Deeg': 'Bharatpur', 'Dholpur': 'Dhaulpur',
                  'Phalodi': 'Jodhpur'},
    'Uttarakhand': {'Udham Singh Nagar': 'Udam Singh Nagar'},
    'Delhi': {'North-east': 'North East', 'North-west': 'North West', 'South-East': 'South East', 'South-West': 'South West'},
    'West Bengal': {'Kolkata North': 'Kolkata', 'Kolkata South': 'Kolkata', 'Paschim Bardhaman': 'Paschim Barddhaman',
                    'Purba Bardhaman': 'Purba Barddhaman', 'North 24 Parganas': 'North Twenty Four Parganas',
                    'South 24 Parganas': 'South Twenty Four Parganas', 'Howrah': 'Haora', 'Malda': 'Maldah',
                    'Alipurduar': 'Jalpaiguri', 'Hooghly': 'Hugli', 'Kalimpong': 'Darjeeling', 'Coochbehar': 'Koch Bihar',
                    'Purulia': 'Puruliya', 'Jhargram': 'Paschim Medinipur', 'Purbo Medinipur': 'Purba Medinipur'},
}


# state: (file under raw/income, value column, year and prices as printed, rows district: income district)
INCOME = {
    'Bihar': ('../../../bihar/raw/gddp_per_capita_2011_12_prices.csv', 'y2022_23', '2022-23, constant 2011-12 prices',
              {'Purnia': 'Purnea'}),
    'Karnataka': ('karnataka_es2025_26_district_gddp_pci.csv', 'Per Capita Income (Rs.)', '2024-25, current prices',
                  {'B.B.M.P (South)': 'Bangalore Urban', 'B.B.M.P (Central)': 'Bangalore Urban',
                   'B.B.M.P (North)': 'Bangalore Urban', 'Gulbarga': 'Kalaburagi', 'Mysore': 'Mysuru', 'Bellary': 'Ballari',
                   'Yadgir': 'Yadagiri', 'Bijapur': 'Vijayapura', 'Bagalkot': 'Bagalkote', 'Davangere': 'Davanagere',
                   'Vijayanagara': 'Vijayanagar', 'Belgaum': 'Belagavi', 'Shimoga': 'Shivamogga',
                   'Ramanagaram': 'Bangalore South', 'Tumkur': 'Tumakuru', 'Chikkmagalur': 'Chikkamagaluru',
                   'Chamarajnagar': 'Chamarajanagar'}),
    'Maharashtra': ('maharashtra_es2025_26_district_gddp_pci.csv', 'Per Capita Nominal NDDP 2024-25+',
                    '2024-25, current prices, first revised',
                    {'Mumbai City': 'Mumbai#', 'Mumbai Suburban': 'Mumbai#', 'Thane': 'Thane$', 'Palghar': 'Thane$',
                     'Aurangabad': 'Chhatrapati Sambhajinagar', 'Amaravati': 'Amravati', 'Osmanabad': 'Dharashiv'}),
    'Telangana': ('telangana_seo2024_district_gddp_pci_2022_23.csv', 'PCI (Rs.) Current Prices 2022-23',
                  '2022-23, current prices',
                  {'Kumaram Bheem Asifabad': 'Kumuram Bheem', 'Yadadri Bhongiri': 'Yadadri',
                   'Jayashankar Bhupalpalle': 'Jayashankar'}),
    'Tamil Nadu': ('tamilnadu_2023_24_district_gddp_pci_constant.csv', 'Per capita Income (in Rupees)',
                   '2023-24, constant 2011-12 prices',
                   {'Tiruppur': 'Thiruppur', 'Thiruvallur': 'Tiruvallur', 'Sivaganga': 'Sivagangai',
                    'Thiruvarur': 'Tiruvarur', 'Tirupathur': 'Thirupathur', 'Viluppuram': 'Villupuram',
                    'The Nilgiris': 'The Nilgris'}),
}


def state_rows(state):
    """[{district, before, removed}] in the state's own measure."""
    if state == 'Rajasthan':
        return [dict(district=d['district'], before=d['roll_2023'], removed=d['fall'])
                for d in json.load(open(os.path.join(ROOT, 'data', 'rajasthan', 'districts.json'), encoding='utf-8'))]
    if state == 'Uttarakhand':
        return [dict(district=d['district'], before=d['roll_before'], removed=d['left_off'])
                for d in json.load(open(os.path.join(ROOT, 'data', 'uttarakhand', 'districts.json'), encoding='utf-8'))]
    if state == 'Delhi':
        out = {}
        for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'delhi', 'raw', 'ac.csv'), encoding='utf-8')):
            u = out.setdefault(r['district_2025'], dict(district=r['district_2025'], before=0, removed=0))
            u['before'] += int(r['roll_before'])
            u['removed'] += int(r['left_off'])
        return list(out.values())
    return rows(state)


def num(x):
    return float(str(x).replace(',', '').strip())


def read_income(state):
    """{income district: income per head}, after checking the table's own totals."""
    f, col, _, _ = INCOME[state]
    path = os.path.join(RAW, 'income', f)
    if state == 'Tamil Nadu':
        rr = list(csv.reader(open(path, encoding='utf-8-sig')))
        head, body = [' '.join(h.split()) for h in rr[0]], [r for r in rr[2:] if r and r[1]]
        ci, gi = head.index(col), head.index('Gross District Domestic Product')
        vals = {r[1]: num(r[ci]) for r in body if r[1] != 'STATE'}
        st = [r for r in body if r[1] == 'STATE'][0]
        g = sum(num(r[gi]) for r in body if r[1] != 'STATE')
        if abs(g - num(st[gi])) > 0.002 * num(st[gi]):
            raise SystemExit('FAIL - Tamil Nadu income: districts add to %s, state %s' % (g, st[gi]))
        return vals
    rs = list(csv.DictReader(open(path, encoding='utf-8-sig')))
    if state == 'Bihar':  # build_bihar.py checks this table's ranks against its printed ranks
        return {r['district']: num(r[col]) for r in rs if r['district'] != 'Bihar'}
    if state == 'Karnataka':
        body = [r for r in rs if r['District'] != 'State']
        tot = [r for r in rs if r['District'] == 'State'][0]
        g = sum(num(r['NDDP Current Prices (Rs. Cr)']) for r in body)
        if abs(g - num(tot['NDDP Current Prices (Rs. Cr)'])) > 0.002 * g:
            raise SystemExit('FAIL - Karnataka income: districts add to %s, state %s' % (g, tot['NDDP Current Prices (Rs. Cr)']))
        return {r['District']: num(r[col]) for r in body}
    if state == 'Maharashtra':
        body, divs, cur = [], [], []
        for r in rs:
            if r['Sr. No.'].strip().isdigit():
                cur.append(r)
                body.append(r)
            elif r['District'].strip().endswith('DIV.'):
                g = sum(num(x['Nominal GDDP 2024-25+']) for x in cur)
                if abs(g - num(r['Nominal GDDP 2024-25+'])) > 2 + 0.001 * g:
                    raise SystemExit('FAIL - Maharashtra income: %s districts add to %s' % (r['District'], g))
                divs.append(r)
                cur = []
        if len(divs) != 6:
            raise SystemExit('FAIL - Maharashtra income: expected six divisions')
        return {r['District']: num(r[col]) for r in body}
    return {r['District']: num(r[col]) for r in rs if r['District']}


def income_units(state):
    _, _, year, m = INCOME[state]
    inc = read_income(state)
    norm = {re.sub('[^a-z]', '', k.lower()): k for k in inc}
    units = {}
    for d in state_rows(state):
        k = m.get(d['district']) or norm.get(re.sub('[^a-z]', '', d['district'].lower()), d['district'])
        if k not in inc:
            raise SystemExit('FAIL - %s income: no district %s (%s)' % (state, d['district'], k))
        u = units.setdefault(k, dict(unit=k.rstrip('#$'), districts=[], before=0, removed=0, income_pc=inc[k]))
        u['districts'].append(d['district'])
        u['before'] += d['before']
        u['removed'] += d['removed']
    if set(units) != set(inc):
        raise SystemExit('FAIL - %s income: districts with no rows: %s' % (state, sorted(set(inc) - set(units))))
    us = sorted(units.values(), key=lambda u: u['unit'])
    for u in us:
        u['per_100'] = round(100 * u['removed'] / u['before'], 4)
    return us, year


def chance(n):
    return round(1.96 / (n - 1) ** 0.5, 4)


def pearson(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
    return round(num / den, 4)


def read_nfhs():
    nf = {}
    for r in csv.DictReader(open(os.path.join(RAW, 'nfhs5_districts.csv'), encoding='utf-8')):
        if r['nfhs5'] == '':
            continue
        st = {v: k for k, v in NFHS_STATE.items()}.get(r['state'], r['state'])
        nf.setdefault((st, r['district']), {})[r['indicator'] + '.'] = float(r['nfhs5'])
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
                    raise SystemExit('FAIL - Bihar %s %s: read %s, earlier reading %s' % (d, num, x, own[(name, num)]))
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
        if state in ALIAS_FILES:
            al = {r['district']: r['nfhs_district'] for r in csv.DictReader(
                open(os.path.join(RAW, 'nfhs5_alias', 'alias_%s.csv' % ALIAS_FILES[state]), encoding='utf-8'))}
        units = {}
        for d in state_rows(state):
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
        if tb != sum(r['before'] for r in state_rows(state)) or tm != sum(r['removed'] for r in state_rows(state)):
            raise SystemExit('FAIL - %s: units do not add up to the state' % state)
        states.append(dict(state=state, measure=measure, units=len(us), districts=len(state_rows(state)),
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

    income = []
    for st in INCOME:
        us, year = income_units(st)
        income.append(dict(state=st, year=year, units=len(us), chance=chance(len(us)), income=correl(us, 'income_pc'),
                           rows=[dict(unit=u['unit'], districts=u['districts'], income_pc=u['income_pc'],
                                      per_100=u['per_100']) for u in us]))
    sv = [k for k, num, _, src in FACTORS if src == 'nfhs']
    clear = {k: [s['state'] for s in states if s['survey'][k] and s['survey'][k]['clear']] for k in sv}
    summary = dict(survey_states=len(states), survey_units=len(units_out), census_states=len(census),
                   bihar_checked=checked, clear=clear,
                   lit_negative=sum(1 for s in states if s['survey']['women_literate']['rho'] < 0),
                   lit_positive=sum(1 for s in states if s['survey']['women_literate']['rho'] > 0))
    return dict(summary=summary, factors=[dict(key=k, nfhs=num, label=l, source=src) for k, num, l, src in FACTORS],
                states=states, census=census, income=income, units=units_out)


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
    for s in d['income']:
        print('income %-11s n=%2d rho %+.2f%s' % (s['state'], s['units'], s['income']['rho'], '*' if s['income']['clear'] else ''))
    for s in d['census']:
        print('%-13s n=%2d chance %.2f  ' % (s['state'], s['units'], s['chance'])
              + '  '.join('%s %+.2f%s' % (k, v['rho'], '*' if v['clear'] else '') for k, v in s['census'].items() if v))


if __name__ == '__main__':
    main()
