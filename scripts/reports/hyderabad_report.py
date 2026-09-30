#!/usr/bin/env python3
"""Hyderabad Old City SIR 2026: the Word report, in the Sabar Institute's structure.

    python3 scripts/reports/hyderabad_report.py OUT.docx

Part I analyses the five constituencies together; Part II gives one chapter
per constituency; one section says what the lists show and what they do not;
the conclusion sets out what verification needs before the final roll. Every
figure is computed from data/hyderabad/*.json.
"""
import json
import os
import statistics as st
import sys

import matplotlib.pyplot as plt
from docx.shared import RGBColor

sys.path.insert(0, os.path.dirname(__file__))
from docxkit import Report, indian, lakh, pct, style_axes

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
S = json.load(open(os.path.join(ROOT, 'data', 'hyderabad', 'summary.json')))
P = json.load(open(os.path.join(ROOT, 'data', 'hyderabad', 'parts.json')))
PR = [dict(zip(P['fields'], r)) for r in P['rows']]
for p in PR:
    if p['locality'] in (None, 'nan'):
        p['locality'] = None
A, t = S['acs'], S['totals']
ACC = ['#8B1E3F', '#0E5E6F', '#E0A526', '#1F618D', '#8E7CC3']
R = Report(RGBColor(0x8B, 0x1E, 0x3F))
s = lambda f: sum(f(a) for a in A)
andj = lambda xs: xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]
names = [a['name'] for a in A]
LK = [a for a in A if a['linked']]
yak = next(a for a in A if a['name'] == 'Yakutpura')
mal = next(a for a in A if a['name'] == 'Malakpet')
overM = [a for a in A if a['deleted'] > a['e2023']['margin']]
overV = [a for a in A if a['e2023']['deleted_over_valid'] > 100]
age = [100 * s(lambda a: a['counts']['age_asd'][i]) / s(lambda a: a['age_all'][i]) for i in range(len(S['bands']))]
rsh = {k: 100 * s(lambda a: a['reasons'][k]) / t['deleted'] for k in S['reasons']}
hin = 100 * s(lambda a: a['counts']['hin_asd']) / s(lambda a: a['counts']['hin_all'])
mus = 100 * s(lambda a: a['counts']['mus_asd']) / s(lambda a: a['counts']['mus_all'])
HM = [a['within_part']['hindu_minus_muslim'] for a in A]
UL = [a['within_part']['unlinked_minus_linked'] for a in LK]
lk = 100 * sum(a['counts']['lk_asd'] for a in LK) / sum(a['counts']['lk_all'] for a in LK)
ul = 100 * sum(a['deleted'] - a['counts']['lk_asd'] for a in LK) / sum(a['electors'] - a['counts']['lk_all'] for a in LK)
fr = 100 * s(lambda a: a['counts']['f_asd']) / s(lambda a: a['counts']['f_all'])
mr = 100 * s(lambda a: a['counts']['m_asd']) / s(lambda a: a['counts']['m_all'])
heavy = max(A, key=lambda a: a['max_slot'])
P100 = [p for p in PR if p['electors'] >= 100]
o60 = [p for p in P100 if p['rate'] > 60]
ruleTot = {k: s(lambda a: a['rules'].get(k, 0)) for k in S['rules']}
valid = s(lambda a: a['e2023']['valid'])

# ------------------------------------------------------------ cover
R.cover('Special Intensive Revision 2026', 'Hyderabad Old City: four in ten struck off',
        'Charminar, Yakutpura, Malakpet, Chandrayangutta and Bahadurpura, polling part by polling part',
        [('electors struck off the five pre-revision rolls', indian(t['deleted'])),
         ('of all electors on those rolls', pct(t['rate'])),
         ('constituencies where more names were struck off than the 2023 margin', '%d of %d' % (len(overM), len(A))),
         ('kept on the roll but summoned to a hearing', indian(t['hearing']))])
R.h1('Contents')
R.toc()

