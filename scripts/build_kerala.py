"""Kerala: the roll, constituency by constituency, from the roll of January
2025 to the SIR draft, the final roll and the roll the 2026 election was held
on, set against the 2026 result.

Reads data/kerala/raw (see SOURCES.md there) and writes data/kerala/summary.json,
constituencies.json, districts.json, constituencies.csv and districts.csv.

    python3 scripts/build_kerala.py           # write
    python3 scripts/build_kerala.py --check   # fail if the output is stale

The CEO published no table of the names left off the draft, by constituency or
for the state. Every roll is published by constituency and sex: the final roll
of the 2025 summary revision (6 January 2025), the SIR draft (23 December
2025), the SIR final roll (21 February 2026) and the roll of 23 March 2026. The
fall from January 2025 to the draft is a change in the roll. It takes in the
ordinary changes of 2025 as well as the revision, so it is never called the
removals, though statewide the two are within 40,000 of each other.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'kerala', 'raw')
OUT = os.path.join(ROOT, 'data', 'kerala')
CHECK = '--check' in sys.argv

PARTY = {
    'Indian National Congress': 'INC', 'Communist Party of India (Marxist)': 'CPI(M)',
    'Indian Union Muslim League': 'IUML', 'Communist Party of India': 'CPI',
    'Kerala Congress': 'KEC', 'Kerala Congress (Jacob)': 'KEC(J)', 'Kerala Congress (M)': 'KEC(M)',
    'Kerala Congress (B)': 'KEC(B)', 'Revolutionary Socialist Party': 'RSP', 'Bharatiya Janata Party': 'BJP',
    'Rashtriya Janata Dal': 'RJD', 'Revolutionary Marxist Party of India': 'RMPI',
    'Communist Marxist Party Kerala State Committee': 'CMP', 'Independent': 'IND',
    'Congress (Secular)': 'C(S)', 'Indian National League': 'INL', 'Indian Socialist Janata Dal': 'ISJD',
    'Kerala Revolutionary Socialist Party (Leninist- Marxist)': 'RSP(L)',
    'Nationalist Congress Party - Sharadchandra Pawar': 'NCP(SP)',
}
DISTRICT = {'KOLLM': 'Kollam'}
# Totals printed in the sources, asserted below.
TOTALS = {'before': 27810942, 'draft': 25442352, 'final': 26953644, 'election': 27142952}
WOMEN = {'before': 14369092, 'draft': 13058731, 'final': 13827319, 'election': 13921868}
FROZEN = 27850855  # the roll frozen for the revision, press reports; 39,913 above January 2025
PRESS_REMOVED = 2408503


def rows(name):
    with open(os.path.join(RAW, name), encoding='utf-8') as fh:
        return {int(r['ac']): r for r in csv.DictReader(fh)}


def ints(r, *keys):
    return [int(r[k]) for k in keys]


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
    T = {k: rows(f) for k, f in (('before', 'roll_before_ac.csv'), ('draft', 'draft_roll_ac.csv'),
                                 ('final', 'final_roll_ac.csv'), ('election', 'election_roll_ac.csv'))}
    res = rows('results_2026.csv')
    for t in list(T.values()) + [res]:
        assert sorted(t) == list(range(1, 141)), 'every table has ACs 1 to 140 once'
    for k, t in T.items():
        assert sum(int(r['total']) for r in t.values()) == TOTALS[k], k
        assert sum(int(r['women']) for r in t.values()) == WOMEN[k], k

    acs = []
    for n in range(1, 141):
        v = {}
        for k, t in T.items():
            m, w, th, tot = ints(t[n], 'men', 'women', 'third', 'total')
            assert m + w + th == tot, (k, n)
            v[k], v[k + '_w'] = tot, w
        x = res[n]
        wv, rv, margin, votes = ints(x, 'winner_votes', 'runner_up_votes', 'margin', 'total_votes')
        assert wv - rv == margin > 0, n
        assert v['draft'] < v['before'] and v['final'] >= v['draft'] and v['election'] >= v['final'], n
        d = T['draft'][n]
        fall_draft, fall = v['before'] - v['draft'], v['before'] - v['election']
        acs.append({
            'ac': n, 'name': d['ac_name'].title(), 'district': DISTRICT.get(d['district'], d['district'].title()),
            'roll_2025': v['before'], 'draft': v['draft'], 'final': v['final'], 'election': v['election'],
            'fall_draft': fall_draft, 'fall': fall,
            'draft_per_100': round(100 * fall_draft / v['before'], 4),
            'per_100': round(100 * fall / v['before'], 4),
            'restored_pct': round(100 * (v['election'] - v['draft']) / fall_draft, 4),
            'women_2025_pct': round(100 * v['before_w'] / v['before'], 4),
            'women_fall_pct': round(100 * (v['before_w'] - v['draft_w']) / fall_draft, 4),
            'winner': PARTY[x['winner_party']], 'runner_up': PARTY[x['runner_up_party']],
            'margin': margin, 'votes': votes, 'turnout': round(100 * votes / v['election'], 4),
            'fall_voters': round(max(fall, 0) * votes / v['election']),
            '_w': {k: v[k + '_w'] for k in T},
        })
    for a in acs:
        a['draft_over_margin'] = a['fall_draft'] > a['margin']
        a['over_margin'] = a['fall'] > a['margin']
        a['could_change'] = a['fall_voters'] > a['margin']

    dist = {}
    for a in acs:
        g = dist.setdefault(a['district'], {'district': a['district'], 'acs': 0, 'roll_2025': 0, 'draft': 0,
                                            'final': 0, 'election': 0, 'women_2025': 0, 'women_draft': 0})
        g['acs'] += 1
        for k in ('roll_2025', 'draft', 'final', 'election'):
            g[k] += a[k]
        g['women_2025'] += a['_w']['before']
        g['women_draft'] += a['_w']['draft']
    for g in dist.values():
        fd = g['roll_2025'] - g['draft']
        g['draft_per_100'] = round(100 * fd / g['roll_2025'], 4)
        g['per_100'] = round(100 * (g['roll_2025'] - g['election']) / g['roll_2025'], 4)
        g['restored_pct'] = round(100 * (g['election'] - g['draft']) / fd, 4)
        g['women_2025_pct'] = round(100 * g['women_2025'] / g['roll_2025'], 4)
        g['women_fall_pct'] = round(100 * (g['women_2025'] - g['women_draft']) / fd, 4)
    districts = sorted(dist.values(), key=lambda g: -g['draft_per_100'])
    assert len(districts) == 14
    for a in acs:
        a['vs_district'] = round(a['draft_per_100'] - dist[a['district']]['draft_per_100'], 4)
        del a['_w']

    by_winner = {}
    for a in acs:
        by_winner.setdefault(a['winner'], []).append(a)
    winners = []
    for w, L in sorted(by_winner.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        winners.append({'party': w, 'seats': len(L),
                        'draft_per_100': round(100 * sum(a['fall_draft'] for a in L) / sum(a['roll_2025'] for a in L), 4),
                        'vs_district': round(sum(a['vs_district'] for a in L) / len(L), 4),
                        'over_margin': sum(a['over_margin'] for a in L)})

    B, D, F, E = (TOTALS[k] for k in ('before', 'draft', 'final', 'election'))
    lo, hi = min(acs, key=lambda a: a['draft_per_100']), max(acs, key=lambda a: a['draft_per_100'])
    summary = {
        'roll_2025': B, 'frozen': FROZEN, 'press_removed': PRESS_REMOVED,
        'draft': D, 'final': F, 'election': E,
        'fall_draft': B - D, 'draft_per_100': round(100 * (B - D) / B, 4),
        'added_final': F - D, 'added_election': E - F,
        'restored_pct': round(100 * (E - D) / (B - D), 4),
        'fall': B - E, 'per_100': round(100 * (B - E) / B, 4),
        'women_2025_pct': round(100 * WOMEN['before'] / B, 4),
        'women_fall_pct': round(100 * (WOMEN['before'] - WOMEN['draft']) / (B - D), 4),
        'women_added_pct': round(100 * (WOMEN['election'] - WOMEN['draft']) / (E - D), 4),
        'districts_women_over': sum(g['women_fall_pct'] > g['women_2025_pct'] for g in districts),
        'acs_women_over': sum(a['women_fall_pct'] > a['women_2025_pct'] for a in acs),
        'acs': len(acs), 'districts': len(districts),
        'rate_min': lo['name'], 'rate_min_v': lo['draft_per_100'], 'rate_max': hi['name'], 'rate_max_v': hi['draft_per_100'],
        'draft_over_margin': sum(a['draft_over_margin'] for a in acs),
        'over_margin': sum(a['over_margin'] for a in acs),
        'could_change': sum(a['could_change'] for a in acs),
        'votes': sum(a['votes'] for a in acs), 'turnout': round(100 * sum(a['votes'] for a in acs) / E, 4),
        'seats_2026': {w['party']: w['seats'] for w in winners},
        'winners': winners,
        'rho_rate_margin': round(spearman([a['draft_per_100'] for a in acs], [a['margin'] / a['votes'] for a in acs]), 3),
        'top_districts': [{'district': g['district'], 'draft_per_100': g['draft_per_100']} for g in districts[:5]],
        'low_districts': [{'district': g['district'], 'draft_per_100': g['draft_per_100']} for g in districts[-3:]],
    }

    out = {}
    out['summary.json'] = json.dumps(summary, ensure_ascii=False, indent=1) + '\n'
    out['constituencies.json'] = json.dumps(acs, ensure_ascii=False, separators=(',', ':')) + '\n'
    out['districts.json'] = json.dumps(districts, ensure_ascii=False, separators=(',', ':')) + '\n'
    cols = ['ac', 'name', 'district', 'roll_2025', 'draft', 'final', 'election', 'fall_draft', 'draft_per_100',
            'fall', 'per_100', 'women_2025_pct', 'women_fall_pct', 'winner', 'runner_up', 'margin', 'votes',
            'turnout', 'over_margin', 'could_change']
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['ac', 'name', 'district', 'roll_jan_2025', 'draft_roll_dec_2025', 'final_roll_feb_2026',
                'roll_mar_2026', 'fall_to_draft', 'fall_to_draft_per_100', 'fall_to_election_roll',
                'fall_to_election_roll_per_100', 'women_pct_2025', 'women_pct_of_fall_to_draft', 'winner_2026',
                'runner_up_2026', 'margin_2026', 'votes_2026', 'turnout_2026', 'fall_over_margin',
                'fall_at_turnout_over_margin'])
    for a in acs:
        w.writerow([a[c] for c in cols])
    out['constituencies.csv'] = buf.getvalue()
    dcols = ['district', 'acs', 'roll_2025', 'draft', 'final', 'election', 'draft_per_100', 'per_100',
             'women_2025_pct', 'women_fall_pct']
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['district', 'acs', 'roll_jan_2025', 'draft_roll_dec_2025', 'final_roll_feb_2026', 'roll_mar_2026',
                'fall_to_draft_per_100', 'fall_to_election_roll_per_100', 'women_pct_2025', 'women_pct_of_fall_to_draft'])
    for g in districts:
        w.writerow([g[c] for c in dcols])
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
            sys.exit('STALE, run python3 scripts/build_kerala.py: ' + ', '.join(stale))
        print('OK: data/kerala matches its raw tables')
    else:
        print('fall to draft %d of %d (%.2f per 100); women %.2f%% of it against %.2f%%; over margin %d, at turnout %d of %d'
              % (s['fall_draft'], s['roll_2025'], s['draft_per_100'], s['women_fall_pct'], s['women_2025_pct'],
                 s['over_margin'], s['could_change'], s['acs']))
