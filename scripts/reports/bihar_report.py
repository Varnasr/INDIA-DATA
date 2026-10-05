#!/usr/bin/env python3
"""Bihar SIR 2025: the Word report, in the Sabar Institute's structure.

    python3 scripts/reports/bihar_report.py OUT.docx

Part I analyses the state; Part II gives one chapter per district; a single
section says what the lists show and what they do not; the conclusion sets out
what the Election Commission should do. Every figure is computed from data/bihar/*.json.
"""
import json
import os
import statistics as st
import sys
from collections import defaultdict

import matplotlib.pyplot as plt
from docx.shared import RGBColor

sys.path.insert(0, os.path.dirname(__file__))
from docxkit import Report, indian, lakh, pct, style_axes

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
J = lambda f: json.load(open(os.path.join(ROOT, 'data', 'bihar', f)))
S, A, DS, ID, RS = J('summary.json'), J('constituencies.json'), J('districts.json'), J('identity.json'), J('reasons.json')
FB = J('final.json')
TS = J('tests.json')
IM = J('impact.json')
SW = J('swing.json')['summary']
RB = J('robust.json')
TD, TM = TS['deaths'], TS['marriage']
FT, FM = FB['totals'], FB['margin']
t = S['totals']
C = {'NDA': '#E67E22', 'INDIA': '#1E8449', 'Other': '#8E7CC3', 'red': '#C0392B', 'grey': '#95A5A6', 'blue': '#1F618D', 'pink': '#AF3B6E'}
R = Report(RGBColor(0xB0, 0x3A, 0x2E))

# ------------------------------------------------------------ figures used throughout
withM = [a for a in A if a['margin2025']]
over = [a for a in withM if a['total'] > a['margin2025']]
nda = [a for a in withM if a['al2025'] == 'NDA']
ndaO = [a for a in nda if a['total'] > a['margin2025']]
indiaW = [a for a in withM if a['al2025'] == 'INDIA']
took = [a for a in withM if a['al2020'] == 'INDIA' and a['al2025'] == 'NDA']
tookO = [a for a in took if a['total'] > a['margin2025']]
polled = sum(a['votes2025'] for a in A)
mAll = sum(a['margin2025'] for a in withM)
mNDA = sum(a['margin2025'] for a in nda)
share = lambda a: 100 * a['total'] / a['votes2025']
ratio = lambda a: a['total'] / a['margin2025']
fem = 100 * t['female'] / (t['female'] + t['male'])
per100 = 100 * t['total'] / t['electorate_2025']
cls = t['hindu'] + t['muslim'] + t['unknown']
mlo, mhi = 100 * t['muslim'] / cls, 100 * (t['muslim'] + t['unknown']) / cls
DI = ID['districts']
fOver = [d for d in DI if d['female_share_deleted'] > d['female_share_roll']]
inside = [d for d in DI if d['muslim_share_deleted_low'] <= d['muslim_share_population_2011'] <= d['muslim_share_deleted_high']]
above = [d for d in DI if d['muslim_share_deleted_low'] > d['muslim_share_population_2011'] + 1]
byD = defaultdict(list)
for a in A:
    byD[a['district']].append(a)
rankA = sorted(A, key=lambda a: -a['per_100'])
rankD = sorted(DS, key=lambda d: -d['per_100'])
bysh = sorted(A, key=lambda a: -share(a))
L = S['by_alliance_label']
W = S['within_seat_2024']
cg = ID['caste']['guardian']
G = ['General', 'BC', 'EBC', 'SC', 'ST', 'Muslim']
up = [g for g in G if cg['A']['groups'][g]['ratio_to_survey'] >= 1 and cg['B']['groups'][g]['ratio_to_survey'] >= 1]
down = [g for g in G if cg['A']['groups'][g]['ratio_to_survey'] < 1 and cg['B']['groups'][g]['ratio_to_survey'] < 1]
b200 = sum(a['booths_200'] for a in A)
RK = ['shifted', 'dead', 'absent', 'already_enrolled']
RN = {'dead': 'dead', 'shifted': 'shifted', 'absent': 'absent', 'already_enrolled': 'already enrolled'}
RT, rtot = RS['totals'], RS['total']
rsh = lambda k: 100 * RT[k] / rtot
xsF = sum(RS['by_sex'][k]['F'] - RS['by_sex'][k]['M'] for k in RK)
xsS = RS['by_sex']['shifted']['F'] - RS['by_sex']['shifted']['M']
yS = RS['by_age']['shifted'][0] + RS['by_age']['shifted'][1]
yW = RS['by_age_women']['shifted'][0] + RS['by_age_women']['shifted'][1]
rOver = lambda k: sum(1 for a in withM if a[k] > a['margin2025'])
RD = sorted(RS['districts'], key=lambda d: -d['absent'] / sum(d[k] for k in RK))
dsum = lambda d: sum(d[k] for k in RK)
andj = lambda xs: xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]

# ------------------------------------------------------------ cover and contents
R.cover('Special Intensive Revision 2025', 'Bihar: 69 lakh names struck off',
        'Removals from the electoral roll, booth by booth, set against the margins and the votes that decided each seat',
        [('names removed across both phases', indian(t['total'])),
         ('of the votes polled in the November 2025 election', pct(100 * t['total'] / polled)),
         ('seats where more names were removed than the seat was won by', '%d of %d' % (len(over), len(withM))),
         ('of the removed are women', pct(fem))])
R.h1('Contents')
R.toc()

# ============================================================ PART I
R.h1('Part I: Bihar as a whole')
R.h2('At a glance')
R.stats([(indian(t['total']), 'names removed, both phases'), (pct(100 * t['total'] / polled), 'of all votes polled in 2025'),
         ('%d of %d' % (len(over), len(withM)), 'seats where removals exceed the margin'), (pct(fem), 'of the removed are women')])
R.p('The Special Intensive Revision, a fresh check of every name on the electoral roll, removed %s names from Bihar\'s roll in 2025. '
    '%s came off before the draft roll of 1 August, the first published version of the revised roll, and this report calls that phase 1. '
    '%s more came off before the final roll of 30 September, published after the hearing of claims and objections, and this report calls that phase 2. '
    'That is %s names for every 100 electors on the final roll, across %s polling booths in %d constituencies. '
    'In the Assembly election that followed in November, %s votes were polled. The names removed equal %s of them, one for every %.1f votes cast.'
    % (indian(t['total']), indian(t['p1']), indian(t['p2']), '%.2f' % per100, indian(t['booths']), len(A), indian(polled),
       pct(100 * t['total'] / polled), polled / t['total']))
