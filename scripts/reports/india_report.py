#!/usr/bin/env python3
"""The overall report: All India, then Bihar and Hyderabad Old City.

    python3 scripts/reports/india_report.py OUT.docx [india/report]

Part I sets the reasons recorded for SIR removals side by side for every
state and union territory; Parts II and III give the headline findings of the
two list-level analyses, whose full reports stand on their own. Every figure
is computed from data/india, data/bihar and data/hyderabad.
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
BS, BA, BR = J('bihar', 'summary.json'), J('bihar', 'constituencies.json'), J('bihar', 'reasons.json')
HS = J('hyderabad', 'summary.json')
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

# Bihar headline figures
bt = BS['totals']
withM = [a for a in BA if a['margin2025']]
bover = [a for a in withM if a['total'] > a['margin2025']]
bfem = 100 * bt['female'] / (bt['female'] + bt['male'])
RT = BR['totals']
brsh = lambda k: 100 * RT[k] / BR['total']
xsF = sum(BR['by_sex'][k]['F'] - BR['by_sex'][k]['M'] for k in RT)
xsS = BR['by_sex']['shifted']['F'] - BR['by_sex']['shifted']['M']
yS = BR['by_age']['shifted'][0] + BR['by_age']['shifted'][1]
yW = BR['by_age_women']['shifted'][0] + BR['by_age_women']['shifted'][1]
babs = sum(1 for a in withM if a['r_absent'] > a['margin2025'])
bpolled = sum(a['votes2025'] for a in BA)
# Hyderabad headline figures
HA, ht = HS['acs'], HS['totals']
hs = lambda f: sum(f(a) for a in HA)
hover = [a for a in HA if a['deleted'] > a['e2023']['margin']]
hoverV = [a for a in HA if a['e2023']['deleted_over_valid'] > 100]
hrsh = {k: 100 * hs(lambda a: a['reasons'][k]) / ht['deleted'] for k in HS['reasons']}
hage = [100 * hs(lambda a: a['counts']['age_asd'][i]) / hs(lambda a: a['age_all'][i]) for i in range(len(HS['bands']))]
LK = [a for a in HA if a['linked']]
hlk = 100 * sum(a['counts']['lk_asd'] for a in LK) / sum(a['counts']['lk_all'] for a in LK)
hul = 100 * sum(a['deleted'] - a['counts']['lk_asd'] for a in LK) / sum(a['electors'] - a['counts']['lk_all'] for a in LK)
yak = next(a for a in HA if a['name'] == 'Yakutpura')

# ------------------------------------------------------------ cover
R.cover('Special Intensive Revision 2025-26', 'India: %s names left off the draft rolls' % crore(T['removed']),
        'The reasons recorded for every removal, state by state, with the list-level analyses of Bihar and Hyderabad Old City',
        [('names left off the draft rolls in %d states and union territories' % T['states'], indian(T['removed'])),
         ('of those split by reason entered as shifted, absent or other', pct(T['shares']['shifted_absent_other'])),
         ('entered as dead', pct(T['shares']['dead'])),
         ('entered as enrolled more than once', pct(T['shares']['duplicate']))])
R.h1('Contents')
R.toc()

# ============================================================ PART I
R.h1('Part I: All India')
R.h2('At a glance')
R.stats([(crore(T['removed']), 'left off the draft rolls'), (pct(T['shares']['shifted_absent_other']), 'shifted, absent or other'),
         (pct(T['shares']['dead']), 'dead'), ('%.1f' % T['per_100'], 'removed per 100 electors')])
R.p('The Special Intensive Revision has been carried out in three phases: Bihar in 2025, twelve states and union territories from November 2025, and eighteen more in 2026. '
    'In the %d that have published a draft roll, %s electors on the rolls before the revision were not carried onto it: %.1f for every 100. Tripura, the last, publishes its draft in December.'
    % (T['states'], indian(T['removed']), T['per_100']))
R.p('Every state gave a reason for most of its removals. Of the %s names it split by reason, %s (%s) were entered as dead, %s (%s) as shifted, absent or other, and %s (%s) as enrolled more than once. '
    'Deaths are about one in five. The other four in five rest on an officer\'s entry that the elector was not where the roll placed them, or was on it twice.'
    % (crore(T['removed'] - T['unsplit']), crore(T['dead']), pct(T['shares']['dead']), crore(T['shifted_absent_other']), pct(T['shares']['shifted_absent_other']),
       crore(T['duplicate']), pct(T['shares']['duplicate'])))
R.p('A reason is what an officer entered after a visit or its absence. It is not a finding. The figures cannot say how many entries were wrong.')

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
R.figure(fig, 'Figure 1. Names left off the draft rolls in each phase, by the reason entered, in lakh.', width=14)
R.p('The share entered as dead fell from %s in Bihar to %s in phase 2 and %s in phase 3, while the share entered as shifted, absent or other rose from %s to %s and %s. '
    'Removals per 100 electors rose with each phase: %.1f, %.1f and %.1f.'
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
R.figure(fig, 'Figure 2. States that published a split by reason, ordered by the share entered as shifted, absent or other.', width=15)
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
R.p('Split: Full, the reasons account for the total (within rounding); Short, the reasons leave some names unexplained (%s); None, no split was found (%s). Figures: rounded where the state published in lakh or crore (%d states).'
    % (andj(short), andj(none), len(rounded)))

R.h2('After the draft roll')
R.p('After the draft rolls, %d states have published how many more names they removed at hearings and on objections: %s in all. No state has said why, so these removals are outside every figure by reason in this report. '
    'Additions after the draft are outside it too; the final rolls of twelve phase 3 states are still to come.' % (AD['states'], lakh(AD['removed'])))

# ============================================================ PART II
R.page_break()
R.h1('Part II: Bihar, from the deletion lists')
R.p('Bihar is the one state where the deletion lists could be counted name by name. The full report, with a chapter for each of the 38 districts, is published separately.')
R.stats([(indian(bt['total']), 'names removed, both phases'), ('%d of %d' % (len(bover), len(withM)), 'seats: removals exceed the 2025 margin'),
         (pct(bfem), 'of the removed are women'), (pct(100 * bt['total'] / bpolled), 'of the votes polled in 2025')])
R.bullets([
    '**%s names removed** in both phases, %s before the draft roll and %s after it.' % (indian(bt['total']), indian(bt['p1']), indian(bt['p2'])),
    '**More than the 2025 winning margin in %d of %d seats.**' % (len(bover), len(withM)),
    '**Reasons entered in phase 1**: shifted %s, dead %s, absent %s, already enrolled %s. Names marked absent alone exceed the margin in %d seats.' % (pct(brsh('shifted')), pct(brsh('dead')), pct(brsh('absent')), pct(brsh('already_enrolled')), babs),
    '**Women are %s of the removed.** %s of the %s more women than men removed in phase 1 were entered as shifted, and %s of those marked shifted aged 18 to 29 are women.' % (pct(bfem), indian(xsS), indian(xsF), pct(100 * yW / yS)),
    '**NDA seats lost more names per elector than INDIA seats**, %.2f against %.2f per 100 by the 2020 winner.' % (BS['by_alliance_label']['2020']['NDA']['per_100'], BS['by_alliance_label']['2020']['INDIA']['per_100']),
])

# ============================================================ PART III
R.h1('Part III: Hyderabad Old City, from the lists')
R.p('In five Old City constituencies of Hyderabad the September lists hold every elector, not only the removed, so each group has a true rate of removal. The full report is published separately.')
R.stats([(indian(ht['deleted']), 'electors struck off'), (pct(ht['rate']), 'of the pre-revision rolls'),
         ('%d of %d' % (len(hover), len(HA)), 'seats: struck off exceed the 2023 margin'), (indian(ht['hearing']), 'kept but summoned to a hearing')])
R.bullets([
    '**%s electors struck off**, %s of the five rolls, and %s more summoned to a hearing.' % (indian(ht['deleted']), pct(ht['rate']), indian(ht['hearing'])),
    '**Reasons entered**: permanently shifted %s, untraceable or absent %s, dead %s, already enrolled %s.' % (pct(hrsh['Permanently Shifted']), pct(hrsh['Untraceable/Absent']), pct(hrsh['Death']), pct(hrsh['Already enrolled'])),
    '**More names struck off than every valid vote cast in 2023** in %s. Yakutpura was won by %s votes and lost %s names.' % (andj([a['name'] for a in hoverV]), indian(yak['e2023']['margin']), indian(yak['deleted'])),
    '**%s of electors aged 80 and over struck off**, against %s of those aged 18 to 24.' % (pct(hage[-1]), pct(hage[0])),
    '**No link to the 2002 roll roughly doubled the chance of being struck off**: %s against %s.' % (pct(hul), pct(hlk)),
])

# ============================================================ CONCLUSION
R.page_break()
R.h1('What the Election Commission should do')
R.p('%s names came off the draft rolls, about four in five of them on an entry that the elector had moved, could not be found, or was on the roll twice. The Election Commission should:' % crore(T['removed']))
R.numbered([
    '**Publish a state-by-state table of its own**, with the reason for every removal at the draft and after it, exact rather than rounded.',
    '**Publish the deletion lists with the reason against each name for every state**, as it did for Bihar, so that removals can be counted by booth, sex and age.',
    '**Publish the basis for entries marked absent and enrolled more than once.**',
    '**Publish the outcome of every claim and objection**, so that restorations can be set against removals.',
    '**Explain why the mix of reasons differs so widely between states** under one set of instructions.',
])

R.h1('Method and sources')
R.p('The All India figures are the Chief Electoral Officers\' own, published when each draft roll came out: from their press notes where those could be read (%s), and otherwise as reported in the press. Bihar\'s row is counted from the deletion lists. '
    'The reasons are grouped into the three every state reported. The state rows add to %s removed, against the %s reported nationally on 30 September 2026; the difference is rounding. Each row\'s source is listed on the method page of the site and in the downloadable table.'
    % (andj([s['state'] for s in S if s['source'] == 'primary']), crore(T['removed']), 'about 13.3 crore'))
R.p('Parts II and III are counted from the lists themselves; their methods are set out in their own reports. No name, EPIC number or address is published.')

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'reports', 'sir-india-report.docx')
R.save(out)
R.save_html(out[:-5] + '.html')
if len(sys.argv) > 2:
    R.save_web(sys.argv[2])
print('ok')