# ============================================================ PART I
R.h1('Part I: The five constituencies')
R.h2('At a glance')
R.stats([(indian(t['deleted']), 'electors struck off'), (pct(t['rate']), 'of the pre-revision rolls'),
         ('%d of %d' % (len(overM), len(A)), 'seats: struck off exceed the 2023 margin'), (indian(t['hearing']), 'kept but summoned to a hearing')])
R.p('The Special Intensive Revision reached Hyderabad in 2026. On the pre-revision rolls of five Old City constituencies stood %s electors. The September lists struck %s of them off, %s, and kept %s more on the draft roll only on condition that they attend a hearing. '
    'Unlike the Bihar lists, which hold only the removed, these lists hold every elector, so each group has a true rate: the share of that group struck off.'
    % (indian(t['electors']), indian(t['deleted']), pct(t['rate']), indian(t['hearing'])))
R.p('Every one of the five lost more names than its 2023 winning margin. In %s the names struck off exceed every valid vote cast in 2023. Yakutpura was won by %s votes and lost %s names. '
    'The heaviest burden fell on the oldest electors and on those who could not be traced to the 2002 roll: %s of electors aged 80 and over were struck off, and electors with no 2002 link were struck off at twice the rate of those with one.'
    % (andj([a['name'] for a in overV]), indian(yak['e2023']['margin']), indian(yak['deleted']), pct(age[-1])))

R.h2('Deletions and coverage')
R.table(['Constituency', 'Electors', 'Struck off', '% struck off', 'Summoned', '% summoned', 'Parts'],
        [[a['name'], indian(a['electors']), indian(a['deleted']), pct(a['rate']), indian(a['hearing']), pct(a['hearing_rate']), a['parts']] for a in A] +
        [['All five', indian(t['electors']), indian(t['deleted']), pct(t['rate']), indian(t['hearing']), pct(100 * t['hearing'] / t['electors']), indian(t['parts'])]],
        widths=[3.4, 2.4, 2.3, 2, 2.3, 2, 1.5], right={1, 2, 3, 4, 5, 6})
R.p('Malakpet\'s list is read by polling-station name, which gives %d stations rather than parts, and it is incomplete: it holds %s names struck off against the %s in an independent count of the published Malakpet list. For the other four constituencies the two counts agree exactly.'
    % (mal['parts'], indian(mal['deleted']), '1,47,799'))

R.h2('Deletions against the margin and the votes polled')
R.p('Each constituency\'s names struck off are set against two yardsticks from the 2023 Assembly election: the margin by which the seat was won, and the valid votes cast. The comparison is not a claim that these electors would have voted, or how. It measures how large the revision is beside the electorate that decided the seat.')
R.table(['Constituency', 'Won by (2023)', 'Margin', 'Struck off', 'Struck off − margin', '× margin', 'Valid votes 2023', '% of valid votes'],
        [[a['name'], a['e2023']['winner'], indian(a['e2023']['margin']), indian(a['deleted']), '+' + indian(a['deleted'] - a['e2023']['margin']),
          '%.1f×' % a['e2023']['deleted_over_margin'], indian(a['e2023']['valid']), pct(a['e2023']['deleted_over_valid'])] for a in sorted(A, key=lambda a: -a['e2023']['deleted_over_valid'])],
        widths=[2.6, 3.2, 1.6, 1.8, 2.1, 1.5, 2.1, 1.8], right={2, 3, 4, 5, 6, 7}, size=7.5)