R.p('A seat\'s winning margin is the number of votes by which its winner beat the runner-up. The removals are larger than the winning margin in %d of %d constituencies. They exceed the combined winning margin of all %d seats, %s, by a factor of %.2f, '
    'and they exceed the combined winning margin of the NDA across the %d seats it won, %s. In %d of the %d seats the NDA took from INDIA, more names were removed than the NDA won by.'
    % (len(over), len(withM), len(withM), lakh(mAll), t['total'] / mAll, len(nda), lakh(mNDA), len(tookO), len(took)))
R.p('Women are %s of those removed and %s of the roll they were removed from, and their share of the removed is higher than their share of the roll in %d of %d districts. '
    'The roll records each elector\'s sex, so this figure is a count and involves no guessing.' % (pct(fem), pct(t['female_share_roll']), len(fOver), len(DI)))

R.h2('Deletions and coverage')
R.p('The booth lists cover every one of Bihar\'s %s polling booths. The table gives each district\'s removals, its removals per 100 electors on the 2025 roll, and its share of the state total. '
    'Counting per 100 electors puts a large district and a small one on the same scale.' % indian(t['booths']))
R.table(['District', 'Seats', 'Names removed', 'Per 100 electors', 'Per booth', 'Share of state'],
        [[d['district'], d['acs'], indian(d['deleted']), '%.2f' % d['per_100'], '%.1f' % d['per_booth'], pct(100 * d['deleted'] / t['total'])] for d in rankD],
        widths=[4.2, 1.5, 3, 2.6, 2.2, 2.6], right={1, 2, 3, 4, 5})
R.p('Removals range from %.1f per 100 electors in %s to %.1f in %s. Among constituencies the range is wider, from %.1f in %s to %.1f in %s.'
    % (rankD[-1]['per_100'], rankD[-1]['district'], rankD[0]['per_100'], rankD[0]['district'], rankA[-1]['per_100'], rankA[-1]['name'], rankA[0]['per_100'], rankA[0]['name']))

R.h2('Deletions against the margins and the votes polled')
R.p('Each constituency\'s removals are compared with two figures from the November 2025 election, the margin by which the seat was won and the votes polled. The comparison makes no claim that these electors would have voted, or how. It measures the size of the revision next to the vote that decided each seat.')
R.stats([('%d of %d' % (len(over), len(withM)), 'seats where removals exceed the margin'), ('%d' % sum(ratio(a) >= 5 for a in withM), 'seats where removals are five times the margin or more'),
         ('%d' % sum(share(a) > 15 for a in A), 'seats where removals exceed 15% of votes polled'), (indian(min(a['margin2025'] for a in withM)), 'smallest margin (%s)' % min(withM, key=lambda a: a['margin2025'])['name'])])
fig, ax = plt.subplots(figsize=(8, 3.2))
cuts, labs = [0, 1, 2, 5, 10, 20, 1e9], ['under 1×', '1–2×', '2–5×', '5–10×', '10–20×', '20× or more']
vals = [sum(cuts[i] <= ratio(a) < cuts[i + 1] for a in withM) for i in range(6)]
ax.bar(labs, vals, color=[C['grey']] + [C['red']] * 5)
for i, v in enumerate(vals):
    ax.text(i, v + 1, str(v), ha='center', fontsize=8)
ax.set_ylabel('Constituencies', fontsize=8)
style_axes(ax, 'Names removed as a multiple of the 2025 winning margin')
R.figure(fig, 'Figure 1. Constituencies by names removed ÷ 2025 winning margin. Grey bars are seats where removals were below the margin.')
top = sorted(withM, key=lambda a: -ratio(a))[:25]
R.table(['Constituency', 'District', 'Won by', 'Margin', 'Names removed', 'Removed − margin', '× margin', '% of votes polled'],
        [['%d %s' % (a['ac'], a['name']), a['district'], '%s (%s)' % (a['win2025'], a['al2025']), indian(a['margin2025']), indian(a['total']),
          '+' + indian(a['total'] - a['margin2025']), '%.1f×' % ratio(a), pct(share(a))] for a in top],
        widths=[3.1, 2.4, 2.6, 1.6, 1.9, 2.1, 1.5, 1.8], right={3, 4, 5, 6, 7}, size=7.5)
R.p('The 25 constituencies where the removals were largest against the margin. Sandesh was won by %s votes and lost %s names.' % (indian(top[0]['margin2025']), indian(top[0]['total'])), italic=True, size=8.5)
fig, ax = plt.subplots(figsize=(8, 5.2))
tp = bysh[:20][::-1]
ax.barh([a['name'] for a in tp], [share(a) for a in tp], color=[C[a['al2025']] for a in tp])
ax.set_xlabel('Names removed as % of votes polled in 2025', fontsize=8)
style_axes(ax, 'The 20 constituencies where the removals were largest against the vote')
R.figure(fig, 'Figure 2. Colour marks the alliance that won the seat in 2025: orange NDA, green INDIA, purple neither.')
ru = [a for a in A if a['total'] > a['runner_up_votes2025']]
R.p('Across Bihar the removals equal %s of the votes polled. In %d constituencies they equal more than 15%%, in %d more than a fifth, and in %s they reach %s. '
    'In %s the names removed exceed the runner-up\'s entire vote. In no constituency do they exceed the total votes polled.'
    % (pct(100 * t['total'] / polled), sum(share(a) > 15 for a in A), sum(share(a) > 20 for a in A), bysh[0]['name'], pct(share(bysh[0])), andj([a['name'] for a in ru]) if ru else 'no constituency'))
fig, ax = plt.subplots(figsize=(8, 3.4))
groups = ['All %d seats' % len(withM), 'The NDA\'s %d wins' % len(nda), '%d seats taken from INDIA' % len(took)]
rem = [t['total'], sum(a['total'] for a in nda), sum(a['total'] for a in took)]
mar = [mAll, mNDA, sum(a['margin2025'] for a in took)]
x = range(3)
ax.bar([i - 0.2 for i in x], [v / 1e5 for v in rem], 0.4, label='Names removed', color=C['red'])
ax.bar([i + 0.2 for i in x], [v / 1e5 for v in mar], 0.4, label='Combined winning margins', color=C['grey'])
ax.set_xticks(list(x), groups)
ax.set_ylabel('Lakh', fontsize=8)
ax.legend(fontsize=8, frameon=False)
style_axes(ax, 'Removals against the combined winning margins')
R.figure(fig, 'Figure 3. In lakh. The combined margin of a group of seats is the sum of each seat\'s margin of victory.')

