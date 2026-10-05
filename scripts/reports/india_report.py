#!/usr/bin/env python3
"""The All India report: the reasons recorded for SIR removals, state by state.

    python3 scripts/reports/india_report.py OUT.docx [india/report]

It sets the reasons recorded for SIR removals side by side for every state and
union territory, with the split by sex where states published one and the
state-level correlations. Every figure is computed from data/india.
"""
import json
import os
import sys

import matplotlib.pyplot as plt
from docx.shared import RGBColor

sys.path.insert(0, os.path.dirname(__file__))
from docxkit import Report, indian, lakh, pct, style_axes

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
J = lambda *p: json.load(open(os.path.join(ROOT, 'data', *p)))
N = J('india', 'states.json')
T, S, P = N['total'], N['states'], N['by_phase']
RK = ['dead', 'shifted_absent_other', 'duplicate']
RN = {'dead': 'Dead', 'shifted_absent_other': 'Shifted, absent or other', 'duplicate': 'Enrolled more than once'}
C = {'dead': '#95A5A6', 'shifted_absent_other': '#1F618D', 'duplicate': '#D4AC0D', 'unsplit': '#8E7CC3', 'red': '#C0392B'}
crore = lambda x: '%.2f crore' % (x / 1e7)
andj = lambda xs: xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]
R = Report(RGBColor(0x1F, 0x4E, 0x79))

has = [s for s in S if s['removed'] is not None]
split = [s for s in S if s['shares']]
rated = sorted([s for s in has if s['per_100'] is not None], key=lambda s: -s['per_100'])
big = sorted([s for s in split if s['removed'] >= 1e6], key=lambda s: -s['shares']['shifted_absent_other'])
hiDead = max(big, key=lambda s: s['shares']['dead'])
hiDup = max(big, key=lambda s: s['shares']['duplicate'])
rounded = [s['state'] for s in S if s['figures'] == 'rounded']
short = [s['state'] for s in S if s['split'] == 'short']
none = [s['state'] for s in S if s['split'] == 'none']
AD = N['after_draft']

# ------------------------------------------------------------ cover
R.cover('Special Intensive Revision 2025-26', 'India: %s names left off the draft rolls' % crore(T['removed']),
        'The reasons recorded for removals in each state, who was removed by sex where states published it, and what goes with the removal rate',
        [('names left off the draft rolls in %d states and union territories' % T['states'], indian(T['removed'])),
         ('of those split by reason entered as shifted, absent or other', pct(T['shares']['shifted_absent_other'])),
         ('entered as dead', pct(T['shares']['dead'])),
         ('entered as enrolled more than once', pct(T['shares']['duplicate']))])
R.h1('Contents')
R.toc()

# ============================================================ PART I
ADU0, FN0, GG0 = N['adults'], N['final'], N['gender']
bigS = sorted(big, key=lambda x: x['shares']['shifted_absent_other'])
rho0 = ADU0['rho_rate']
R.h2('In short')
R.numbered([
    'Before the revision, the rolls already held %s of adults in the %d states with population projections. Only %d of those states had more names on the roll than adults.'
    % (pct(100 * ADU0['roll_total'] / ADU0['adults_total']), ADU0['states'], len(ADU0['over_100'])),
    'The revision still left %s names off the draft rolls, the first published versions of the revised rolls, in %d states. That is %.1f of every 100 electors, and the draft rolls now hold %s of adults. %s'
    % (crore(T['removed']), T['states'], T['per_100'], pct(100 * ADU0['draft_total'] / ADU0['adults_total']),
       'States whose rolls were most over-full did not cut more.' if abs(rho0) < 0.2 else ('States whose rolls were most over-full did cut more.' if rho0 > 0 else 'States whose rolls were most over-full cut less.')),
    'The names removed were enough to decide most seats where they can be counted, because they outnumber the winning margin, the votes by which the winner beat the runner-up. In Bihar and Tamil Nadu they were more than the winning margin in %d of %d assembly seats, and in West Bengal and Kerala the fall in the roll was more than the margin in %d of %d.'
    % (J('india', 'margins.json')['removed']['assembly_over'], J('india', 'margins.json')['removed']['assembly_seats'], J('india', 'margins.json')['fall']['assembly_over'], J('india', 'margins.json')['fall']['assembly_seats']),
    'Of the names removed with a reason given, only %s were entered as dead. The rest are names an officer marked as moved, missing or on the roll twice.' % pct(T['shares']['dead']),
    'The same rules gave very different results. %s removed %.1f of every 100 electors and %s %.1f. Among the big states, the share marked moved or not found runs from %s in %s to %s in %s.'
    % (rated[0]['state'], rated[0]['per_100'], rated[-1]['state'], rated[-1]['per_100'], pct(bigS[0]['shares']['shifted_absent_other']), bigS[0]['state'],
       pct(bigS[-1]['shares']['shifted_absent_other']), bigS[-1]['state']),
    'Women were more likely to be removed. In %d of the %d states that report by sex, women are a bigger share of the names removed than of the roll.'
    % (len([g for g in GG0 if g['gap'] > 1]), len(GG0)),
    'Little has come back. In the %d states with a final roll, the roll published after claims and objections are heard, the rolls grew back by at most %s of what was cut, and that rise includes new voters.' % (FN0['states'], pct(FN0['made_up_pct'])),
])
R.p('Two limits. The adult figures count people where they live, so states that draw migrants look short of electors who are registered in their home states. '
    'And these figures show what happened. They cannot show why it happened, or that anyone meant it to.', italic=True)

