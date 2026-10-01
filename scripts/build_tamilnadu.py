"""Tamil Nadu: the draft-roll removals by constituency, the final roll, and
the 2026 assembly result, joined on the constituency number.

Reads data/tamilnadu/raw (see SOURCES.md there) and writes
data/tamilnadu/summary.json, constituencies.json, constituencies.csv and
districts.csv.

    python3 scripts/build_tamilnadu.py           # write
    python3 scripts/build_tamilnadu.py --check   # fail if the output is stale

The roll before the revision is the draft roll plus the names left off it,
because the CEO publishes the removals against the draft and no constituency
table of the roll of 27 October 2025. The CEO publishes no split of the
removals by sex or age, so there is none here.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'tamilnadu', 'raw')
OUT = os.path.join(ROOT, 'data', 'tamilnadu')
CHECK = '--check' in sys.argv

# Party names as ECI prints them in 2026, and as the 2021 file abbreviates
# them, to one short label.
PARTY = {
    'Tamilaga Vettri Kazhagam': 'TVK', 'Dravida Munnetra Kazhagam': 'DMK',
    'All India Anna Dravida Munnetra Kazhagam': 'AIADMK', 'Indian National Congress': 'INC',
    'Pattali Makkal Katchi': 'PMK', 'Indian Union Muslim League': 'IUML',
    'Communist Party of India': 'CPI', 'Communist Party of India (Marxist)': 'CPI(M)',
    'Viduthalai Chiruthaigal Katchi': 'VCK', 'Amma Makkal Munnettra Kazagam': 'AMMK',
    'Bharatiya Janata Party': 'BJP', 'Desiya Murpokku Dravida Kazhagam': 'DMDK',
    'Naam Tamilar Katchi': 'NTK', 'Independent': 'IND',
    'ADMK': 'AIADMK', 'CPM': 'CPI(M)',
}
# Expected totals, from the CEO's own Total rows.
REMOVED = (2694672, 6644881, 398278, 9737831)
DRAFT, FINAL = 54376756, 56707380


def rows(name):
    with open(os.path.join(RAW, name), encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def ints(r, *keys):
    return [int(r[k]) for k in keys]


def party(name):
    return PARTY.get(name, name)


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
    asd = {int(r['ac']): r for r in rows('asd_ac.csv')}
    draft = {int(r['ac']): r for r in rows('draft_roll_ac.csv')}
    final = {int(r['ac']): r for r in rows('final_roll_ac.csv')}
    r26 = {int(r['ac']): r for r in rows('results_2026.csv')}
    r21 = {int(r['ac']): r for r in rows('results_2021.csv')}
    for t in (asd, draft, final, r26, r21):
        assert sorted(t) == list(range(1, 235)), 'every table has ACs 1 to 234 once'

    acs = []
    for n in range(1, 235):
        a, d, f, e, p = asd[n], draft[n], final[n], r26[n], r21[n]
        assert d['ac_name'] == f['ac_name'] and d['district'] == f['district'], n
        dead, sh, mult, rem = ints(a, 'dead', 'shifted_absent', 'multiple', 'total')
        assert dead + sh + mult == rem, n
        dm, dw, dt, dtot = ints(d, 'men', 'women', 'third', 'total')
        fm, fw, ft, ftot = ints(f, 'men', 'women', 'third', 'total')
        assert dm + dw + dt == dtot and fm + fw + ft == ftot, n
        wv, rv, margin, votes = ints(e, 'winner_votes', 'runner_up_votes', 'margin', 'total_votes')
        assert wv - rv == margin > 0, n
        wv21, rv21, m21 = ints(p, 'winner_votes', 'runner_up_votes', 'margin')
        assert wv21 - rv21 == m21 > 0, n
        before = dtot + rem
        turnout = votes / ftot
        acs.append({
            'ac': n, 'name': d['ac_name'], 'district': d['district'],
            'before': before, 'removed': rem, 'dead': dead, 'shifted_absent': sh, 'multiple': mult,
            'per_100': round(100 * rem / before, 2),
            'draft': dtot, 'draft_women': dw, 'final': ftot, 'final_women': fw,
            'added_net': ftot - dtot, 'net_fall': before - ftot,
            'net_per_100': round(100 * (before - ftot) / before, 2),
            'winner': party(e['winner_party']), 'runner_up': party(e['runner_up_party']),
            'margin': margin, 'votes': votes, 'turnout': round(100 * turnout, 2),
            # living removed names, voting at the seat's own turnout
            'removed_voters': round((rem - dead) * turnout),
            'winner_2021': party(p['winner_party']), 'margin_2021': m21, 'electors_2021': int(p['electors']),
        })
    T = lambda k: sum(a[k] for a in acs)
    assert (T('dead'), T('shifted_absent'), T('multiple'), T('removed')) == REMOVED
    assert T('draft') == DRAFT and T('final') == FINAL

    for a in acs:
        a['over_margin'] = a['removed'] > a['margin']
        a['net_over_margin'] = a['net_fall'] > a['margin']
        a['could_change'] = a['removed_voters'] > a['margin']
        a['changed_hands'] = a['winner'] != a['winner_2021']

    # districts
    dist = {}
    for a in acs:
        g = dist.setdefault(a['district'], {'district': a['district'], 'acs': 0, 'before': 0, 'removed': 0, 'dead': 0,
                                            'shifted_absent': 0, 'multiple': 0, 'final': 0})
        g['acs'] += 1
        for k in ('before', 'removed', 'dead', 'shifted_absent', 'multiple', 'final'):
            g[k] += a[k]
    for g in dist.values():
        g['per_100'] = round(100 * g['removed'] / g['before'], 2)
        g['net_per_100'] = round(100 * (g['before'] - g['final']) / g['before'], 2)
        g['shifted_share'] = round(100 * g['shifted_absent'] / g['removed'], 2)
        g['dead_share'] = round(100 * g['dead'] / g['removed'], 2)
    districts = sorted(dist.values(), key=lambda g: -g['per_100'])
    assert len(districts) == 38

    # each seat against its own district, so that Chennai does not decide
    # every comparison between parties
    for a in acs:
        g = dist[a['district']]
        a['vs_district'] = round(a['per_100'] - g['per_100'], 2)
    by_winner = {}
    for a in acs:
        by_winner.setdefault(a['winner'], []).append(a)
    winners = []
    for w, L in sorted(by_winner.items(), key=lambda kv: -len(kv[1])):
        rem, bef = sum(a['removed'] for a in L), sum(a['before'] for a in L)
        winners.append({'party': w, 'seats': len(L), 'per_100': round(100 * rem / bef, 2),
                        'vs_district': round(sum(a['vs_district'] for a in L) / len(L), 2)})

    before, rem, fin = T('before'), T('removed'), T('final')
    chennai = dist['Chennai']
    summary = {
        'before': before, 'removed': rem, 'draft': T('draft'), 'final': fin,
        'per_100': round(100 * rem / before, 2),
        'dead': T('dead'), 'shifted_absent': T('shifted_absent'), 'multiple': T('multiple'),
        'shares': {k: round(100 * T(k) / rem, 2) for k in ('dead', 'shifted_absent', 'multiple')},
        'added_net': fin - T('draft'), 'net_fall': before - fin,
        'net_per_100': round(100 * (before - fin) / before, 2),
        'made_up_pct': round(100 * (fin - T('draft')) / rem, 2),
        'women_draft_pct': round(100 * T('draft_women') / T('draft'), 2),
        'women_final_pct': round(100 * T('final_women') / fin, 2),
        'acs': len(acs), 'districts': len(districts),
        'rate_min': min(acs, key=lambda a: a['per_100'])['name'], 'rate_min_v': min(a['per_100'] for a in acs),
        'rate_max': max(acs, key=lambda a: a['per_100'])['name'], 'rate_max_v': max(a['per_100'] for a in acs),
        'over_margin': sum(a['over_margin'] for a in acs),
        'net_over_margin': sum(a['net_over_margin'] for a in acs),
        'could_change': sum(a['could_change'] for a in acs),
        'changed_hands': sum(a['changed_hands'] for a in acs),
        'votes': T('votes'), 'turnout': round(100 * T('votes') / fin, 2),
        'electors_2021': T('electors_2021'),
        'seats_2026': {w['party']: w['seats'] for w in winners},
        'winners': winners,
        'rho_rate_shifted': round(spearman([a['per_100'] for a in acs],
                                           [a['shifted_absent'] / a['removed'] for a in acs]), 3),
        'rho_rate_margin': round(spearman([a['per_100'] for a in acs],
                                          [a['margin'] / a['votes'] for a in acs]), 3),
        'chennai': {k: chennai[k] for k in ('acs', 'before', 'removed', 'per_100', 'net_per_100',
                                            'shifted_share', 'dead_share')},
        'chennai_share_of_removed': round(100 * chennai['removed'] / rem, 2),
        'chennai_share_of_roll': round(100 * chennai['before'] / before, 2),
        'top_districts': [g['district'] for g in districts[:5]],
    }
    summary['chennai']['over_margin'] = sum(a['over_margin'] for a in acs if a['district'] == 'Chennai')

    out = {}
    out['summary.json'] = json.dumps(summary, ensure_ascii=False, indent=1) + '\n'
    out['constituencies.json'] = json.dumps(acs, ensure_ascii=False, separators=(',', ':')) + '\n'
    out['districts.json'] = json.dumps(districts, ensure_ascii=False, separators=(',', ':')) + '\n'
    cols = ['ac', 'name', 'district', 'before', 'removed', 'dead', 'shifted_absent', 'multiple', 'per_100',
            'draft', 'final', 'net_fall', 'net_per_100', 'winner', 'runner_up', 'margin', 'votes', 'turnout',
            'removed_voters', 'over_margin', 'net_over_margin', 'could_change', 'winner_2021', 'margin_2021']
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(cols)
    for a in acs:
        w.writerow([a[c] for c in cols])
    out['constituencies.csv'] = buf.getvalue()
    dcols = ['district', 'acs', 'before', 'removed', 'dead', 'shifted_absent', 'multiple', 'per_100',
             'final', 'net_per_100']
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(dcols)
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
            sys.exit('STALE, run python3 scripts/build_tamilnadu.py: ' + ', '.join(stale))
        print('OK: data/tamilnadu matches its raw tables')
    else:
        print('%d removed of %d (%.2f per 100); over margin %d, net over margin %d, could change %d of %d'
              % (s['removed'], s['before'], s['per_100'], s['over_margin'], s['net_over_margin'],
                 s['could_change'], s['acs']))
