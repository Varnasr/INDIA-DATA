"""Assertions over the Rajasthan raw tables. Run: python3 check_raw.py"""
import csv, os, sys
H = os.path.dirname(os.path.abspath(__file__))
def rd(f): return list(csv.DictReader(open(os.path.join(H, f))))
ok = []
def check(cond, msg):
    if not cond: sys.exit('FAIL: ' + msg)
    ok.append(msg)

# final roll, 12.03.2026
ac = rd('final_roll_ac.csv'); di = rd('final_roll_district.csv')
check(len(ac) == 200 and sorted(int(r['ac']) for r in ac) == list(range(1, 201)), 'final roll: ACs 1-200 once each')
check(all(int(r['men']) + int(r['women']) == int(r['total']) for r in ac), 'final roll: men + women = total in every AC')
grand = [r for r in di if r['district'] == 'GRAND TOTAL'][0]; di = [r for r in di if r is not grand]
check(len(di) == 41 and len({r['district'] for r in ac}) == 41, 'final roll: 41 districts')
for d in di:
    rows = [r for r in ac if r['district'] == d['district']]
    for k in ('polling_stations', 'men', 'women', 'total'):
        check(sum(int(r[k]) for r in rows) == int(d[k]), f"final roll: {d['district']} {k} equals its published Total row")
for k in ('polling_stations', 'men', 'women', 'total'):
    check(sum(int(r[k]) for r in ac) == int(grand[k]), f'final roll: AC {k} sum equals GRAND TOTAL {grand[k]}')
check(sum(int(d['total']) for d in di) == int(grand['total']), 'final roll: district totals sum to GRAND TOTAL')

# 2023 results
res = rd('results_2023.csv'); cand = rd('results_2023_candidates.csv'); turn = rd('results_2023_turnout.csv')
gt = [r for r in turn if r['ac'] == 'GRAND TOTAL'][0]; turn = {int(r['ac']): r for r in turn if r is not gt}
check(len(res) == 200 and sorted(int(r['ac']) for r in res) == list(range(1, 201)), 'results: ACs 1-200 once each')
for r in res:
    a = int(r['ac']); cs = [c for c in cand if int(c['ac']) == a]
    check(sum(1 for c in cs if c['party'] == 'NOTA') == 1, f'results: AC {a} one NOTA row')
    for k in ('general_votes', 'postal_votes', 'total_votes'):
        check(sum(int(c[k]) for c in cs) == int(turn[a][k]), f'results: AC {a} candidate {k} sum to published TOTAL row')
    check(all(int(c['general_votes']) + int(c['postal_votes']) == int(c['total_votes']) for c in cs), f'results: AC {a} general + postal = total')
    nn = sorted((c for c in cs if c['party'] != 'NOTA'), key=lambda c: -int(c['total_votes']))
    check(nn[0]['candidate'] == r['winner'] and int(nn[0]['total_votes']) == int(r['winner_votes']), f'results: AC {a} winner is top candidate')
    check(int(r['winner_votes']) - int(r['runner_up_votes']) == int(r['margin']) > 0, f'results: AC {a} margin = winner - runner-up > 0')
    check(int(r['total_votes']) == int(turn[a]['total_votes']), f'results: AC {a} total_votes')
for k in ('general_votes', 'postal_votes', 'total_votes'):
    check(sum(int(c[k]) for c in cand) == int(gt[k]), f'results: candidate {k} sum equals GRAND TOTAL {gt[k]}')

# state summary consistency
s = {(r['item'], r['scope']): r for r in rd('sir_state_summary.csv')}
v = lambda i, sc, k='total': float(s[(i, sc)][k])
for sc in ('199 ACs (excl. 193 Anta)', '200 ACs'):
    check(v('draft_roll', sc) + v('draft_roll_additions_to_final', sc) - v('draft_roll_deletions_to_final', sc) == v('final_roll_general', sc), f'summary: draft + additions - deletions = final ({sc})')
    check(v('final_roll_general', sc) + v('final_roll_service', sc) == v('final_roll_incl_service', sc), f'summary: general + service = total ({sc})')
    for i in ('draft_roll', 'final_roll_general', 'final_roll_incl_service'):
        check(v(i, sc, 'men') + v(i, sc, 'women') == v(i, sc), f'summary: {i} men + women = total ({sc})')
check(v('final_roll_general', '200 ACs') == int(grand['total']), 'summary: 12.03.2026 fact sheet final roll equals AC table GRAND TOTAL')
print(f'PASS: {len(ok)} assertions')