fig, ax = plt.subplots(figsize=(8, 3.2))
srt = sorted(A, key=lambda a: -a['e2023']['deleted_over_valid'])
ax.barh([a['name'] for a in srt][::-1], [a['e2023']['deleted_over_valid'] for a in srt][::-1], color=['#C0392B' if a['e2023']['deleted_over_valid'] > 100 else '#E0A526' for a in srt][::-1])
ax.axvline(100, ls='--', color='#1C2833', lw=1)
ax.set_xlabel('Names struck off as % of valid votes cast in 2023', fontsize=8)
style_axes(ax, 'Names struck off against the whole 2023 vote')
R.figure(fig, 'Figure 1. Past the dashed line, more names were struck off than there were valid votes in 2023.')
R.p('Across the five constituencies the names struck off equal %s of the valid votes cast in 2023. In every constituency more names were struck off than the winning candidate received.'
    % pct(100 * t['deleted'] / valid) if all(a['deleted'] > a['e2023']['winner_votes'] for a in A) else
    'Across the five constituencies the names struck off equal %s of the valid votes cast in 2023.' % pct(100 * t['deleted'] / valid))

R.h2('The reasons recorded')
R.p('The list of the absent, shifted and dead carries the reason an officer entered against each name. %s of removals were entered as "permanently shifted", %s as "untraceable or absent", %s as dead and %s as enrolled elsewhere. Each is an officer\'s entry after a visit or its absence, not a finding.'
    % tuple(pct(rsh[k]) for k in ['Permanently Shifted', 'Untraceable/Absent', 'Death', 'Already enrolled']))
R.table(['Constituency'] + ['Shifted', 'Untraceable or absent', 'Dead', 'Enrolled elsewhere'],
        [[a['name']] + [pct(100 * a['reasons'][k] / a['deleted']) for k in S['reasons']] for a in A], widths=[3.4, 2.6, 3.4, 2, 3], right={1, 2, 3, 4})
ut = [100 * a['reasons']['Untraceable/Absent'] / a['deleted'] for a in A]
R.p('The untraceable share runs from %s in %s to %s in %s. Those entries rest on an officer not finding someone, and they are where verification should begin.'
    % (pct(min(ut)), A[ut.index(min(ut))]['name'], pct(max(ut)), A[ut.index(max(ut))]['name']))

R.h2('Age')
fig, ax = plt.subplots(figsize=(8, 3.4))
for i, a in enumerate(A):
    ax.plot(S['bands'], a['age_rate'], marker='o', ms=3, color=ACC[i], label=a['name'])
ax.set_ylabel('% struck off', fontsize=8)
ax.legend(fontsize=7, frameon=False, ncol=5, loc='upper left')
style_axes(ax, 'Share of each age band struck off')
R.figure(fig, 'Figure 2. Deletion rate by age band, each constituency.')
a80 = [a['age_rate'][-1] for a in A]
a18 = [a['age_rate'][0] for a in A]
R.p('The older the elector, the likelier the removal, in every constituency: between %s and %s of electors aged 80 and over were struck off, against %s to %s of those aged 18 to 24. '
    'Death accounts for part of the top of the range; %s deaths were recorded. But the rate roughly doubles between 18 to 24 and 30 to 39, ages at which almost nobody dies, so death is not the whole of it.'
    % (pct(min(a80)), pct(max(a80)), pct(min(a18)), pct(max(a18)), indian(s(lambda a: a['reasons']['Death']))))

R.h2('Women and men')
fm = [a['within_part']['female_minus_male']['diff_pp'] for a in A]
R.p('Women and men were struck off at similar rates: %s of women and %s of men. Inside the same polling part the gap runs from %.1f to %.1f points and changes sign between constituencies. In Bihar women were 55.5%% of the removed and over-represented in every district; the Old City shows no such pattern.'
    % (pct(fr), pct(mr), min(fm), max(fm)))

R.h2('Religion')
R.p('The roll records no religion; it is estimated from each elector\'s name, and a second, independent classification agrees on 99%% of names. Across the five constituencies %s of Hindu-name electors were struck off and %s of Muslim-name electors. '
    'Inside the same polling part, where the booth officer, the street and the housing are the same for everyone, Hindu-name electors were struck off %.1f to %.1f points more often, in %d of %d parts large enough to compare. '
    'The lists give religion and age separately, not together, so part of this gap may be an age gap.'
    % (pct(hin), pct(mus), min(h['diff_pp'] for h in HM), max(h['diff_pp'] for h in HM), sum(h['a_higher'] for h in HM), sum(h['parts'] for h in HM)))
