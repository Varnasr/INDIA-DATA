#!/usr/bin/env python3
"""Recompute the Bihar figures from the raw files, independently of the build.

    python3 scripts/verify_bihar.py

build_bihar.py writes the JSON the site reads. This script does not import it:
it reads data/bihar/raw again with its own code, recomputes every figure the
pages state as a finding, and compares each with the published JSON. A figure
that disagrees is printed with both values and the run fails.
"""
import csv
import gzip
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'bihar', 'raw')
OUT = os.path.join(ROOT, 'data', 'bihar')
FAIL = []


def pub(name):
    with open(os.path.join(OUT, name), encoding='utf-8') as fh:
        return json.load(fh)


def same(label, mine, theirs, tol=0.0):
    ok = (mine == theirs) if tol == 0 else abs(float(mine) - float(theirs)) <= tol
    print(('  ok    ' if ok else '  FAIL  ') + label + ('' if ok else ': recomputed %r, published %r' % (mine, theirs)))
    if not ok:
        FAIL.append(label)


NDA = {'BJP', 'JD(U)', 'LJP(RV)', 'HAM(S)', 'RLM'}
INDIA = {'RJD', 'INC', 'CPI(ML)L', 'CPI', 'CPI(M)', 'VIP', 'IIP'}
NDA20 = {'BJP', 'JD(U)', 'VIP', 'HAM(S)'}
INDIA20 = {'RJD', 'INC', 'CPI(ML)L', 'CPI', 'CPI(M)'}
NAMES = {'CPI(ML)(L)': 'CPI(ML)L', 'CPIM-L': 'CPI(ML)L', 'CPI(ML)': 'CPI(ML)L', 'CPM': 'CPI(M)',
         'LJPRV': 'LJP(RV)', 'JDU': 'JD(U)', 'HAM': 'HAM(S)'}


def al(p, year=2024):
    if not isinstance(p, str):
        return None
    if year == 2020:
        return 'NDA' if p in NDA20 else 'INDIA' if p in INDIA20 else 'Other'
    return 'NDA' if p in NDA else 'INDIA' if p in INDIA else 'Other'


print('Booth file')
b = pd.read_csv(os.path.join(RAW, 'booths_deletions_ls2024.csv.gz'))
b.columns = ['uid', 'ac', 'booth', 'deleted', 'acname', 'win2020', 'm2020', 'm2020p', 'party', 'votes', 'share']
per = b.groupby('uid').agg(ac=('ac', 'first'), booth=('booth', 'first'), deleted=('deleted', 'first'), n=('deleted', 'nunique'))
same('every booth carries one removal count on all its rows', int((per.n > 1).sum()), 0)
same('booths', len(per), 77837)
same('phase 1 removals in the booth file', int(per.deleted.sum()), 6559626)

S = pub('summary.json')
C = {a['ac']: a for a in pub('constituencies.json')}
same('published booth count', S['totals']['booths'], len(per))
same('published removals by booth, per seat, all 243',
     sum(1 for ac, g in per.groupby('ac') if int(g.deleted.sum()) == sum(r[1] for r in pub('booths/ac_%03d.json' % ac)['rows'])), 243)

print('Constituency totals (CEO table)')
x = pd.read_excel(os.path.join(RAW, 'sir_deletions_by_ac_gender_phase.xlsx'), header=None).iloc[3:]
x = x[pd.to_numeric(x[0], errors='coerce').notna()]
x = x.assign(ac=x[0].astype(int), p1f=x[2].astype(int), p1m=x[3].astype(int), p1=x[4].astype(int),
             p2=x[7].astype(int), tf=x[8].astype(int), tm=x[9].astype(int), tot=x[10].astype(int)).set_index('ac')
