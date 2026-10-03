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

    def totals(kind):
        A = [a for a in assembly if a['kind'] == kind]
        L = [x for x in ls_seat if x['kind'] == kind]
        return {'states': [a['state'] for a in A], 'assembly_seats': sum(a['seats'] for a in A), 'assembly_over': sum(a['over_margin'] for a in A),
                'ls_seats': len(L), 'ls_over': sum(x['over_margin'] for x in L)}
    data = {'source': SOURCE, 'assembly': assembly, 'removed': totals('removed'), 'fall': totals('fall'), 'ls_seat': ls_seat,
            'even': even, 'even_test': test, 'even_total': {'states': len(even), 'pcs': sum(e['pcs'] for e in even), 'over_margin': sum(e['over_margin'] for e in even)},
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