IS, IB = IM['summary'], IM['breakeven_bands']['lower']
seatlist = lambda k: andj(['%s to %s' % (x['name'], x['runner_up']) for x in IS[k]['seats']]) if IS[k]['seats'] else 'none'
nda_won = sum(1 for x in IM['seats'] if x['alliance_w'] == 'NDA')
kept = [nda_won - IS[k]['to_india'] + IS[k]['to_nda'] for k in IS]
R.h2('Could the removals have changed who won?')
R.p('A name removed is not a vote lost to one side. Some of the removed had died, many would not have voted, and those who would have voted would have split between the parties. '
    'Each seat\'s count here is the names still off the final roll, less those entered as dead, at the seat\'s 2025 turnout. That comes to %s electors across Bihar. That count is low, because the names added after the draft include new electors, so every estimate is also run on all the names removed, with nothing added back (%s).'
    % (indian(IM['voters_lower']), indian(IM['voters_upper'])))
R.p('In %d of %d seats the removed electors who would have voted were enough to change the result had they backed the runner-up. In %d of them a lean of under 55%% would have done it (%s). That share, the part of the removed voters the runner-up would have needed, is called the break-even figure below. In the other %d seats the margin was larger than every removed vote put together. '
    'This is the one figure that needs no assumption about how anyone votes.'
    % (IM['seats_total'] - IB['over_100'], IM['seats_total'], IB['under_55'], andj([x['name'] for x in IM['close']]), IB['over_100']))
c = IM['comp_booth_all']
R.p('The lists do not say how the removed would have voted. Going by how their own polling booths voted in 2024, in the %d seats the two alliances fought each other, those who would have voted lean %s NDA, %s INDIA and %s other parties. '
    'On that reading %d seats would have changed hands counting only the names still off the final roll (%s), and %d counting every name removed (%s).'
    % (IM['seats_nda_vs_india'], pct(c['NDA']), pct(c['INDIA']), pct(c['Other']), IS['booth_lower']['flips'], seatlist('booth_lower'), IS['booth_upper']['flips'], seatlist('booth_upper')))
R.p('Weighting instead by how Muslims and others, or women and men, voted in the %s, %d and %d seats change hands on the high count (%s; %s). On every estimate the NDA keeps between %d and %d of the 243 seats.'
    % (IM['poll_source'], IS['religion_upper']['flips'], IS['sex_upper']['flips'], seatlist('religion_upper'), seatlist('sex_upper'), min(kept), max(kept)))
out = [x for x in IM['seats'] if not x['modelled'] and x['breakeven_lower'] < 55]
if out:
    R.p('Seats where the winner or runner-up is outside the two alliances get the break-even figure only, because the booth results and the poll both count every other party together. Two of those were close. They were %s.'
        % andj(['%s (%s over %s by %s)' % (x['name'], x['winner'], x['runner_up'], indian(x['margin'])) for x in out]))
rows = sorted([x for x in IM['seats'] if x['breakeven_lower'] < 65], key=lambda x: x['breakeven_lower'])
R.table(['Constituency', 'Winner / runner-up', 'Margin', 'Removed who would have voted', 'Share the runner-up needed', 'Booth estimate, net to runner-up'],
        [['%d %s' % (x['ac'], x['name']), '%s / %s' % (x['winner'], x['runner_up']), indian(x['margin']), indian(x['voters_lower']), pct(x['breakeven_lower']),
          '–' if x['booth_lower'] is None else indian(x['booth_lower'])] for x in rows],
        widths=[3.2, 3.0, 1.6, 2.6, 2.4, 2.6], right={2, 3, 4, 5}, size=7.5)
R.p('Each estimate assumes something the lists cannot show. People marked shifted may vote where they now live, people who moved may vote less than their neighbours, and an exit poll carries its own error. None of it can say whether any removal was right.', italic=True, size=8.5)

sg = lambda v: ('+' if v > 0 else '') + '%.1f' % v
R.h2('Did the vote move where more names were removed?')
R.p('Between the 2020 and 2025 Assembly elections the NDA parties gained votes across Bihar. If the removals had taken away more of INDIA\'s voters than the NDA\'s, INDIA\'s share should have fallen most where the most names came off the roll. '
    'The candidate-wise results for both elections were counted with the parties grouped as they stood in 2025: BJP, JD(U), LJP(RV), HAM(S) and RLM for the NDA, and RJD, Congress, the three Left parties, VIP and IIP for INDIA.')
R.table(['Seats', 'Number', 'Removed per 100, average', 'Change in NDA share, points', 'Change in INDIA share, points', 'Change in NDA lead, allowing for 2020', 'Growth in votes cast'],
        [[n, str(x['n']), '%.1f (%.1f–%.1f)' % (x['per_100'], x['lo'], x['hi']), sg(x['d_nda']), sg(x['d_india']), sg(x['d_lead_adj']), sg(x['votes_growth']) + '%']
         for n, x in zip(['Fewest removals', 'Middle', 'Most removals'], SW['thirds'])],
        widths=[2.6, 1.2, 2.8, 2.3, 2.3, 2.5, 2.1], right={1, 2, 3, 4, 5, 6}, size=8)
T, w, w0 = SW['thirds'], SW['within']['lead_adj'], SW['within']['lead']
verdict = ('The results fall short of both, so the vote shows no sign that the removals cost INDIA its voters on a scale large enough to see.' if w['hi'] < SW['scenario_half'] else
           'The whole range lies above zero, so the vote points to the removals having cost INDIA some of its voters.' if w['lo'] > 0 else
           'That range takes in no effect at all and both of these, so the vote cannot tell whether the removals cost INDIA its voters.' if w['hi'] >= SW['scenario_all_against'] else
           'That range takes in no effect at all and the second of these, so the vote cannot tell whether the removals cost INDIA its voters.')