same('seats in the CEO table', len(x), 243)
same('both phases, total', int(x.tot.sum()), S['totals']['total'])
same('phase 2', int(x.p2.sum()), S['totals']['p2'])
same('women, both phases', int(x.tf.sum()), S['totals']['female'])
same('men, both phases', int(x.tm.sum()), S['totals']['male'])
same('per-seat totals match the published file', int(sum(C[ac]['total'] == r.tot and C[ac]['p2'] == r.p2 for ac, r in x.iterrows())), 243)
diff = (per.groupby('ac').deleted.sum() - x.p1).abs()
print('        booth file against the CEO phase 1 table: %d seats identical, largest gap %d names (total gap %d)'
      % (int((diff == 0).sum()), int(diff.max()), int(per.deleted.sum() - x.p1.sum())))

print('Sex and religion by booth')
g = pd.read_csv(os.path.join(RAW, 'booth_gender_religion.csv.gz'))
g.columns = ['ac', 'uid', 'sex', 'hindu', 'muslim', 'unknown']
g['n'] = g.hindu + g.muslim + g.unknown
gs = g.groupby('uid').n.sum()
m = per.join(gs.rename('gn'), how='left')
print('        the sex and religion file covers %d of %d booths exactly and %s of phase 1 removals (%d names)'
      % (int((m.gn == m.deleted).sum()), len(m), '{:.2f}%'.format(100 * g.n.sum() / per.deleted.sum()), int(g.n.sum())))
same('Hindu names', int(g.hindu.sum()), S['totals']['hindu'])
same('Muslim names', int(g.muslim.sum()), S['totals']['muslim'])
same('unclassified names', int(g.unknown.sum()), S['totals']['unknown'])

print('2024 result by booth')
amap = pd.read_csv(os.path.join(RAW, 'wikipedia_ac_pc_map.csv'))
amap.columns = ['ac', 'name', 'res', 'district', 'pc', 'electorate']
amap.loc[amap.ac == 90, 'pc'] = 'Vaishali'
pcof = dict(zip(amap.ac, amap.pc))
fixes = S['label_fixes']
b['p'] = b.party.map(lambda p: NAMES.get(p, p) if isinstance(p, str) else p)
b['pc'] = b.ac.map(pcof)
b['p'] = [fixes.get(pc, {}).get(p, {}).get('party', p) for pc, p in zip(b.pc, b.p)]
res = pd.read_csv(os.path.join(RAW, 'wikipedia_ls2024_pc_results.csv'))
# A booth's total poll is votes / share for any party listed in it; the three
# listed parties alone would understate it and inflate every share.
bt = b.dropna(subset=['votes'])
bt = bt[bt.share > 0].assign(t=lambda d: d.votes / (d.share / 100)).groupby('uid').t.median()
ok = 0
for _, r in res.iterrows():
    name = r['Constituency_Name'].replace(' (SC)', '')
    q = b[b.pc == name].drop_duplicates(['uid', 'party'])
    v = q.groupby('p').votes.sum().sort_values(ascending=False)
    total = bt[bt.index.isin(q.uid)].sum()
    top = list(v.index[:2])
    want = [NAMES.get(r['Winner_Party.1'], r['Winner_Party.1']), NAMES.get(r['Runner Up_Party.1'], r['Runner Up_Party.1'])]
    sh = 100 * v.iloc[:2] / total
    good = top == want and abs(sh.iloc[0] - r['Winner_%']) < 1 and abs(sh.iloc[1] - r['Runner Up_%']) < 1
    ok += good
    if not good:
        print('        %s: booth sums give %s at %s, declared %s at %s' % (name, top, [round(s, 2) for s in sh], want, [r['Winner_%'], r['Runner Up_%']]))
same('Lok Sabha seats whose booth sums give the declared winner and runner-up, within a point', ok, 40)
lead = b.dropna(subset=['votes']).drop_duplicates(['uid', 'party']).groupby(['uid', 'p']).votes.sum().reset_index()
lead = lead.sort_values(['uid', 'votes'], ascending=[True, False]).drop_duplicates('uid').set_index('uid').p
odd = lead[lead.isin(['NOTA', 'Unnamed: 7'])]
print('        booths led by NOTA or an unnamed column: %d' % len(odd))
per = per.join(lead.rename('lead'))
pubbooth = {}
for ac in C:
    B = pub('booths/ac_%03d.json' % ac)
    for r in B['rows']:
        pubbooth[(ac, r[0])] = r[2]
