"""How sure are we? Each headline Bihar finding put through the checks that
could undo it, and written to data/bihar/robust.json.

A pattern seen across all seats can reverse, or vanish, once seats are
compared only with like seats (Simpson's paradox). So every finding is
measured more than one way:

  margins  names removed against the 2025 margin, on the draft removals and on
           the net fall to the final roll.
  women    women's share of the removed against their share of the roll it
           came from, in every district and every seat, and in phase 1 alone.
  ground   removals per 100 electors on NDA and INDIA ground: across all seats,
           within each district (a dummy per district), within each seat (the
           booths each alliance led in 2024), and leaving out Seemanchal.
  swing    the change in the NDA's lead from 2020 to 2025 against removals:
           across all seats, between districts, within districts, within
           districts allowing for each seat's 2020 lead, by 2020 winner, and
           leaving out Seemanchal.

Intervals are two robust standard errors either side. Writes
data/bihar/robust.json; --check fails if it is stale.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BIHAR = os.path.join(ROOT, 'data', 'bihar')
CHECK = '--check' in sys.argv
SEEMANCHAL = {'Purnia', 'Katihar', 'Araria', 'Kishanganj'}


def J(f):
    return json.load(open(os.path.join(BIHAR, f), encoding='utf-8'))


def r(x, n=2):
    return round(float(x), n)


def fe(y, x, groups, controls=()):
    """Slope of y on x with a dummy per group, robust (HC1) interval."""
    g = sorted(set(groups))
    D = np.array([[a == k for k in g] for a in groups], float)
    X = np.column_stack([x, *controls, D])
    XtXi = np.linalg.pinv(X.T @ X)
    b = XtXi @ X.T @ y
    e = y - X @ b
    n, p = X.shape
    V = XtXi @ (X.T * e ** 2) @ X @ XtXi * n / (n - np.linalg.matrix_rank(X))
    se = float(np.sqrt(V[0, 0]))
    return {'est': r(b[0]), 'lo': r(b[0] - 2 * se), 'hi': r(b[0] + 2 * se)}


def build():
    C = J('constituencies.json')
    F = {s['ac']: s for s in J('final.json')['seats']}
    S = J('summary.json')
    ID = J('identity.json')
    W = {s['ac']: s for s in J('swing.json')['seats']}
    out = {'as_of': '2026-10-01'}

    # ---- margins
    withM = [c for c in C if c.get('margin2025')]
    out['margins'] = {'seats': len(withM),
                      'draft': sum(1 for c in withM if c['total'] > c['margin2025']),
                      'net': sum(1 for c in withM if F[c['ac']]['net_fall'] > c['margin2025'])}

    # ---- women: seat by seat, against the roll the names came from
    over = 0
    for c in C:
        f = F[c['ac']]
        draft_f = f['final_f'] - f['added_f'] + f['removed_after_f']
        draft_m = f['final_m'] - f['added_m'] + f['removed_after_m']
        roll_f = draft_f + c['p1_f']
        roll = roll_f + draft_m + c['p1_m']
        if c['p1_f'] / (c['p1_f'] + c['p1_m']) > roll_f / roll:
            over += 1
    D = ID['districts']
    out['women'] = {'districts': len(D), 'districts_over': sum(1 for d in D if d['female_share_deleted'] > d['female_share_roll']),
                    'seats': len(C), 'seats_over': over}

    # ---- NDA ground
    held = [c for c in C if c['al2020'] in ('NDA', 'INDIA')]
    P = np.array([c['per_100'] for c in held])
    nda = np.array([c['al2020'] == 'NDA' for c in held], float)
    dist = [c['district'] for c in held]
    rest = [i for i, c in enumerate(held) if c['district'] not in SEEMANCHAL]
    ws = S['within_seat_2024']
    AL = S['by_alliance_label']['2020']
    out['ground'] = {
        'pooled': {'nda': r(AL['NDA']['per_100']), 'india': r(AL['INDIA']['per_100'])},
        'within_district': fe(P, nda, dist),
        'within_district_ex_seemanchal': fe(P[rest], nda[rest], [dist[i] for i in rest]),
        'within_seat': {'diff': ws['pooled_nda_minus_india'], 'seats': ws['seats_compared'], 'nda_higher': ws['seats_nda_higher']}}

    # ---- swing
    rows = [W[c['ac']] for c in C]
    dl = np.array([(s['nda25'] - s['nda20']) - (s['india25'] - s['india20']) for s in rows])
    l20 = np.array([s['nda20'] - s['india20'] for s in rows])
    Ps = np.array([s['per_100'] for s in rows])
    ds = [s['district'] for s in rows]
    one = ['all'] * len(rows)
    dm = {d: (Ps[[x == d for x in ds]].mean(), dl[[x == d for x in ds]].mean()) for d in set(ds)}
    bx = np.array([v[0] for v in dm.values()]); by = np.array([v[1] for v in dm.values()])
    al20 = [c['al2020'] for c in C]
    sub = lambda keep: [i for i in range(len(rows)) if keep(i)]
    def adj(idx):
        return fe(dl[idx], Ps[idx], [ds[i] for i in idx], [l20[idx]])
    # district by district, on the lead net of the 2020 lead
    X = np.column_stack([np.ones(len(rows)), l20])
    res = dl - X @ np.linalg.lstsq(X, dl, rcond=None)[0]
    signs = []
    for d in set(ds):
        m = np.array([x == d for x in ds])
        if m.sum() >= 4 and Ps[m].std() > 0:
            signs.append(np.polyfit(Ps[m], res[m], 1)[0])
    allidx = list(range(len(rows)))
    out['swing'] = {
        'pooled': fe(dl, Ps, one),
        'between_district': {'est': r(np.polyfit(bx, by, 1)[0])},
        'within_district': fe(dl, Ps, ds),
        'within_district_2020': adj(allidx),
        'held_nda_2020': adj(sub(lambda i: al20[i] == 'NDA')),
        'held_india_2020': adj(sub(lambda i: al20[i] == 'INDIA')),
        'ex_seemanchal': adj(sub(lambda i: ds[i] not in SEEMANCHAL)),
        'districts_compared': len(signs), 'districts_positive': int(sum(1 for x in signs if x > 0))}
    return out


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
    o = build()
    write(os.path.join(BIHAR, 'robust.json'), o)
    print('OK' if CHECK else json.dumps(o, indent=1))