s2 = lambda v: ('+' if v > 0 else '') + '%.2f' % v
R.p('Once each seat\'s 2020 result is allowed for, the NDA\'s lead over INDIA grew by between %.1f and %.1f points in each third, about the same whether a seat lost few names or many. Before that allowance INDIA seemed to lose most where the fewest names were removed (%s points against %s), and part of that is seats giving back in 2025 what they had gained in 2020. Votes cast grew by about the same amount in all three. '
    'Comparing each seat only with other seats in its own district, and allowing for its 2020 result, each extra name removed per 100 electors went with a change of %s points in the NDA\'s lead, most likely somewhere between %s and %s. '
    'Had every removed person who was alive and would have voted voted against the NDA, its lead should have grown by about %.2f points more for each extra name removed per 100 electors, and by about %.2f if three in four of them had. %s '
    'Without the allowance for 2020 the figure is %s (between %s and %s). The two models disagree even on the direction, which is itself a reason to read little into either.'
    % (min(x['d_lead_adj'] for x in T), max(x['d_lead_adj'] for x in T), sg(T[0]['d_india']), sg(T[2]['d_india']), s2(w['slope']), s2(w['lo']), s2(w['hi']),
       SW['scenario_all_against'], SW['scenario_half'], verdict, s2(w0['slope']), s2(w0['lo']), s2(w0['hi'])))
R.p('This asks only whether the removals moved votes between the alliances. It cannot say whether each name was rightly removed, and a voter wrongly removed has lost a vote whichever way it would have gone. A small lean either way would not show, and five years separate the two elections, in which LJP rejoined the NDA, VIP changed sides and Jan Suraaj entered.', italic=True, size=8.5)

R.h2('After the final roll')
R.p('The final roll of 30 September 2025 was published after the claims and objections on the draft were heard. A claim asks for a name to be added or put back, and an objection asks for one to be removed. Format 4B, the Election Commission\'s standard return for a final roll, gives seat by seat and by sex the names added and removed after the draft and the final roll itself. It agrees with the press note of the Chief Electoral Officer, the Commission\'s officer in charge of the state\'s rolls. '
    'The roll of June 2025 is published only as a state total, so a seat\'s roll before the revision is taken here as its draft roll plus the names on its phase 1 list.')
R.stats([(lakh(FT['added']), 'added after the draft'), (lakh(FT['removed_after']), 'removed after the draft'), (pct(FT['made_up_pct']), 'of the draft removals made up'),
         ('%d of %d' % (FM['net'], FM['seats']), 'seats where the net fall exceeds the margin')])
fig, ax = plt.subplots(figsize=(8, 3.2))
als = ['NDA', 'INDIA', 'Other']
xs = range(len(als))
ax.bar([x - 0.27 for x in xs], [FM['won_by_alliance'].get(al, 0) for al in als], width=0.27, color=C['grey'], label='Seats won')
ax.bar(list(xs), [sum(1 for a in over if a['al2025'] == al) for al in als], width=0.27, color=C['NDA'], label='Removed at the draft exceed the margin')
ax.bar([x + 0.27 for x in xs], [FM['net_by_alliance'].get(al, 0) for al in als], width=0.27, color=C['red'], label='Net fall at the final roll exceeds the margin')
ax.set_xticks(list(xs))
ax.set_xticklabels(als, fontsize=8)
ax.set_ylabel('Seats', fontsize=8)
ax.legend(fontsize=7, frameon=False)
style_axes(ax, 'Seats where the removals exceed the 2025 margin, at the draft and at the final roll')
R.figure(fig, 'Figure 4. By the alliance that won the seat in 2025.')
R.p('After the draft, %s names were added on claims and %s removed on objections, so the final roll rose by %s over the draft. That rise equals %s of the %s names removed at the draft. '
    'That rise counts new electors as well as names put back, and the Commission has not said how many of those added had been removed at the draft, so it is the most that can have been put back. '
    'The final roll was %s names smaller than the roll before the revision. This report calls that difference the net fall, and the roll fell in every one of the %d seats.'
    % (indian(FT['added']), indian(FT['removed_after']), indian(FT['net_after']), pct(FT['made_up_pct']), indian(FT['p1']), indian(FT['net_fall_press']), len(FB['seats'])))
R.p('In %d of %d seats the fall that remained at the final roll was still larger than the 2025 winning margin, against %d when the draft removals are counted alone. Of those %d, the NDA won %d, INDIA %d and others %d.'
    % (FM['net'], FM['seats'], FM['total'], FM['net'], FM['net_by_alliance'].get('NDA', 0), FM['net_by_alliance'].get('INDIA', 0), FM['net_by_alliance'].get('Other', 0)))
R.p('Women were %s of the names removed at the draft and %s of those added after it, so their share of the roll fell from %s before the revision to %s on the final roll. '
    'Of the %s names removed after the draft, %s were entered as dead, %s as shifted and %s as repeated, and %s have no reason at all.'
    % (pct(FT['women_share_p1']), pct(FT['women_share_added']), pct(FT['women_share_before']), pct(FT['women_share_final']),
       indian(FT['removed_after']), indian(FT['r_expired']), indian(FT['r_shifted']), indian(FT['r_repeated']), indian(FT['r_unstated'])))

R.h2('Women and the deletions')
R.p('The roll records each elector\'s sex, so women\'s share of the removed needs no estimate. Women are %s of all removals. That is %s women against %s men, %s more women than men. '
    'Their share of the removed exceeds their share of the roll before the revision in %d of %d districts, by up to %.1f points in %s. The roll before the revision is the draft roll by sex plus the names removed at the draft by sex.'
    % (pct(fem), indian(t['female']), indian(t['male']), indian(t['female'] - t['male']), len(fOver), len(DI),
       max(d['female_share_deleted'] - d['female_share_roll'] for d in DI),
       max(DI, key=lambda d: d['female_share_deleted'] - d['female_share_roll'])['district']))
fig, ax = plt.subplots(figsize=(6, 4.4))
ax.scatter([d['female_share_roll'] for d in DI], [d['female_share_deleted'] for d in DI], color=C['pink'], s=18)
ax.plot([45, 65], [45, 65], ls='--', color=C['grey'], lw=1)
ax.set_xlim(46.5, 50)
ax.set_xlabel('Women, % of the district\'s roll before the revision', fontsize=8)
ax.set_ylabel('Women, % of names removed', fontsize=8)
style_axes(ax, 'Every district above the line')
R.figure(fig, 'Figure 5. Each dot is a district. Above the dashed line, women\'s share of the removed exceeds their share of the roll.', width=12)
R.p('Phase 1 removed %s more women than men, and %s of that difference (%s) were entered as shifted. Among those marked shifted aged 18 to 29, %s are women, the pattern that women who move on marriage would produce. '
    'The lists do not show whether any of them were enrolled again where they now live. If they were not, they have lost the vote.'
    % (indian(xsF), indian(xsS), pct(100 * xsS / xsF), pct(100 * yW / yS)))