same('booth leaders identical to the published booth files', int(sum(pubbooth.get((r.ac, r.booth)) == (r.lead if isinstance(r.lead, str) else None) for r in per.itertuples())), len(per))
per['al'] = per.lead.map(al)

print('Alliances')
ae = pd.read_csv(os.path.join(RAW, 'wikipedia_ae2025_ac_results.csv'))
ae['ac'] = ae['Constituency_No.']
ae = ae.set_index('ac')
el = dict(zip(amap.ac, amap.electorate))
tot = x.tot
seg = per.dropna(subset=['lead']).groupby('ac').apply(lambda d: None)  # placeholder, segments come from summed votes
segv = b.dropna(subset=['votes']).drop_duplicates(['uid', 'party']).groupby(['ac', 'p']).votes.sum().reset_index()
segv = segv.sort_values(['ac', 'votes'], ascending=[True, False]).drop_duplicates('ac').set_index('ac').p
w20 = per.groupby('ac').apply(lambda d: b[b.ac == d.name].win2020.iloc[0])
for year, lab in [('2025', {ac: al(NAMES.get(ae.loc[ac, 'Winner_Party.1'], ae.loc[ac, 'Winner_Party.1'])) for ac in ae.index}),
                  ('2024', {ac: al(segv.get(ac)) for ac in x.index}),
                  ('2020', {ac: al(NAMES.get(w20[ac], w20[ac]), 2020) for ac in x.index})]:
    for side in ['NDA', 'INDIA']:
        acs = [ac for ac in x.index if lab.get(ac) == side]
        v = round(100 * sum(tot[a] for a in acs) / sum(el[a] for a in acs), 2)
        same('per 100 electors, %s seats, %s labels' % (side, year), v, S['by_alliance_label'][year][side]['per_100'])

print('Within the same seat')
d = per[per.al.isin(['NDA', 'INDIA'])].copy()
d['dm'] = d.deleted - d.groupby('ac').deleted.transform('mean')
pooled = round(float(d[d.al == 'NDA'].dm.mean() - d[d.al == 'INDIA'].dm.mean()), 2)
same('NDA-led minus INDIA-led booths, pooled within seat', pooled, S['within_seat_2024']['pooled_nda_minus_india'])
hi = lo = n = 0
for ac, q in d.groupby('ac'):
    c = q.al.value_counts()
    if c.get('NDA', 0) >= 20 and c.get('INDIA', 0) >= 20:
        dd = q[q.al == 'NDA'].deleted.mean() - q[q.al == 'INDIA'].deleted.mean()
        n += 1; hi += dd > 0; lo += dd < 0
same('seats compared', n, S['within_seat_2024']['seats_compared'])
same('seats where NDA-led booths lost more', hi, S['within_seat_2024']['seats_nda_higher'])

print('Intensity')
edges = [0, 50, 100, 150, 200, 250, 300, 400, 10 ** 9]
for i, pb in enumerate(S['intensity']['bins']):
    q = per[(per.deleted >= edges[i]) & (per.deleted < edges[i + 1])]
    c = q.al.value_counts()
    same('booths %s, NDA share' % pb['bin'], round(100 * c.get('NDA', 0) / (c.get('NDA', 0) + c.get('INDIA', 0) + c.get('Other', 0)), 1), pb['nda_pct'])