R.table(['Constituency', 'Muslim names, % of roll', 'Hindu names struck off', 'Muslim names struck off', 'Gap inside parts (points)'],
        [[a['name'], pct(a['muslim_share_roll']), pct(a['hindu_rate']), pct(a['muslim_rate']), '%+.1f' % a['within_part']['hindu_minus_muslim']['diff_pp']] for a in A],
        widths=[3.4, 3, 3, 3, 3], right={1, 2, 3, 4})

R.h2('The 2002 roll')
R.p('The revision asks each elector to show a link to the 2002 intensive revision, through their own name or a parent\'s. Where the lists record it, %s of electors with no link were struck off against %s of those with one. '
    'Inside the same polling part unlinked electors were struck off %.0f to %.0f points more often, in %s of %s parts. Anyone who moved to the city after 2002, or whose family name is spelt differently on the old roll, starts at a disadvantage. Malakpet\'s list carries no linkage.'
    % (pct(ul), pct(lk), min(u['diff_pp'] for u in UL), max(u['diff_pp'] for u in UL), indian(sum(u['a_higher'] for u in UL)), indian(sum(u['parts'] for u in UL))))
fig, ax = plt.subplots(figsize=(8, 3))
x = range(len(LK))
ax.bar([i - 0.2 for i in x], [a['linked_rate'] for a in LK], 0.4, color='#0E5E6F', label='Linked to 2002')
ax.bar([i + 0.2 for i in x], [a['unlinked_rate'] for a in LK], 0.4, color='#C0392B', label='No 2002 link')
ax.set_xticks(list(x), [a['name'] for a in LK])
ax.set_ylabel('% struck off', fontsize=8)
ax.legend(fontsize=8, frameon=False)
style_axes(ax, 'Linked and unlinked electors struck off')
R.figure(fig, 'Figure 3. The four constituencies whose lists record the 2002 link.')

R.h2('Hearings')
R.p('%s electors kept on the draft roll were summoned to a hearing, %s of the pre-revision rolls, across %s hearing slots. Not being traceable to the last intensive revision was the commonest reason, %s of flags. '
    'The heaviest single slot listed %s cases, in %s, where the median slot listed %d. The lists do not record how long a slot lasted.'
    % (indian(t['hearing']), pct(100 * t['hearing'] / t['electors']), indian(s(lambda a: a['slots'])), pct(100 * ruleTot['Unmapped with Last SIR'] / sum(ruleTot.values())),
       indian(heavy['max_slot']), heavy['name'], heavy['median_slot']))
R.table(['Rule that sent the elector to a hearing'] + names + ['All five'],
        [[k] + [indian(a['rules'].get(k, 0)) for a in A] + [indian(ruleTot[k])] for k in S['rules']],
        widths=[4.4, 1.9, 1.9, 1.9, 2.2, 1.9, 1.9], right={1, 2, 3, 4, 5, 6}, size=7.5)

R.h2('Polling parts')
R.p('Part removal rates run from %.0f%% to %.0f%%, and %d parts lost more than 60%% of their roll: %s. Across parts, the Muslim-name share of the roll and the removal rate move in opposite directions in every constituency. A part far above its neighbours is where verification on the ground should start.'
    % (min(p['rate'] for p in P100), max(p['rate'] for p in P100), len(o60),
       andj(['%d in %s' % (a['parts_over_60'], a['name']) for a in A if a['parts_over_60']])))
top = sorted(P100, key=lambda p: -p['rate'])[:15]
R.table(['Constituency', 'Part', 'Locality', 'Electors', 'Struck off', '% struck off', 'Muslim names %', 'Untraceable % of removals'],
        [[p['ac'], p['part'], p['locality'] or '–', indian(p['electors']), indian(p['deleted']), pct(p['rate']), '%.0f' % p['muslim_share_roll'] if p['muslim_share_roll'] is not None else '–',
          '%.0f' % p['untraceable_share_of_deleted'] if p['untraceable_share_of_deleted'] is not None else '–'] for p in top],
        widths=[2.4, 1.1, 3.4, 1.6, 1.6, 1.7, 1.9, 2.3], right={1, 3, 4, 5, 6, 7}, size=7.5)

