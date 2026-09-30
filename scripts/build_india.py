#!/usr/bin/env python3
"""All India: the reasons recorded for SIR removals, state by state.

    python3 scripts/build_india.py          # writes data/india/states.json and states.csv
    python3 scripts/build_india.py --check  # fails if either is stale

Source: data/india/raw/states.csv, one row per state or union territory,
curated from the Chief Electoral Officers' draft-roll figures (their press
notes where they could be read, press reports of them otherwise) and, for
Bihar, from the phase 1 deletion lists on this site.

The figures are those at the draft roll: the names left off it at the end of
enumeration, with the reason entered for each. The reasons are folded into
the three that every state reports: dead, shifted or absent (with "others"
where a state reported it), and enrolled more than once. Names removed after
the draft, at hearings and on objections, carry no reason in any state and
are kept apart.
"""
import csv
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(ROOT, 'data', 'india', 'raw', 'states.csv')
OUT_J = os.path.join(ROOT, 'data', 'india', 'states.json')
OUT_C = os.path.join(ROOT, 'data', 'india', 'states.csv')
R = ['dead', 'shifted_absent_other', 'duplicate']
COV = os.path.join(ROOT, 'data', 'india', 'raw', 'covariates.csv')
GEN = os.path.join(ROOT, 'data', 'india', 'raw', 'gender.csv')
BIHAR_REASONS = os.path.join(ROOT, 'data', 'bihar', 'reasons.json')
# Characteristics set against the removal rate and the mix of reasons. Census
# 2011 unless stated; income is per capita NSDP, 2023-24.
CHAR = [('income_pc', 'Income per head'), ('urban_pct', 'Urban share'), ('literacy', 'Literacy'),
        ('female_literacy', 'Women\'s literacy'), ('muslim_pct', 'Muslim share'), ('sc_pct', 'SC share'),
        ('st_pct', 'ST share'), ('sex_ratio', 'Sex ratio'), ('out_migration', 'Born here, living elsewhere'),
        ('in_migration', 'Living here, born elsewhere')]
BIG = 5e6  # states of 50 lakh people or more in 2011