R.h2('At a glance')
R.stats([(crore(T['removed']), 'left off the draft rolls'), (pct(T['shares']['shifted_absent_other']), 'shifted, absent or other'),
         (pct(T['shares']['dead']), 'dead'), ('%.1f' % T['per_100'], 'removed per 100 electors')])
R.p('The Special Intensive Revision is a fresh check of every name on the electoral rolls, and it has been carried out in three phases. Bihar came first, in 2025, then twelve states and union territories from November 2025, and eighteen more in 2026. '
    'In the %d that have published a draft roll, %s electors on the rolls before the revision were not carried onto it. That is %.1f for every 100. Tripura, the last, publishes its draft in December.'
    % (T['states'], indian(T['removed']), T['per_100']))
R.p('Every state gave a reason for most of its removals. Of the %s names it split by reason, %s (%s) were entered as dead, %s (%s) as shifted, absent or other, and %s (%s) as enrolled more than once. '
    'Deaths are about one in five. The other four in five rest on an officer\'s entry that the elector was not where the roll placed them, or was on it twice.'
    % (crore(T['removed'] - T['unsplit']), crore(T['dead']), pct(T['shares']['dead']), crore(T['shifted_absent_other']), pct(T['shares']['shifted_absent_other']),
       crore(T['duplicate']), pct(T['shares']['duplicate'])))
R.p('A reason is what an officer wrote down after a visit, or after failing to find the elector, and nobody has checked it. The figures cannot say how many entries were wrong.')

R.h2('State by state, on one map')
BIN, FILL = [8, 12, 16, 20], ['#deebf7', '#9ecae1', '#2878b3', '#1c5f96', '#08306b']
byS = {x['state']: x for x in S}
fig, ax = plt.subplots(figsize=(6.2, 5.6))
for t in N['tiles']:
    x = byS.get(t['state'])
    v = x['per_100'] if x else None
    b = sum(v >= c for c in BIN) if v is not None else None
    f = FILL[b] if b is not None else '#F2F3F4'
    ax.add_patch(plt.Rectangle((t['col'], -t['row']), 0.92, 0.92, facecolor=f, edgecolor='#95A5A6' if b is None else f, linestyle='--' if b is None else '-', lw=0.8))
    ink = '#1C2833' if b is None or b < 2 else 'white'
    ax.text(t['col'] + 0.46, -t['row'] + 0.58, t['code'], ha='center', va='center', fontsize=8, fontweight='bold', color=ink)
    ax.text(t['col'] + 0.46, -t['row'] + 0.30, '%.1f' % v if v is not None else '–', ha='center', va='center', fontsize=7, color=ink)
ax.set_xlim(-0.1, 9)
ax.set_ylim(-7.1, 1)
ax.set_aspect('equal')
ax.axis('off')
labs = ['under 8', '8 to 12', '12 to 16', '16 to 20', '20 or more']
for i, (l, f) in enumerate(zip(labs, FILL)):
    ax.add_patch(plt.Rectangle((5.2, -5.2 - i * 0.42), 0.3, 0.3, facecolor=f))
    ax.text(5.6, -5.05 - i * 0.42, l, va='center', fontsize=7)
ax.set_title('Removed per 100 electors', fontsize=9, fontweight='bold', loc='left')
R.figure(fig, 'Figure 1. One tile per state or union territory, placed roughly where it lies, so the tiles show no borders. Grey tiles are states not in the revision (Jammu and Kashmir, Ladakh, Himachal Pradesh, Assam), with no draft roll yet (Tripura), or with no exact roll from before it (Chandigarh).', width=13)