print('Margins and votes polled')
res = pd.read_csv(os.path.join(RAW, 'ae2025_results.csv')).set_index('ac')
mg = res.winner_votes - res.runner_up_votes
same('margins recomputed as winner minus runner-up', int(sum(mg[ac] == C[ac]['margin2025'] for ac in x.index)), len(x.index))
over = sum(1 for ac in x.index if tot[ac] > mg[ac])
same('seats where removals exceed the 2025 margin', over, sum(1 for a in C.values() if a['margin2025'] is not None and a['total'] > a['margin2025']))
polled = {ac: round(res.turnout_pct[ac] / 100 * el[ac]) for ac in x.index}
same('votes polled, turnout on the 2025 roll', int(sum(polled.values())), sum(a['votes2025'] for a in C.values()))
share = round(100 * sum(tot[ac] for ac in x.index) / sum(polled.values()), 2)
same('removals as a share of all votes polled', share, round(100 * sum(a['total'] for a in C.values()) / sum(a['votes2025'] for a in C.values()), 2))
# The second table's own arithmetic: winner's votes over winner's share.
alt = ae['Winner_Votes'] / (ae['Winner_%'] / 100)
dev = max(abs(polled[ac] / alt[ac] - 1) for ac in x.index)
print('  note  turnout-based votes polled are within %.1f%% of winner votes / winner share in every seat' % (100 * dev))
assert dev < 0.06, 'votes polled disagree with the second source by more than 6%'

print('Women by district')
cen = pd.read_csv(os.path.join(RAW, 'census2011_districts_all_india.csv'))
ID = {dd['district']: dd for dd in pub('identity.json')['districts']}
xd = x.join(amap.set_index('ac').district)
f = xd.groupby('district')[['tf', 'tm']].sum()
same('districts', len(f), 38)
same('women\'s share of removals, every district', int(sum(abs(100 * r.tf / (r.tf + r.tm) - ID[k]['female_share_deleted']) < 0.05 for k, r in f.iterrows() if k in ID)), 38)
same('districts where women are over-represented among the removed',
     int(sum(100 * r.tf / (r.tf + r.tm) > ID[k]['female_share_roll'] for k, r in f.iterrows())), 38)

print('Reasons for removal')
# Read the counts file with the csv module, not pandas, and check it three
# ways: against the published reasons, against the booth file booth by booth,
# and against the official table's phase 1 women and men in every seat.
rs, sx_ac, bb = {}, {}, {}
with gzip.open(os.path.join(RAW, 'reasons_by_booth.csv.gz'), 'rt', encoding='utf-8') as fh:
    for row in csv.DictReader(fh):
        n = int(row['count'])
        rs[row['reason']] = rs.get(row['reason'], 0) + n
        k = (int(row['ac']), row['sex'])
        sx_ac[k] = sx_ac.get(k, 0) + n
        kb = (int(row['ac']), int(row['jan_part']))
        bb[kb] = bb.get(kb, 0) + n
R = pub('reasons.json')
for k in ['dead', 'shifted', 'absent', 'already_enrolled']:
    same('removals entered as ' + k.replace('_', ' '), rs.get(k, 0), R['totals'][k])
same('reasons cover every phase 1 removal', sum(rs.values()), int(x.p1.sum()) + sum(v for (ac, sx_), v in sx_ac.items() if sx_ == 'T'))
same('women by reason add up to the official phase 1 women, every seat', int(sum(sx_ac.get((ac, 'F'), 0) == x.p1f[ac] for ac in x.index)), len(x.index))
same('men by reason add up to the official phase 1 men, every seat', int(sum(sx_ac.get((ac, 'M'), 0) == x.p1m[ac] for ac in x.index)), len(x.index))
booths = {}
for ac in x.index:
    for r_ in pub('booths/ac_%03d.json' % ac)['rows']:
        booths[(ac, r_[0])] = r_[1]
same('booths where the reasons add up to the booth\'s removals', int(sum(bb.get(k, -1) == v for k, v in booths.items())), len(booths))

print('FAIL: %d' % len(FAIL) if FAIL else 'PASS: every recomputed figure matches the published data')
sys.exit(1 if FAIL else 0)