def ranks(x):
    o = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and x[o[j + 1]] == x[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(pts):
    """Rank correlation of (x, y) pairs; None below six pairs."""
    if len(pts) < 6:
        return None
    x, y = ranks([a for a, _ in pts]), ranks([b for _, b in pts])
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    den = (sum((v - mx) ** 2 for v in x) * sum((v - my) ** 2 for v in y)) ** 0.5
    return round(num / den, 2)


def median(v):
    v = sorted(v)
    n = len(v)
    return None if not n else (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2)
INT = ['electors_before', 'removed', 'removed_after_draft'] + R


def load():
    rows = []
    for x in csv.DictReader(open(RAW, encoding='utf-8')):
        for k in INT:
            x[k] = int(x[k]) if x[k] else None
        rows.append(x)
    return rows


def build():
    rows = load()
    names = [x['state'] for x in rows]
    assert len(names) == len(set(names)) == 32, 'one row for each of the 32 states and union territories'
    for x in rows:
        split = x['split']
        cats = [x[k] for k in R]
        if split in ('complete', 'short'):
            assert all(c is not None for c in cats), x['state']
            s = sum(cats)
            gap = x['removed'] - s
            # A complete split may miss by rounding (lakh figures), never by more than 0.5%.
            if split == 'complete':
                assert abs(gap) <= 0.005 * x['removed'], (x['state'], gap)
            else:
                assert gap > 0, x['state']
            x['unsplit'] = max(gap, 0)
            x['shares'] = {k: round(100 * x[k] / s, 2) for k in R}
        else:
            assert all(c is None for c in cats), x['state']
            x['unsplit'] = x['removed']
            x['shares'] = None
        x['per_100'] = round(100 * x['removed'] / x['electors_before'], 2) if x['removed'] and x['electors_before'] else None
    has = [x for x in rows if x['removed'] is not None]

    def total(xs):
        t = {'states': len(xs), 'removed': sum(x['removed'] for x in xs)}
        for k in R:
            t[k] = sum(x[k] or 0 for x in xs)
        t['unsplit'] = t['removed'] - sum(t[k] for k in R)
        split = sum(t[k] for k in R)
        t['shares'] = {k: round(100 * t[k] / split, 2) for k in R}
        wb = [x for x in xs if x['electors_before']]
        t['per_100'] = round(100 * sum(x['removed'] for x in wb) / sum(x['electors_before'] for x in wb), 2)
        return t

    # ---- characteristics
    cov = {}
    for x in csv.DictReader(open(COV, encoding='utf-8')):
        c = {}
        for k, _ in CHAR + [('population_2011', '')]:
            c[k] = float(x[k]) if x[k] not in ('', None) else None
        c['intl_border'] = x['intl_border'] == 'yes'
        c['border_countries'] = x['border_countries'] or ''
        cov[x['state']] = c
    assert set(cov) == set(names), 'a characteristics row for every state'
    for x in rows:
        x['char'] = cov[x['state']]
    outcomes = [('per_100', lambda x: x['per_100'])] + [(k, (lambda k: lambda x: x['shares'][k] if x['shares'] else None)(k)) for k in R]
    groups = [('all', lambda x: True), ('big', lambda x: x['char']['population_2011'] >= BIG),
              ('phase2', lambda x: x['phase'] == '2'), ('phase3', lambda x: x['phase'] == '3')]
    corr = []
    for k, label in CHAR:
        row = {'key': k, 'label': label}
        for yk, yf in outcomes:
            for g, gf in groups:
                pts = [(x['char'][k], yf(x)) for x in has if gf(x) and x['char'][k] is not None and yf(x) is not None]
                row[yk + '_' + g] = spearman(pts)
                row['n_' + yk + '_' + g] = len(pts)
        corr.append(row)
    border = {}
    for yk, yf in outcomes:
        for side in ('yes', 'no'):
            v = [yf(x) for x in has if yf(x) is not None and x['char']['intl_border'] == (side == 'yes')]
            border[yk + '_' + side] = round(median(v), 2)
            border['n_' + yk + '_' + side] = len(v)

    # ---- women among the removed
    rs = json.load(open(BIHAR_REASONS, encoding='utf-8'))
    bf = sum(rs['by_sex'][k]['F'] for k in rs['by_sex'])
    bm = sum(rs['by_sex'][k]['M'] for k in rs['by_sex'])
    gender = [{'state': 'Bihar', 'women_removed': bf, 'men_removed': bm, 'women_share_removed': round(100 * bf / (bf + bm), 2),
               'women_share_roll': 47.86, 'quality': 'lists', 'source_url': '',
               'note': 'Counted from the phase 1 deletion lists. The roll by sex is not in these sources, so the comparison is with women\'s share of the 2011 population.'}]
    for x in csv.DictReader(open(GEN, encoding='utf-8')):
        assert x['state'] in names, x['state']
        g = dict(x)
        for k in ('women_removed', 'men_removed'):
            g[k] = int(g[k])
        for k in ('women_share_removed', 'women_share_roll'):
            g[k] = float(g[k])
        assert abs(100 * g['women_removed'] / (g['women_removed'] + g['men_removed']) - g['women_share_removed']) < 0.01, x['state']
        gender.append(g)
    for g in gender:
        g['gap'] = round(g['women_share_removed'] - g['women_share_roll'], 2)
        g['phase'] = next(x['phase'] for x in rows if x['state'] == g['state'])

    out = {
        'as_of': '2026-09-30',
        'characteristics': [{'key': k, 'label': l} for k, l in CHAR],
        'correlations': corr,
        'border': border,
        'gender': gender,
        'reasons': R,
        'total': total(has),
        'by_phase': {p: total([x for x in has if x['phase'] == p]) for p in ('1', '2', '3')},
        'pending': [x['state'] for x in rows if x['removed'] is None],
        'after_draft': {'states': sum(1 for x in rows if x['removed_after_draft'] is not None),
                        'removed': sum(x['removed_after_draft'] or 0 for x in rows)},
        'states': rows,
    }
    return out


def dump_csv(d):
    import io
    cols = ['state', 'phase', 'draft_date', 'electors_before', 'removed', 'per_100', 'dead', 'shifted_absent_other', 'duplicate', 'unsplit',
            'split', 'figures', 'source', 'source_url', 'removed_after_draft', 'final_date', 'note']
    gen = {g['state']: g for g in d['gender']}
    b = io.StringIO()
    cols = cols + ['women_share_removed', 'women_share_roll', 'sex_split_quality'] + [k for k, _ in CHAR] + ['intl_border']
    w = csv.DictWriter(b, fieldnames=cols, extrasaction='ignore', lineterminator='\n')
    w.writeheader()
    for x in d['states']:
        g = gen.get(x['state'], {})
        row = {k: ('' if x.get(k) is None else x[k]) for k in cols}
        row.update({'women_share_removed': g.get('women_share_removed', ''), 'women_share_roll': g.get('women_share_roll', ''), 'sex_split_quality': g.get('quality', '')})
        row.update({k: ('' if x['char'][k] is None else x['char'][k]) for k, _ in CHAR})
        row['intl_border'] = 'yes' if x['char']['intl_border'] else 'no'
        w.writerow(row)
    return b.getvalue()


def main():
    d = build()
    j = json.dumps(d, ensure_ascii=False, indent=1) + '\n'
    c = dump_csv(d)
    if '--check' in sys.argv:
        stale = [p for p, s in ((OUT_J, j), (OUT_C, c)) if not os.path.exists(p) or open(p, encoding='utf-8').read() != s]
        if stale:
            sys.exit('stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale) + ' (run scripts/build_india.py)')
        print('PASS: data/india is current')
        return
    open(OUT_J, 'w', encoding='utf-8').write(j)
    open(OUT_C, 'w', encoding='utf-8').write(c)
    t = d['total']
    print('%d states, %s removed, dead %.1f%%, shifted/absent/other %.1f%%, duplicate %.1f%%, not split %s'
          % (t['states'], t['removed'], t['shares']['dead'], t['shares']['shifted_absent_other'], t['shares']['duplicate'], t['unsplit']))


if __name__ == '__main__':
    main()
