"""One table of every constituency's roll through the revision, for the four
states that published their rolls constituency by constituency: Tamil Nadu,
Kerala, West Bengal and Uttarakhand.

    python3 scripts/build_ac_change.py           # write
    python3 scripts/build_ac_change.py --check   # fail if stale

Reads only the states' own checked constituency files (data/<state>/
constituencies.json) and writes data/india/ac_change.csv and .json. Each
state measures something different, and every column says which roll it is.
Nothing is added up across states.

It also writes data/india/ac_finder.json, which the page's finder reads: every
constituency with a figure anywhere on the site, in nine places, each with the
one count its own state page leads with and that count's own measure. The
measures differ from state to state, so the finder names the measure beside
every figure and never ranks one state's seats against another's.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECK = '--check' in sys.argv
J = lambda p: json.load(open(os.path.join(ROOT, 'data', p), encoding='utf-8'))

# what each state's columns are, in plain words, for the page and the CSV
STATES = {
    'Tamil Nadu': {
        'earlier': 'Roll when the revision began (27 October 2025), the draft plus the names left off',
        'left_off': "Names left off the draft (the Chief Electoral Officer's list by constituency)",
        'draft': 'Draft roll, 19 December 2025', 'after': 'Final roll, 23 February 2026',
        'gross': 'Not published by constituency'},
    'Kerala': {
        'earlier': 'Final roll of the January 2025 summary revision',
        'left_off': 'Not published, even for the state',
        'draft': 'Draft roll, 23 December 2025', 'after': 'Final roll, 21 February 2026',
        'gross': 'Not published by constituency'},
    'West Bengal': {
        'earlier': 'Roll of the 2024 Lok Sabha election',
        'left_off': 'Not published below the state',
        'draft': 'Draft roll, 16 December 2025', 'after': 'Roll at the 2026 nominations (no final roll was published by constituency)',
        'gross': 'Not published by constituency'},
    'Uttarakhand': {
        'earlier': 'Not published by constituency',
        'left_off': 'Not published below the state',
        'draft': 'Draft roll', 'after': 'Final roll, 3 October 2026',
        'gross': "Claims admitted (Form 6 and 6A) and objections admitted, from the Chief Electoral Officer's PN 63/2026"},
}
COLS = ['state', 'ac', 'constituency', 'district', 'earlier_roll', 'left_off_draft', 'draft', 'added_after_draft',
        'removed_after_draft', 'later_roll', 'change_draft_to_later', 'change_earlier_to_later', 'change_earlier_to_later_per_100']


def rows():
    out = []
    for r in J('tamilnadu/constituencies.json'):
        out.append(['Tamil Nadu', r['ac'], r['name'], r['district'], r['before'], r['removed'], r['draft'], None, None, r['final']])
    for r in J('kerala/constituencies.json'):
        out.append(['Kerala', r['ac'], r['name'], r['district'], r['roll_2025'], None, r['draft'], None, None, r['final']])
    for r in J('westbengal/constituencies.json'):
        out.append(['West Bengal', r['ac'], r['name'], r['district'], r['roll_2024'], None, r['draft'], None, None, r['election']])
    for r in J('uttarakhand/constituencies.json'):
        if r['draft'] + r['claims'] - r['objections'] != r['final']:
            raise SystemExit('FAIL - Uttarakhand %s: draft plus claims less objections is not the final roll' % r['name'])
        out.append(['Uttarakhand', r['ac'], r['name'], r['district'], None, None, r['draft'], r['claims'], r['objections'], r['final']])
    full = []
    for s, ac, nm, dist, early, left, draft, add, rem, later in out:
        if early is not None and left is not None and early - left != draft:
            raise SystemExit('FAIL - %s %s: the earlier roll less the names left off is not the draft' % (s, nm))
        ch = later - draft
        ce = later - early if early is not None else None
        full.append([s, ac, nm, dist, early, left, draft, add, rem, later, ch, ce, round(100 * ce / early, 4) if ce is not None else None])
    return full


# The finder: each place's lead count, in its own words, and where its seats open
FINDER = [
    # place id, state, page, file, count field, base field, per, what the count is, what the base is
    ('bihar', 'Bihar', 'bihar/results/', 'bihar/constituencies.json', 'total', 'electorate_2025', 100,
     'names removed in both phases', 'the 2025 roll'),
    ('tn', 'Tamil Nadu', 'tamilnadu/', 'tamilnadu/constituencies.json', 'removed', 'before', 100,
     'names left off the draft', 'the roll before the revision'),
    ('wb', 'West Bengal', 'westbengal/', 'westbengal/constituencies.json', 'fall_draft', 'roll_2024', 100,
     'fall in the roll from the 2024 Lok Sabha roll to the draft', 'the 2024 roll'),
    ('kl', 'Kerala', 'kerala/', 'kerala/constituencies.json', 'fall_draft', 'roll_2025', 100,
     'fall in the roll from the January 2025 roll to the draft', 'the January 2025 roll'),
    ('rj', 'Rajasthan', 'rajasthan/', 'rajasthan/constituencies.json', 'fall', 'roll_2023', 100,
     'change in the roll from the 2023 election to the final roll, more than two years', 'the 2023 roll'),
    ('dl', 'Delhi', 'delhi/', 'delhi/constituencies.json', 'left_off', 'roll_before', 100,
     'names left off the draft (forms not collected)', 'the roll before the revision'),
    ('gj', 'Gujarat', 'gujarat/', 'gujarat/constituencies.json', 'removed', 'before', 100,
     'names left off the draft', 'the roll before the revision'),
    ('uk', 'Uttarakhand', 'uttarakhand/', 'uttarakhand/constituencies.json', 'left_off', 'roll_before', 100,
     'names left off the draft', 'the roll before the revision'),
    ('mh', 'Maharashtra', 'maharashtra/', 'maharashtra/constituencies.json', 'left_off', 'before', 100,
     'names left off the draft', 'the roll before the revision'),
    ('as', 'Assam', 'assam/', 'assam/constituencies.json', 'fall', 'draft', 1000,
     'fall in the roll from the draft to the final roll of the Special Revision, names removed less names added', 'the draft'),
]


def finder():
    rows, places = [], []
    for pid, state, page, f, cnt, base, per, what, of in FINDER:
        rs = J(f)
        places.append({'id': pid, 'state': state, 'page': page, 'what': what, 'of': of, 'per': per, 'acs': len(rs)})
        for r in rs:
            if not r[base]:
                raise SystemExit('FAIL - %s %s has no %s' % (state, r['name'], base))
            # a state with constituency pages (make_seat_pages.py) opens the seat's own page
            href = f.split('/')[0] + '/seat/%d/' % r['ac'] if pid in ('tn', 'wb', 'kl', 'dl', 'uk', 'gj', 'rj', 'mh', 'bihar', 'as') else page + '#ac-%d' % r['ac']
            rows.append([pid, r['ac'], r['name'], r['district'], r[cnt], round(per * r[cnt] / r[base], 4), href])
    h = J('hyderabad/summary.json')['acs']
    places.append({'id': 'hyd', 'state': 'Telangana (Hyderabad Old City)', 'page': 'hyderabad/explorer/', 'what': 'names removed from the lists',
                   'of': 'the roll before the revision', 'per': 100, 'acs': len(h)})
    for a in h:
        rows.append(['hyd', None, a['name'], 'Hyderabad', a['deleted'], round(100 * a['deleted'] / a['electors'], 4), 'hyderabad/explorer/#' + a['name']])
    return {'cols': ['place', 'ac', 'constituency', 'district', 'count', 'rate', 'href'], 'places': places, 'rows': rows}


def main():
    R = rows()
    summ = {}
    for s in STATES:
        rs = [r for r in R if r[0] == s]
        x = {'acs': len(rs), 'draft': sum(r[6] for r in rs), 'later': sum(r[9] for r in rs),
             'grew': sum(1 for r in rs if r[10] > 0), 'fell': sum(1 for r in rs if r[10] < 0)}
        if rs[0][4] is not None:
            x['earlier'] = sum(r[4] for r in rs)
            x['below_earlier'] = sum(1 for r in rs if r[11] < 0)
        if rs[0][5] is not None:
            x['left_off'] = sum(r[5] for r in rs)
        if rs[0][7] is not None:
            x['added'] = sum(r[7] for r in rs)
            x['removed'] = sum(r[8] for r in rs)
        summ[s] = dict(x, labels=STATES[s])
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(COLS)
    for r in R:
        w.writerow(['' if v is None else v for v in r])
    files = {os.path.join(ROOT, 'data', 'india', 'ac_change.csv'): buf.getvalue(),
             os.path.join(ROOT, 'data', 'india', 'ac_change.json'): json.dumps({'cols': COLS, 'rows': R, 'states': summ}, ensure_ascii=False) + '\n',
             os.path.join(ROOT, 'data', 'india', 'ac_finder.json'): json.dumps(finder(), ensure_ascii=False, separators=(',', ':')) + '\n'}
    stale = [p for p, t in files.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != t]
    if CHECK:
        if stale:
            raise SystemExit('FAIL - stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale))
        print('OK: %d constituencies in four states' % len(R))
        return
    for p, t in files.items():
        open(p, 'w', encoding='utf-8').write(t)
    for s, x in summ.items():
        print(s, {k: v for k, v in x.items() if k != 'labels'})


if __name__ == '__main__':
    main()
