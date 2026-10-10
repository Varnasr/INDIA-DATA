"""West Bengal: the change in the roll, constituency by constituency, from the
2024 Lok Sabha roll to the SIR draft and to the roll the 2026 election was
held on, set against the 2026 result.

Reads data/westbengal/raw (see SOURCES.md there) and writes
data/westbengal/summary.json, constituencies.json, districts.json,
constituencies.csv and districts.csv.

    python3 scripts/build_westbengal.py           # write
    python3 scripts/build_westbengal.py --check   # fail if the output is stale

The CEO published no table of the names removed by constituency. What is
published by constituency is three rolls: the roll at the 2024 Lok Sabha
nominations, the SIR draft of 16 December 2025, and the roll at the 2026
nominations. The fall from the first to the others is a change in the roll.
It takes in eighteen months of ordinary additions and deletions as well as
the revision, so it is never called the removals. The removals and their
reasons are published for the state only (press note PN-05-2026), and those
state figures are carried here as they were printed.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'westbengal', 'raw')
OUT = os.path.join(ROOT, 'data', 'westbengal')
CHECK = '--check' in sys.argv

PARTY = {
    'Bharatiya Janata Party': 'BJP', 'All India Trinamool Congress': 'AITC',
    'Indian National Congress': 'INC', 'Communist Party of India (Marxist)': 'CPI(M)',
    'All India Secular Front': 'ISF', 'Aam Janata Unnayan party': 'AJUP',
    'Bharatiya Gorkha Prajatantrik Morcha': 'BGPM',
}
# Totals printed in the sources, asserted below.
R24, DRAFT, ELEC = 76010006, 70816630, 68251008
R24_W, DRAFT_W, ELEC_W = 37394818, 34615837, 33314628
# Press note PN-05-2026: the state's revision, as printed.
PN05 = {
    'before': 76637529, 'before_men': 38903865, 'before_women': 37731887,
    'dead': 2416852, 'absent': 1220039, 'shifted': 1988076, 'duplicate': 138328, 'other': 57604,
    'removed': 5820899, 'draft': 70816630,
    'added': 188707, 'form7': 546053, 'adjudication': 6006675, 'final': 64452609,
}


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
    p = PN05
    assert p['dead'] + p['absent'] + p['shifted'] + p['duplicate'] + p['other'] == p['removed']
    assert p['before'] - p['removed'] == p['draft']
    assert p['draft'] + p['added'] - p['form7'] - p['adjudication'] == p['final']

    with open(os.path.join(RAW, 'adjudication_state.csv'), encoding='utf-8') as fh:
        AD = {r['measure']: int(r['value']) for r in csv.DictReader(fh)}
    assert AD['under_adjudication'] == p['adjudication']
    assert AD['appeals_by_excluded'] + AD['appeals_against_inclusion'] == AD['appeals_total']
    assert AD['appeals_decided'] + AD['appeals_pending'] == AD['appeals_total']
    AD['not_accounted'] = AD['under_adjudication'] - AD['found_eligible'] - AD['found_not_eligible']
    assert 0 <= AD['not_accounted'] < 50000
    AD['not_eligible_no_appeal'] = AD['found_not_eligible'] - AD['appeals_by_excluded']
    assert AD['not_eligible_no_appeal'] > 0
    AD['not_eligible_pct'] = round(100 * AD['found_not_eligible'] / AD['under_adjudication'], 2)
    AD['inclusion_appeal_pct'] = round(100 * AD['appeals_against_inclusion'] / AD['found_eligible'], 2)
    AD['pending_pct'] = round(100 * AD['appeals_pending'] / AD['appeals_total'], 2)

    r24, dr, el, res = rows('roll_2024_ls_ac.csv'), rows('draft_roll_ac.csv'), rows('electors_nomination_2026_ac.csv'), rows('results_2026.csv')
    for t in (r24, dr, el, res):
        assert sorted(t) == list(range(1, 295)), 'every table has ACs 1 to 294 once'

    acs = []
    for n in range(1, 295):
        a, d, e, x = r24[n], dr[n], el[n], res[n]
        am, aw, at, atot = ints(a, 'men', 'women', 'third', 'total')
        dm, dw, dt, dtot = ints(d, 'men', 'women', 'third', 'total')
        em, ew, et, etot = ints(e, 'men', 'women', 'third', 'total')
        assert am + aw + at == atot and dm + dw + dt == dtot and em + ew + et == etot, n
        # a row read against the wrong segment shows up here (see SOURCES.md)
        assert abs(int(a['polling_stations']) - int(d['polling_stations'])) <= 50, n
        assert dtot <= 1.02 * atot, n
        wv, rv, margin, votes = ints(x, 'winner_votes', 'runner_up_votes', 'margin', 'total_votes')
        assert wv - rv == margin > 0, n
        fall = atot - etot
        acs.append({
            'ac': n, 'name': d['ac_name'], 'district': d['district'],
            'roll_2024': atot, 'draft': dtot, 'election': etot,
            'fall_draft': atot - dtot, 'fall': fall,
            'draft_per_100': round(100 * (atot - dtot) / atot, 2),
            'per_100': round(100 * fall / atot, 2),
            'after_draft': etot - dtot,
            'women_2024_pct': round(100 * aw / atot, 2),
            'women_election_pct': round(100 * ew / etot, 2),
            'women_fall': aw - ew,
            'winner': PARTY[x['winner_party']], 'runner_up': PARTY[x['runner_up_party']],
            'margin': margin, 'votes': votes, 'turnout': round(100 * votes / etot, 2),
            'fall_voters': round(max(fall, 0) * votes / etot),
        })
    T = lambda k: sum(a[k] for a in acs)
    assert (T('roll_2024'), T('draft'), T('election')) == (R24, DRAFT, ELEC)
    assert sum(int(r24[n]['women']) for n in r24) == R24_W
    assert sum(int(dr[n]['women']) for n in dr) == DRAFT_W
    assert sum(int(el[n]['women']) for n in el) == ELEC_W

    for a in acs:
        a['draft_over_margin'] = a['fall_draft'] > a['margin']
        a['over_margin'] = a['fall'] > a['margin']
        a['could_change'] = a['fall_voters'] > a['margin']

    dist = {}
    for a in acs:
        g = dist.setdefault(a['district'], {'district': a['district'], 'acs': 0, 'roll_2024': 0, 'draft': 0,
                                            'election': 0, 'women_2024': 0, 'women_election': 0, 'seats_bjp': 0, 'seats_aitc': 0})
        g['acs'] += 1
        for k in ('roll_2024', 'draft', 'election'):
            g[k] += a[k]
        g['women_2024'] += int(r24[a['ac']]['women'])
        g['women_election'] += int(el[a['ac']]['women'])
        g['seats_bjp'] += a['winner'] == 'BJP'
        g['seats_aitc'] += a['winner'] == 'AITC'
    for g in dist.values():
        g['draft_per_100'] = round(100 * (g['roll_2024'] - g['draft']) / g['roll_2024'], 2)
        g['per_100'] = round(100 * (g['roll_2024'] - g['election']) / g['roll_2024'], 2)
        g['women_2024_pct'] = round(100 * g['women_2024'] / g['roll_2024'], 2)
        g['women_fall_pct'] = round(100 * (g['women_2024'] - g['women_election']) / (g['roll_2024'] - g['election']), 2)
    districts = sorted(dist.values(), key=lambda g: -g['per_100'])
    assert len(districts) == 24
    for a in acs:
        a['vs_district'] = round(a['per_100'] - dist[a['district']]['per_100'], 2)

    by_winner = {}
    for a in acs:
        by_winner.setdefault(a['winner'], []).append(a)
    winners = []
    for w, L in sorted(by_winner.items(), key=lambda kv: -len(kv[1])):
        winners.append({'party': w, 'seats': len(L),
                        'per_100': round(100 * sum(a['fall'] for a in L) / sum(a['roll_2024'] for a in L), 2),
                        'vs_district': round(sum(a['vs_district'] for a in L) / len(L), 2),
                        'over_margin': sum(a['over_margin'] for a in L)})

    fall = R24 - ELEC
    women_fall = R24_W - ELEC_W
    lo, hi = min(acs, key=lambda a: a['per_100']), max(acs, key=lambda a: a['per_100'])
    summary = {
        'pn05': dict(p, removed_per_100=round(100 * p['removed'] / p['before'], 2),
                     women_before_pct=round(100 * p['before_women'] / p['before'], 2),
                     women_removed_pct=round(100 * (p['before_women'] - DRAFT_W) / p['removed'], 2),
                     shares={k: round(100 * p[k] / p['removed'], 4) for k in ('dead', 'absent', 'shifted', 'duplicate', 'other')}),
        'adj': AD,
        'roll_2024': R24, 'draft': DRAFT, 'election': ELEC,
        'after_final': ELEC - p['final'],
        'fall_draft': R24 - DRAFT, 'fall': fall,
        'draft_per_100': round(100 * (R24 - DRAFT) / R24, 2),
        'per_100': round(100 * fall / R24, 2),
        'growth_2024_to_oct2025': p['before'] - R24,
        'fall_from_oct2025': p['before'] - ELEC,
        'women_2024_pct': round(100 * R24_W / R24, 2),
        'women_election_pct': round(100 * ELEC_W / ELEC, 2),
        'women_fall_pct': round(100 * women_fall / fall, 2),
        'districts_women_over': sum(g['women_fall_pct'] > g['women_2024_pct'] for g in districts),
        'acs': len(acs), 'districts': len(districts),
        'grew': sum(a['fall'] < 0 for a in acs),
        'rate_min': lo['name'], 'rate_min_v': lo['per_100'], 'rate_max': hi['name'], 'rate_max_v': hi['per_100'],
        'draft_over_margin': sum(a['draft_over_margin'] for a in acs),
        'over_margin': sum(a['over_margin'] for a in acs),
        'could_change': sum(a['could_change'] for a in acs),
        'votes': T('votes'), 'turnout': round(100 * T('votes') / ELEC, 2),
        'seats_2026': {w['party']: w['seats'] for w in winners},
        'winners': winners,
        'rho_rate_margin': round(spearman([a['per_100'] for a in acs], [a['margin'] / a['votes'] for a in acs]), 3),
        'top_districts': [{'district': g['district'], 'per_100': g['per_100']} for g in districts[:5]],
        'low_districts': [{'district': g['district'], 'per_100': g['per_100']} for g in districts[-3:]],
    }

    out = {}
    out['summary.json'] = json.dumps(summary, ensure_ascii=False, indent=1) + '\n'
    out['constituencies.json'] = json.dumps(acs, ensure_ascii=False, separators=(',', ':')) + '\n'
    out['districts.json'] = json.dumps(districts, ensure_ascii=False, separators=(',', ':')) + '\n'
    cols = ['ac', 'name', 'district', 'roll_2024', 'draft', 'election', 'fall_draft', 'fall', 'per_100',
            'women_2024_pct', 'women_election_pct', 'winner', 'runner_up', 'margin', 'votes', 'turnout',
            'over_margin', 'could_change']
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['ac', 'name', 'district', 'roll_2024_ls', 'draft_roll_2025', 'roll_2026_election',
                'fall_to_draft', 'fall_to_election_roll', 'fall_per_100', 'women_pct_2024', 'women_pct_2026',
                'winner_2026', 'runner_up_2026', 'margin_2026', 'votes_2026', 'turnout_2026',
                'fall_over_margin', 'fall_at_turnout_over_margin'])
    for a in acs:
        w.writerow([a[c] for c in cols])
    out['constituencies.csv'] = buf.getvalue()
    dcols = ['district', 'acs', 'roll_2024', 'draft', 'election', 'draft_per_100', 'per_100', 'women_2024_pct', 'women_fall_pct']
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['district', 'acs', 'roll_2024_ls', 'draft_roll_2025', 'roll_2026_election', 'fall_to_draft_per_100',
                'fall_to_election_roll_per_100', 'women_pct_2024', 'women_pct_of_fall'])
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
            sys.exit('STALE, run python3 scripts/build_westbengal.py: ' + ', '.join(stale))
        print('OK: data/westbengal matches its raw tables')
    else:
        print('fall %d of %d (%.2f per 100); women %.2f%% of the fall against %.2f%% of the roll; over margin %d, at turnout %d of %d'
              % (s['fall'], s['roll_2024'], s['per_100'], s['women_fall_pct'], s['women_2024_pct'], s['over_margin'], s['could_change'], s['acs']))