R.h2('Reasons for removal')
R.p('The phase 1 lists record, against every one of the %s names, the reason the officer entered for removing it. Counted as they were entered, %s were marked permanently shifted (%s), %s dead (%s), %s absent (%s) and %s already enrolled elsewhere (%s). '
    'The counts agree with the booth list in every booth, and the counts of women and men agree with the Chief Electoral Officer\'s phase 1 figures in every constituency. The %s names removed in phase 2 carry no reason in the lists.'
    % (indian(rtot), indian(RT['shifted']), pct(rsh('shifted')), indian(RT['dead']), pct(rsh('dead')), indian(RT['absent']), pct(rsh('absent')),
       indian(RT['already_enrolled']), pct(rsh('already_enrolled')), indian(t['p2'])))
R.p('A reason is what the officer wrote down after a visit, or after failing to find the elector, and nobody checked it. Someone marked shifted may have been away for work when the officer called, and someone marked absent may have been at home. '
    'Of the four, absent rests on the least, because it records only that the officer did not find the elector. Already enrolled is a fair removal only if the other entry is the same person.')
fig, ax = plt.subplots(figsize=(8, 4.2))
bands = RS['bands']; bottom = [0] * len(bands)
RCOL = {'dead': C['grey'], 'shifted': C['blue'], 'absent': C['red'], 'already_enrolled': '#D4AC0D'}
for k in ['dead', 'shifted', 'absent', 'already_enrolled']:
    tot = [sum(RS['by_age'][j][i] for j in RK) for i in range(len(bands))]
    v = [100 * RS['by_age'][k][i] / tot[i] for i in range(len(bands))]
    ax.bar(bands, v, bottom=bottom, color=RCOL[k], label=RN[k].capitalize())
    bottom = [b + x for b, x in zip(bottom, v)]
ax.set_ylabel('% of the removed in each age band', fontsize=8)
ax.legend(fontsize=7, ncol=4, loc='upper center', bbox_to_anchor=(0.5, -0.12), frameon=False)
style_axes(ax, 'Reason entered, by age')
R.figure(fig, 'Figure 6. The reason entered against each phase 1 removal, by the elector\'s age.', width=15)
R.p('Among the removed aged 80 and over, %s were entered as dead, and among those aged 18 to 24, %s. The young were mostly marked shifted or absent.'
    % (pct(100 * RS['by_age']['dead'][-1] / sum(RS['by_age'][k][-1] for k in RK)), pct(100 * RS['by_age']['dead'][0] / sum(RS['by_age'][k][0] for k in RK))))
R.p('Taken alone, the names marked absent exceed the 2025 margin in %d of %d seats, and the names marked already enrolled in %d. The names marked shifted exceed it in %d and the dead in %d. '
    'The absent share is highest in %s.'
    % (rOver('r_absent'), len(withM), rOver('r_enrolled'), rOver('r_shifted'), rOver('r_dead'), andj(['%s (%s)' % (d['district'], pct(100 * d['absent'] / dsum(d))) for d in RD[:3]])))
R.table(['District', 'Phase 1 removed', 'Shifted', 'Dead', 'Absent', 'Already enrolled'],
        [[d['district'], indian(dsum(d))] + [pct(100 * d[k] / dsum(d)) for k in RK] for d in RD],
        widths=[4.2, 2.8, 2.2, 2.2, 2.2, 2.8], right={1, 2, 3, 4, 5})

R.h3('Two reasons, set against the records')
R.p('The %s names entered as dead equal about %.1f years of adult deaths in Bihar. At the Sample Registration System\'s 2024 death rates by age and sex, the population aged 20 and over has about %s deaths a year. '
    'The ages of those entered as dead are close to those of registered deaths. %s of those aged 25 or over were 70 or older, and %s of registered deaths at those ages in 2024. '
    'Their sex does not match. Women are %s of those entered as dead but %s of adult deaths, which means %s women where %s would be expected. Women were only %s of registered deaths at 25 and over in 2024, so women\'s deaths are registered less often and more of them may have stayed on the roll. The other possibility is that more women who are alive were entered as dead. The lists cannot tell the two apart.'
    % (lakh(TD['dead_removed']), TD['years_of_deaths'], lakh(TD['adult_deaths']), pct(TD['over70_share_dead']), pct(TD['over70_share_registered']),
       pct(TD['women_share_dead']), pct(TD['women_share_expected']), lakh(TD['women_dead']), lakh(TD['women_expected']), pct(TD['registered_women_share'])))
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.scatter([d['recent_marriage_pct'] for d in TM['districts']], [d['women_share'] for d in TM['districts']], color=C['blue'], s=18)
for d in TM['districts']:
    if d['district'] in TM['top'][:3]:
        ax.annotate(d['district'], (d['recent_marriage_pct'], d['women_share']), fontsize=7, xytext=(4, 2), textcoords='offset points')
ax.set_xlabel('Women who moved on marriage in the ten years to 2011, % of women', fontsize=8)
ax.set_ylabel('Women, % of those aged 18-29 marked shifted', fontsize=8)
style_axes(ax, 'Young women marked shifted, against marriage movement, by district')
R.figure(fig, 'Figure 7. Each dot is a district. Marriage movement from the 2011 census migration table D-3, counted where women arrived.')
R.p('Among those aged 18 to 29 marked shifted, %s were women and %s men, so women outnumber men by %s. Marriage alone could account for a number that size. In the ten years before the 2011 census, %s women in Bihar moved on marriage, about %s a year, so the excess is about %.2f of one year\'s marriage moves. '
    'The districts do not fit. Where more women had moved on marriage, women were %s share of the young marked shifted (rank correlation %.2f). A rank correlation runs from -1 to 1 and shows whether districts that rank high on one measure also rank high on the other. Marriage can explain how many young women were marked shifted, but it cannot explain where they were. The census counts women in the district they moved to, and its figures are fifteen years old.'
    % (indian(TM['young_shifted_f']), indian(TM['young_shifted_m']), indian(TM['excess']), lakh(TM['recent_marriage']), lakh(TM['recent_marriage_per_year']), TM['excess_years'],
       'a smaller' if TM['rho_share'] <= -0.2 else ('a larger' if TM['rho_share'] >= 0.2 else 'neither a larger nor a smaller'), TM['rho_share']))