R.h2('The rolls against the adult population')
ADU = N['adults']
adS = sorted([x for x in S if x.get('roll_adult_pct') is not None], key=lambda x: -x['roll_adult_pct'])
fig, ax = plt.subplots(figsize=(8, 4.2))
xs = range(len(adS))
ax.bar([i - 0.2 for i in xs], [x['roll_adult_pct'] for x in adS], width=0.4, color=C['dead'], label='Roll before the revision')
ax.bar([i + 0.2 for i in xs], [x['draft_adult_pct'] for x in adS], width=0.4, color=C['shifted_absent_other'], label='Draft roll')
ax.axhline(100, color='#1C2833', lw=0.8, ls='--')
ax.set_xticks(list(xs))
ax.set_xticklabels([x['state'] for x in adS], rotation=60, ha='right', fontsize=7)
ax.set_ylim(50, 120)
ax.set_ylabel('% of projected adults, 1 March 2026', fontsize=8)
ax.legend(fontsize=7, frameon=False)
style_axes(ax, 'Rolls as a share of the projected adult population')
R.figure(fig, 'Figure 2. Nineteen states with projections by age. The dashed line is a roll equal to the adult population.', width=15)
dl = sorted(adS, key=lambda x: x['draft_adult_pct'])
R.p('A roll larger than the adult population is what a roll swollen by the dead and the departed would look like, and it is the case the revision was meant to answer. Across the %d states with projections by age, the rolls before the revision held %s of the projected population aged 18 and over, and the draft rolls hold %s. '
    'Only %d had a roll larger than their adult population (%s). How far a roll exceeded its adult population has no relationship with how many names the state removed (rank correlation %.2f). '
    'A rank correlation runs from -1 to 1 and shows whether states that rank high on one measure also rank high on the other. The lowest draft rolls against the adult population are in %s. '
    'The projections count residents, so a state that receives many migrants counts adults who may be registered in their home state, which lowers its ratio.'
    % (ADU['states'], pct(100 * ADU['roll_total'] / ADU['adults_total']), pct(100 * ADU['draft_total'] / ADU['adults_total']), len(ADU['over_100']), andj(ADU['over_100']), ADU['rho_rate'],
       andj(['%s (%s)' % (x['state'], pct(x['draft_adult_pct'])) for x in dl[:3]])))
vS = sorted([x for x in S if x.get('removed_pct_votes24') is not None], key=lambda x: -x['removed_pct_votes24'])
R.p('Set against the 2024 Lok Sabha election, the names left off the draft roll equal a fifth or more of the votes polled in %d states, led by %s.'
    % (sum(x['removed_pct_votes24'] >= 20 for x in vS), andj(['%s (%s)' % (x['state'], pct(x['removed_pct_votes24'])) for x in vS[:3]])))

R.h2('The three reasons, by phase')
fig, ax = plt.subplots(figsize=(7, 4))
labs = ['Phase 1\n(Bihar)', 'Phase 2\n(%d states)' % P['2']['states'], 'Phase 3\n(%d states)' % P['3']['states']]
bottom = [0, 0, 0]
for k in RK + ['unsplit']:
    v = [P[p][k] / 1e5 for p in ('1', '2', '3')]
    ax.bar(labs, v, bottom=bottom, color=C[k], label=RN.get(k, 'Not split by reason'))
    bottom = [b + x for b, x in zip(bottom, v)]
ax.set_ylabel('Names removed, lakh', fontsize=8)
ax.legend(fontsize=7, ncol=4, loc='upper center', bbox_to_anchor=(0.5, -0.16), frameon=False)
style_axes(ax, 'Names left off the draft rolls, by reason')
R.figure(fig, 'Figure 3. Names left off the draft rolls in each phase, by the reason entered, in lakh.', width=14)
R.p('The share entered as dead fell from %s in Bihar to %s in phase 2 and %s in phase 3, while the share entered as shifted, absent or other rose from %s to %s and %s. '
    'Removals per 100 electors rose with each phase, from %.1f to %.1f and then %.1f.'
    % (pct(P['1']['shares']['dead']), pct(P['2']['shares']['dead']), pct(P['3']['shares']['dead']),
       pct(P['1']['shares']['shifted_absent_other']), pct(P['2']['shares']['shifted_absent_other']), pct(P['3']['shares']['shifted_absent_other']),
       P['1']['per_100'], P['2']['per_100'], P['3']['per_100']))

R.h2('State by state')
fig, ax = plt.subplots(figsize=(8, 8.5))
mix = sorted(split, key=lambda s: s['shares']['shifted_absent_other'])
left = [0] * len(mix)
for k in RK:
    v = [s['shares'][k] for s in mix]
    ax.barh([s['state'] for s in mix], v, left=left, color=C[k], label=RN[k])
    left = [a + b for a, b in zip(left, v)]
