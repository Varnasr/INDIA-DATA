"""Did seats with more removals swing to the NDA between 2020 and 2025?

Reads the candidate-wise Assembly results for both years
(data/bihar/raw/ae_party_votes_2020_2025.csv, one row per seat, year and party,
pooled from the Election Commission's Detailed Results, statistical report 10,
for each election) and sets each seat's change in vote
share against its removals per 100 electors.

Both years are counted on the 2025 line-up, so a change is a change in what the
same parties won together:

  NDA    BJP, JD(U), LJP(RV) (LJP in 2020, which fought alone), HAM(S),
         RLM (RLSP in 2020)
  INDIA  RJD, INC, CPI(ML)L, CPI, CPI(M), VIP (with the NDA in 2020), IIP

Shares are of all votes, NOTA included. The slope is estimated within
district (a dummy for each district), so a region that swung as a whole, such
as Seemanchal, does not count as a removal effect, and again allowing for each
seat's 2020 lead, because seats the NDA won big in 2020 gave some of it back
whatever their removals. The second is the standard swing model and the one
the pages lead with; it moves the slope from negative to positive. Intervals are two robust
standard errors either side.

The scenario figure is what the slope would be if every removed elector who
was alive and would have voted had voted against the NDA: an extra removal per
100 electors takes away (share alive x turnout) votes per 100 electors, out of
(turnout x 100) votes, so the NDA's lead grows by share alive points.

Writes data/bihar/swing.json. --check fails if it is stale.
"""
import csv
import json
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BIHAR = os.path.join(ROOT, 'data', 'bihar')
CHECK = '--check' in sys.argv

NDA = {'BJP', 'JD(U)', 'LJP(RV)', 'LJP', 'HAM(S)', 'RLM', 'RLSP'}
INDIA = {'RJD', 'INC', 'CPI(ML)L', 'CPI', 'CPI(M)', 'VIP', 'IIP'}


def r(x, n=4):
    return round(float(x), n)


def load():
    v = defaultdict(lambda: defaultdict(int))
    for row in csv.DictReader(open(os.path.join(BIHAR, 'raw', 'ae_party_votes_2020_2025.csv'))):
        v[(int(row['year']), int(row['ac']))][row['party']] += int(row['votes'])
    out = {}
    for (y, ac), p in v.items():
        el = p.pop('_electors')
        tot = sum(p.values())
        out[(y, ac)] = {'nda': 100 * sum(n for k, n in p.items() if k in NDA) / tot,
                        'india': 100 * sum(n for k, n in p.items() if k in INDIA) / tot,
                        'votes': tot, 'electors': el,
                        'top': sorted((n for k, n in p.items() if k != 'NOTA'), reverse=True)}
    return out


def fe_slope(y, x, groups, controls=()):
    g = sorted(set(groups))
    D = np.array([[a == k for k in g] for a in groups], float)
    X = np.column_stack([x, *controls, D])
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    e = y - X @ b
    n, p = X.shape
    V = XtXi @ (X.T * e ** 2) @ X @ XtXi * n / (n - p)
    se = np.sqrt(V[0, 0])
    return {'slope': r(b[0]), 'lo': r(b[0] - 2 * se), 'hi': r(b[0] + 2 * se)}


def build():
    seats = json.load(open(os.path.join(BIHAR, 'constituencies.json'), encoding='utf-8'))
    res = load()
    rows = []
    for c in seats:
        a, b = res[(2020, c['ac'])], res[(2025, c['ac'])]
        # the 2025 figures must be the declared result (independents are
        # pooled by party here, so a seat with one in the top two is skipped)
        if 'IND' not in (c['win2025'], c['ru2025']):
            assert {c['winner_votes2025'], c['runner_up_votes2025']} <= set(b['top']), c['name']
        rows.append({'ac': c['ac'], 'name': c['name'], 'district': c['district'], 'per_100': c['per_100'],
                     'nda20': r(a['nda']), 'nda25': r(b['nda']), 'india20': r(a['india']), 'india25': r(b['india']),
                     'votes20': a['votes'], 'votes25': b['votes']})
    P = np.array([s['per_100'] for s in rows])
    dn = np.array([s['nda25'] - s['nda20'] for s in rows])
    di = np.array([s['india25'] - s['india20'] for s in rows])
    vg = np.array([100 * (s['votes25'] / s['votes20'] - 1) for s in rows])
    dist = [s['district'] for s in rows]
    # A seat's 2020 lead predicts its swing on its own: seats the NDA won big
    # in 2020 gave some of it back. Allowing for that is the standard swing
    # model, and it changes the answer, so both are kept.
    l20 = np.array([s['nda20'] - s['india20'] for s in rows])
    dl = dn - di
    X = np.column_stack([np.ones(len(rows)), l20])
    adj = dl - X @ np.linalg.lstsq(X, dl, rcond=None)[0] + dl.mean()
    cut = np.quantile(P, [1 / 3, 2 / 3])
    g = np.digitize(P, cut)
    thirds = [{'n': int((g == i).sum()), 'lo': r(P[g == i].min(), 1), 'hi': r(P[g == i].max(), 1),
               'per_100': r(P[g == i].mean(), 1), 'd_nda': r(dn[g == i].mean(), 1),
               'd_india': r(di[g == i].mean(), 1), 'd_lead': r(dl[g == i].mean(), 1),
               'd_lead_adj': r(adj[g == i].mean(), 1), 'votes_growth': r(vg[g == i].mean(), 1)} for i in range(3)]
    dead = sum(c['r_dead'] for c in seats)
    p1 = sum(c['p1'] for c in seats)
    alive = 1 - dead / p1
    summary = {'n': len(rows), 'd_nda': r(dn.mean(), 1), 'd_india': r(di.mean(), 1), 'votes_growth': r(vg.mean(), 1),
               'thirds': thirds,
               'within': {'nda': fe_slope(dn, P, dist), 'india': fe_slope(di, P, dist),
                          'lead': fe_slope(dl, P, dist), 'lead_adj': fe_slope(dl, P, dist, [l20]),
                          'votes': fe_slope(vg, P, dist)},
               'alive_share': r(100 * alive, 1),
               'scenario_all_against': r(alive), 'scenario_half': r(alive / 2),
               'districts': len(set(dist))}
    return {'as_of': '2026-09-30', 'summary': summary, 'seats': rows}


def write(path, obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    if CHECK:
        old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
        if old != s:
            print('STALE', path)
            sys.exit(1)
        return
    open(path, 'w', encoding='utf-8').write(s)


if __name__ == '__main__':
    out = build()
    write(os.path.join(BIHAR, 'swing.json'), out)
    if CHECK:
        print('OK')
    else:
        print(json.dumps(out['summary'], indent=1))