R.h2('Religion')
R.p('The roll records no religion, so religion here is guessed from names. The booth lists classify removed names as Hindu or Muslim where the name allows it, and leave %s of names unclassified. '
    'The Muslim share of removals is therefore given as a range. It is %s counting only names classified Muslim, and %s if every unclassified name were Muslim. '
    'Bihar\'s Muslim population was 16.87%% in the 2011 census and 17.70%% in the 2023 caste survey. The census share lies inside the range in %d of %d districts. '
    'In %d districts (%s) the classified Muslim share alone runs more than a point above the census share.'
    % (pct(100 * t['unknown'] / cls), pct(mlo), pct(mhi), len(inside), len(DI), len(above), andj([d['district'] for d in above])))
pin = [d for d in DI if d['muslim_share_deleted_low'] <= d['muslim_share_projected_2025'] <= d['muslim_share_deleted_high']]
pab = [d for d in DI if d['muslim_share_deleted_low'] > d['muslim_share_projected_2025'] + 1]
pmx = max(abs(d['muslim_share_projected_2025'] - d['muslim_share_population_2011']) for d in DI)
R.p('The 2011 census is the last count of religion by district, so each district\'s share is also carried forward to 2025 at the growth rates of its Muslim and total populations between the 2001 and 2011 censuses. '
    'That puts Bihar\'s Muslim share at %s in 2025, close to the caste survey\'s %s, and moves no district by more than %.1f points. '
    'On the 2025 shares the range holds the population share in %d districts, and the classified Muslim share is still more than a point above it in %d districts (%s).'
    % (pct(ID['muslim_projected_2025']), pct(ID['survey_baseline']['Muslim']), pmx, len(pin), len(pab), andj([d['district'] for d in pab])))
fig, ax = plt.subplots(figsize=(8, 7))
dd = sorted(DI, key=lambda d: d['muslim_share_population_2011'])
y = range(len(dd))
ax.hlines(y, [d['muslim_share_deleted_low'] for d in dd], [d['muslim_share_deleted_high'] for d in dd], color='#9CC5CE', lw=5)
ax.scatter([d['muslim_share_population_2011'] for d in dd], y, color='#1C2833', s=14, zorder=3, label='Census 2011')
ax.scatter([d['muslim_share_projected_2025'] for d in dd], y, facecolors='none', edgecolors='#1C2833', s=14, lw=0.9, zorder=4, label='Carried forward to 2025')
ax.set_yticks(list(y), [d['district'] for d in dd], fontsize=7)
ax.set_xlabel('Muslim share, %', fontsize=8)
ax.legend(fontsize=8, frameon=False, loc='lower right')
style_axes(ax, 'Muslim share of removals, as a range, against the census')
R.figure(fig, 'Figure 8. The bar runs from names classified Muslim to all names that could be Muslim, the filled dot is the 2011 census share, and the open dot that share carried forward to 2025.')

R.h2('Caste')
R.p('Caste is not recorded either. It can be read, in part, from the surname of the father or husband listed with each removed elector, and two classifications are used because surnames cross caste lines. '
    'Classification A places %s of removals in a group. The stricter classification B sets aside surnames carried by more than one group and places %s. Only what holds under both is reported here.'
    % (pct(cg['A']['coverage_pct']), pct(cg['B']['coverage_pct'])))
R.table(['Group', 'Survey share 2023', 'Share under A', 'Ratio A', 'Share under B', 'Ratio B'],
        [[g, pct(cg['A']['groups'][g]['survey_share'], 2), pct(cg['A']['groups'][g]['share_of_classified']), '%.2f' % cg['A']['groups'][g]['ratio_to_survey'],
          pct(cg['B']['groups'][g]['share_of_classified']), '%.2f' % cg['B']['groups'][g]['ratio_to_survey']] for g in G],
        widths=[2.6, 2.8, 2.6, 2, 2.6, 2], right={1, 2, 3, 4, 5})
R.p('A ratio above 1 means the group\'s share of the removed exceeds its share of the population. Under both classifications, %s families are removed at or above their population share and %s families below it. The two disagree on Muslim families.'
    % (andj(up), andj(down)))

R.h2('Booths')
hk = list(S['booth_histogram'].keys())
fig, ax = plt.subplots(figsize=(8, 3))
ax.bar(hk, [S['booth_histogram'][k] for k in hk], color=C['blue'])
ax.set_xlabel('Names removed in the booth', fontsize=8)
ax.set_ylabel('Booths', fontsize=8)
style_axes(ax, 'How many names each booth lost')
R.figure(fig, 'Figure 9. Booths by the number of names removed.')
R.p('The typical booth lost %d names. %s booths lost 200 or more each, and %d lost 400 or more. A booth serves on average about %d electors, so 200 removals is a fifth of a booth\'s roll.'
    % (st.median(a['booth_median'] for a in A), indian(b200), S['booth_histogram']['400+'], round(t['electorate_2025'] / t['booths'])))

R.h2('Border districts')
borders = defaultdict(list)
for a in A:
    borders[a['border'] or 'Interior'].append(a)
rate = lambda rows: 100 * sum(a['total'] for a in rows) / sum(a['electorate_2025'] for a in rows)
bd = sorted(borders, key=lambda k: -rate(borders[k]))
R.table(['District neighbours', 'Seats', 'Names removed', 'Per 100 electors', 'Women %'],
        [[k.replace(';', ' + '), len(borders[k]), indian(sum(a['total'] for a in borders[k])), '%.2f' % rate(borders[k]),
          pct(100 * sum(a['t_f'] for a in borders[k]) / sum(a['t_f'] + a['t_m'] for a in borders[k]))] for k in bd],
        widths=[5.5, 1.5, 3, 2.8, 2.2], right={1, 2, 3, 4})
brd = [a for a in A if a['is_border']]
R.p('A constituency counts as a border seat when its district touches Nepal, West Bengal, Jharkhand or Uttar Pradesh. Border seats lost %.2f names per 100 electors, the interior %.2f.' % (rate(brd), rate(borders['Interior'])))