ax.set_xlim(0, 100)
ax.tick_params(axis='y', labelsize=7)
ax.set_xlabel('% of the state\'s removals split by reason', fontsize=8)
ax.legend(fontsize=7, ncol=3, loc='upper center', bbox_to_anchor=(0.5, -0.07), frameon=False)
style_axes(ax, 'Reasons entered, share of each state\'s removals')
R.figure(fig, 'Figure 4. States that published a split by reason, ordered by the share entered as shifted, absent or other.', width=15)
R.p('Among states that removed ten lakh names or more, the share entered as shifted, absent or other runs from %s in %s to %s in %s. Among them the share entered as dead is highest in %s (%s), and the share entered as enrolled more than once in %s (%s). '
    'One revision under one set of instructions produced very different mixes of reasons from state to state, and the Commission has not explained why.'
    % (pct(big[-1]['shares']['shifted_absent_other']), big[-1]['state'], pct(big[0]['shares']['shifted_absent_other']), big[0]['state'],
       hiDead['state'], pct(hiDead['shares']['dead']), hiDup['state'], pct(hiDup['shares']['duplicate'])))
R.p('Removals per 100 electors range from %.1f in %s to %.1f in %s. %s removed the most names in all, %s.'
    % (rated[-1]['per_100'], rated[-1]['state'], rated[0]['per_100'], rated[0]['state'], max(has, key=lambda s: s['removed'])['state'], crore(max(s['removed'] for s in has))))
SPN = {'complete': 'Full', 'short': 'Short', 'none': 'None', 'pending': 'No draft'}
fmt = lambda v: indian(v) if v is not None else '–'
R.table(['State or UT', 'Phase', 'Removed', 'Per 100', 'Dead', 'Shifted, absent, other', 'Duplicate', 'Split', 'Figures'],
        [[s['state'], s['phase'], fmt(s['removed']), '%.1f' % s['per_100'] if s['per_100'] is not None else '–', fmt(s['dead']), fmt(s['shifted_absent_other']), fmt(s['duplicate']),
          SPN[s['split']], s['figures'] or '–'] for s in sorted(S, key=lambda s: -(s['removed'] or 0))],
        widths=[3.6, 1.1, 2.1, 1.3, 1.9, 2.3, 1.8, 1.3, 1.5], right={1, 2, 3, 4, 5, 6}, size=7.5)
R.p('Under Split, Full means the reasons account for the total within rounding, Short means they leave some names unexplained (%s), and None means no split was found (%s). Under Figures, rounded means the state published in lakh or crore (%d states).'
    % (andj(short), andj(none), len(rounded)))

R.h2('Women among the removed')
G = sorted(N['gender'], key=lambda g: -g['gap'])
gOver = [g for g in G if g['gap'] > 1]
gEven = [g for g in G if abs(g['gap']) <= 1]
gUnder = [g for g in G if g['gap'] < -1]
QN = {'exact': 'exact', 'rounded': 'rounded', 'proxy': 'earlier roll', 'unverified': 'unverified', 'lists': 'lists'}
fig, ax = plt.subplots(figsize=(7, 4.2))
ys = list(range(len(G)))[::-1]
ax.barh([y + 0.2 for y in ys], [g['women_share_removed'] for g in G], height=0.4, color='#AF3B6E', label='Women, % of names removed')
ax.barh([y - 0.2 for y in ys], [g['women_share_roll'] for g in G], height=0.4, color=C['dead'], label='Women, % of the roll')
ax.set_yticks(ys)
ax.set_yticklabels([g['state'] for g in G], fontsize=8)
ax.set_xlim(40, 60)
ax.legend(fontsize=7, frameon=False, loc='lower right')
style_axes(ax, 'Women\'s share of removals and of the roll')
R.figure(fig, 'Figure 5. States that published a split by sex. Bihar\'s roll before the revision is its draft roll plus the names removed at the draft, by sex.', width=14)
R.p('Only ten states have published their removals by sex, or their roll by sex before the revision and on the draft. In %d of the ten, women are a larger share of the names removed than of the roll, by up to %.1f points in %s. %s %s within a point of even, and %s runs the other way, by %.1f points. '
    'Most phase 3 states have published no split by sex, so this is not the national picture.'
    % (len(gOver), G[0]['gap'], G[0]['state'], andj([g['state'] for g in gEven]), 'is' if len(gEven) == 1 else 'are',
       andj([g['state'] for g in gUnder]), -gUnder[0]['gap'] if gUnder else 0))
