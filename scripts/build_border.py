"""Border districts against the rest of their state, in every state the site
has district figures for and the official list names border districts in.

Writes data/india/border.json and data/india/border.csv.

    python3 scripts/build_border.py           # write
    python3 scripts/build_border.py --check   # fail if the output is stale

- The border districts are the Government of India's list of Border Guarding
  Districts, as printed in Annexure XI of the Staff Selection Commission's
  notice of 1 December 2025 for constables in the Home Ministry's armed police
  forces (data/india/raw/border_districts.csv, all 119 rows). No district is
  chosen by this site. Bihar's seven match the seven Nepal-border districts
  the Bihar pages already use, and the build fails if they stop matching.
- One measure per state, the one its own page uses, and states are never
  ranked against each other. Uttar Pradesh and Gujarat: names left off per
  100 on the roll before. Bihar: both phases per 100 on the 2025 roll. West
  Bengal: the fall in the roll from the 2024 Lok Sabha roll to the draft.
  Uttarakhand: names removed after the draft per 1,000 on the draft, because
  its earlier removals are a state total only.
- Rajasthan is left out. Its district figure is the change in the roll over
  more than two years, and Barmer, one of its four border districts, was split
  to make Balotara in 2023, so the list and the districts no longer line up.
- Cities lost the most names and none is on the border, so the interior is
  also given without the city's own districts (data/india/cities.json).
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'india')
CHECK = '--check' in sys.argv
# the list's spelling -> the spelling in the state's own table
NAMES = {'LakhimpurKheri': 'Kheri',
         'Shravasti': 'Shrawasti', 'Cooch Behar': 'Coochbehar', 'Kalimgpong': 'Kalimpong'}


def load(*p):
    return json.load(open(os.path.join(ROOT, 'data', *p), encoding='utf-8'))


def rows(state):
    """[{district, base, count, reasons}] in the state's own measure."""
    if state == 'Uttar Pradesh':
        return [dict(district=r['district'], base=r['roll_before'], count=r['total'],
                     dead=r['dead'], shifted_absent=r['shifted'] + r['untraceable_absent'], elsewhere=r['multiple']) for r in load('uttarpradesh', 'districts.json')]
    if state == 'Gujarat':
        return [dict(district=r['district'], base=r['before'], count=r['removed'],
                     dead=r['dead'], shifted_absent=r['shifted'] + r['absent'], elsewhere=r['enrolled_elsewhere']) for r in load('gujarat', 'districts.json')]
    if state == 'Bihar':
        return [dict(district=r['district'], base=round(r['deleted'] * 100 / r['per_100']), count=r['deleted'], own=r['border']) for r in load('bihar', 'districts.json')]
    if state == 'West Bengal':
        return [dict(district=r['district'], base=r['roll_2024'], count=r['roll_2024'] - r['draft']) for r in load('westbengal', 'districts.json')]
    if state == 'Uttarakhand':
        return [dict(district=r['district'], base=r['draft'], count=r['objections']) for r in load('uttarakhand', 'districts.json')]
    raise SystemExit(state)


STATES = [('Uttar Pradesh', 'names left off per 100 on the roll before', 100, 'uttarpradesh/'),
          ('Gujarat', 'names left off per 100 on the roll before', 100, 'gujarat/'),
          ('Bihar', 'names removed in both phases per 100 on the 2025 roll', 100, 'bihar/border/'),
          ('West Bengal', 'fall in the roll per 100, 2024 roll to the draft', 100, 'westbengal/'),
          ('Uttarakhand', 'names removed after the draft per 1,000 on the draft', 1000, 'uttarakhand/')]


def agg(rs, per):
    b = sum(r['base'] for r in rs)
    c = sum(r['count'] for r in rs)
    out = dict(districts=len(rs), base=b, count=c, rate=round(per * c / b, 4))
    if rs and all('dead' in r for r in rs):
        for k in ('dead', 'shifted_absent', 'elsewhere'):
            out[k + '_share'] = round(100 * sum(r[k] for r in rs) / c, 1)
    return out