R.h2('The alliances')
R.p('Seats the NDA won in 2020 lost %.2f names per 100 electors, and seats INDIA won lost %.2f. The order stays the same when seats are labelled by the 2024 or 2025 result. Inside the same constituency, booths the NDA led in 2024 lost %.1f more names each than booths INDIA led. '
    'A booth\'s leading party shows how most of its voters voted in 2024 and says nothing about the removed electors, since every booth has voters on both sides. The seats INDIA lost in 2025 did not lose names faster than the seats it kept. '
    'The lists do establish the scale of the removals against the margins, set out above.'
    % (L['2020']['NDA']['per_100'], L['2020']['INDIA']['per_100'], W['pooled_nda_minus_india']))

R.h2('Key insights')
R.bullets([
    '%s names were removed, %s per 100 electors on the final roll, across %s booths.' % (indian(t['total']), '%.2f' % per100, indian(t['booths'])),
    'The names removed equal %s of the votes polled in the November 2025 election, one for every %.1f votes cast.' % (pct(100 * t['total'] / polled), polled / t['total']),
    'The removals were larger than the winning margin in %d of %d seats, five times the margin or more in %d, and ten times or more in %d.' % (len(over), len(withM), sum(ratio(a) >= 5 for a in withM), sum(ratio(a) >= 10 for a in withM)),
    'They were larger than the NDA\'s combined winning margin in its %d wins (%s against %s).' % (len(nda), lakh(t['total']), lakh(mNDA)),
    'In %d of the %d seats the NDA took from INDIA, more names were removed than the NDA won by.' % (len(tookO), len(took)),
    'Women are %s of the removed, and over-represented in %d of %d districts.' % (pct(fem), len(fOver), len(DI)),
    'Muslim names, guessed from names, are %s to %s of removals, against 16.87%% of the population in 2011, and more than a point above the census share in %d districts.' % (pct(mlo), pct(mhi), len(above)),
    'In %d seats the removed who would have voted were enough to change the result, and in %d a lean of just over half among them would have done it.' % (IM['seats_total'] - IM['breakeven_bands']['lower']['over_100'], IM['breakeven_bands']['lower']['under_55']),
    'Women are %s of the names entered as dead, against %s of adult deaths in Bihar.' % (pct(TD['women_share_dead']), pct(TD['women_share_expected'])),
    '%s booths lost 200 names or more each.' % indian(b200),
    'In phase 1, %s of removals were entered as shifted, %s as dead, %s as absent and %s as already enrolled. %s of the %s more women than men removed were marked shifted.' % (pct(rsh('shifted')), pct(rsh('dead')), pct(rsh('absent')), pct(rsh('already_enrolled')), indian(xsS), indian(xsF)),
    'The names marked absent, taken alone, exceed the margin in %d seats, and the names marked already enrolled in %d.' % (rOver('r_absent'), rOver('r_enrolled')),
    'The final roll made up %s of the draft removals, and the fall that remained still exceeded the margin in %d of %d seats. Women were %s of those added after the draft.' % (pct(FT['made_up_pct']), FM['net'], FM['seats'], pct(FT['women_share_added'])),
])

R.h2('How sure are we?')
iv = lambda x: '%s%.2f (%.2f to %.2f)' % ('+' if x['est'] > 0 else '', x['est'], x['lo'], x['hi'])
M_, W_, G_, S_ = RB['margins'], RB['women'], RB['ground'], RB['swing']
R.p('A pattern seen across all seats can weaken or turn round once seats are compared only with seats like them. Each finding was measured again within each district, within each seat, and with Seemanchal left out.')
R.table(['Finding', 'How it was checked', 'Result'], [
    ['More names removed than the winning margin', 'Draft removals: %d of %d seats. Net fall to the final roll: %d of %d.' % (M_['draft'], M_['seats'], M_['net'], M_['seats']), 'Holds on both counts'],
    ['Women removed out of proportion to the roll', 'Districts: %d of %d. Constituencies: %d of %d.' % (W_['districts_over'], W_['districts'], W_['seats_over'], W_['seats']),
     'Holds in every district' if W_['districts_over'] == W_['districts'] else 'Holds in most districts'],
    ['More names removed on NDA ground', 'All seats: %.2f per 100 electors where the NDA won in 2020, %.2f where INDIA won. Seats in the same district: %s per 100. Booths in the same seat: NDA-led booths lost %.1f more names each, and more in %d of %d seats.'
     % (G_['pooled']['nda'], G_['pooled']['india'], iv(G_['within_district']), G_['within_seat']['diff'], G_['within_seat']['nda_higher'], G_['within_seat']['seats']),
     'Holds at every level' if G_['within_district']['lo'] > 0 else 'Holds inside seats. Between seats in the same district the gap is too small to be sure of'],
    ['Seats with more removals swung further to the NDA', 'All seats: %s. Within districts: %s. Within districts, allowing for the 2020 result: %s. Seats the NDA held: %s. Seats INDIA held: %s. Leaving out Seemanchal: %s. Positive in %d of %d districts.'
     % (iv(S_['pooled']), iv(S_['within_district']), iv(S_['within_district_2020']), iv(S_['held_nda_2020']), iv(S_['held_india_2020']), iv(S_['ex_seemanchal']), S_['districts_positive'], S_['districts_compared']),
     'Cannot tell. The answer changes with the comparison']],
    widths=[3.6, 9.0, 3.4], size=8)
R.p('Two findings survive every check. In most constituencies more names were removed than the margin that decided the seat, on the draft count and on the final roll, and women were removed out of proportion in all %d districts and %d of %d constituencies.' % (W_['districts'], W_['seats_over'], W_['seats']))

R.h2('What this shows and what it does not')
R.p('The lists show how many names were removed, where, who the removed were by sex, age and name, and the reason the officer entered against each phase 1 removal, and they allow the removals to be set against the margins and votes that decided each seat. '
    'They do not show whether that reason was true of the person, whether the removal was right, or how the elector voted. Religion and caste are guessed from names, so they are given as ranges or under two classifications. '
    'Votes polled are the turnout on the 2025 roll, within about 1% of a second calculation from each winner\'s vote and share.')

