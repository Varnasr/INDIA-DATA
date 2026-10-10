"""Names removed against winning margins, for the SIR in numbers page.

Three comparisons, each kept apart because they rest on different counts:

1. Assembly seats in the four states with seat-level figures. Bihar and Tamil
   Nadu count the names removed; West Bengal and Kerala publish no removals
   below the state, so their count is the fall in the roll. They are totalled
   separately and never added together.
2. The 2024 Lok Sabha seats of the same four states, each seat's count summed
   from its assembly segments (statistical report 34) and set against its
   2024 margin.
3. Every state, with its removals spread evenly over its Lok Sabha seats. No
   state has published removals by Lok Sabha seat, so this is an assumption
   and is labelled as one wherever it appears.

The revision came after the 2024 election. The comparison asks whether the
names removed are as many as the votes that decided a seat, not whether they
decided it.

Writes data/india/margins.json and data/india/margins_ls2024.csv; --check
fails if either is stale.
"""
import csv, io, json, os, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, 'data', *p)
OUT_JSON, OUT_CSV = D('india', 'margins.json'), D('india', 'margins_ls2024.csv')
SOURCE = 'Election Commission of India, 2024 Lok Sabha results and statistical report 34 (assembly segments), through a published compilation of them'
# state, election, page, file, the count used, what it is
STATES = [
    ('Bihar', '2025', 'bihar/results/', 'removed', 'names removed, both phases'),
    ('Tamil Nadu', '2026', 'tamilnadu/elections/', 'removed', 'names removed'),
    ('West Bengal', '2026', 'westbengal/elections/', 'fall', 'fall in the roll from 2024 to the 2026 election'),
    ('Kerala', '2026', 'kerala/elections/', 'fall', 'fall in the roll from January 2025 to the 2026 election'),
]


def seats(state):
    """[(ac, name, count, assembly margin)] for one of the four states."""
    if state == 'Bihar':
        rows = json.load(open(D('bihar', 'final.json')))['seats']
        return [(r['ac'], r['name'], r['total'], r['margin2025']) for r in rows]
    f = {'Tamil Nadu': ('tamilnadu', 'removed'), 'West Bengal': ('westbengal', 'fall'), 'Kerala': ('kerala', 'fall')}[state]
    rows = json.load(open(D(f[0], 'constituencies.json')))
    return [(r['ac'], r['name'], r[f[1]], r['margin']) for r in rows]


# Assembly seats in every state with a constituency table of its latest
# Assembly election. No state but the ones with pages of their own published
# its names left off by constituency, so each state's count is spread over its
# seats in proportion to their electors, an assumption tested below where the
# seats' own counts exist. (state, election, file under data/india/raw/assembly,
# where the figures come from)
ASM = [
    ('Andhra Pradesh', '2024', 'andhrapradesh_2024.csv', 'c'), ('Arunachal Pradesh', '2024', 'arunachal_2024.csv', 'c'),
    ('Chhattisgarh', '2023', 'chhattisgarh_2023.csv', 'e'), ('Goa', '2022', 'goa_2022.csv', 'c'),
    ('Haryana', '2024', 'haryana_2024.csv', 'c'), ('Jharkhand', '2024', 'jharkhand_2024.csv', 'c'),
    ('Karnataka', '2023', 'karnataka_2023.csv', 'c'), ('Madhya Pradesh', '2023', 'madhyapradesh_2023.csv', 'e'),
    ('Maharashtra', '2024', 'maharashtra_2024.csv', 'c'), ('Odisha', '2024', 'odisha_2024.csv', 'c'),
    ('Puducherry', '2026', 'puducherry_2026.csv', 'c'), ('Punjab', '2022', 'punjab_2022.csv', 'c'),
    ('Sikkim', '2024', 'sikkim_2024.csv', 'c'), ('Telangana', '2023', 'telangana_2023.csv', 'e'),
    ('Uttarakhand', '2022', 'uttarakhand_2022.csv', 'c'),
    ('Manipur', '2022', 'manipur_2022.csv', 'c'), ('Meghalaya', '2023', 'meghalaya_2023.csv', 'c'),
    ('Nagaland', '2023', 'nagaland_2023.csv', 'c'), ('Mizoram', '2023', 'mizoram_2023.csv', 'c'),
    ('Uttar Pradesh', '2022', 'uttarpradesh_2022.csv', 'c'),
]
SRC = {'e': "the Election Commission's statistical report", 'c': "a published compilation of the Election Commission's results, checked seat by seat against a second"}
# states with constituency pages of their own: (state, election, file, weight, actual count or None)
OWN = [
    ('Bihar', '2025', ('bihar', 'final.json'), 'before', 'total'), ('Tamil Nadu', '2026', ('tamilnadu', 'constituencies.json'), 'before', 'removed'),
    ('Gujarat', '2022', ('gujarat', 'constituencies.json'), 'before', 'removed'), ('Delhi', '2025', ('delhi', 'constituencies.json'), 'roll_before', 'left_off'),
    ('West Bengal', '2026', ('westbengal', 'constituencies.json'), 'roll_2024', None), ('Kerala', '2026', ('kerala', 'constituencies.json'), 'roll_2025', None),
    ('Rajasthan', '2023', ('rajasthan', 'constituencies.json'), 'roll_2023', None),
]
ODISHA_SIX = {'Malkangiri': 146, 'Sanakhemundi': 130, 'Choudwar': 91, 'Bhubaneswar North': 113, 'Udala': 31, 'Sonepur': 65}