R.h2('Key insights')
R.bullets([
    '**%s electors struck off**, %s of the five pre-revision rolls, and %s more summoned to a hearing.' % (indian(t['deleted']), pct(t['rate']), indian(t['hearing'])),
    '**More names struck off than the 2023 margin in all %d constituencies**; more than every valid vote cast in %s.' % (len(A), andj([a['name'] for a in overV])),
    '**Yakutpura was won by %s votes** and lost %s names, %.0f times the margin.' % (indian(yak['e2023']['margin']), indian(yak['deleted']), yak['e2023']['deleted_over_margin']),
    '**%s of electors aged 80 and over struck off**, against %s of those aged 18 to 24.' % (pct(age[-1]), pct(age[0])),
    '**No link to the 2002 roll roughly doubled the chance of being struck off**: %s against %s.' % (pct(ul), pct(lk)),
    '**%s of removals entered as "untraceable or absent"**, ranging from %s to %s between constituencies.' % (pct(rsh['Untraceable/Absent']), pct(min(ut)), pct(max(ut))),
    '**%s cases listed for a single hearing slot** in %s.' % (indian(heavy['max_slot']), heavy['name']),
    '**%d polling parts lost more than 60%% of their roll.**' % len(o60),
])

R.h2('What this shows and what it does not')
R.p('The lists show how many electors were struck off, from which parts, and who they were by age, sex, religion estimated from name, and 2002 linkage. They do not show whether any individual removal was right. '
    'The reason code records the officer\'s entry, not the truth of it: a household that moved out of the Old City is a correct "shifted" deletion, and the files cannot tell it from an elector who was at home and missed. '
    'Religion and age are aggregated separately, so a religion gap may partly be an age gap. The Malakpet list used here is incomplete. These are the September lists; the Commission extended the calendar on 7 September, with hearings to 5 November and the final roll on 9 November, so restorations after hearings are not in these counts.')

# ============================================================ PART II
R.page_break()
R.h1('Part II: Constituency chapters')
for i, a in enumerate(A):
    e = a['e2023']
    R.h2(a['name'])
    R.stats([(indian(a['deleted']), 'struck off'), (pct(a['rate']), 'of the pre-revision roll'),
             ('%.1f×' % e['deleted_over_margin'], 'the 2023 margin'), (pct(e['deleted_over_valid']), 'of valid votes cast in 2023')])
    pr = [p for p in P100 if p['ac'] == a['name']]
    hi = max(pr, key=lambda p: p['rate'])
    lab = 'polling stations' if a['partlabel'] != 'part' else 'polling parts'
    R.p('%s had %s electors on its pre-revision roll, in %d %s. The lists struck %s of them off, %s, and summoned %s more to a hearing, %s. '
        'In 2023 %s won the seat with %s votes, by a margin of %s; the names struck off are %.1f times that margin and %s of the valid votes cast.'
        % (a['name'], indian(a['electors']), a['parts'], lab, indian(a['deleted']), pct(a['rate']), indian(a['hearing']), pct(a['hearing_rate']),
           e['winner'], indian(e['winner_votes']), indian(e['margin']), e['deleted_over_margin'], pct(e['deleted_over_valid'])))
    R.p('Officers entered %s of the removals as "permanently shifted" and %s as "untraceable or absent". %s of electors aged 80 and over were struck off, against %s of those aged 18 to 24. '
        'Women were struck off at %s and men at %s. Hindu-name electors were struck off at %s and Muslim-name electors at %s; inside the same part the gap is %+.1f points.'
        % (pct(100 * a['reasons']['Permanently Shifted'] / a['deleted']), pct(100 * a['reasons']['Untraceable/Absent'] / a['deleted']),
           pct(a['age_rate'][-1]), pct(a['age_rate'][0]), pct(a['female_rate']), pct(a['male_rate']), pct(a['hindu_rate']), pct(a['muslim_rate']),
           a['within_part']['hindu_minus_muslim']['diff_pp']))
    if a['linked']:
        R.p('Electors linked to the 2002 roll were struck off at %s, those with no link at %s; inside the same part the gap is %+.1f points, in %d of %d parts.'
            % (pct(a['linked_rate']), pct(a['unlinked_rate']), a['within_part']['unlinked_minus_linked']['diff_pp'], a['within_part']['unlinked_minus_linked']['a_higher'], a['within_part']['unlinked_minus_linked']['parts']))
    else:
        R.p('Malakpet\'s list carries no 2002 linkage and no part numbers, and %s electors on its roll appear in none of the three outcomes; its figures should not be cited alone until that is resolved.' % indian(a['unaccounted']))
    R.p('Hearings: %s slots, a median of %d cases per slot and %s in the heaviest. The %s with the highest removal rate is %s%s, at %s.'
        % (indian(a['slots']), a['median_slot'], indian(a['max_slot']), 'station' if a['partlabel'] != 'part' else 'part',
           ('%s ' % hi['part']) if a['partlabel'] == 'part' else '', ('(%s)' % hi['locality']) if hi['locality'] else '', pct(hi['rate'])))
    R.table(['Age band'] + S['bands'], [['% struck off'] + ['%.1f' % v for v in a['age_rate']]], widths=[2.4] + [1.7] * 8, right=set(range(1, 9)), size=7.5)

