#!/usr/bin/env python3
"""Bihar SIR 2025: the Word report, in the Sabar Institute's structure.

    python3 scripts/reports/bihar_report.py OUT.docx

Part I analyses the state; Part II gives one chapter per district; a single
section says what the lists show and what they do not; the conclusion sets out
what an audit needs. Every figure is computed from data/bihar/*.json.
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
S, A, DS, ID = J('summary.json'), J('constituencies.json'), J('districts.json'), J('identity.json')
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
R.figure(fig, 'Figure 4. Each dot is a district. Above the dashed line, women\'s share of the removed exceeds their share of the population.', width=12)
R.p('Women who move on marriage and are marked "shifted" at their parents\' address are likely to be a large part of this. The lists do not show whether any of them were enrolled again where they now live. If they were not, they have lost the vote.')

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
R.figure(fig, 'Figure 5. The bar runs from names classified Muslim to all names that could be Muslim; the dot is the 2011 census share.')

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
R.figure(fig, 'Figure 6. Booths by the number of names removed.')
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
])

R.h2('What this shows and what it does not')
R.p('The lists show how many names were removed, where, and who the removed were by sex and by name, and they allow the removals to be set against the margins and votes that decided each seat. '
    'They do not show why an individual name was removed, whether the removal was right, or how the elector voted. Religion and caste are read from names and are estimates, given as ranges or under two classifications. '
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
    R.table(['Constituency', 'Removed', 'Per 100', 'Women %', 'Won by (2025)', 'Margin', '× margin', '% polled'],
            [['%d %s' % (a['ac'], a['name']), indian(a['total']), '%.2f' % a['per_100'], pct(100 * a['t_f'] / (a['t_f'] + a['t_m'])),
              '%s (%s)' % (a['win2025'], a['al2025']), indian(a['margin2025']), '%.1f×' % ratio(a), pct(share(a))] for a in rows],
            widths=[3.4, 1.8, 1.5, 1.6, 2.8, 1.7, 1.6, 1.6], right={1, 2, 3, 5, 6, 7}, size=7.5)

# ============================================================ CONCLUSION
R.page_break()
R.h1('Conclusion and what an audit needs')
R.p('The revision removed %s names from Bihar\'s roll in the months before an Assembly election. '
    % indian(t['total']) + 
    'The names removed exceed the margin in %d of %d seats and equal %s of all votes polled. Whatever the reason entered against each name, a change to the roll of that size is larger than the decision at the ballot box in most of the state.'
    % (len(over), len(withM), pct(100 * t['total'] / polled)))
R.p('Women carried a larger share of the removals than their share of the population in every district, and the lists cannot show whether those women were enrolled again where they now live. '
    'The reasons officers entered, dead, shifted, absent or enrolled twice, are entries after a visit or its absence, not findings, and the lists used here do not carry them against each name.')
R.p('What would settle the questions the lists leave open:')
R.numbered([
    '**A name-by-name verification** of the removals in every constituency where they exceed the margin, starting with the %d where they exceed it five times or more.' % sum(ratio(a) >= 5 for a in withM),
    '**Publication, booth by booth, of every claim and objection** filed after the draft roll, with its outcome, so that restorations can be counted against removals.',
    '**The reason entered against each removed name**, published with the booth lists, and the evidence for each "shifted" and "absent" entry.',
    '**A check of women removed as "shifted"** against new enrolments in the constituencies they moved to.',
    '**An independent review** of the revision\'s method before it is repeated in other states.',
])

R.h1('Method and sources')
R.bullets([
    'Removals by polling booth: the phase 1 deletion lists the Chief Electoral Officer, Bihar published against the draft roll of 1 August 2025, for all %s booths.' % indian(t['booths']),
    'Removals by constituency, phase and sex: Chief Electoral Officer, Bihar.',
    'Religion and surnames of the removed: counts from the same lists, by booth; no individual records.',
    '2025 Assembly results: winner, runner-up and turnout for each constituency, cross-checked between two independent tables; where they disagreed, the figure matching the reported result was used.',
    '2024 Lok Sabha result by booth: Form 20. Census of India 2011; Bihar caste-based survey, 2 October 2023; Bihar Economic Survey.',
])
R.p('Each booth is counted once. Every headline figure is recomputed from the lists by a second, independent program before publication. Votes polled are the turnout applied to the 2025 roll. No name, EPIC number or address is published.')

out = sys.argv[1] if len(sys.argv) > 1 else '/home/user/reports/Bihar_SIR_2025_Report.docx'
R.save(out)
R.save_html(out[:-5] + '.html')
print('ok')