def asm_rows(fname):
    """[(ac, name, electors, margin or None if unopposed)] from a results table."""
    out = []
    for r in csv.DictReader(open(D('india', 'raw', 'assembly', fname), encoding='utf-8')):
        unop = (r.get('unopposed') or '').strip().lower() == 'yes'
        m = None if unop else int(r['margin'])
        if m is not None:
            assert m == int(r['winner_votes']) - int(r['runner_up_votes']), '%s AC %s: margin is not winner less runner-up' % (fname, r['ac'])
        out.append((int(r['ac']), r['ac_name'], int(r['electors']), m))
    acs = [x[0] for x in out]
    assert len(acs) == len(set(acs)) == max(acs), '%s: ACs are not numbered 1 to %d once each' % (fname, max(acs))
    return out


def spread_count(rows, total):
    """Seats whose margin is below the state's count spread over seats by electors."""
    W = sum(e for _, _, e, _ in rows)
    est = {ac: total * e / W for ac, _, e, _ in rows}
    return est, sum(1 for ac, _, _, m in rows if m is not None and m < est[ac])


def spread_assembly(st_rows):
    removed = {s['state']: s['removed'] for s in st_rows if s.get('removed')}
    spread, test = [], []
    for st, year, fname, src in ASM:
        if not os.path.exists(D('india', 'raw', 'assembly', fname)):
            continue
        rows = asm_rows(fname)
        est, over = spread_count(rows, removed[st])
        spread.append({'state': st, 'election': year, 'seats': len(rows), 'contested': sum(1 for r in rows if r[3] is not None),
                       'removed': removed[st], 'over_margin': over, 'own': False, 'source': SRC[src]})
    for st, year, f, wk, ak in OWN:
        data = json.load(open(D(*f)))
        data = data['seats'] if isinstance(data, dict) else data
        mk = 'margin2025' if st == 'Bihar' else 'margin'
        rows = [(int(r['ac']), r['name'], r[wk], r[mk]) for r in data if r.get(wk) and r.get(mk) is not None]
        est, over = spread_count(rows, removed[st])
        spread.append({'state': st, 'election': year, 'seats': len(data), 'contested': len(rows), 'removed': removed[st],
                       'over_margin': over, 'own': True, 'source': 'this site\'s own constituency figures'})
        if ak:
            # the spread tested against the seats' own counts, the same total spread
            act = {int(r['ac']): r[ak] for r in data}
            e2, o2 = spread_count(rows, sum(act[ac] for ac, _, _, _ in rows))
            real = sum(1 for ac, _, _, m in rows if act[ac] > m)
            test.append({'state': st, 'election': year, 'seats': len(rows), 'actual': real, 'spread': o2,
                         'spread_only': sum(1 for ac, _, _, m in rows if m < e2[ac] and not act[ac] > m),
                         'actual_only': sum(1 for ac, _, _, m in rows if act[ac] > m and not m < e2[ac])})
    spread.sort(key=lambda x: -x['over_margin'] / x['contested'])
    # Odisha's six seats with a count in the press, against the spread
    six = []
    if os.path.exists(D('india', 'raw', 'assembly', 'odisha_2024.csv')):
        rows = asm_rows('odisha_2024.csv')
        est, _ = spread_count(rows, removed['Odisha'])
        press = {r['name']: int(r['left_off']) for r in csv.DictReader(open(D('odisha', 'raw', 'district_ac_press_partial.csv'), encoding='utf-8')) if r['level'] == 'ac'}
        assert set(press) == set(ODISHA_SIX), 'Odisha press seats changed: %s' % sorted(press)
        by = {r[0]: r for r in rows}
        for name, ac in ODISHA_SIX.items():
            m = by[ac][3]
            six.append({'name': name, 'ac': ac, 'press': press[name], 'spread': round(est[ac]), 'margin': m,
                        'press_over': press[name] > m, 'spread_over': est[ac] > m})
    return spread, test, six