# ============================================================ CONCLUSION
R.page_break()
R.h1('Conclusion and what verification needs')
R.p('In five constituencies the revision struck off %s of the electors on the rolls, more names than the margin that decided every one of the five seats in 2023, and in two of them more than every valid vote cast. '
    'The burden fell on the old, and on those the process could not trace to a roll prepared 24 years earlier. The final roll has not yet been published, and the hearings are still being held.'
    % pct(t['rate']))
R.p('What would settle the questions the lists leave open, before the final roll:')
R.numbered([
    '**Verification of every removal entered as "untraceable or absent"**, %s names, by a visit with notice and a record of the attempt.' % indian(s(lambda a: a['reasons']['Untraceable/Absent'])),
    '**A review of every removal of an elector with no link to the 2002 roll**, since the link is the revision\'s own test and the gap it produces is the largest in the files.',
    '**Hearing schedules that allow each elector a real hearing**: no slot of several hundred cases.',
    '**Ground checks in the %d parts that lost more than 60%% of their roll**, and in every part far above the rest of its constituency.' % len(o60),
    '**Publication of restorations after hearings**, part by part, so that the final count can be set against these.',
])

R.h1('Method and sources')
R.bullets([
    'Pre-revision rolls, the list of the absent, shifted and dead, and the discrepancy and no-mapping lists: the Chief Electoral Officer, Telangana, for the five constituencies, September 2026, aggregated to the polling part.',
    'Religion: estimated from each elector\'s name; a second, independent classification agrees on 99% of names. The roll records none.',
    'Hearing schedules: the same lists, 28 August to 12 October 2026.',
    '2023 Assembly result: Election Commission of India.',
])
R.p('Deletion rate: electors on the list of the absent, shifted and dead divided by electors on the pre-revision roll, for the group in question. Within-part difference: the rate of one group minus the other inside each part, pooled across parts with at least 20 of each and weighted by the smaller group. Part counts sum exactly to the constituency totals. No name, EPIC number or address is published.')

out = sys.argv[1] if len(sys.argv) > 1 else '/home/user/reports/Hyderabad_OldCity_SIR_2026_Report.docx'
R.save(out)
R.save_html(out[:-5] + '.html')
if len(sys.argv) > 2:
    R.save_web(sys.argv[2])  # the page on the site, e.g. hyderabad/report
print('ok')
