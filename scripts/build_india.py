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
ADU = os.path.join(ROOT, 'data', 'india', 'raw', 'adults_ls2024.csv')
BIHAR_REASONS = os.path.join(ROOT, 'data', 'bihar', 'reasons.json')
# Characteristics set against the removal rate and the mix of reasons. Census
# 2011 unless stated; income is per capita NSDP, 2023-24.
CHAR = [('income_pc', 'Income per head'), ('mpce_rural', 'Rural spending per head'), ('mpce_urban', 'Urban spending per head'),
        ('urban_pct', 'Urban share'), ('literacy', 'Literacy'), ('female_literacy', 'Women\'s literacy'),
        ('muslim_pct', 'Muslim share'), ('sc_pct', 'SC share'), ('st_pct', 'ST share'), ('sex_ratio', 'Sex ratio'),
        ('out_migration', 'Born here, living elsewhere'), ('in_migration', 'Living here, born elsewhere')]
# Where each characteristic comes from. Census 2011 only where nothing newer is
# published by state: the two migration measures.
RECENT = os.path.join(ROOT, 'data', 'india', 'raw', 'benchmarks_recent.csv')
PICK = {
    'mpce_rural': ('HCES 2023-24: average monthly per capita consumption expenditure (MPCE)', 'all', 'rural'),
    'mpce_urban': ('HCES 2023-24: average monthly per capita consumption expenditure (MPCE)', 'all', 'urban'),
    'urban_pct': ('Projected urban population as % of total population, 1 March 2026', 'person', 'total'),
    'literacy': ('Literacy rate, age 7 years and above (PLFS 2023-24)', 'person', 'total'),
    'female_literacy': ('Literacy rate, age 7 years and above (PLFS 2023-24)', 'female', 'total'),
    'muslim_pct': ('NFHS-5: households by religion of household head: Muslim', 'all', 'total'),
    'sc_pct': ('NFHS-5: households by caste/tribe of household head: Scheduled caste', 'all', 'total'),
    'st_pct': ('NFHS-5: households by caste/tribe of household head: Scheduled tribe', 'all', 'total'),
    'sex_ratio': ('NFHS-5: 3. Sex ratio of the total population (females per 1,000 males)', 'person', 'total'),
}
SOURCE_OF = {'income_pc': 'RBI, 2023-24', 'mpce_rural': 'HCES 2023-24', 'mpce_urban': 'HCES 2023-24', 'urban_pct': 'Technical Group projection, 2026',
             'literacy': 'PLFS 2023-24', 'female_literacy': 'PLFS 2023-24', 'muslim_pct': 'NFHS-5, 2019-21 (households)', 'sc_pct': 'NFHS-5, 2019-21 (households)',
             'st_pct': 'NFHS-5, 2019-21 (households)', 'sex_ratio': 'NFHS-5, 2019-21', 'out_migration': 'Census 2011', 'in_migration': 'Census 2011'}
