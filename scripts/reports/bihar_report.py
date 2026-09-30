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
fOver = [d for d in DI if d['female_share_deleted'] > d['female_share_population_2011']]
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
         ('%d of %d' % (len(over), len(withM)), 'seats: removals exceed the margin'), (pct(fem), 'of the removed are women')])
R.p('The Special Intensive Revision removed %s names from Bihar\'s electoral roll in 2025: %s before the draft roll of 1 August and %s more before the final roll. '
    'That is %s names for every 100 electors on the final roll, across %s polling booths in %d constituencies. '
    'In the Assembly election that followed in November, %s votes were polled. The names removed equal %s of them, one for every %.1f votes cast.'
    % (indian(t['total']), indian(t['p1']), indian(t['p2']), '%.2f' % per100, indian(t['booths']), len(A), indian(polled),
       pct(100 * t['total'] / polled), polled / t['total']))
R.p('Set against the results, the removals are larger than the margin of victory in %d of %d constituencies. They exceed the combined winning margin of all %d seats, %s, by a factor of %.2f, '
    'and they exceed the combined winning margin of the NDA across the %d seats it won, %s. In %d of the %d seats the NDA took from INDIA, more names were removed than the NDA won by.'
    % (len(over), len(withM), len(withM), lakh(mAll), t['total'] / mAll, len(nda), lakh(mNDA), len(tookO), len(took)))
R.p('Women are %s of those removed, against 47.86%% of Bihar\'s population in the 2011 census, and their share of the removed is higher than their share of the population in %d of %d districts. '
    'Sex is recorded on the roll, so this figure rests on no estimate.' % (pct(fem), len(fOver), len(DI)))

R.h2('Deletions and coverage')
R.p('The booth lists account for every one of Bihar\'s %s polling booths. The table gives each district\'s removals, removals per 100 electors on the 2025 roll, and its share of the state total.' % indian(t['booths']))
R.table(['District', 'Seats', 'Names removed', 'Per 100 electors', 'Per booth', 'Share of state'],
        [[d['district'], d['acs'], indian(d['deleted']), '%.2f' % d['per_100'], '%.1f' % d['per_booth'], pct(100 * d['deleted'] / t['total'])] for d in rankD],
        widths=[4.2, 1.5, 3, 2.6, 2.2, 2.6], right={1, 2, 3, 4, 5})
R.p('Removals range from %.1f per 100 electors in %s to %.1f in %s. Among constituencies the range is wider, from %.1f in %s to %.1f in %s.'
    % (rankD[-1]['per_100'], rankD[-1]['district'], rankD[0]['per_100'], rankD[0]['district'], rankA[-1]['per_100'], rankA[-1]['name'], rankA[0]['per_100'], rankA[0]['name']))

R.h2('Deletions against the margins and the votes polled')
R.p('Each constituency\'s removals are set against two yardsticks from the November 2025 election: the margin by which the seat was won, and the votes polled. The comparison is not a claim that these electors would have voted, or how. It measures the size of the revision beside the vote that decided each seat.')
R.stats([('%d of %d' % (len(over), len(withM)), 'seats: removals exceed the margin'), ('%d' % sum(ratio(a) >= 5 for a in withM), 'seats: removals five times the margin or more'),
         ('%d' % sum(share(a) > 15 for a in A), 'seats: removals over 15% of votes polled'), (indian(min(a['margin2025'] for a in withM)), 'smallest margin (%s)' % min(withM, key=lambda a: a['margin2025'])['name'])])
fig, ax = plt.subplots(figsize=(8, 3.2))
cuts, labs = [0, 1, 2, 5, 10, 20, 1e9], ['under 1×', '1–2×', '2–5×', '5–10×', '10–20×', '20× or more']
vals = [sum(cuts[i] <= ratio(a) < cuts[i + 1] for a in withM) for i in range(6)]
ax.bar(labs, vals, color=[C['grey']] + [C['red']] * 5)
for i, v in enumerate(vals):
    ax.text(i, v + 1, str(v), ha='center', fontsize=8)
