#!/usr/bin/env python3
"""Build the Hyderabad Old City SIR figures from the explorer's own aggregates.

    python3 scripts/build_hyderabad.py          # writes data/hyderabad/summary.json and parts.json
    python3 scripts/build_hyderabad.py --check  # fails if they are stale

The explorer at hyderabad/explorer/ carries, per polling part, counts of every
elector by fate, reason, age band, sex, name-estimated religion, 2002 linkage
and hearing rule. Those counts were built from the CEO Telangana SIR exports
by the HDCC data team; no row-level file is in this repository. They are kept
in data/hyderabad/explorer.json, which the explorer page fetches. This script
reads the same file the explorer renders, so the two cannot disagree, and
derives the analyses the Bihar pages carry: rates by group, and, because the
Old City files cover every elector, comparisons *within* the same part.

Within-part comparisons matter here for the same reason within-seat ones do
in Bihar. A constituency-wide gap between two groups can arise because one
group lives in parts where everyone was struck off more. Comparing the two
groups inside each part, and pooling with each part weighted by its smaller
group, removes that.
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The explorer's counts, which hyderabad/explorer/ fetches. Edited by hand
# from the HDCC aggregates; nothing in this repository writes it.
SRC = os.path.join(ROOT, 'data', 'hyderabad', 'explorer.json')
OUT = os.path.join(ROOT, 'data', 'hyderabad')
CHECK = '--check' in sys.argv
STALE = []


def load():
    with open(SRC, encoding='utf-8') as fh:
        return json.load(fh)


def rate(a, b, k=4):
    return None if not b else round(100 * a / b, k)


def within(parts, a_num, a_den, b_num, b_den, min_n=20):
    """Pooled within-part difference in deletion rate, group A minus group B,
    each part weighted by the smaller of its two groups. Also how many parts
    go each way."""
    num = den = 0.0
    up = down = n = 0
    for p in parts:
        na, nb = p[a_den], p[b_den]
        if na < min_n or nb < min_n:
            continue
        d = 100 * p[a_num] / na - 100 * p[b_num] / nb
        w = min(na, nb)
        num += w * d
        den += w
        n += 1
        up += d > 0
        down += d < 0
    return {'diff_pp': round(num / den, 4) if den else None, 'parts': n, 'a_higher': up, 'b_higher': down}


def spearman(x, y):
    def ranks(a):
        s = sorted(range(len(a)), key=lambda i: a[i])
        r = [0.0] * len(a)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and a[s[j + 1]] == a[s[i]]:
                j += 1
            for k in range(i, j + 1):
                r[s[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    sy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return round(sxy / (sx * sy), 3)


def build():
    D = load()
    acs, parts_out = [], []
    for name, A in D['acs'].items():
        T, P = A['total'], A['parts']
        assert sum(p['asd'] for p in P) == T['asd'] and sum(p['total'] for p in P) == T['total'], name
        # the no-mapping list is inside the summoned count in every part, so the
        # discrepancy-only count below cannot go negative
        assert all(p['nomap'] <= p['hear'] for p in P) and T['nomap'] <= T['hear'], name
        link = bool(T.get('haslink'))
        rates = [100 * p['asd'] / p['total'] for p in P if p['total'] >= 100]
        rates.sort()
        mus_share = [100 * p['mus_all'] / p['total'] for p in P if p['total'] >= 100]
        prate = [100 * p['asd'] / p['total'] for p in P if p['total'] >= 100]
        old_share = [100 * p['age_all'][7] / p['total'] for p in P if p['total'] >= 100]
        untr = [100 * p['reasons'][1] / p['asd'] for p in P if p['total'] >= 100 and p['asd'] >= 20]
        prate_u = [100 * p['asd'] / p['total'] for p in P if p['total'] >= 100 and p['asd'] >= 20]
        e = A['e2023']
        acs.append({
            'name': name, 'partlabel': A['partlabel'], 'parts': len(P), 'electors': T['total'], 'deleted': T['asd'],
            'hearing': T['hear'], 'nomap': T['nomap'], 'unaccounted': T['unacc'],
            # summoned from the discrepancy list and not on the no-mapping list;
            # an elector on both is counted once, under no mapping
            'discrepancy_only': T['hear'] - T['nomap'],
            'nomap_rate': rate(T['nomap'], T['total']), 'discrepancy_rate': rate(T['hear'] - T['nomap'], T['total']),
            'rate': rate(T['asd'], T['total']), 'hearing_rate': rate(T['hear'], T['total']),
            'reasons': dict(zip(D['reasons'], T['reasons'])),
            'age_rate': [rate(a, b) for a, b in zip(T['age_asd'], T['age_all'])],
            'age_all': T['age_all'],
            'female_rate': rate(T['f_asd'], T['f_all']), 'male_rate': rate(T['m_asd'], T['m_all']),
            'female_share_deleted': rate(T['f_asd'], T['asd']), 'female_share_roll': rate(T['f_all'], T['total']),
            'muslim_rate': rate(T['mus_asd'], T['mus_all']), 'hindu_rate': rate(T['hin_asd'], T['hin_all']),
            'muslim_share_roll': rate(T['mus_all'], T['total']), 'hindu_share_roll': rate(T['hin_all'], T['total']),
            'other_religion_roll': T['total'] - T['mus_all'] - T['hin_all'],
            'linked': link,
            'linked_rate': rate(T['lk_asd'], T['lk_all']) if link else None,
            'unlinked_rate': rate(T['asd'] - T['lk_asd'], T['total'] - T['lk_all']) if link else None,
            'linked_share_roll': rate(T['lk_all'], T['total']) if link else None,
            'counts': {k: T[k] for k in ['f_asd', 'f_all', 'm_asd', 'm_all', 'mus_asd', 'mus_all', 'hin_asd', 'hin_all', 'lk_asd', 'lk_all', 'age_asd']},
            'rules': dict(zip(D['rules'], T['rules'])),
            'slots': T.get('nslots'), 'max_slot': T.get('maxslot'), 'median_slot': T.get('median_slot'),
            'daily': A['daily'],
            'e2023': {'valid': e['valid'], 'winner_votes': e['winner'], 'margin': e['margin'], 'winner': e['name'],
                      'deleted_over_margin': round(T['asd'] / e['margin'], 1), 'deleted_over_valid': rate(T['asd'], e['valid'])},
            'part_rate_quartiles': [round(rates[int(q * (len(rates) - 1))], 1) for q in (0, .25, .5, .75, 1)],
            'parts_over_60': sum(r > 60 for r in rates),
            'within_part': {
                'hindu_minus_muslim': within(P, 'hin_asd', 'hin_all', 'mus_asd', 'mus_all'),
                'female_minus_male': within(P, 'f_asd', 'f_all', 'm_asd', 'm_all'),
                'unlinked_minus_linked': within([dict(p, ul_asd=p['asd'] - p['lk_asd'], ul_all=p['total'] - p['lk_all']) for p in P],
                                                'ul_asd', 'ul_all', 'lk_asd', 'lk_all') if link else None,
            },
            'part_correlations': {
                'muslim_share_vs_rate': spearman(mus_share, prate),
                'aged80_share_vs_rate': spearman(old_share, prate),
                'untraceable_share_vs_rate': spearman(untr, prate_u),
            },
        })
        for p in P:
            if p['total'] < 100:
                continue
            # Rates to four places, so a one-decimal reading rounds the same
            # way in Python and JavaScript (80.25 reads 80.2 in one, 80.3 in
            # the other). A locality the export left blank is empty.
            loc = p.get('loc') or ''
            if loc.strip().lower() in ('nan', 'none'):
                loc = ''
            parts_out.append([name, p['part'], loc, p['total'], p['asd'], rate(p['asd'], p['total'], 4),
                              rate(p['mus_all'], p['total'], 4), rate(p['mus_asd'], p['mus_all'], 4) if p['mus_all'] >= 20 else None,
                              rate(p['hin_asd'], p['hin_all'], 4) if p['hin_all'] >= 20 else None,
                              rate(p['reasons'][1], p['asd'], 4) if p['asd'] else None, rate(p['hear'], p['total'], 4)])
    tot = lambda k: sum(a[k] for a in acs)
    summary = {
        'totals': {'electors': tot('electors'), 'deleted': tot('deleted'), 'hearing': tot('hearing'),
                   'parts': tot('parts'), 'rate': rate(tot('deleted'), tot('electors'))},
        'bands': D['bands'], 'reasons': D['reasons'], 'rules': D['rules'], 'acs': acs,
    }
    write('summary.json', summary)
    write('parts.json', {'fields': ['ac', 'part', 'locality', 'electors', 'deleted', 'rate', 'muslim_share_roll',
                                    'muslim_rate', 'hindu_rate', 'untraceable_share_of_deleted', 'hearing_rate'],
                         'rows': parts_out})
    return summary


def write(name, obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    path = os.path.join(OUT, name)
    if CHECK:
        if not os.path.exists(path) or open(path, encoding='utf-8').read() != s:
            STALE.append(name)
        return
    os.makedirs(OUT, exist_ok=True)
    open(path, 'w', encoding='utf-8').write(s)


if __name__ == '__main__':
    s = build()
    if CHECK:
        if STALE:
            print('STALE: %s' % STALE)
            sys.exit(1)
        print('OK: Hyderabad data matches the explorer')
    else:
        print('wrote data/hyderabad: %d constituencies, %d parts, %d deleted of %d' % (
            len(s['acs']), s['totals']['parts'], s['totals']['deleted'], s['totals']['electors']))