CENSUS_2011 = ['urban_pct', 'literacy', 'female_literacy', 'muslim_pct', 'sc_pct', 'st_pct', 'sex_ratio']
BIG = 5e6  # states of 50 lakh people or more in 2011
# A tile map: one equal square per state or union territory, placed roughly
# where it lies, so the picture carries no boundaries. (state, code, row, column)
TILES = [('Jammu and Kashmir', 'JK', 0, 2), ('Ladakh', 'LA', 0, 3), ('Chandigarh', 'CH', 1, 1), ('Punjab', 'PB', 1, 2), ('Himachal Pradesh', 'HP', 1, 3), ('Arunachal Pradesh', 'AR', 1, 7), ('Rajasthan', 'RJ', 2, 1), ('Haryana', 'HR', 2, 2), ('Delhi', 'DL', 2, 3), ('Uttarakhand', 'UK', 2, 4), ('Sikkim', 'SK', 2, 5), ('Assam', 'AS', 2, 6), ('Nagaland', 'NL', 2, 7), ('Gujarat', 'GJ', 3, 1), ('Madhya Pradesh', 'MP', 3, 2), ('Uttar Pradesh', 'UP', 3, 3), ('Bihar', 'BR', 3, 4), ('West Bengal', 'WB', 3, 5), ('Meghalaya', 'ML', 3, 6), ('Manipur', 'MN', 3, 7), ('Dadra and Nagar Haveli and Daman and Diu', 'DD', 4, 0), ('Maharashtra', 'MH', 4, 1), ('Chhattisgarh', 'CG', 4, 2), ('Jharkhand', 'JH', 4, 3), ('Odisha', 'OD', 4, 4), ('Tripura', 'TR', 4, 6), ('Mizoram', 'MZ', 4, 7), ('Goa', 'GA', 5, 1), ('Telangana', 'TG', 5, 2), ('Andhra Pradesh', 'AP', 5, 3), ('Lakshadweep', 'LD', 6, 0), ('Karnataka', 'KA', 6, 1), ('Tamil Nadu', 'TN', 6, 2), ('Puducherry', 'PY', 6, 3), ('Kerala', 'KL', 7, 1), ('Andaman and Nicobar Islands', 'AN', 7, 4)]


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
INT = ['electors_before', 'removed'] + R
FIN = os.path.join(ROOT, 'data', 'india', 'raw', 'final.csv')
FIN_INT = ['electors_draft', 'added_after_draft', 'removed_after_draft', 'withheld', 'electors_final']


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
        for k, _ in [kv for kv in CHAR if kv[0] not in ('mpce_rural', 'mpce_urban')] + [('population_2011', '')]:
            c[k] = float(x[k]) if x[k] not in ('', None) else None
        c['intl_border'] = x['intl_border'] == 'yes'
        c['border_countries'] = x['border_countries'] or ''
        cov[x['state']] = c
    assert set(cov) == set(names), 'a characteristics row for every state'
    # The 2011 values are kept beside the recent ones, to show which
    # relationships survive the change of source.
    rec = {}
    for x in csv.DictReader(open(RECENT, encoding='utf-8')):
        for k, (ind, sex, sec) in PICK.items():
            if x['indicator'] == ind and x['sex'] == sex and x['sector'] == sec and x['value']:
                assert (x['state'], k) not in rec, (x['state'], k)
                rec[(x['state'], k)] = float(x['value'])
    for st, c in cov.items():
        for k in CENSUS_2011:
            c[k + '_2011'] = c[k]
        c['mpce_rural'] = c['mpce_urban'] = None
        for k in PICK:
            c[k] = rec.get((st, k))
    missing = [(st, k) for st in names for k in PICK if (st, k) not in rec]
    assert len(missing) <= 3, missing  # DNH & DD urban (projected in two parts); Chandigarh has no rural MPCE row if blank
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
    robust = []
    for k in CENSUS_2011:
        pts_new = [(x['char'][k], x['per_100']) for x in has if x['char'][k] is not None and x['per_100'] is not None]
        pts_old = [(x['char'][k + '_2011'], x['per_100']) for x in has if x['char'][k + '_2011'] is not None and x['per_100'] is not None]
        robust.append({'key': k, 'rho_recent': spearman(pts_new), 'rho_2011': spearman(pts_old), 'n_recent': len(pts_new), 'n_2011': len(pts_old)})
    border = {}
    for yk, yf in outcomes:
        for side in ('yes', 'no'):
            v = [yf(x) for x in has if yf(x) is not None and x['char']['intl_border'] == (side == 'yes')]
            border[yk + '_' + side] = round(median(v), 2)
            border['n_' + yk + '_' + side] = len(v)

    # ---- the rolls against the projected adult population, and the 2024 vote
    adu = {x['state']: x for x in csv.DictReader(open(ADU, encoding='utf-8'))}
    assert set(adu) == set(names), 'an adults and 2024 row for every state'
    for x in rows:
        a = adu[x['state']]
        ad = float(a['adults_2026']) if a['adults_2026'] else None
        v24 = float(a['votes_2024']) if a['votes_2024'] else None
        x['adults_2026'] = ad
        x['roll_adult_pct'] = round(100 * x['electors_before'] / ad, 1) if ad and x['electors_before'] else None
        x['draft_adult_pct'] = round(100 * (x['electors_before'] - x['removed']) / ad, 1) if ad and x['electors_before'] and x['removed'] else None
        x['removed_pct_votes24'] = round(100 * x['removed'] / v24, 1) if v24 and x['removed'] else None
    ra = [x for x in rows if x['roll_adult_pct'] is not None and x['per_100'] is not None]
    adults = {'states': len(ra), 'rho_rate': spearman([(x['roll_adult_pct'], x['per_100']) for x in ra]),
              'over_100': [x['state'] for x in sorted(ra, key=lambda x: -x['roll_adult_pct']) if x['roll_adult_pct'] > 100],
              'roll_total': sum(x['electors_before'] for x in ra), 'draft_total': sum(x['electors_before'] - x['removed'] for x in ra),
              'adults_total': sum(x['adults_2026'] for x in ra)}

    # ---- the final rolls. The draft and final come from one source per state;
    # the fall at the draft is the one used everywhere else on the page.
    fin = {}
    for f in csv.DictReader(open(FIN, encoding='utf-8')):
        assert f['state'] in names, f['state']
        for k in FIN_INT:
            f[k] = int(f[k]) if f[k] else None
        a, r_, w_ = f['added_after_draft'], f['removed_after_draft'], f['withheld'] or 0
        if f['reconciles'] in ('exact', 'rounded'):
            gap = f['electors_draft'] + a - r_ - w_ - f['electors_final']
            assert abs(gap) <= (0 if f['reconciles'] == 'exact' else 0.001 * f['electors_final']), (f['state'], gap)
        else:
            assert f['reconciles'] in ('net only', 'no') and f['note'], f['state']
        assert f['source'] in ('primary', 'press') and f['source_url'].startswith('http'), f['state']
        fin[f['state']] = f
    for x in rows:
        f = fin.get(x['state'])
        for k in ('removed_after_draft', 'added_after_draft', 'withheld', 'electors_final', 'final_date', 'reconciles'):
            x[k] = f[k] if f else None
        x['net_after_draft'] = x['net_fall'] = x['net_fall_per_100'] = x['made_up_pct'] = None
        x['final_source'] = f and {'source': f['source'], 'url': f['source_url'], 'note': f['note']}
        if f:
            dr = x['electors_before'] - x['removed'] if x['electors_before'] and x['removed'] else None
            # The draft in the final-roll source must agree with the draft figures above.
            if dr is not None:
                assert abs(dr - f['electors_draft']) <= 0.005 * dr or x['figures'] == 'rounded' or x['state'] in ('Kerala', 'Bihar'), (x['state'], dr, f['electors_draft'])
            x['net_after_draft'] = f['electors_final'] - f['electors_draft']
            x['net_fall'] = x['removed'] - x['net_after_draft']
            x['made_up_pct'] = round(100 * x['net_after_draft'] / x['removed'], 1)
            if x['electors_before']:
                x['net_fall_per_100'] = round(100 * x['net_fall'] / x['electors_before'], 2)
    fr = [x for x in rows if x['electors_final'] is not None]
    fb = [x for x in fr if x['electors_before']]
    final = {'states': len(fr), 'removed': sum(x['removed'] for x in fr), 'net_after_draft': sum(x['net_after_draft'] for x in fr),
             'withheld': sum(x['withheld'] or 0 for x in fr),
             'gross': sum(1 for x in fr if x['reconciles'] in ('exact', 'rounded')),
             'per_100': round(100 * sum(x['removed'] for x in fb) / sum(x['electors_before'] for x in fb), 2),
             'net_per_100': round(100 * sum(x['net_fall'] for x in fb) / sum(x['electors_before'] for x in fb), 2),
             'shrank': [x['state'] for x in fr if x['net_after_draft'] < 0],
             'waiting': [x['state'] for x in rows if x['removed'] is not None and x['electors_final'] is None]}
    final['made_up_pct'] = round(100 * final['net_after_draft'] / final['removed'], 1)
    final['made_up_pct_ex_withheld'] = round(100 * (final['net_after_draft'] + final['withheld']) / final['removed'], 1)
    final['net_per_100_ex_withheld'] = round(100 * (sum(x['net_fall'] for x in fb) - final['withheld']) / sum(x['electors_before'] for x in fb), 2)
    final['rho_made_up'] = spearman([(x['per_100'], x['made_up_pct']) for x in fb])

    # ---- women among the removed
    rs = json.load(open(BIHAR_REASONS, encoding='utf-8'))
    bf = sum(rs['by_sex'][k]['F'] for k in rs['by_sex'])
    bm = sum(rs['by_sex'][k]['M'] for k in rs['by_sex'])
    gender = [{'state': 'Bihar', 'women_removed': bf, 'men_removed': bm, 'women_share_removed': round(100 * bf / (bf + bm), 2),
               'women_share_roll': json.load(open(os.path.join(ROOT, 'data', 'bihar', 'summary.json'), encoding='utf-8'))['totals']['female_share_roll'],
               'quality': 'lists', 'source_url': '',
               'note': 'Counted from the phase 1 deletion lists. The roll before the revision by sex is the draft roll by sex (Format 4B) plus the names removed at the draft by sex.'}]
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
        'adults': adults,
        'tiles': [{'state': a, 'code': c, 'row': r, 'col': k} for a, c, r, k in TILES],
        'characteristics': [{'key': k, 'label': l, 'source': SOURCE_OF[k]} for k, l in CHAR],
        'robustness_2011': robust,
        'correlations': corr,
        'border': border,
        'gender': gender,
        'reasons': R,
        'total': total(has),
        'by_phase': {p: total([x for x in has if x['phase'] == p]) for p in ('1', '2', '3')},
        'pending': [x['state'] for x in rows if x['removed'] is None],
        'after_draft': {'states': sum(1 for x in rows if x['removed_after_draft'] is not None),
                        'removed': sum(x['removed_after_draft'] or 0 for x in rows)},
        'final': final,
        'states': rows,
    }
    return out


def dump_csv(d):
    import io
    cols = ['state', 'phase', 'draft_date', 'electors_before', 'removed', 'per_100', 'dead', 'shifted_absent_other', 'duplicate', 'unsplit',
            'split', 'figures', 'source', 'source_url', 'final_date', 'added_after_draft', 'removed_after_draft', 'withheld', 'electors_final', 'net_after_draft', 'net_fall', 'net_fall_per_100', 'made_up_pct', 'note']
    gen = {g['state']: g for g in d['gender']}
    b = io.StringIO()
    cols = cols + ['roll_adult_pct', 'draft_adult_pct', 'removed_pct_votes24', 'women_share_removed', 'women_share_roll', 'sex_split_quality'] + [k for k, _ in CHAR] + ['intl_border']
    w = csv.DictWriter(b, fieldnames=cols, extrasaction='ignore', lineterminator='\n')
    w.writeheader()
    for x in d['states']:
        g = gen.get(x['state'], {})
        row = {k: ('' if x.get(k) is None else x[k]) for k in cols}
        row.update({'roll_adult_pct': x.get('roll_adult_pct') or '', 'draft_adult_pct': x.get('draft_adult_pct') or '', 'removed_pct_votes24': x.get('removed_pct_votes24') or ''})
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
