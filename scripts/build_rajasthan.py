"""Rajasthan: the revision's state figures, and the roll constituency by
constituency from the 2023 election to the final SIR roll, set against the
2023 result.

Reads data/rajasthan/raw (see SOURCES.md there) and writes data/rajasthan/
summary.json, constituencies.json, districts.json, constituencies.csv and
districts.csv.

    python3 scripts/build_rajasthan.py           # write
    python3 scripts/build_rajasthan.py --check   # fail if the output is stale

The Chief Electoral Officer published the names left off the draft only as a
state total, with the three reasons in lakh. No table of them by constituency
or district exists outside the lists of individual electors, which are not
opened. Below the state the pages therefore measure the change in the roll,
general electors only, from the roll of the 2023 election (ECI statistical
report 11) to the final SIR roll of 12 March 2026. It takes in more than two
years of ordinary changes as well as the revision, so it is never called the
removals. Women in the 2026 table include 565 third-gender electors statewide,
so the 2023 third-gender electors are added to women before comparing.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'rajasthan', 'raw')
OUT = os.path.join(ROOT, 'data', 'rajasthan')
CHECK = '--check' in sys.argv
ANTA = 193  # revised separately after its bye-election of November 2025


def rd(name):
    with open(os.path.join(RAW, name), encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    return cov / (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5


# The district election officers' figures for the draft, as Dainik Bhaskar and
# Amar Ujala printed them on 16 and 17 December 2025 (draft_district_press.csv,
# draft_ac_press.csv; sources in SOURCES.md). Press, partial: 22 of 41 districts
# and 110 of 199 constituencies. Each printed table is held to its own
# identities; the disagreements below are the printed tables' own, kept as
# printed, and a new one fails the build.
DIST_GAPS = {  # district: (roll before - left off - draft, reasons - left off)
    'Kota': (-1010, 0), 'Alwar': (0, -20), 'Ajmer': (0, 54), 'Jaisalmer': (0, 30)}
SUM_GAPS = {  # (district, column): AC rows summed less the printed district row
    ('Alwar', 'roll_before'): 60, ('Alwar', 'left_off'): -50, ('Alwar', 'dead'): 49, ('Alwar', 'shifted'): 20,
    ('Alwar', 'other'): -2, ('Ajmer', 'shifted'): -54, ('Ajmer', 'other'): 60, ('Pali', 'absent'): -3100,
    ('Jaisalmer', 'left_off'): 30, ('Kota', 'roll_before'): 1000, ('Kota', 'draft'): -10}
REASONS = ('dead', 'absent', 'shifted', 'duplicate', 'other')


def outlet(url):
    return 'Amar Ujala' if 'amarujala' in url else 'Dainik Bhaskar'


def build_press(acs, dist):
    I = lambda x: int(x) if x not in ('', None) else None
    D = rd('draft_district_press.csv')
    A = rd('draft_ac_press.csv')
    byac = {a['ac']: a for a in acs}
    rows = []
    for d in D:
        before, left, draft = I(d['roll_before']), I(d['left_off']), I(d['draft'])
        rs = [I(d[k]) for k in ('dead', 'absent', 'shifted', 'multiple', 'other')]
        gap = (before - left - draft, (sum(rs) - left) if None not in rs else 0)
        assert gap == DIST_GAPS.get(d['district'], (0, 0)), (d['district'], gap)
        assert d['district'] in dist, d['district']
        r = {'district': d['district'], 'roll_before': before, 'left_off': left, 'draft': draft,
             'per_100': round(100 * left / before, 4), 'outlet': outlet(d['source']), 'source': d['source'],
             'fall_per_100': dist[d['district']]['per_100']}
        if None not in rs:
            for k, v in zip(REASONS, rs):
                r[k] = v
            r['shifted_absent_pct'] = round(100 * (rs[1] + rs[2]) / sum(rs), 4)
            r['dead_pct'] = round(100 * rs[0] / sum(rs), 4)
        if d['no_mapping']:
            r['no_mapping'] = I(d['no_mapping'])
        rows.append(r)
    rows.sort(key=lambda r: -r['per_100'])
    seen = {}
    pa = {}
    for a in A:
        n = int(a['ac'])
        assert a['district'] == byac[n]['district'], n
        v = {k: I(a[k]) for k in ('roll_before', 'left_off', 'draft') + REASONS + ('no_mapping',)}
        seen.setdefault(a['district'], []).append(v)
        if n == 190:  # the printed roll before repeats Kota North's, so it is draft plus left off
            v['roll_before'] = v['draft'] + v['left_off']
        p = {'left_off': v['left_off'], 'clean': a['check'] in ('before-left=draft;reasons=left', 'before-left=draft', 'reasons=left'),
             'outlet': outlet(a['source'])}
        if v['roll_before']:
            p['roll_before'] = v['roll_before']
            p['per_100'] = round(100 * v['left_off'] / v['roll_before'], 4)
        if v['draft']:
            p['draft'] = v['draft']
            p['after_per_100'] = round(100 * (byac[n]['final'] - v['draft']) / v['draft'], 4)
        if None not in [v[k] for k in REASONS]:
            for k in REASONS:
                p[k] = v[k]
        if v['no_mapping'] is not None:
            p['no_mapping'] = v['no_mapping']
        m = byac[n]
        p['over_margin'] = v['left_off'] > m['margin']
        p['could_change'] = v['left_off'] * m['turnout'] / 100 > m['margin']
        pa[n] = p
    for d in D:
        L = seen.get(d['district'], [])
        if not L:
            continue
        for k in ('roll_before', 'left_off', 'draft', 'dead', 'absent', 'shifted', 'other'):
            vals = [x[k] for x in L]
            if None in vals or not d[k]:
                continue
            got = sum(vals) - int(d[k])
            assert got == SUM_GAPS.get((d['district'], k), 0), (d['district'], k, got)
    covered = sum(r['left_off'] for r in rows)
    withr = [r for r in rows if 'dead' in r]
    tot = {k: sum(r[k] for r in withr) for k in REASONS}
    rate = [p for p in pa.values() if 'per_100' in p]
    fall = [byac[n]['per_100'] for n, p in pa.items() if 'per_100' in p]
    sx = {r['stage']: r for r in rd('sirohi_sex_press.csv')}
    sb, sd = sx['roll_before'], sx['draft_16_12_2025']
    for r in (sb, sd):
        assert int(r['men']) + int(r['women']) + int(r['other']) == int(r['total'])
    assert int(sb['total']) == next(r for r in rows if r['district'] == 'Sirohi')['roll_before']
    assert int(sd['total']) == next(r for r in rows if r['district'] == 'Sirohi')['draft']
    sw = int(sb['women']) - int(sd['women'])
    sl = int(sb['total']) - int(sd['total'])
    hi, lo = max(rate, key=lambda p: p['per_100']), min(rate, key=lambda p: p['per_100'])
    nm = lambda p: byac[next(n for n, q in pa.items() if q is p)]['name']
    press = {
        'districts': rows, 'districts_n': len(rows), 'left_off_covered': covered,
        'covered_pct': round(100 * covered / 4184891, 4),
        'reasons_districts': len(withr), 'reasons_total': tot, 'reasons_left_off': sum(r['left_off'] for r in withr),
        'acs_n': len(pa), 'acs_rate_n': len(rate), 'acs_reasons_n': sum('dead' in p for p in pa.values()),
        'acs_over_margin': sum(p['over_margin'] for p in pa.values()), 'acs_could_change': sum(p['could_change'] for p in pa.values()),
        'ac_max': nm(hi), 'ac_max_v': hi['per_100'], 'ac_min': nm(lo), 'ac_min_v': lo['per_100'],
        'rho_fall': round(spearman([p['per_100'] for p in rate], fall), 3),
        'rho_fall_districts': round(spearman([r['per_100'] for r in rows], [r['fall_per_100'] for r in rows]), 3),
        'sirohi': {'women_left_pct': round(100 * sw / sl, 4), 'women_before_pct': round(100 * int(sb['women']) / int(sb['total']), 4),
                   'left_off': sl, 'women_left': sw},
    }
    return press, pa


def build():
    S = {(r['item'], r['scope']): r for r in rd('sir_state_summary.csv')}
    s199 = '199 ACs (excl. 193 Anta)'
    g = lambda item, scope=s199, col='total': S[(item, scope)][col]
    before, draft = int(g('roll_before_revision')), int(g('draft_roll'))
    added, deleted, final = int(g('draft_roll_additions_to_final')), int(g('draft_roll_deletions_to_final')), int(g('final_roll_general'))
    assert draft + added - deleted == final, 'draft + additions - deletions = final, 199 ACs'
    left = before - draft
    assert left == 4184891, 'names not carried into the draft'
    reasons = {k: float(g('asd_%s_lakh' % k)) for k in ('dead', 'shifted_absent', 'multiple')}

    e23 = {int(r['ac']): r for r in rd('electors_2023_ac.csv')}
    f26 = {int(r['ac']): r for r in rd('final_roll_ac.csv')}
    res = {int(r['ac']): r for r in rd('results_2023.csv')}
    for t in (e23, f26, res):
        assert sorted(t) == list(range(1, 201)), 'every table has ACs 1 to 200 once'
    assert sum(int(r['general']) for r in e23.values()) == 52788931
    assert sum(int(r['total']) for r in f26.values()) == int(g('final_roll_general', '200 ACs'))

    # The CEO's final-roll table misspells one name. The 2023 report and the
    # results spell it Marwar Junction, so the page does too.
    NAME_FIX = {119: ('Marwar Junciton', 'Marwar Junction')}
    acs = []
    for n in range(1, 201):
        a, b, x = e23[n], f26[n], res[n]
        r23, r26 = int(a['general']), int(b['total'])
        w23, w26 = int(a['women']) + int(a['third']), int(b['women'])
        margin, votes = int(x['margin']), int(x['total_votes'])
        assert int(x['winner_votes']) - int(x['runner_up_votes']) == margin > 0, n
        fall = r23 - r26
        acs.append({
            'ac': n, 'name': NAME_FIX[n][1] if n in NAME_FIX and b['ac_name'] == NAME_FIX[n][0] else b['ac_name'], 'district': b['district'],
            'roll_2023': r23, 'final': r26, 'fall': fall, 'per_100': round(100 * fall / r23, 4),
            'women_2023_pct': round(100 * w23 / r23, 4), 'women_2026_pct': round(100 * w26 / r26, 4),
            'women_change': round(100 * w26 / r26 - 100 * w23 / r23, 4),
            'winner': x['winner_party'], 'runner_up': x['runner_up_party'], 'margin': margin, 'votes': votes,
            'turnout': round(100 * votes / int(x['electors']), 4),
            'fall_voters': round(max(fall, 0) * votes / int(x['electors'])),
            'separate': n == ANTA,
        })
    for a in acs:
        a['over_margin'] = a['fall'] > a['margin']
        a['could_change'] = a['fall_voters'] > a['margin']

    dist = {}
    for a in acs:
        d = dist.setdefault(a['district'], {'district': a['district'], 'acs': 0, 'roll_2023': 0, 'final': 0, 'w23': 0, 'w26': 0})
        d['acs'] += 1
        d['roll_2023'] += a['roll_2023']
        d['final'] += a['final']
        d['w23'] += a['women_2023_pct'] * a['roll_2023'] / 100
        d['w26'] += a['women_2026_pct'] * a['final'] / 100
    for d in dist.values():
        d['fall'] = d['roll_2023'] - d['final']
        d['per_100'] = round(100 * d['fall'] / d['roll_2023'], 4)
        d['women_2023_pct'] = round(100 * d.pop('w23') / d['roll_2023'], 4)
        d['women_2026_pct'] = round(100 * d.pop('w26') / d['final'], 4)
        d['women_change'] = round(d['women_2026_pct'] - d['women_2023_pct'], 4)
    districts = sorted(dist.values(), key=lambda d: -d['per_100'])
    assert len(districts) == 41
    for a in acs:
        a['vs_district'] = round(a['per_100'] - dist[a['district']]['per_100'], 4)

    by_w = {}
    for a in acs:
        by_w.setdefault(a['winner'], []).append(a)
    winners = [{'party': p, 'seats': len(L), 'per_100': round(100 * sum(a['fall'] for a in L) / sum(a['roll_2023'] for a in L), 4),
                'vs_district': round(sum(a['vs_district'] for a in L) / len(L), 4), 'over_margin': sum(a['over_margin'] for a in L)}
               for p, L in sorted(by_w.items(), key=lambda kv: (-len(kv[1]), kv[0]))]

    R23, R26 = sum(a['roll_2023'] for a in acs), sum(a['final'] for a in acs)
    W23 = sum(int(e23[n]['women']) + int(e23[n]['third']) for n in e23)
    W26 = sum(int(r['women']) for r in f26.values())
    grew = [a for a in acs if a['fall'] < 0]
    lo, hi = min(acs, key=lambda a: a['per_100']), max(acs, key=lambda a: a['per_100'])
    summary = {
        'scope_state': s199,
        'before': before, 'forms': int(g('enumeration_forms_collected')), 'draft': draft, 'left_off': left,
        'left_per_100': round(100 * left / before, 4), 'reasons_lakh': reasons, 'reasons_lakh_sum': round(sum(reasons.values()), 4),
        'added': added, 'deleted_after': deleted, 'final': final, 'made_up_pct': round(100 * (final - draft) / left, 4),
        'removed_by_final': left + deleted,
        'draft_women_pct': round(100 * int(g('draft_roll', col='women')) / draft, 4),
        'final_women_pct': round(100 * int(g('final_roll_general', col='women')) / final, 4),
        'added_women_pct': round(100 * int(g('draft_roll_additions_to_final', col='women')) / added, 4),
        'deleted_women_pct': round(100 * int(g('draft_roll_deletions_to_final', col='women')) / deleted, 4),
        'service_final': int(g('final_roll_service')),
        'anta_draft': int(g('draft_roll', '200 ACs')) - draft,
        'roll_2023': R23, 'final_200': R26, 'fall': R23 - R26, 'per_100': round(100 * (R23 - R26) / R23, 4),
        'women_2023_pct': round(100 * W23 / R23, 4), 'women_2026_pct': round(100 * W26 / R26, 4),
        'acs': len(acs), 'districts': len(districts), 'acs_grew': len(grew),
        'acs_women_fell': sum(a['women_change'] < 0 for a in acs),
        'rate_min': lo['name'], 'rate_min_v': lo['per_100'], 'rate_max': hi['name'], 'rate_max_v': hi['per_100'],
        'over_margin': sum(a['over_margin'] for a in acs), 'could_change': sum(a['could_change'] for a in acs),
        'seats_2023': {w['party']: w['seats'] for w in winners}, 'winners': winners,
        'rho_rate_margin': round(spearman([a['per_100'] for a in acs], [a['margin'] / a['votes'] for a in acs]), 3),
        'top_districts': [{'district': d['district'], 'per_100': d['per_100']} for d in districts[:5]],
        'low_districts': [{'district': d['district'], 'per_100': d['per_100']} for d in districts[-3:]],
    }

    press, press_acs = build_press(acs, dist)
    summary['press'] = press
    for a in acs:
        if a['ac'] in press_acs:
            a['press'] = press_acs[a['ac']]

    out = {'summary.json': json.dumps(summary, ensure_ascii=False, indent=1) + '\n',
           'constituencies.json': json.dumps(acs, ensure_ascii=False, separators=(',', ':')) + '\n',
           'districts.json': json.dumps(districts, ensure_ascii=False, separators=(',', ':')) + '\n'}
    cols = ['ac', 'name', 'district', 'roll_2023', 'final', 'fall', 'per_100', 'women_2023_pct', 'women_2026_pct', 'women_change',
            'winner', 'runner_up', 'margin', 'votes', 'turnout', 'over_margin', 'could_change', 'separate']
    buf = io.StringIO(); w = csv.writer(buf, lineterminator='\n')
    w.writerow(['ac', 'name', 'district', 'general_electors_2023', 'final_roll_mar_2026', 'fall_in_roll', 'fall_per_100',
                'women_pct_2023', 'women_pct_2026', 'women_pct_change', 'winner_2023', 'runner_up_2023', 'margin_2023', 'votes_2023',
                'turnout_2023', 'fall_over_margin', 'fall_at_turnout_over_margin', 'revised_separately'])
    for a in acs:
        w.writerow([a[c] for c in cols])
    out['constituencies.csv'] = buf.getvalue()
    buf = io.StringIO(); w = csv.writer(buf, lineterminator='\n')
    w.writerow(['district', 'acs', 'general_electors_2023', 'final_roll_mar_2026', 'fall_in_roll', 'fall_per_100', 'women_pct_2023', 'women_pct_2026', 'women_pct_change'])
    for d in districts:
        w.writerow([d[c] for c in ('district', 'acs', 'roll_2023', 'final', 'fall', 'per_100', 'women_2023_pct', 'women_2026_pct', 'women_change')])
    out['districts.csv'] = buf.getvalue()

    buf = io.StringIO(); w = csv.writer(buf, lineterminator='\n')
    w.writerow(['ac', 'name', 'district', 'roll_before_27_oct_2025', 'left_off_draft', 'left_off_per_100', 'draft_16_dec_2025',
                'dead', 'shifted', 'absent', 'enrolled_elsewhere', 'other', 'no_mapping', 'adds_up_as_printed', 'newspaper'])
    for a in acs:
        p = a.get('press')
        if p:
            w.writerow([a['ac'], a['name'], a['district'], p.get('roll_before', ''), p['left_off'], p.get('per_100', ''), p.get('draft', ''),
                        p.get('dead', ''), p.get('shifted', ''), p.get('absent', ''), p.get('duplicate', ''), p.get('other', ''),
                        p.get('no_mapping', ''), p['clean'], p['outlet']])
    out['press_constituencies.csv'] = buf.getvalue()
    buf = io.StringIO(); w = csv.writer(buf, lineterminator='\n')
    w.writerow(['district', 'roll_before_27_oct_2025', 'left_off_draft', 'left_off_per_100', 'draft_16_dec_2025',
                'dead', 'shifted', 'absent', 'enrolled_elsewhere', 'other', 'no_mapping', 'newspaper', 'source'])
    for r in summary['press']['districts']:
        w.writerow([r['district'], r['roll_before'], r['left_off'], r['per_100'], r['draft'], r.get('dead', ''), r.get('shifted', ''),
                    r.get('absent', ''), r.get('duplicate', ''), r.get('other', ''), r.get('no_mapping', ''), r['outlet'], r['source']])
    out['press_districts.csv'] = buf.getvalue()

    stale = []
    for name, text in out.items():
        path = os.path.join(OUT, name)
        old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
        if old != text:
            stale.append(name)
            if not CHECK:
                open(path, 'w', encoding='utf-8').write(text)
    return summary, stale


if __name__ == '__main__':
    s, stale = build()
    if CHECK:
        if stale:
            sys.exit('STALE, run python3 scripts/build_rajasthan.py: ' + ', '.join(stale))
        print('OK: data/rajasthan matches its raw tables')
    else:
        print(json.dumps({k: v for k, v in s.items() if k not in ('winners', 'top_districts', 'low_districts')}, indent=0)[:2500])
        print(s['winners'][:4], s['top_districts'], s['low_districts'])