def build():
    pcs = list(csv.DictReader(open(D('india', 'raw', 'ls2024_pc_results.csv'), encoding='utf-8')))
    acpc = list(csv.DictReader(open(D('india', 'raw', 'ls2024_ac_pc.csv'), encoding='utf-8')))
    assert len(pcs) == 543, '%d Lok Sabha seats, expected 543' % len(pcs)
    for p in pcs:
        if p['margin']:
            assert int(p['margin']) == int(p['margin_published']), '%s %s: margin differs from the published one' % (p['state'], p['pc_name'])
    # Bihar's 40 margins agree with the Wikipedia table already in the repository
    wk = {int(r['Constituency_#']): int(r['Margin']) for r in csv.DictReader(open(D('bihar', 'raw', 'wikipedia_ls2024_pc_results.csv'), encoding='utf-8'))}
    for p in pcs:
        if p['state'] == 'Bihar':
            assert int(p['margin']) == wk[int(p['pc'])], 'Bihar %s: margin differs from the Wikipedia table' % p['pc_name']
    pcmap = {(r['state'], int(r['ac'])): int(r['pc']) for r in acpc}
    pcrow = {(p['state'], int(p['pc'])): p for p in pcs}

    assembly, ls_seat = [], []
    for st, year, page, kind, label in STATES:
        S = seats(st)
        over = sum(1 for _, _, c, m in S if c > m)
        assembly.append({'state': st, 'election': year, 'page': page, 'kind': kind, 'label': label, 'seats': len(S), 'over_margin': over})
        tot = defaultdict(int)
        for ac, name, c, _ in S:
            assert (st, ac) in pcmap, '%s AC %d has no Lok Sabha seat' % (st, ac)
            tot[pcmap[(st, ac)]] += c
        n_pc = sum(1 for k in pcrow if k[0] == st)
        assert len(tot) == n_pc, '%s: %d seats from segments, %d in the results' % (st, len(tot), n_pc)
        for pc, c in sorted(tot.items()):
            p = pcrow[(st, pc)]
            ls_seat.append({'state': st, 'pc': pc, 'name': p['pc_name'].title(), 'kind': kind, 'count': c, 'margin': int(p['margin']),
                            'winner_party': p['winner_party'], 'runner_up_party': p['runner_up_party'], 'over_margin': c > int(p['margin'])})
    # Bihar's assembly count must stay the one its own pages carry
    assert assembly[0]['over_margin'] == json.load(open(D('bihar', 'final.json')))['margin']['total'], 'Bihar seat count differs from bihar/final.json'

    st_rows = json.load(open(D('india', 'states.json')))['states']
    even = []
    for s in st_rows:
        if not s.get('removed'):
            continue
        P = [p for p in pcs if p['state'] == s['state'] and p['margin']]
        if not P:
            continue
        avg = s['removed'] / len([p for p in pcs if p['state'] == s['state']])
        even.append({'state': s['state'], 'phase': s['phase'], 'removed': s['removed'], 'pcs': len(P), 'per_pc': round(avg),
                     'over_margin': sum(1 for p in P if int(p['margin']) < avg)})
    covered = {s['state'] for s in st_rows if s.get('removed')}
    missing = sorted(covered - {e['state'] for e in even})
    assert not missing, 'states with removals but no 2024 results: %s' % missing

    # the even spread tested where seat counts exist: the same comparison two ways.
    # Bihar and Tamil Nadu only, where both use names removed; West Bengal and
    # Kerala have the fall in the roll by seat and the press-note removals for
    # the state, which are different counts
    test = []
    for st in ('Bihar', 'Tamil Nadu'):
        L = [x for x in ls_seat if x['state'] == st]
        e = [x for x in even if x['state'] == st][0]
        test.append({'state': st, 'pcs': len(L), 'actual': sum(x['over_margin'] for x in L), 'even': e['over_margin'],
                     # seats the even spread counts that lost fewer names than their margin, and the reverse
                     'even_only': sum(1 for x in L if x['margin'] < e['per_pc'] and not x['over_margin']),
                     'actual_only': sum(1 for x in L if x['over_margin'] and not x['margin'] < e['per_pc'])})

    spread, spread_test, odisha_six = spread_assembly(st_rows)

    def totals(kind):
        A = [a for a in assembly if a['kind'] == kind]
        L = [x for x in ls_seat if x['kind'] == kind]
        return {'states': [a['state'] for a in A], 'assembly_seats': sum(a['seats'] for a in A), 'assembly_over': sum(a['over_margin'] for a in A),
                'ls_seats': len(L), 'ls_over': sum(x['over_margin'] for x in L)}
    data = {'source': SOURCE, 'assembly': assembly, 'removed': totals('removed'), 'fall': totals('fall'), 'ls_seat': ls_seat,
            'even': even, 'even_test': test, 'spread': spread, 'spread_test': spread_test, 'odisha_six': odisha_six,
            'spread_total': {'states': len(spread), 'seats': sum(x['contested'] for x in spread), 'over_margin': sum(x['over_margin'] for x in spread)}, 'even_total': {'states': len(even), 'pcs': sum(e['pcs'] for e in even), 'over_margin': sum(e['over_margin'] for e in even)},
            'ls_close': {'under_50000': sum(1 for p in pcs if p['margin'] and int(p['margin']) < 50000), 'under_100000': sum(1 for p in pcs if p['margin'] and int(p['margin']) < 100000), 'contested': sum(1 for p in pcs if p['margin'])}}
    j = json.dumps(data, ensure_ascii=False, indent=1) + '\n'
    buf = io.StringIO(); w = csv.writer(buf, lineterminator='\n')
    w.writerow(['state', 'pc', 'lok_sabha_seat', 'count', 'what_is_counted', 'margin_2024', 'winner_party_2024', 'runner_up_party_2024', 'count_exceeds_margin', 'source'])
    for x in ls_seat:
        w.writerow([x['state'], x['pc'], x['name'], x['count'], dict((s[0], s[4]) for s in STATES)[x['state']], x['margin'], x['winner_party'], x['runner_up_party'], 'yes' if x['over_margin'] else 'no', SOURCE])
    return j, buf.getvalue()


def main():
    j, c = build()
    if '--check' in sys.argv:
        for path, text in ((OUT_JSON, j), (OUT_CSV, c)):
            if not os.path.exists(path) or open(path, encoding='utf-8').read() != text:
                sys.exit('%s is stale: run scripts/build_margins.py' % os.path.relpath(path, ROOT))
        print('OK: margins current')
        return
    open(OUT_JSON, 'w', encoding='utf-8').write(j)
    open(OUT_CSV, 'w', encoding='utf-8').write(c)
    print('wrote', os.path.relpath(OUT_JSON, ROOT), os.path.relpath(OUT_CSV, ROOT))


if __name__ == '__main__':
    main()