ax.set_ylabel('Constituencies', fontsize=8)
style_axes(ax, 'Names removed as a multiple of the 2025 winning margin')
R.figure(fig, 'Figure 1. Constituencies by names removed ÷ 2025 winning margin. Grey: removals below the margin.')
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
    'In %s the names removed exceed the runner-up\'s entire vote. In no constituency do they exceed the total votes polled: Bihar removed about nine names per hundred electors, where the Old City of Hyderabad removed forty.'
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

R.h2('After the final roll')
R.p('The final roll of 30 September 2025 was published after the claims and objections on the draft. The Election Commission\'s Format 4B return for it gives, seat by seat and by sex, the names added and removed after the draft and the final roll, and agrees with the Chief Electoral Officer\'s press note. '
    'The roll of June 2025 is published only as a state total, so a seat\'s roll before the revision is taken here as its draft roll plus the names on its phase 1 list.')
R.stats([(lakh(FT['added']), 'added after the draft'), (lakh(FT['removed_after']), 'removed after the draft'), (pct(FT['made_up_pct']), 'of the draft removals made up'),
         ('%d of %d' % (FM['net'], FM['seats']), 'seats: net fall exceeds the margin')])
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
R.p('After the draft, %s names were added on claims and %s removed on objections, so the final roll rose by %s over the draft: %s of the %s names removed at the draft. '
    'That rise counts new electors as well as names put back, and the Commission has not said how many of those added had been removed at the draft, so it is the most that can have been put back. '
    'The final roll was %s names smaller than the roll before the revision, and smaller in every one of the %d seats.'
    % (indian(FT['added']), indian(FT['removed_after']), indian(FT['net_after']), pct(FT['made_up_pct']), indian(FT['p1']), indian(FT['net_fall_press']), len(FB['seats'])))
R.p('In %d of %d seats the fall that remained at the final roll was still larger than the 2025 winning margin, against %d when the draft removals are counted alone. Of those %d, the NDA won %d, INDIA %d and others %d.'
    % (FM['net'], FM['seats'], FM['total'], FM['net'], FM['net_by_alliance'].get('NDA', 0), FM['net_by_alliance'].get('INDIA', 0), FM['net_by_alliance'].get('Other', 0)))
R.p('Women were %s of the names removed at the draft and %s of those added after it, so their share of the roll fell from %s before the revision to %s on the final roll. '
    'Of the %s names removed after the draft, %s were entered as dead, %s as shifted and %s as repeated; %s carry no reason at all.'
    % (pct(FT['women_share_p1']), pct(FT['women_share_added']), pct(FT['women_share_before']), pct(FT['women_share_final']),
       indian(FT['removed_after']), indian(FT['r_expired']), indian(FT['r_shifted']), indian(FT['r_repeated']), indian(FT['r_unstated'])))

R.h2('Women and the deletions')
R.p('The roll records each elector\'s sex, so women\'s share of the removed needs no estimate. Women are %s of all removals: %s women and %s men, %s more women than men. '
    'Their share of the removed exceeds their share of the population in %d of %d districts, by up to %.1f points in %s.'
    % (pct(fem), indian(t['female']), indian(t['male']), indian(t['female'] - t['male']), len(fOver), len(DI),
       max(d['female_share_deleted'] - d['female_share_population_2011'] for d in DI),
       max(DI, key=lambda d: d['female_share_deleted'] - d['female_share_population_2011'])['district']))
fig, ax = plt.subplots(figsize=(6, 4.4))
ax.scatter([d['female_share_population_2011'] for d in DI], [d['female_share_deleted'] for d in DI], color=C['pink'], s=18)
ax.plot([45, 65], [45, 65], ls='--', color=C['grey'], lw=1)
ax.set_xlim(46, 50)
ax.set_xlabel('Women, % of district population (2011)', fontsize=8)
ax.set_ylabel('Women, % of names removed', fontsize=8)
style_axes(ax, 'Every district above the line')
R.figure(fig, 'Figure 5. Each dot is a district. Above the dashed line, women\'s share of the removed exceeds their share of the population.', width=12)
R.p('Phase 1 removed %s more women than men, and %s of that difference (%s) were entered as shifted. Among those marked shifted aged 18 to 29, %s are women, the pattern that women who move on marriage would produce. '
    'The lists do not show whether any of them were enrolled again where they now live. If they were not, they have lost the vote.'
    % (indian(xsF), indian(xsS), pct(100 * xsS / xsF), pct(100 * yW / yS)))