R.table(['State', 'Women removed', 'Men removed', 'Women, % removed', 'Women, % of roll', 'Difference', 'Figures'],
        [[g['state'], indian(g['women_removed']), indian(g['men_removed']), '%.1f' % g['women_share_removed'], '%.1f' % g['women_share_roll'], '%+.1f' % g['gap'], QN[g['quality']]] for g in G],
        widths=[3.2, 2.4, 2.4, 2.1, 2.1, 1.8, 2.2], right={1, 2, 3, 4, 5}, size=8)

R.h2('What goes with the removal rate')
CR = N['correlations']
CL = {'income_pc': 'income per head', 'mpce_rural': 'rural spending per head', 'mpce_urban': 'urban spending per head', 'urban_pct': 'urban share', 'literacy': 'literacy', 'female_literacy': 'women\'s literacy', 'muslim_pct': 'Muslim share of households',
      'sc_pct': 'SC share of households', 'st_pct': 'ST share of households', 'sex_ratio': 'sex ratio', 'out_migration': 'share born here but living in another state',
      'in_migration': 'share of residents born in another state'}
CS = {c['key']: c['source'] for c in N['characteristics']}
both = [c for c in CR if c['per_100_phase2'] is not None and c['per_100_phase3'] is not None and abs(c['per_100_phase2']) >= 0.2 and abs(c['per_100_phase3']) >= 0.2 and (c['per_100_phase2'] > 0) == (c['per_100_phase3'] > 0)]
fmtr = lambda c, k: '–' if c[k] is None else '%.2f (%d)' % (c[k], c['n_' + k])
top = max(CR, key=lambda c: abs(c['per_100_all']))
p3 = [CL[c['key']] for c in CR if c['per_100_phase3'] is not None and abs(c['per_100_phase3']) >= 0.4]
mus = next(c for c in CR if c['key'] == 'muslim_pct')
dupTop = max(CR, key=lambda c: abs(c['duplicate_big']))
B = N['border']
R.p('Each state\'s removals per 100 electors, and the shares of its removals entered as dead or as enrolled more than once, are set against its characteristics as rank correlations across states. A value of 1 means the two rise together, 0 means no relationship, and anything under 0.2 either way is read as none. The number of states in each is in brackets.')
R.table(['Characteristic', 'Rate, all states', 'Rate, phase 2', 'Rate, phase 3', 'Share dead', 'Share twice, larger states'],
        [[CL[c['key']][0].upper() + CL[c['key']][1:] + ' (' + CS[c['key']] + ')', fmtr(c, 'per_100_all'), fmtr(c, 'per_100_phase2'), fmtr(c, 'per_100_phase3'), fmtr(c, 'dead_all'), fmtr(c, 'duplicate_big')]
         for c in sorted(CR, key=lambda c: -c['per_100_all'])],
        widths=[6.0, 2.2, 2.2, 2.2, 2.0, 2.4], right={1, 2, 3, 4, 5}, size=7.5)
R.p('Across all states the removal rate goes most with the %s (%.2f), and that comes from phase 3 (%.2f). In phase 2 it is %.2f. In phase 3, %s all go with the removal rate, because the big states that draw migrants were revised in the same phase as the North-East, and they differ from it on all of these at once. With only %d states in the phase, there is no telling these apart. '
    '%s The Muslim share of households has no consistent relationship, %.2f across all states, %.2f in phase 2 and %.2f in phase 3. Among the larger states, the share entered as enrolled more than once goes most with %s (%.2f). '
    'Migration is from the 2011 census because no newer figure is published by state, and every other characteristic is from 2019 to 2026. Run on the 2011 census values instead, the reading changes only for %s.'
    % (CL[top['key']], top['per_100_all'], top['per_100_phase3'], top['per_100_phase2'], andj(p3), top['n_per_100_phase3'],
       ('The only characteristics that go with the removal rate the same way in both phases are %s.' % andj(['%s (%.2f in phase 2, %.2f in phase 3)' % (CL[c['key']], c['per_100_phase2'], c['per_100_phase3']) for c in both])) if both else 'No characteristic goes with the removal rate the same way in both phases.',
       mus['per_100_all'], mus['per_100_phase2'], mus['per_100_phase3'], CL[dupTop['key']], dupTop['duplicate_big'],
       andj([x['key'].replace('_pct', ' share').replace('_', ' ') for x in N['robustness_2011'] if x['rho_recent'] is not None and x['rho_2011'] is not None and ((abs(x['rho_recent']) >= 0.2) != (abs(x['rho_2011']) >= 0.2) or (abs(x['rho_recent']) >= 0.2 and (x['rho_recent'] > 0) != (x['rho_2011'] > 0)))]) or 'none of them'))
