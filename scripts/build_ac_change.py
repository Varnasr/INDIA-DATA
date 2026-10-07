"""One table of every constituency's roll through the revision, for the four
states that published their rolls constituency by constituency: Tamil Nadu,
Kerala, West Bengal and Uttarakhand.

    python3 scripts/build_ac_change.py           # write
    python3 scripts/build_ac_change.py --check   # fail if stale

Reads only the states' own checked constituency files (data/<state>/
constituencies.json) and writes data/india/ac_change.csv and .json. Each
state measures something different, and every column says which roll it is.
Nothing is added up across states.
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
        full.append([s, ac, nm, dist, early, left, draft, add, rem, later, ch, ce, round(100 * ce / early, 2) if ce is not None else None])
    return full


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
    buf.write('\n# Each state measures a different thing. Read the columns with these labels.\n')
    for s, lab in STATES.items():
        for k, v in lab.items():
            buf.write('# %s, %s: %s\n' % (s, k, v))
    files = {os.path.join(ROOT, 'data', 'india', 'ac_change.csv'): buf.getvalue(),
             os.path.join(ROOT, 'data', 'india', 'ac_change.json'): json.dumps({'cols': COLS, 'rows': R, 'states': summ}, ensure_ascii=False) + '\n'}
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