def build():
    listed = {}
    for r in csv.DictReader(open(os.path.join(OUT, 'raw', 'border_districts.csv'), encoding='utf-8')):
        listed.setdefault(r['state'], []).append(NAMES.get(r['district'], r['district']))
    if sum(len(v) for v in listed.values()) != 119:
        raise SystemExit('FAIL - the list should have 119 districts')
    cities = {}
    for c in load('india', 'cities.json')['cities']:
        cities.setdefault(c['state'], []).extend(c['core']['districts'])
    out = []
    for state, unit, per, page in STATES:
        rs = rows(state)
        have = {r['district'] for r in rs}
        border = listed[state]
        missing = set(border) - have
        if missing:
            raise SystemExit('FAIL - %s: no district %s' % (state, sorted(missing)))
        if state == 'Bihar':
            own = {r['district'] for r in rs if 'Nepal' in r['own']}
            if own != set(border):
                raise SystemExit('FAIL - Bihar: the official list %s differs from the Bihar pages %s' % (sorted(border), sorted(own)))
        b = [r for r in rs if r['district'] in border]
        i = [r for r in rs if r['district'] not in border]
        city = [d for d in cities.get(state, []) if d in have and d not in border]
        i_nc = [r for r in i if r['district'] not in city]
        whole = agg(rs, per)
        row = dict(state=state, unit=unit, per=per, page=page, state_rate=whole['rate'],
                   border=agg(b, per), interior=agg(i, per), city_districts=city,
                   interior_without_city=agg(i_nc, per) if city else None,
                   share_of_roll=round(100 * sum(r['base'] for r in b) / whole['base'], 1),
                   share_of_count=round(100 * sum(r['count'] for r in b) / whole['count'], 1),
                   districts=sorted([dict(district=r['district'], rate=round(per * r['count'] / r['base'], 4),
                                          above_interior=per * r['count'] / r['base'] > agg(i, per)['rate']) for r in b], key=lambda x: -x['rate']))
        row['ratio'] = round(row['border']['rate'] / row['interior']['rate'], 4)
        row['above'] = sum(1 for x in row['districts'] if x['above_interior'])
        out.append(row)
    return dict(source=dict(title='List of Border Guarding Districts, Annexure XI, Staff Selection Commission notice of 1 December 2025',
                            url='https://ssc.gov.in/api/attachment/uploads/masterData/NoticeBoards/notice_01122025.pdf', districts=119),
                higher=sum(1 for r in out if r['border']['rate'] > r['interior']['rate']), states=out)


def as_csv(d):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['state', 'measure', 'part', 'districts', 'base', 'count', 'rate', 'dead_share', 'shifted_absent_share', 'enrolled_elsewhere_share'])
    for s in d['states']:
        for part in ('border', 'interior', 'interior_without_city'):
            x = s[part]
            if x:
                w.writerow([s['state'], s['unit'], part, x['districts'], x['base'], x['count'], x['rate'],
                            x.get('dead_share', ''), x.get('shifted_absent_share', ''), x.get('elsewhere_share', '')])
        for x in s['districts']:
            w.writerow([s['state'], s['unit'], 'border district: ' + x['district'], 1, '', '', x['rate'], '', '', ''])
    return buf.getvalue()


def main():
    d = build()
    files = {os.path.join(OUT, 'border.json'): json.dumps(d, ensure_ascii=False, indent=1) + '\n',
             os.path.join(OUT, 'border.csv'): as_csv(d)}
    stale = [p for p, t in files.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != t]
    if CHECK:
        if stale:
            raise SystemExit('FAIL - stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale))
        print('OK: border table up to date')
        return
    for p, t in files.items():
        open(p, 'w', encoding='utf-8').write(t)
    for s in d['states']:
        print(s['state'], 'border', s['border']['rate'], 'interior', s['interior']['rate'],
              'interior w/o city', s['interior_without_city'] and s['interior_without_city']['rate'],
              'above', s['above'], 'of', len(s['districts']), 'reasons', {k: v for k, v in s['border'].items() if k.endswith('share')},
              {k: v for k, v in s['interior'].items() if k.endswith('share')})


if __name__ == '__main__':
    main()