R.p('States on an international border removed fewer names than interior states. The typical border state removed %.1f per 100 electors across %d states, and the typical interior state %.1f across %d. None of these relationships says who was removed inside a state, because a pattern across states tells us nothing about individuals.'
    % (B['per_100_yes'], B['n_per_100_yes'], B['per_100_no'], B['n_per_100_no']))

R.h2('After the final rolls')
FN = N['final']
fS = sorted([s for s in S if s['electors_final'] is not None and s['net_fall_per_100'] is not None], key=lambda s: s['net_fall_per_100'])
fig, ax = plt.subplots(figsize=(8, 6.5))
y = list(range(len(fS)))
ax.barh([i + 0.2 for i in y], [s['per_100'] for s in fS], height=0.4, color='#9aa5b1', label='Removed at the draft')
ax.barh([i - 0.2 for i in y], [s['net_fall_per_100'] for s in fS], height=0.4, color='#1f3a5f', label='Net fall at the final roll')
ax.set_yticks(y)
ax.set_yticklabels([s['state'] for s in fS], fontsize=7)
ax.set_xlabel('Per 100 electors on the roll before the revision', fontsize=8)
ax.legend(fontsize=7, ncol=2, loc='upper center', bbox_to_anchor=(0.5, -0.08), frameon=False)
style_axes(ax, 'Removed at the draft, and the fall that remains at the final roll')
R.figure(fig, 'Figure 6. States whose final roll is out and whose roll before the revision was published exactly enough to set against it.', width=15)
wb = next(s for s in S if s['withheld'])
R.p('In the %d states and union territories with a final roll, %s names were left off the drafts, and the final rolls came out %s larger than the drafts, which is %s of the fall. '
    '%s kept %s names off its final roll while they are decided, and without them the final rolls were %s larger, %s of the fall. '
    'The net fall is the roll before the revision less the final roll. It comes to %.1f per 100 electors, against %.1f left off at the draft.'
    % (FN['states'], crore(FN['removed']), crore(FN['net_after_draft']), pct(FN['made_up_pct']), wb['state'], lakh(FN['withheld']),
       crore(FN['net_after_draft'] + FN['withheld']), pct(FN['made_up_pct_ex_withheld']), FN['net_per_100'], FN['per_100']))
R.p('The rise from draft to final counts new electors as well as names put back, and no state has said how many of those added had been removed at the draft, so it is the most that can have been put back. '
    'The final roll is smaller than the draft in %d states (%s). %s'
    % (len(FN['shrank']), andj(FN['shrank']), ('How many names a state removed at the draft has no relationship with how much of that its final roll made up (rank correlation %.2f).' if abs(FN['rho_made_up']) < 0.2
                             else 'States that removed more at the draft made up a different share of it at the final roll (rank correlation %.2f).') % FN['rho_made_up']))
RCN = {'exact': 'Adds up', 'rounded': 'Rounded', 'net only': 'Net only', 'no': 'Does not add up'}
sn = lambda v: '–' if v is None else ('−' + indian(-v) if v < 0 else indian(v))
R.table(['State or UT', 'Removed at draft', 'Added after', 'Removed after', 'Final less draft', 'Made up', 'Net fall per 100', 'Figures'],
        [[s['state'], fmt(s['removed']), fmt(s['added_after_draft']), fmt(s['removed_after_draft']), sn(s['net_after_draft']), pct(s['made_up_pct']),
          '%.1f' % s['net_fall_per_100'] if s['net_fall_per_100'] is not None else '–', RCN[s['reconciles']]]
         for s in sorted([s for s in S if s['electors_final'] is not None], key=lambda s: -s['removed'])],
        widths=[3.6, 2.2, 2.0, 2.0, 2.2, 1.5, 1.7, 2.0], right={1, 2, 3, 4, 5, 6}, size=7.5)
R.p('Under Figures, adds up means the draft plus additions less removals equals the final roll, net only means the state published the draft and final rolls but not the additions and removals behind the difference, and does not add up means the published figures do not match (%s). '
    'Removals after the draft carry no reason in any state except Bihar, so they are outside every figure by reason in this report. %s have not yet published a final roll.'
    % (andj([s['state'] for s in S if s['reconciles'] == 'no']), andj(FN['waiting'])))

# ------------------------------------------------------------ against the winning margins
M = J('india', 'margins.json')
IMB, BF = J('bihar', 'impact.json'), J('bihar', 'final.json')
R.h2('Against the winning margins')
R.p('A seat is decided by the votes between its winner and its runner-up. Where more names left a seat\'s roll than that margin, the names removed were enough to decide the seat. '
    'Whether they did depends on how those people would have voted, and that can be estimated only where the lists say who they were.')
