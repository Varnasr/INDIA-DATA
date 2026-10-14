"""The cities: how many names each large city lost against its state, from
the district and constituency tables the state pages already use.

Writes data/india/cities.json and data/india/cities.csv.

    python3 scripts/build_cities.py           # write
    python3 scripts/build_cities.py --check   # fail if the output is stale

- A city is set down as its districts, named in CITIES below, because every
  state that published below its own level published by district or by
  constituency, never by municipal boundary. The definition differs from city
  to city and each one is stated on the page.
- Each city has a core and, where its suburbs spread into other districts, a
  ring. The rest of the state is the state less the core and the ring.
  Delhi's ring is in Uttar Pradesh (Ghaziabad, Gautam Buddha Nagar), so it is
  measured on Uttar Pradesh's revision, and Haryana's suburbs have no figure.
- Two measures. Most states published the names left off the draft roll
  against the roll before the revision. West Bengal and Kerala published no
  removals below the state, so Kolkata and Kochi are measured by the fall in
  the roll (West Bengal: the 2024 Lok Sabha roll to the draft; Kerala: the
  January 2025 roll to the draft), which takes in ordinary deaths and moves
  as well. They are kept apart and never ranked with the others.
- Hyderabad's district figures are the state's as reported in the press;
  the Telangana page says so and so does this one.
- Patna is both of Bihar's phases per 100 electors on the 2025 roll, the
  rate the Bihar pages use, because Bihar's roll before the revision was
  published for the state only. The denominator differs from the other
  cities', so Patna is compared with Bihar and not ranked against them.
  Bihar and Hyderabad appear side by side here only, as the owner decided
  in October 2026.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'india')
CHECK = '--check' in sys.argv


def load(*p):
    return json.load(open(os.path.join(ROOT, 'data', *p), encoding='utf-8'))


# states drawn by district in each one's own measure, as on its district pages
SHARED = {
    'Andhra Pradesh': ('andhrapradesh', lambda r: r['removed'], 'before'),
    'Meghalaya': ('meghalaya', lambda r: r['removed'], 'before'),
    'Manipur': ('manipur', lambda r: r['before'] - r['final'], 'before'),
    'Odisha': ('odisha', lambda r: r['before'] - r['draft'], 'before'),
    'Assam': ('assam', lambda r: r['draft'] - r['final'], 'draft'),
    'Chhattisgarh': ('chhattisgarh', lambda r: r['final'] - r['draft'], 'draft'),
    'Mizoram': ('mizoram', lambda r: r['final'] - r['draft'], 'draft'),
}


def rows(state):
    """District rows for a state as [{district, before, removed, reasons}]."""
    if state == 'Karnataka':
        return [dict(district=r['district'], before=r['before'], removed=r['removed'],
                     shifted_absent=r['shifted'] + r['absent'], dead=r['dead']) for r in load('karnataka', 'districts.json')]
    if state == 'Maharashtra':
        return [dict(district=r['district'], before=r['before'], removed=r['left_off']) for r in load('maharashtra', 'districts.json')]
    if state == 'Tamil Nadu':
        return [dict(district=r['district'], before=r['before'], removed=r['removed'],
                     shifted_absent=r['shifted_absent'], dead=r['dead']) for r in load('tamilnadu', 'districts.json')]
    if state == 'Uttar Pradesh':
        return [dict(district=r['district'], before=r['roll_before'], removed=r['total'],
                     shifted_absent=r['shifted'] + r['untraceable_absent'], dead=r['dead']) for r in load('uttarpradesh', 'districts.json')]
    if state == 'Gujarat':
        return [dict(district=r['district'], before=r['before'], removed=r['removed'],
                     shifted_absent=r['shifted'] + r['absent'], dead=r['dead']) for r in load('gujarat', 'districts.json')]
    if state == 'Telangana':
        return [dict(district=r['district'], before=r['electors_pre'], removed=r['removed']) for r in load('hyderabad', 'telangana.json')['districts']]
    if state == 'Bihar':
        # both phases by district, per 100 on the 2025 roll (the Bihar pages' rate)
        return [dict(district=r['district'], before=round(r['deleted'] * 100 / r['per_100']), removed=r['deleted']) for r in load('bihar', 'districts.json')]
    if state == 'Delhi':
        s = load('delhi', 'summary.json')
        sh = s.get('reasons', {})
        return [dict(district='Delhi', before=s['roll_before'], removed=s['left_off'],
                     shifted_absent=sh['shifted_absent_other'], dead=sh['dead'])]
    if state == 'West Bengal':
        return [dict(district=r['district'], before=r['roll_2024'], removed=r['roll_2024'] - r['draft']) for r in load('westbengal', 'districts.json')]
    if state == 'Kerala':
        return [dict(district=r['district'], before=r['roll_2025'], removed=r['roll_2025'] - r['draft']) for r in load('kerala', 'districts.json')]
    if state == 'Uttarakhand':
        # the CEO's table of the draft: names left off by district
        return [dict(district=r['district'], before=r['roll_before'], removed=r['left_off']) for r in load('uttarakhand', 'districts.json')]
    if state in SHARED:
        slug, count, base = SHARED[state]
        return [dict(district=r['district'], before=r[base], removed=count(r)) for r in load(slug, 'districts.json')]
    raise SystemExit('no rows for ' + state)


# (city, state, core districts, ring districts, ring state if not the city's, measure)
CITIES = [
    ('Bengaluru', 'Karnataka', ['B.B.M.P (South)', 'B.B.M.P (Central)', 'B.B.M.P (North)', 'Bangalore Urban'], ['Bangalore Rural', 'Ramanagaram'], None, 'left_off'),
    ('Hyderabad', 'Telangana', ['Hyderabad'], ['Rangareddy', 'Medchal Malkajgiri', 'Sangareddy'], None, 'left_off'),
    ('Chennai', 'Tamil Nadu', ['Chennai'], ['Chengalpattu', 'Kancheepuram', 'Thiruvallur'], None, 'left_off'),
    ('Mumbai', 'Maharashtra', ['Mumbai City', 'Mumbai Suburban'], ['Thane', 'Palghar'], None, 'left_off'),
    ('Pune', 'Maharashtra', ['Pune'], [], None, 'left_off'),
    ('Delhi', 'Delhi', ['Delhi'], ['Ghaziabad', 'Gautam Buddha Nagar'], 'Uttar Pradesh', 'left_off'),
    ('Lucknow', 'Uttar Pradesh', ['Lucknow'], ['Barabanki', 'Unnao'], None, 'left_off'),
    ('Ahmedabad', 'Gujarat', ['Ahmedabad'], ['Gandhinagar'], None, 'left_off'),
    ('Surat', 'Gujarat', ['Surat'], [], None, 'left_off'),
    ('Patna', 'Bihar', ['Patna'], [], None, 'left_off'),
    ('Kolkata', 'West Bengal', ['Kolkata North', 'Kolkata South'], ['Howrah', 'North 24 Parganas'], None, 'fall'),
    ('Kochi', 'Kerala', ['Ernakulam'], [], None, 'fall'),
]
STATE_PAGE = {'Karnataka': 'karnataka/', 'Telangana': 'hyderabad/telangana/', 'Tamil Nadu': 'tamilnadu/', 'Maharashtra': 'maharashtra/',
              'Delhi': 'delhi/', 'Uttar Pradesh': 'uttarpradesh/', 'Gujarat': 'gujarat/', 'Bihar': 'bihar/districts/',
              'West Bengal': 'westbengal/', 'Kerala': 'kerala/'}


def agg(rs):
    b = sum(r['before'] for r in rs)
    m = sum(r['removed'] for r in rs)
    out = dict(before=b, removed=m, per_100=round(100 * m / b, 4))
    if rs and all(r.get('shifted_absent') is not None for r in rs):
        out['shifted_absent_share'] = round(100 * sum(r['shifted_absent'] for r in rs) / m, 1)
        out['dead_share'] = round(100 * sum(r['dead'] for r in rs) / m, 1)
    return out


def pick(rs, names, state):
    got = [r for r in rs if r['district'] in names]
    missing = set(names) - {r['district'] for r in got}
    if missing:
        raise SystemExit('FAIL - %s: no district %s' % (state, sorted(missing)))
    return got


def build():
    out = []
    for city, state, core, ring, ring_state, measure in CITIES:
        rs = rows(state)
        c = agg(pick(rs, core, state))
        st = agg(rs)
        r = None
        if ring:
            rr = rows(ring_state or state)
            r = agg(pick(rr, ring, ring_state or state))
            r['districts'] = ring
            r['state'] = ring_state or state
        rest_rows = [x for x in rs if x['district'] not in core and (ring_state or x['district'] not in ring)]
        rest = agg(rest_rows) if rest_rows else None
        row = dict(city=city, state=state, measure=measure, page=STATE_PAGE[state], core=dict(districts=core, **c), ring=r, rest=rest,
                   state_per_100=st['per_100'], times_state=round(c['per_100'] / st['per_100'], 4),
                   share_of_roll=round(100 * c['before'] / st['before'], 1) if state != 'Delhi' else None,
                   share_of_removed=round(100 * c['removed'] / st['removed'], 1) if state != 'Delhi' else None,
                   reported=state == 'Telangana', roll_2025=state == 'Bihar')
        out.append(row)
    # checks: the cores and rings add up from the rows, and every rate is a rate
    for x in out:
        for part in ('core', 'ring', 'rest'):
            p = x[part]
            if p and not (0 < p['per_100'] < 100):
                raise SystemExit('FAIL - %s %s rate %s' % (x['city'], part, p['per_100']))
        if x['rest'] and x['state'] != 'Delhi':
            same = x['ring'] and x['ring']['state'] == x['state']
            whole = x['core']['before'] + (x['ring']['before'] if same else 0) + x['rest']['before']
            if abs(whole - agg(rows(x['state']))['before']) > 0:
                raise SystemExit('FAIL - %s: core, ring and rest do not add to the state' % x['city'])
    ranked = sorted([x for x in out if x['measure'] == 'left_off' and not x['roll_2025']], key=lambda x: -x['core']['per_100'])
    over = [x for x in ranked if x['state'] != 'Delhi']
    summary = dict(cities=len(ranked), above_state=sum(1 for x in over if x['core']['per_100'] > x['state_per_100']),
                   compared=len(over), times_min=min(x['times_state'] for x in over), times_max=max(x['times_state'] for x in over),
                   ring_below_core=sum(1 for x in ranked if x['ring'] and x['ring']['per_100'] < x['core']['per_100']),
                   with_ring=sum(1 for x in ranked if x['ring']), top=ranked[0]['city'], top_v=ranked[0]['core']['per_100'])
    return dict(summary=summary, cities=out)


def as_csv(d):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    # The base is the roll before the revision except for three cities, whose
    # state published no removals below the state or reports them per 100 on
    # a later roll. The column says which roll it is.
    BASE = {'West Bengal': '2024 Lok Sabha roll', 'Kerala': 'January 2025 roll', 'Bihar': '2025 election roll'}
    w.writerow(['city', 'state', 'measure', 'part', 'districts', 'base_roll', 'base_roll_is', 'names_left_off_or_fall', 'per_100', 'state_per_100', 'note'])
    for x in d['cities']:
        note = 'figures as reported in the press' if x['reported'] else 'per 100 on the 2025 roll' if x['roll_2025'] else ''
        for part in ('core', 'ring', 'rest'):
            p = x[part]
            if not p:
                continue
            ds = '; '.join(p.get('districts', [])) if part != 'rest' else 'rest of state'
            st = (p.get('state') if part == 'ring' else None) or x['state']
            w.writerow([x['city'], st, x['measure'], part, ds, p['before'], BASE.get(x['state'], 'roll before the revision'), p['removed'], p['per_100'], x['state_per_100'], note])
    return buf.getvalue()


def main():
    d = build()
    files = {os.path.join(OUT, 'cities.json'): json.dumps(d, ensure_ascii=False, indent=1) + '\n',
             os.path.join(OUT, 'cities.csv'): as_csv(d)}
    stale = [p for p, t in files.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != t]
    if CHECK:
        if stale:
            raise SystemExit('FAIL - stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale))
        print('OK: cities up to date')
        return
    for p, t in files.items():
        open(p, 'w', encoding='utf-8').write(t)
    s = d['summary']
    print('wrote cities: %d ranked, %d of %d cores above their state (%.1f to %.1f times), ring below core in %d of %d'
          % (s['cities'], s['above_state'], s['compared'], s['times_min'], s['times_max'], s['ring_below_core'], s['with_ring']))


if __name__ == '__main__':
    main()