R.h2('Reasons for removal')
R.p('The phase 1 lists record, against every one of the %s names, the reason the officer entered for removing it. Counted as entered: %s were marked permanently shifted (%s), %s dead (%s), %s absent (%s) and %s already enrolled elsewhere (%s). '
    'The counts agree with the booth list in every booth, and the counts of women and men agree with the Chief Electoral Officer\'s phase 1 figures in every constituency. The %s names removed in phase 2 carry no reason in the lists.'
    % (indian(rtot), indian(RT['shifted']), pct(rsh('shifted')), indian(RT['dead']), pct(rsh('dead')), indian(RT['absent']), pct(rsh('absent')),
       indian(RT['already_enrolled']), pct(rsh('already_enrolled')), indian(t['p2'])))
R.p('A reason is what an officer entered after a visit or its absence. It is not a finding. Someone marked shifted may have been away for work when the officer called; someone marked absent may have been at home. '
    'Of the four, absent rests on the least: it records only that the elector was not found. Already enrolled is a removal only if the other entry is the same person.')
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
R.p('Among the removed aged 80 and over, %s were entered as dead; among those aged 18 to 24, %s. The young were mostly marked shifted or absent.'
    % (pct(100 * RS['by_age']['dead'][-1] / sum(RS['by_age'][k][-1] for k in RK)), pct(100 * RS['by_age']['dead'][0] / sum(RS['by_age'][k][0] for k in RK))))
R.p('Taken alone, the names marked absent exceed the 2025 margin in %d of %d seats, and the names marked already enrolled in %d. The names marked shifted exceed it in %d and the dead in %d. '
    'The absent share is highest in %s.'
    % (rOver('r_absent'), len(withM), rOver('r_enrolled'), rOver('r_shifted'), rOver('r_dead'), andj(['%s (%s)' % (d['district'], pct(100 * d['absent'] / dsum(d))) for d in RD[:3]])))
R.table(['District', 'Phase 1 removed', 'Shifted', 'Dead', 'Absent', 'Already enrolled'],
        [[d['district'], indian(dsum(d))] + [pct(100 * d[k] / dsum(d)) for k in RK] for d in RD],
        widths=[4.2, 2.8, 2.2, 2.2, 2.2, 2.8], right={1, 2, 3, 4, 5})