R.table(['State', 'Election', 'Seats', 'Count larger than the margin', 'What is counted'],
        [[a['state'], a['election'], str(a['seats']), '%d (%s)' % (a['over_margin'], pct(100 * a['over_margin'] / a['seats'])), a['label']] for a in M['assembly']],
        widths=[3.2, 1.8, 1.4, 3.6, 6.0], right={2, 3}, size=8)
fl = [IMB['summary'][k]['flips'] for k in ('booth_lower', 'booth_upper')]
nda0 = BF['margin']['won_by_alliance']['NDA']
ndaR = [nda0 + v['to_nda'] - v['to_india'] for v in IMB['summary'].values()]
R.p('In Bihar and Tamil Nadu, where the names removed are counted seat by seat, they were more than the winning margin in %d of %d assembly seats. '
    'West Bengal and Kerala publish no removals by seat, so their count is the fall in the roll, which also takes in ordinary deaths and moves, and it was more than the margin in %d of %d. '
    'The two are kept apart because they count different things.' % (M['removed']['assembly_over'], M['removed']['assembly_seats'], M['fall']['assembly_over'], M['fall']['assembly_seats']))
R.p('Bihar is the one state whose lists show who was removed. Estimating how they would have voted from their own booths in 2024, %d to %d seats would have changed hands, in both directions, and on every estimate the NDA keeps a majority, with %d to %d of %d seats.'
    % (min(fl), max(fl), min(ndaR), max(ndaR), BF['margin']['seats']))
LTc = {'Bihar': '#C0392B', 'Tamil Nadu': '#D4AC0D', 'West Bengal': '#1F618D', 'Kerala': '#17A589'}
fig, ax = plt.subplots(figsize=(7.5, 5.2))
for st, col in LTc.items():
    xs = [x for x in M['ls_seat'] if x['state'] == st]
    ax.scatter([x['margin'] / 1e5 for x in xs], [x['count'] / 1e5 for x in xs], s=18, color=col, alpha=.85, label=st)
mx = max(max(x['margin'], x['count']) for x in M['ls_seat']) / 1e5
ax.plot([0, mx], [0, mx], ls='--', lw=0.8, color='#555')
ax.set_xlabel('2024 winning margin, lakh', fontsize=8)
ax.set_ylabel('Count in the seat, lakh', fontsize=8)
ax.legend(fontsize=7, frameon=False)
style_axes(ax, '2024 Lok Sabha seats: the count in each seat against its margin')
R.figure(fig, 'Figure 7. Each dot is a 2024 Lok Sabha seat in the four states, its count added up from its assembly segments. Above the dashed line, the count is larger than the margin. Below zero are Kerala seats whose roll grew.', width=14)
tn = [t for t in M['even_test'] if t['state'] == 'Tamil Nadu'][0]
bt = [t for t in M['even_test'] if t['state'] == 'Bihar'][0]
R.p('Set against the 2024 Lok Sabha results, the count in each seat was larger than the margin in %d of %d seats in Bihar and Tamil Nadu and %d of %d in West Bengal and Kerala. '
    'The revision came after the 2024 election, so this measures how large the removals are against the votes that decide a seat, and it does not say what happened in 2024.'
    % (M['removed']['ls_over'], M['removed']['ls_seats'], M['fall']['ls_over'], M['fall']['ls_seats']))
R.p('No state has published its removals by Lok Sabha seat. Spread evenly over each state\'s seats, the removals would be larger than the 2024 margin in %d of %d seats in %d states and union territories. '
    'Where seat counts exist the even spread can be tested. In Bihar it gives %d seats against %d counted, and in Tamil Nadu %d against %d, because removals there were heaviest in the cities and most seats lost fewer names than the state average. '
    'It is a rough guide that can run high. In 2024, %d of %d contested seats were won by fewer than 50,000 votes.'
    % (M['even_total']['over_margin'], M['even_total']['pcs'], M['even_total']['states'], bt['even'], bt['actual'], tn['even'], tn['actual'], M['ls_close']['under_50000'], M['ls_close']['contested']))