# ============================================================ PART II
R.page_break()
R.h1('Part II: District chapters')
R.p('One chapter for each of Bihar\'s 38 districts, in order of removals per 100 electors. Each gives the district\'s totals and every constituency in it, with the 2025 result.')
for d in rankD:
    rows = sorted(byD[d['district']], key=lambda a: a['ac'])
    di = next(x for x in DI if x['district'] == d['district'])
    dover = [a for a in rows if a['margin2025'] and a['total'] > a['margin2025']]
    dpol = sum(a['votes2025'] for a in rows)
    R.h2('%s' % d['district'])
    R.stats([(indian(d['deleted']), 'names removed'), ('%.2f' % d['per_100'], 'per 100 electors (#%d of 38)' % (rankD.index(d) + 1)),
             (pct(100 * d['deleted'] / dpol), 'of votes polled in 2025'), ('%d of %d' % (len(dover), len(rows)), 'seats: removals exceed margin')])
    heavy = max(rows, key=lambda a: a['per_100'])
    worst = max(rows, key=lambda a: ratio(a) if a['margin2025'] else 0)
    wins = defaultdict(int)
    for a in rows:
        wins[a['al2025']] += 1
    R.p('%s lost %s names across %d constituencies, %.2f for every 100 electors. Women are %s of those removed, against %s of the district\'s roll. '
        'Names classified Muslim are %s to %s of removals, against a 2011 census share of %s. '
        'The constituency with the most removals for its size is %s, at %.2f per 100 electors, and the largest multiple of the margin is in %s, where %s names were removed against a margin of %s. '
        'In 2025 the NDA won %d of the district\'s seats and INDIA %d%s.'
        % (d['district'], indian(d['deleted']), len(rows), d['per_100'], pct(di['female_share_deleted']), pct(di['female_share_roll']),
           pct(di['muslim_share_deleted_low']), pct(di['muslim_share_deleted_high']), pct(di['muslim_share_population_2011']),
           heavy['name'], heavy['per_100'], worst['name'], indian(worst['total']), indian(worst['margin2025']), wins['NDA'], wins['INDIA'],
           (', and %d went to neither alliance' % wins['Other']) if wins['Other'] else ''))
    rd = next(x for x in RS['districts'] if x['district'] == d['district'])
    R.p('Of its %s phase 1 removals, the officers entered %s as shifted, %s as dead, %s as absent and %s as already enrolled.'
        % (indian(dsum(rd)), pct(100 * rd['shifted'] / dsum(rd)), pct(100 * rd['dead'] / dsum(rd)), pct(100 * rd['absent'] / dsum(rd)), pct(100 * rd['already_enrolled'] / dsum(rd))))
    R.table(['Constituency', 'Removed', 'Per 100', 'Women %', 'Won by (2025)', 'Margin', '× margin', '% polled'],
            [['%d %s' % (a['ac'], a['name']), indian(a['total']), '%.2f' % a['per_100'], pct(100 * a['t_f'] / (a['t_f'] + a['t_m'])),
              '%s (%s)' % (a['win2025'], a['al2025']), indian(a['margin2025']), '%.1f×' % ratio(a), pct(share(a))] for a in rows],
            widths=[3.4, 1.8, 1.5, 1.6, 2.8, 1.7, 1.6, 1.6], right={1, 2, 3, 5, 6, 7}, size=7.5)

# ============================================================ CONCLUSION
R.page_break()
R.h1('Conclusion and what the Election Commission should do')
R.p('The revision removed %s names from Bihar\'s roll in the months before an Assembly election. '
    % indian(t['total']) + 
    'The names removed exceed the margin in %d of %d seats and equal %s of all votes polled. Whatever reason was written against each name, in most of the state the roll changed by more than the vote that decided the seat.'
    % (len(over), len(withM), pct(100 * t['total'] / polled)))
R.p('Women carried a larger share of the removals than their share of the roll in every district, and the lists cannot show whether those women were enrolled again where they now live. '
    'Of the four reasons entered, absent rests on the least. %s names were removed as absent, and those alone exceed the margin in %d seats.' % (indian(RT['absent']), rOver('r_absent')))
R.p('What the Election Commission should do:')
R.numbered([
    'Publish the reason for each of the %s phase 2 removals, name by name. The lists give none, and the Format 4B return gives reasons only by constituency, with %s names left without any.' % (indian(t['p2']), indian(FT['r_unstated'])),
    'Publish the basis for each entry marked absent or already enrolled, the %s marked absent and the %s marked already enrolled in phase 1.' % (indian(RT['absent']), indian(RT['already_enrolled'])),
    'Publish every claim and objection filed after the draft roll, booth by booth, with its outcome, and say how many of the %s added had been removed at the draft, so that restorations can be counted against removals.' % lakh(FT['added']),
    'Publish new enrolments by constituency after the revision, so that women removed as shifted can be matched against enrolments where they now live.',
])

R.h1('Method and sources')
R.bullets([
    'Removals by polling booth come from the phase 1 deletion lists that the Chief Electoral Officer, Bihar published with the draft roll of 1 August 2025, for all %s booths.' % indian(t['booths']),
    'Removals by constituency, phase and sex come from the Chief Electoral Officer, Bihar.',
    'The final roll is from Format 4B, the Election Commission\'s return for the final roll of 30 September 2025, as published by the Chief Electoral Officer, Bihar, by constituency and sex. The same return gives the draft roll by sex, which with the phase 1 removals gives women\'s share of the roll before the revision.',
    'Religion and surnames of the removed are counted by booth from the same lists, with no individual records kept.',
    'The reason, sex and age of every phase 1 removal are counted by constituency and booth from the deletion list, with no individual records kept.',
    'Deaths come from the Sample Registration System Statistical Report 2024 and the Civil Registration System 2024, and marriage migration from Census of India 2011, table D-3.',
    'The 2025 Assembly results give the winner, runner-up and turnout for each constituency, checked across two separate tables. Where they disagreed, the figure matching the reported result was used.',
    'The 2024 Lok Sabha result by booth is from Form 20. The other sources are the Census of India 2001 and 2011 for religion by district, the National Family Health Survey 2019-20 for women\'s literacy, schooling and marriage before 18 by district, the Bihar caste-based survey of 2 October 2023, and the Bihar Economic Survey.',
])
R.p('Each booth is counted once. A second program, written separately, recomputes every headline figure from the lists before publication. Votes polled are the turnout applied to the 2025 roll. No name, EPIC number or address is published.')

out = sys.argv[1] if len(sys.argv) > 1 else '/home/user/reports/Bihar_SIR_2025_Report.docx'
R.save(out)
R.save_html(out[:-5] + '.html')
if len(sys.argv) > 2:
    R.save_web(sys.argv[2])  # the page on the site, e.g. bihar/report
print('ok')