R.h3('Two reasons, set against the records')
R.p('The %s names entered as dead equal about %.1f years of adult deaths in Bihar: at the Sample Registration System\'s 2024 death rates by age and sex, the population aged 20 and over has about %s deaths a year. '
    'Their ages are close to those of registered deaths: %s of those entered as dead and aged 25 or over were 70 or older, against %s of registered deaths at those ages in 2024. '
    'Their sex is not: women are %s of those entered as dead, against %s of adult deaths, or %s women where %s would be expected. Registered deaths at 25 and over were %s women in 2024, below their share of deaths, so women\'s deaths are registered less often and more of them may have stayed on the roll; or more women still living were entered as dead. The lists cannot say which.'
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
R.p('Among those aged 18 to 29 marked shifted, %s were women and %s men, an excess of %s women. In scale that is within what marriage produces: in the ten years before the 2011 census, %s women in Bihar had moved on marriage, about %s a year, so the excess is about %.2f of a year\'s marriage moves. '
    'District by district it does not follow: where more women had moved on marriage, women were %s share of the young marked shifted (rank correlation %.2f). Marriage can account for the number of young women marked shifted, not for where they were. The census counts women where they arrived, not where they left, and it is fifteen years old.'
    % (indian(TM['young_shifted_f']), indian(TM['young_shifted_m']), indian(TM['excess']), lakh(TM['recent_marriage']), lakh(TM['recent_marriage_per_year']), TM['excess_years'],
       'a smaller' if TM['rho_share'] <= -0.2 else ('a larger' if TM['rho_share'] >= 0.2 else 'neither a larger nor a smaller'), TM['rho_share']))

R.h2('Religion')
R.p('The roll records no religion. The booth lists classify removed names as Hindu or Muslim where the name allows it, and leave %s of names unclassified. '
    'The Muslim share of removals is therefore a range: %s counting only names classified Muslim, and %s if every unclassified name were Muslim. '
    'Bihar\'s Muslim population was 16.87%% in the 2011 census and 17.70%% in the 2023 caste survey. The census share lies inside the range in %d of %d districts. '
    'In %d districts the classified Muslim share alone runs more than a point above the census share: %s.'
    % (pct(100 * t['unknown'] / cls), pct(mlo), pct(mhi), len(inside), len(DI), len(above), andj([d['district'] for d in above])))
fig, ax = plt.subplots(figsize=(8, 7))
dd = sorted(DI, key=lambda d: d['muslim_share_population_2011'])
y = range(len(dd))
ax.hlines(y, [d['muslim_share_deleted_low'] for d in dd], [d['muslim_share_deleted_high'] for d in dd], color='#9CC5CE', lw=5)
ax.scatter([d['muslim_share_population_2011'] for d in dd], y, color='#1C2833', s=14, zorder=3, label='Census 2011')
ax.set_yticks(list(y), [d['district'] for d in dd], fontsize=7)
ax.set_xlabel('Muslim share, %', fontsize=8)
ax.legend(fontsize=8, frameon=False, loc='lower right')
style_axes(ax, 'Muslim share of removals, as a range, against the census')
R.figure(fig, 'Figure 8. The bar runs from names classified Muslim to all names that could be Muslim; the dot is the 2011 census share.')

R.h2('Caste')
R.p('Caste is not recorded either. It can be read, in part, from the surname of the father or husband listed with each removed elector, and two classifications are used because surnames cross caste lines. '
    'Classification A places %s of removals in a group; the stricter classification B, which sets aside surnames carried by more than one group, places %s. Only what holds under both is reported here.'
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
R.p('The median booth lost %d names. %s booths lost 200 or more each, and %d lost 400 or more. A booth serves on average about %d electors, so 200 removals is a fifth of a booth\'s roll.'
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
R.p('Seats the NDA held lost %.2f names per 100 electors, and INDIA seats %.2f (2020 winners); the order is the same under 2024 and 2025 labels. Within the same constituency, booths the NDA led in 2024 lost %.1f more names each than booths INDIA led. '
    'A booth\'s leader says how most of its voters voted in 2024, not how the removed electors voted; every booth holds voters of both sides. Names were not removed at a higher rate in the seats INDIA lost in 2025 than in the seats it kept. '
    'What the lists establish is the scale of the removals against the margins, set out above.'
    % (L['2020']['NDA']['per_100'], L['2020']['INDIA']['per_100'], W['pooled_nda_minus_india']))

R.h2('Key insights')
R.bullets([
    '**%s names removed**, %s per 100 electors on the final roll, across %s booths.' % (indian(t['total']), '%.2f' % per100, indian(t['booths'])),
    '**Equal to %s of the votes polled** in the November 2025 election: one name for every %.1f votes cast.' % (pct(100 * t['total'] / polled), polled / t['total']),
    '**Larger than the margin in %d of %d seats**, five times the margin or more in %d, ten times or more in %d.' % (len(over), len(withM), sum(ratio(a) >= 5 for a in withM), sum(ratio(a) >= 10 for a in withM)),
    '**Larger than the NDA\'s combined winning margin** in its %d wins (%s against %s).' % (len(nda), lakh(t['total']), lakh(mNDA)),
    '**%d of the %d seats the NDA took from INDIA** lost more names than the NDA won by.' % (len(tookO), len(took)),
    '**Women are %s of the removed**, over-represented in %d of %d districts.' % (pct(fem), len(fOver), len(DI)),
    '**Muslim names are %s to %s of removals**, against 16.87%% of the population; above the census share by more than a point in %d districts.' % (pct(mlo), pct(mhi), len(above)),
    '**%s booths lost 200 names or more each.**' % indian(b200),
    '**Reasons entered in phase 1**: shifted %s, dead %s, absent %s, already enrolled %s. %s of the %s more women than men removed were marked shifted.' % (pct(rsh('shifted')), pct(rsh('dead')), pct(rsh('absent')), pct(rsh('already_enrolled')), indian(xsS), indian(xsF)),
    '**Names marked absent alone exceed the margin in %d seats**, names marked already enrolled in %d.' % (rOver('r_absent'), rOver('r_enrolled')),
    '**The final roll made up %s of the draft removals**, and the fall that remained still exceeded the margin in %d of %d seats; women were %s of those added after the draft.' % (pct(FT['made_up_pct']), FM['net'], FM['seats'], pct(FT['women_share_added'])),
])

R.h2('What this shows and what it does not')
R.p('The lists show how many names were removed, where, who the removed were by sex, age and name, and the reason the officer entered against each phase 1 removal, and they allow the removals to be set against the margins and votes that decided each seat. '
    'They do not show whether that reason was true of the person, whether the removal was right, or how the elector voted. Religion and caste are read from names and are estimates, given as ranges or under two classifications. '
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
    R.p('%s lost %s names across %d constituencies, %.2f for every 100 electors. Women are %s of those removed, against %s of the district\'s population in 2011. '
        'Names classified Muslim are %s to %s of removals, against a census share of %s. '
        'The heaviest constituency is %s, at %.2f per 100 electors; the largest multiple of the margin is in %s, where %s names were removed against a margin of %s. '
        'In 2025 the NDA won %d of the district\'s seats and INDIA %d%s.'
        % (d['district'], indian(d['deleted']), len(rows), d['per_100'], pct(di['female_share_deleted']), pct(di['female_share_population_2011']),
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
    'The names removed exceed the margin in %d of %d seats and equal %s of all votes polled. Whatever the reason entered against each name, a change to the roll of that size is larger than the decision at the ballot box in most of the state.'
    % (len(over), len(withM), pct(100 * t['total'] / polled)))
R.p('Women carried a larger share of the removals than their share of the population in every district, and the lists cannot show whether those women were enrolled again where they now live. '
    'The reasons officers entered, dead, shifted, absent or enrolled twice, are entries after a visit or its absence, not findings. %s names were removed as absent, the entry that rests on the least, and they alone exceed the margin in %d seats.' % (indian(RT['absent']), rOver('r_absent')))
R.p('What the Election Commission should do:')
R.numbered([
    '**Publish the reason for each of the %s phase 2 removals, name by name**: the lists do not carry one, and the Format 4B return gives reasons only by constituency, with %s names left without any.' % (indian(t['p2']), indian(FT['r_unstated'])),
    '**Publish the basis for each entry marked absent or already enrolled**: %s marked absent and %s marked already enrolled in phase 1.' % (indian(RT['absent']), indian(RT['already_enrolled'])),
    '**Publish every claim and objection filed after the draft roll, booth by booth, with its outcome, and say how many of the %s added had been removed at the draft**, so that restorations can be counted against removals.' % lakh(FT['added']),
    '**Publish new enrolments by constituency after the revision**, so that women removed as shifted can be matched against enrolments where they now live.',
])

R.h1('Method and sources')
R.bullets([
    'Removals by polling booth: the phase 1 deletion lists the Chief Electoral Officer, Bihar published against the draft roll of 1 August 2025, for all %s booths.' % indian(t['booths']),
    'Removals by constituency, phase and sex: Chief Electoral Officer, Bihar.',
    'The final roll: Format 4B, the Election Commission\'s return for the final roll of 30 September 2025, as the Chief Electoral Officer, Bihar published it, by constituency and sex.',
    'Religion and surnames of the removed: counts from the same lists, by booth; no individual records.',
    'Reason, sex and age of every phase 1 removal: counts from the row-level deletion list, by constituency and booth; no individual records.',
    'Deaths: Sample Registration System, Statistical Report 2024, and Civil Registration System 2024. Marriage migration: Census of India 2011, table D-3.',
    '2025 Assembly results: winner, runner-up and turnout for each constituency, cross-checked between two independent tables; where they disagreed, the figure matching the reported result was used.',
    '2024 Lok Sabha result by booth: Form 20. Census of India 2011; Bihar caste-based survey, 2 October 2023; Bihar Economic Survey.',
])
R.p('Each booth is counted once. Every headline figure is recomputed from the lists by a second, independent program before publication. Votes polled are the turnout applied to the 2025 roll. No name, EPIC number or address is published.')

out = sys.argv[1] if len(sys.argv) > 1 else '/home/user/reports/Bihar_SIR_2025_Report.docx'
R.save(out)
R.save_html(out[:-5] + '.html')
if len(sys.argv) > 2:
    R.save_web(sys.argv[2])  # the page on the site, e.g. bihar/report
print('ok')
