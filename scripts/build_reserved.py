"""Seats reserved for Scheduled Castes and Scheduled Tribes against general
seats, in every state the site has constituency figures for.

Writes data/india/reserved.json and data/india/reserved.csv.

    python3 scripts/build_reserved.py           # write
    python3 scripts/build_reserved.py --check   # fail if the output is stale

- A seat's reservation is the Delimitation Order of 2008. Bihar's comes from
  its own constituency file; Gujarat, Delhi, Rajasthan and Uttarakhand carry it
  in the seat's official name, "(SC)" or "(ST)"; Tamil Nadu, West Bengal and
  Kerala are in data/india/raw/reserved_ac.csv, taken from Wikipedia's lists
  of each assembly's constituencies (October 2026). The build fails unless
  every state's count of SC and ST seats equals the Delimitation Order's.
- Three measures, never mixed. Bihar, Tamil Nadu, Gujarat and Delhi published
  the names left off by constituency (Bihar per 100 on its 2025 roll, the
  others per 100 on the roll before). West Bengal and Kerala published only
  the roll, so for them it is the fall from the earlier roll to the draft.
  Rajasthan and Uttarakhand are left out: Rajasthan's constituency figure is
  the change over more than two years, and Uttarakhand's covers only the
  months after the draft.
- Reserved seats are not spread evenly over a state, so a gap between them
  and general seats can be geography. Each reserved seat is therefore also
  set against the general seats of its own district, and the page reports
  both.
"""
import csv
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'india')
CHECK = '--check' in sys.argv
# Delimitation of Parliamentary and Assembly Constituencies Order, 2008
ORDER = {'Bihar': (38, 2), 'Tamil Nadu': (44, 2), 'Gujarat': (13, 27), 'Delhi': (12, 0), 'West Bengal': (68, 16), 'Kerala': (14, 2)}


def load(*p):
    return json.load(open(os.path.join(ROOT, 'data', *p), encoding='utf-8'))


def from_name(n):
    return 'SC' if re.search(r'\(\s*SC\s*\)', n) else 'ST' if re.search(r'\(\s*ST\s*\)', n) else 'GEN'


RES = {}
for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'india', 'raw', 'reserved_ac.csv'), encoding='utf-8')):
    RES[(r['state'], int(r['ac']))] = r['reserved']


def seats(state):
    """[{ac, name, district, cat, base, count}] for a state."""
    if state == 'Bihar':
        return [dict(ac=r['ac'], name=r['name'], district=r['district'], cat=r['reserved'], base=r['electorate_2025'], count=r['total']) for r in load('bihar', 'constituencies.json')]
    if state == 'Tamil Nadu':
        return [dict(ac=r['ac'], name=r['name'], district=r['district'], cat=RES.get((state, r['ac']), 'GEN'), base=r['before'], count=r['removed']) for r in load('tamilnadu', 'constituencies.json')]
    if state == 'Gujarat':
        return [dict(ac=r['ac'], name=r['name'], district=r['district'], cat=from_name(r['name']), base=r['before'], count=r['removed']) for r in load('gujarat', 'constituencies.json')]
    if state == 'Delhi':
        return [dict(ac=r['ac'], name=r['name'], district=r['district'], cat=from_name(r['name']), base=r['roll_before'], count=r['left_off']) for r in load('delhi', 'constituencies.json')]
    if state == 'West Bengal':
        return [dict(ac=r['ac'], name=r['name'], district=r['district'], cat=RES.get((state, r['ac']), 'GEN'), base=r['roll_2024'], count=r['roll_2024'] - r['draft']) for r in load('westbengal', 'constituencies.json')]
    if state == 'Kerala':
        return [dict(ac=r['ac'], name=r['name'], district=r['district'], cat=RES.get((state, r['ac']), 'GEN'), base=r['roll_2025'], count=r['roll_2025'] - r['draft']) for r in load('kerala', 'constituencies.json')]
    raise SystemExit(state)


STATES = [('Bihar', 'left_off', 'per 100 on the 2025 roll'), ('Tamil Nadu', 'left_off', 'per 100 on the roll before'),
          ('Gujarat', 'left_off', 'per 100 on the roll before'), ('Delhi', 'left_off', 'per 100 on the roll before'),
          ('West Bengal', 'fall', 'fall per 100, 2024 roll to the draft'), ('Kerala', 'fall', 'fall per 100, January 2025 roll to the draft')]


def rate(rs):
    b = sum(r['base'] for r in rs)
    return round(100 * sum(r['count'] for r in rs) / b, 2) if b else None


def build():
    out = []
    for state, measure, unit in STATES:
        S = seats(state)
        n = {c: sum(1 for r in S if r['cat'] == c) for c in ('SC', 'ST')}
        if (n['SC'], n['ST']) != ORDER[state]:
            raise SystemExit('FAIL - %s: %d SC and %d ST seats, the Delimitation Order has %d and %d' % (state, n['SC'], n['ST'], *ORDER[state]))
        row = dict(state=state, measure=measure, unit=unit, seats=len(S), state_rate=rate(S))
        for c in ('GEN', 'SC', 'ST'):
            rs = [r for r in S if r['cat'] == c]
            row[c] = dict(seats=len(rs), rate=rate(rs)) if rs else None
            if c == 'GEN' or not rs:
                continue
            # each reserved seat against the general seats of its own district
            gaps, above, each = [], 0, []
            for r in rs:
                g = [x for x in S if x['district'] == r['district'] and x['cat'] == 'GEN']
                if not g:
                    continue
                gap = 100 * r['count'] / r['base'] - rate(g)
                gaps.append(gap)
                above += gap > 0
                each.append(dict(ac=r['ac'], name=r['name'], district=r['district'], gap=round(gap, 2)))
            row[c].update(compared=len(gaps), above_district=above, gap_vs_district=round(sum(gaps) / len(gaps), 2) if gaps else None, each=each)
        out.append(row)
    return dict(states=out)


def as_csv(d):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['state', 'measure', 'category', 'seats', 'rate', 'mean_gap_vs_general_seats_same_district', 'seats_above_their_district', 'seats_compared'])
    for s in d['states']:
        for c in ('GEN', 'SC', 'ST'):
            x = s[c]
            if x:
                w.writerow([s['state'], s['unit'], c, x['seats'], x['rate'], x.get('gap_vs_district', ''), x.get('above_district', ''), x.get('compared', '')])
    return buf.getvalue()


def main():
    d = build()
    files = {os.path.join(OUT, 'reserved.json'): json.dumps(d, ensure_ascii=False, indent=1) + '\n',
             os.path.join(OUT, 'reserved.csv'): as_csv(d)}
    stale = [p for p, t in files.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != t]
    if CHECK:
        if stale:
            raise SystemExit('FAIL - stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale))
        print('OK: reserved seats up to date')
        return
    for p, t in files.items():
        open(p, 'w', encoding='utf-8').write(t)
    for s in d['states']:
        print(s['state'], s['GEN']['rate'], s['SC'] and (s['SC']['rate'], s['SC']['gap_vs_district'], s['SC']['above_district'], s['SC']['compared']),
              s['ST'] and (s['ST']['rate'], s['ST']['gap_vs_district'], s['ST']['above_district'], s['ST']['compared']))


if __name__ == '__main__':
    main()
