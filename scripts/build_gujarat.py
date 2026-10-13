"""Gujarat: the names left off the SIR draft roll of 19 December 2025, by
assembly constituency and district, with the reason entered, the final roll of
17 February 2026 by district, and the 2022 assembly result.

Reads data/gujarat/raw (see SOURCES.md there; check_raw.py there asserts every
raw table) and writes data/gujarat/summary.json, constituencies.json,
districts.json, final.json, constituencies.csv and districts.csv.

    python3 scripts/build_gujarat.py           # write
    python3 scripts/build_gujarat.py --check   # fail if the output is stale

- The tables are the Chief Electoral Officer's, known only as images of the
  CEO office's printouts published by DeshGujarat. The CEO's site carries
  nothing on the revision, so every page says the tables are the CEO's as
  published in the press.
- The roll before the revision is the roll with respect to 1 October 2025, as
  printed. Nothing is split by sex or age, at any level.
- The final roll is by district only (34 districts, Vav-Tharad printed apart
  from Banaskantha). Here Vav-Tharad is added back into Banaskantha, so that
  the final table lines up exactly with the 33 districts of the draft tables;
  no assignment of constituencies to Vav-Tharad is used. As printed, the final
  roll is 50 electors more than the draft plus the net change, in seven
  districts; the printed final and the printed net are both kept.
- The 2022 result is the Election Commission's own statistical report
  (eci2022_ac.csv: report 10 for the candidates' votes, report 12 for the
  electors and votes polled). The published compilation used before
  (results_2022.csv) is kept as a record and checked against it: the parties
  agree in all 182 seats and the margins in 180 (Viramgam and Wankaner are
  one vote apart). Turnout is votes polled over the 2022 electors, and the
  names left off are set against the margin at that turnout too.
- Ahmedabad's 21 constituencies after the draft (added, deleted, final) are
  from a graphic in Gujarat Samachar (17 February 2026), checked against the
  CEO's draft by seat and final by district: the seats add to the district,
  and draft plus added less deleted is the final in 20 seats; Danilimda is 25
  over, the same 25 the CEO's district row carries.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'gujarat', 'raw')
OUT = os.path.join(ROOT, 'data', 'gujarat')
CHECK = '--check' in sys.argv

REASONS = ('death', 'untraceable_absent', 'shifted', 'already_enrolled', 'other')
# The "Total of State" rows as printed
STATE = (50843436, 1807278, 969662, 4025553, 381470, 189364, 7373327, 43470109)
FINAL_STATE = (43470109, 956121, 395555, 560566, 44030725)
SEATS_2022 = {'BJP': 156, 'INC': 17, 'AAP': 5, 'IND': 3, 'SP': 1}
# The two districts that hold the state's two largest cities
CITY = ('Ahmedabad', 'Surat')
# Dates, from the CEO's tables as published and the Commission's release
DRAFT_DATE, FINAL_DATE, BEFORE_DATE = '2025-12-19', '2026-02-17', '2025-10-01'


def read(name):
    with open(os.path.join(RAW, name), encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def r2(x):
    return round(x, 4)


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
    ac = read('ac.csv')
    res = {int(r['ac']): r for r in read('eci2022_ac.csv')}
    comp = {int(r['ac']): r for r in read('results_2022.csv')}
    off = sorted(n for n in res if res[n]['margin'] != comp[n]['margin'])
    assert all(res[n]['winner_party'] == comp[n]['winner_party'] and res[n]['runner_up_party'] == comp[n]['runner_up_party'] for n in res)
    assert off == [39, 67] and all(abs(int(res[n]['margin']) - int(comp[n]['margin'])) == 1 for n in off), off
    E = lambda k: sum(int(r[k]) for r in res.values())
    assert (E('electors_total'), E('voted_total'), E('valid_votes'), E('nota')) == (49163277, 31879194, 31326370, 501202)
    assert [int(r['ac']) for r in ac] == list(range(1, 183)) and sorted(res) == list(range(1, 183)), 'ACs 1 to 182 once'

    A = []
    for r in ac:
        n = int(r['ac'])
        v = {k: int(r[k]) for k in ('before', 'total', 'draft') + REASONS}
        assert sum(v[k] for k in REASONS) == v['total'], n
        assert v['before'] - v['total'] == v['draft'], n
        e = res[n]
        assert e['ac_name'] == r['ac_name'] or n in (97, 177), n
        wv, rv, margin = int(e['winner_votes']), int(e['runner_up_votes']), int(e['margin'])
        assert wv - rv == margin > 0, n
        assert e['runner_up_party'] != 'NOTA', n
        rem = v['total']
        a = {'ac': n, 'name': r['ac_name'], 'district': r['district'],
             'before': v['before'], 'removed': rem, 'draft': v['draft'],
             'dead': v['death'], 'absent': v['untraceable_absent'], 'shifted': v['shifted'],
             'enrolled_elsewhere': v['already_enrolled'], 'other': v['other'],
             'per_100': r2(100 * rem / v['before']),
             'winner_party': e['winner_party'], 'runner_up_party': e['runner_up_party'], 'margin': margin,
             'electors_2022': int(e['electors_total']), 'turnout_2022': r2(100 * int(e['voted_total']) / int(e['electors_total'])),
             'women_2022_pct': r2(100 * int(e['electors_female']) / int(e['electors_total']))}
        for k in ('dead', 'absent', 'shifted', 'enrolled_elsewhere', 'other'):
            a[k + '_share'] = r2(100 * a[k] / rem)
        # three counts against the margin, from the widest to the narrowest:
        # every name left off; those not entered as dead; and those entered as
        # absent, shifted or other, leaving out the dead and the names already
        # on a roll somewhere else, who keep a vote there
        a['alive'] = rem - a['dead']
        a['not_elsewhere'] = rem - a['dead'] - a['enrolled_elsewhere']
        a['over_margin'] = rem > margin
        a['alive_over_margin'] = a['alive'] > margin
        a['narrow_over_margin'] = a['not_elsewhere'] > margin
        # the names not entered as dead, at the seat's 2022 turnout
        a['at_turnout'] = round(a['alive'] * a['turnout_2022'] / 100)
        a['turnout_over_margin'] = a['at_turnout'] > margin
        A.append(a)

    T = lambda k, L=A: sum(a[k] for a in L)
    assert (T('before'), T('dead'), T('absent'), T('shifted'), T('enrolled_elsewhere'), T('other'), T('removed'), T('draft')) == STATE
    seats = {}
    for a in A:
        seats[a['winner_party']] = seats.get(a['winner_party'], 0) + 1
    assert seats == SEATS_2022, seats

    # districts, in the printout's order (the order of district.csv and of the map)
    order = [r['district'] for r in read('district.csv')]
    prn = {r['district']: r for r in read('district.csv')}
    assert sorted(order) == sorted({a['district'] for a in A}) and len(order) == 33
    D = []
    for i, name in enumerate(order, 1):
        L = [a for a in A if a['district'] == name]
        g = {'district': name, 'id': i, 'acs': len(L), 'city': name in CITY}
        for k in ('before', 'removed', 'draft', 'dead', 'absent', 'shifted', 'enrolled_elsewhere', 'other'):
            g[k] = T(k, L)
        p = prn[name]
        assert (g['before'], g['removed'], g['draft'], g['dead'], g['absent'], g['shifted'], g['enrolled_elsewhere'], g['other']) == tuple(
            int(p[k]) for k in ('before', 'total', 'draft', 'death', 'untraceable_absent', 'shifted', 'already_enrolled', 'other')), name
        g['per_100'] = r2(100 * g['removed'] / g['before'])
        for k in ('dead', 'absent', 'shifted', 'enrolled_elsewhere', 'other'):
            g[k + '_share'] = r2(100 * g[k] / g['removed'])
        g['over_margin'] = sum(a['over_margin'] for a in L)
        D.append(g)
    byd = {g['district']: g for g in D}
    for a in A:
        a['vs_district'] = r2(a['per_100'] - byd[a['district']]['per_100'])

    # the final roll, by district as printed (34), and folded into the 33 of
    # the draft tables by adding Vav-Tharad back into Banaskantha
    fin = read('final_district.csv')
    assert len(fin) == 34
    FP = []
    for r in fin:
        f = {'district': r['district'], 'draft': int(r['draft']), 'added': int(r['addition']), 'deleted': int(r['deletion']),
             'net': int(r['net']), 'final': int(r['final'])}
        assert f['net'] == f['added'] - f['deleted'], r['district']
        f['gap'] = f['final'] - f['draft'] - f['net']
        FP.append(f)
    assert tuple(sum(f[k] for f in FP) for k in ('draft', 'added', 'deleted', 'net', 'final')) == FINAL_STATE
    assert sum(f['gap'] for f in FP) == 50 and sum(1 for f in FP if f['gap']) == 7
    fold = {}
    for f in FP:
        key = 'Banaskantha' if f['district'] == 'Vav-Tharad' else f['district']
        g = fold.setdefault(key, {'draft': 0, 'added': 0, 'deleted': 0, 'net': 0, 'final': 0, 'gap': 0})
        for k in g:
            g[k] += f[k]
    assert sorted(fold) == sorted(order)
    for g in D:
        f = fold[g['district']]
        assert f['draft'] == g['draft'], g['district']
        g['added'], g['deleted'], g['net'], g['final'], g['final_gap'] = f['added'], f['deleted'], f['net'], f['final'], f['gap']
        g['added_per_100'] = r2(100 * f['added'] / g['draft'])
        g['deleted_per_100'] = r2(100 * f['deleted'] / g['draft'])
        g['net_fall'] = g['before'] - g['final']
        g['net_per_100'] = r2(100 * g['net_fall'] / g['before'])
        g['made_up_pct'] = r2(100 * f['net'] / g['removed'])
    vt = [f for f in FP if f['district'] == 'Vav-Tharad'][0]

    # Ahmedabad's 21 seats after the draft, from the press
    ahd = []
    for r in read('ahmedabad_final_ac_press.csv'):
        n = int(r['ac']); a = A[n - 1]
        assert a['district'] == 'Ahmedabad', n
        x = {'ac': n, 'name': a['name'], 'draft': a['draft'], 'added': int(r['added']), 'deleted': int(r['deleted']), 'final': int(r['final'])}
        x['gap'] = x['final'] - x['draft'] - x['added'] + x['deleted']
        x['added_per_100'] = r2(100 * x['added'] / x['draft'])
        x['deleted_per_100'] = r2(100 * x['deleted'] / x['draft'])
        x['removed_per_100'] = a['per_100']
        x['net_fall_per_100'] = r2(100 * (a['before'] - x['final']) / a['before'])
        x['winner_party'] = a['winner_party']
        a.update(final=x['final'], added=x['added'], deleted=x['deleted'])
        ahd.append(x)
    ga = byd['Ahmedabad']
    assert len(ahd) == 21 and sum(x['added'] for x in ahd) == ga['added'] and sum(x['deleted'] for x in ahd) == ga['deleted'] and sum(x['final'] for x in ahd) == ga['final']
    assert [x['ac'] for x in ahd if x['gap']] == [54] and ahd[[x['ac'] for x in ahd].index(54)]['gap'] == ga['final_gap'] == 25

    # by the party that won in 2022, raw and against the seat's own district
    winners = []
    for p in sorted(seats, key=lambda p: -seats[p]):
        L = [a for a in A if a['winner_party'] == p]
        winners.append({'party': p, 'seats': len(L), 'per_100': r2(100 * T('removed', L) / T('before', L)),
                        'vs_district': r2(sum(a['vs_district'] for a in L) / len(L)),
                        'over_margin': sum(a['over_margin'] for a in L)})

    before, rem, draft = T('before'), T('removed'), T('draft')
    city_acs = [a for a in A if a['district'] in CITY]
    rest_acs = [a for a in A if a['district'] not in CITY]

    def block(L, Dl):
        b, r = T('before', L), T('removed', L)
        return {'acs': len(L), 'before': b, 'removed': r, 'per_100': r2(100 * r / b),
                'share_of_roll': r2(100 * b / before), 'share_of_removed': r2(100 * r / rem),
                'shifted_share': r2(100 * T('shifted', L) / r), 'dead_share': r2(100 * T('dead', L) / r),
                'over_margin': sum(a['over_margin'] for a in L),
                'net_per_100': r2(100 * (b - sum(g['final'] for g in Dl)) / b)}

    fs = {k: sum(f[k] for f in FP) for k in ('added', 'deleted', 'net', 'final')}
    byrate = sorted(A, key=lambda a: -a['per_100'])
    close = sorted(A, key=lambda a: a['margin'])
    summary = {
        'before_date': BEFORE_DATE, 'draft_date': DRAFT_DATE, 'final_date': FINAL_DATE,
        'before': before, 'removed': rem, 'draft': draft, 'per_100': r2(100 * rem / before),
        'reasons': {k: T(k) for k in ('dead', 'absent', 'shifted', 'enrolled_elsewhere', 'other')},
        'shares': {k: r2(100 * T(k) / rem) for k in ('dead', 'absent', 'shifted', 'enrolled_elsewhere', 'other')},
        'acs': len(A), 'districts': len(D),
        'rate_max': byrate[0]['name'], 'rate_max_v': byrate[0]['per_100'], 'rate_max_district': byrate[0]['district'],
        'rate_min': byrate[-1]['name'], 'rate_min_v': byrate[-1]['per_100'], 'rate_min_district': byrate[-1]['district'],
        'acs_over_25': sum(a['per_100'] >= 25 for a in A), 'acs_under_10': sum(a['per_100'] < 10 for a in A),
        'over_margin': sum(a['over_margin'] for a in A),
        'alive_over_margin': sum(a['alive_over_margin'] for a in A),
        'narrow_over_margin': sum(a['narrow_over_margin'] for a in A),
        'turnout_over_margin': sum(a['turnout_over_margin'] for a in A),
        'turnout_2022': r2(100 * E('voted_total') / E('electors_total')),
        'margins_source': 'eci',
        'closest': [{'name': a['name'], 'margin': a['margin'], 'removed': a['removed'], 'winner_party': a['winner_party']} for a in close[:3]],
        'closest20_over': sum(a['over_margin'] for a in close[:20]),
        'margin_median': sorted(a['margin'] for a in A)[len(A) // 2 - 1: len(A) // 2 + 1],
        'seats_2022': seats, 'winners': winners,
        'city_names': list(CITY),
        'city': block(city_acs, [g for g in D if g['city']]),
        'rest': block(rest_acs, [g for g in D if not g['city']]),
        'final': fs['final'], 'added': fs['added'], 'deleted': fs['deleted'], 'net': fs['net'],
        'final_gap': fs['final'] - draft - fs['net'], 'final_gap_districts': sum(1 for f in FP if f['gap']),
        'net_fall': before - fs['final'], 'net_per_100': r2(100 * (before - fs['final']) / before),
        'made_up_pct': r2(100 * fs['net'] / rem),
        'net_negative': [g['district'] for g in D if g['net'] < 0],
        'vav_tharad': {k: vt[k] for k in ('draft', 'added', 'deleted', 'net', 'final')},
        'ahmedabad': ahd,
        'ahd_rho_removed_deleted': round(spearman([x['removed_per_100'] for x in ahd], [x['deleted_per_100'] for x in ahd]), 3),
        'ahd_rho_removed_added': round(spearman([x['removed_per_100'] for x in ahd], [x['added_per_100'] for x in ahd]), 3),
        'final_districts_printed': len(FP),
        # across the 182 seats: where more names were left off, were more of
        # them entered as shifted, and fewer as dead?
        'rho_rate_shifted': round(spearman([a['per_100'] for a in A], [a['shifted_share'] for a in A]), 3),
        'rho_rate_dead': round(spearman([a['per_100'] for a in A], [a['dead_share'] for a in A]), 3),
        'rho_rate_margin': round(spearman([a['per_100'] for a in A], [a['margin'] for a in A]), 3),
    }
    summary['margin_median'] = round(sum(summary['margin_median']) / 2)

    out = {}
    out['summary.json'] = json.dumps(summary, ensure_ascii=False, indent=1) + '\n'
    out['constituencies.json'] = json.dumps(A, ensure_ascii=False, separators=(',', ':')) + '\n'
    out['districts.json'] = json.dumps(sorted(D, key=lambda g: -g['per_100']), ensure_ascii=False, separators=(',', ':')) + '\n'
    out['final.json'] = json.dumps(FP, ensure_ascii=False, separators=(',', ':')) + '\n'
    cols = ['ac', 'name', 'district', 'before', 'removed', 'per_100', 'dead', 'absent', 'shifted', 'enrolled_elsewhere', 'other',
            'draft', 'vs_district', 'winner_party', 'runner_up_party', 'margin', 'over_margin']
    dcols = ['district', 'acs', 'before', 'removed', 'per_100', 'dead', 'absent', 'shifted', 'enrolled_elsewhere', 'other',
             'draft', 'added', 'deleted', 'net', 'final', 'final_gap', 'net_per_100']
    for name, rows, cs in (('constituencies.csv', A, cols), ('districts.csv', D, dcols)):
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator='\n')
        w.writerow(cs)
        for x in rows:
            w.writerow([x[c] for c in cs])
        out[name] = buf.getvalue()

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
            sys.exit('STALE, run python3 scripts/build_gujarat.py: ' + ', '.join(stale))
        print('OK: data/gujarat matches its raw tables')
    else:
        print('%d left off of %d (%.2f per 100); over the 2022 margin in %d of %d (%d not dead, %d narrow)'
              % (s['removed'], s['before'], s['per_100'], s['over_margin'], s['acs'], s['alive_over_margin'], s['narrow_over_margin']))