# ------------------------------------------------------------ the roll over forty years
LSE = J('india', 'lok_sabha_electors.json')['rows']
R.h2('The roll over forty years')
fig, ax = plt.subplots(figsize=(7.5, 4.2))
ax.plot([r['year'] for r in LSE], [r['electors'] / 1e7 for r in LSE], marker='o', color='#1F4E79', lw=2, label='Electors on the roll')
ax.plot([r['year'] for r in LSE], [r['pop_voting_age'] / 1e7 for r in LSE], marker='o', color='#17A589', lw=2, ls='--', label='Population of voting age')
ax.set_xticks([r['year'] for r in LSE if r['election'] != '1998'])
ax.set_xticklabels([r['election'] for r in LSE if r['election'] != '1998'], fontsize=6.5, rotation=45, ha='right')
ax.set_ylim(0, 110)
ax.set_ylabel('Crore', fontsize=8)
ax.legend(fontsize=7, frameon=False, loc='lower right')
style_axes(ax, 'Electors and the population of voting age, every Lok Sabha election')
R.figure(fig, 'Figure 8. Electors from the Election Commission\'s Atlas 2024 (Graph 6.1). Population of voting age, 21 and over in 1984-85 and 18 and over from 1989, from the UN World Population Prospects 2024, a modelled estimate that counts everyone living in India, citizens or not.', width=14)
ov = [r for r in LSE if r['electors_per_100'] > 100]
un = [r for r in LSE if r['electors_per_100'] <= 100]
g10 = LSE[-1]['electors'] - [r for r in LSE if r['election'] == '2014'][0]['electors']
R.p('The roll grew from %s in %s to %s in %s. In every election to %s it held more names than there were people of voting age, up to %.1f for every 100 in %s. If the population estimate is right, a roll that large carried the names of people who had died or moved, or counted some people twice. '
    'From %s it has held fewer, %.0f for every 100 in %s. Some of that gap is people who are not citizens, whom the population counts and the roll cannot.'
    % (crore(LSE[0]['electors']), LSE[0]['election'], crore(LSE[-1]['electors']), LSE[-1]['election'], ov[-1]['election'], max(r['electors_per_100'] for r in ov),
       max(ov, key=lambda r: r['electors_per_100'])['election'], un[0]['election'], LSE[-1]['electors_per_100'], LSE[-1]['election']))
R.p('In the ten years from 2014 to 2024 the roll gained %s. The %s names left off the draft rolls are %d in every 100 of that gain, though the two are not strictly alike, because the revision covered %d states and union territories and the Lok Sabha figure is all India.'
    % (crore(g10), crore(T['removed']), round(100 * T['removed'] / g10), T['states']))

# ------------------------------------------------------------ how the revision was run
PR = J('india', 'process.json')
R.h2('How the revision was run')
moves = lambda r: len([st for st in r['steps'] if st.get('kind') != 'published']) - 1
R.p('The rules changed while the revision was under way. The site\'s page on how the revision was run lists %d orders, letters and judgments in date order, %d of them from the Supreme Court, each linked to its document, '
    'and draws every state\'s schedule as it was set and as it was moved. Across %d states and union territories, dates were changed %d times in the orders and notes that could be read.'
    % (len(PR['timeline']), len([t for t in PR['timeline'] if t['who'] == 'sc']), len(PR['schedules']), sum(moves(r) for r in PR['schedules'])))
R.p('What made it harder to stay on the roll, each point resting on an order or a judgment:')
R.numbered(['%s. %s' % (b['title'], b['text']) for b in PR['burdens']])
R.p('The page also lists %d press reports of problems in the field, each attributed to its outlet and kept apart from the points above because no document confirms them.' % len(PR['reported']), italic=True)

# ============================================================ CONCLUSION
R.h1('What the Election Commission should do')
R.p('%s names came off the draft rolls, about four in five of them on an entry that the elector had moved, could not be found, or was on the roll twice. The Election Commission should:' % crore(T['removed']))
R.numbered([
    'Publish a state-by-state table of its own, in exact figures, with the reason for every removal at the draft and after it.',
    'Publish the deletion lists with the reason against each name for every state, as it did for Bihar, so that removals can be counted by booth, sex and age.',
    'Publish the basis for entries marked absent and enrolled more than once.',
    'Publish the outcome of every claim and objection, and say how many of those added at the final roll had been removed at the draft, so that restorations can be set against removals.',
    'Explain why the mix of reasons differs so widely between states under one set of instructions.',
])

R.h1('Method and sources')
R.p('Each state\'s Chief Electoral Officer, the Election Commission\'s officer in charge of its rolls, published figures when the draft roll came out, and the All India figures are those officers\' own. They are taken from the press notes where those could be read (%s) and from press reports otherwise. Bihar\'s row is counted from the deletion lists. '
    'The reasons are grouped into the three every state reported. The state rows add up to %s removed, against the %s reported nationally on 30 September 2026, and the difference is rounding. Each row\'s source is listed on the method page of the site and in the downloadable table.'
    % (andj([s['state'] for s in S if s['source'] == 'primary']), crore(T['removed']), 'about 13.3 crore'))
R.p('No name, EPIC number or address is published.')

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'reports', 'sir-india-report.docx')
R.save(out)
R.save_html(out[:-5] + '.html')
if len(sys.argv) > 2:
    R.save_web(sys.argv[2])
print('ok')
