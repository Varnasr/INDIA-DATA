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

    acs = []
    for n in range(1, 201):
        a, b, x = e23[n], f26[n], res[n]
        r23, r26 = int(a['general']), int(b['total'])
        w23, w26 = int(a['women']) + int(a['third']), int(b['women'])
        margin, votes = int(x['margin']), int(x['total_votes'])
        assert int(x['winner_votes']) - int(x['runner_up_votes']) == margin > 0, n
        fall = r23 - r26
        acs.append({
            'ac': n, 'name': b['ac_name'], 'district': b['district'],
            'roll_2023': r23, 'final': r26, 'fall': fall, 'per_100': round(100 * fall / r23, 2),
            'women_2023_pct': round(100 * w23 / r23, 2), 'women_2026_pct': round(100 * w26 / r26, 2),
            'women_change': round(100 * w26 / r26 - 100 * w23 / r23, 2),
            'winner': x['winner_party'], 'runner_up': x['runner_up_party'], 'margin': margin, 'votes': votes,
            'turnout': round(100 * votes / int(x['electors']), 2),
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
        d['per_100'] = round(100 * d['fall'] / d['roll_2023'], 2)
        d['women_2023_pct'] = round(100 * d.pop('w23') / d['roll_2023'], 2)
        d['women_2026_pct'] = round(100 * d.pop('w26') / d['final'], 2)
        d['women_change'] = round(d['women_2026_pct'] - d['women_2023_pct'], 2)
    districts = sorted(dist.values(), key=lambda d: -d['per_100'])
    assert len(districts) == 41
    for a in acs:
        a['vs_district'] = round(a['per_100'] - dist[a['district']]['per_100'], 2)

    by_w = {}
    for a in acs:
        by_w.setdefault(a['winner'], []).append(a)
    winners = [{'party': p, 'seats': len(L), 'per_100': round(100 * sum(a['fall'] for a in L) / sum(a['roll_2023'] for a in L), 2),
                'vs_district': round(sum(a['vs_district'] for a in L) / len(L), 2), 'over_margin': sum(a['over_margin'] for a in L)}
               for p, L in sorted(by_w.items(), key=lambda kv: (-len(kv[1]), kv[0]))]

    R23, R26 = sum(a['roll_2023'] for a in acs), sum(a['final'] for a in acs)
    W23 = sum(int(e23[n]['women']) + int(e23[n]['third']) for n in e23)
    W26 = sum(int(r['women']) for r in f26.values())
    grew = [a for a in acs if a['fall'] < 0]
    lo, hi = min(acs, key=lambda a: a['per_100']), max(acs, key=lambda a: a['per_100'])
    summary = {
        'scope_state': s199,
        'before': before, 'forms': int(g('enumeration_forms_collected')), 'draft': draft, 'left_off': left,
        'left_per_100': round(100 * left / before, 2), 'reasons_lakh': reasons, 'reasons_lakh_sum': round(sum(reasons.values()), 2),
        'added': added, 'deleted_after': deleted, 'final': final, 'made_up_pct': round(100 * (final - draft) / left, 2),
        'removed_by_final': left + deleted,
        'draft_women_pct': round(100 * int(g('draft_roll', col='women')) / draft, 2),
        'final_women_pct': round(100 * int(g('final_roll_general', col='women')) / final, 2),
        'added_women_pct': round(100 * int(g('draft_roll_additions_to_final', col='women')) / added, 2),
        'deleted_women_pct': round(100 * int(g('draft_roll_deletions_to_final', col='women')) / deleted, 2),
        'service_final': int(g('final_roll_service')),
        'anta_draft': int(g('draft_roll', '200 ACs')) - draft,
        'roll_2023': R23, 'final_200': R26, 'fall': R23 - R26, 'per_100': round(100 * (R23 - R26) / R23, 2),
        'women_2023_pct': round(100 * W23 / R23, 2), 'women_2026_pct': round(100 * W26 / R26, 2),
        'acs': len(acs), 'districts': len(districts), 'acs_grew': len(grew),
        'acs_women_fell': sum(a['women_change'] < 0 for a in acs),
        'rate_min': lo['name'], 'rate_min_v': lo['per_100'], 'rate_max': hi['name'], 'rate_max_v': hi['per_100'],
        'over_margin': sum(a['over_margin'] for a in acs), 'could_change': sum(a['could_change'] for a in acs),
        'seats_2023': {w['party']: w['seats'] for w in winners}, 'winners': winners,
        'rho_rate_margin': round(spearman([a['per_100'] for a in acs], [a['margin'] / a['votes'] for a in acs]), 3),
        'top_districts': [{'district': d['district'], 'per_100': d['per_100']} for d in districts[:5]],
        'low_districts': [{'district': d['district'], 'per_100': d['per_100']} for d in districts[-3:]],
    }

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
