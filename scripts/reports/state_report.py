#!/usr/bin/env python3
"""The four 2026 state reports: Tamil Nadu, Karnataka, West Bengal, Kerala.

    python3 scripts/reports/state_report.py <state> OUT.docx

state is tamilnadu, karnataka, westbengal or kerala. Writes the Word file and
the print-ready HTML beside it (scripts/reports/pdf.mjs prints that to PDF).

Each report says what the state's pages say, in the order the four state pages
share: the map, the roll step by step, West Bengal's adjudication, per 100
electors by district, the reasons, the city, women, after the draft, every
district, and then the 2026 election where a state has one. Every figure is
computed from data/<state>/*.json when the report is built.
"""
import json
import math
import os
import sys

import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from docx.shared import RGBColor

sys.path.insert(0, os.path.dirname(__file__))
from docxkit import Report, indian, lakh, pct, style_axes

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
J = lambda *p: json.load(open(os.path.join(ROOT, 'data', *p)))
crore = lambda x: '%.2f crore' % (x / 1e7)
andj = lambda xs: xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]
d1 = lambda v: '%.1f' % v
sg = lambda v: ('+' if v > 0 else '') + '%.1f' % v
RED, NAVY, GREY, AMBER, PURPLE, TEAL, WOMEN = '#C0392B', '#1F618D', '#95A5A6', '#D4AC0D', '#8E7CC3', '#17A589', '#AF3B6E'
REASON = 'A reason on the list is what the officer wrote down, and nobody checked it.'


def rank(xs):
    o = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and xs[o[j + 1]] == xs[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    a, b = rank(x), rank(y)
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    c = sum((p - ma) * (q - mb) for p, q in zip(a, b))
    return c / math.sqrt(sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b))


# ------------------------------------------------------------ charts
class Figs:
    """Numbers the figures and draws the chart forms the state pages use."""

    def __init__(self, R):
        self.R, self.n = R, 0

    def add(self, fig, caption, width=15):
        self.n += 1
        self.R.figure(fig, 'Figure %d. %s' % (self.n, caption), width=width)

    def map(self, geo, val, title, inset=None, inset_name=None, key='ac', legend_loc='lower left'):
        """Five quantile bins of one red, as on the site's maps. A city's seats
        are drawn again, enlarged, beside the state."""
        feats = geo['features']
        vals = sorted(v for v in (val(f['properties'][key]) for f in feats) if v is not None)
        q = [vals[int(t * (len(vals) - 1))] for t in (0.2, 0.4, 0.6, 0.8)]
        op = [0.14, 0.3, 0.48, 0.68, 0.9]
        ys = [p[1] for f in feats for p in self._pts(f['geometry'])]
        kx = math.cos((min(ys) + max(ys)) / 2 * math.pi / 180)

        def draw(ax, fs, lw):
            polys, cols = [], []
            for f in fs:
                v = val(f['properties'][key])
                b = sum(v > c for c in q) if v is not None else None
                for ring in self._rings(f['geometry']):
                    polys.append([(x * kx, y) for x, y in ring])
                    cols.append((0.75, 0.22, 0.17, op[b]) if b is not None else (0.9, 0.9, 0.9, 1))
            ax.add_collection(PolyCollection(polys, facecolors=cols, edgecolors='white', linewidths=lw))
            ax.autoscale_view()
            ax.set_aspect('equal')
            ax.axis('off')
        if inset:
            fig, (ax, ax2) = plt.subplots(1, 2, figsize=(8, 6.2), gridspec_kw={'width_ratios': [2.3, 1]})
            draw(ax2, [f for f in feats if f['properties'][key] in inset], 0.6)
            ax2.set_title(inset_name, fontsize=8, loc='left')
        else:
            fig, ax = plt.subplots(figsize=(7, 6.2))
        draw(ax, feats, 0.3)
        edges = [vals[0]] + q + [vals[-1]]
        from matplotlib.patches import Patch
        hs = [Patch(facecolor=(0.75, 0.22, 0.17, op[i]), label='%s to %s' % (d1(edges[i]), d1(edges[i + 1]))) for i in range(5)]
        (fig if inset else ax).legend(handles=hs, fontsize=7, frameon=False, loc='lower right' if inset else legend_loc, title='Per 100 electors', title_fontsize=7)
        ax.set_title(title, fontsize=9, fontweight='bold', loc='left')
        return fig

    @staticmethod
    def _rings(g):
        if g['type'] == 'Polygon':
            return [g['coordinates'][0]]
        return [p[0] for p in g['coordinates']]

    def _pts(self, g):
        return [p for r in self._rings(g) for p in r]

    def waterfall(self, steps, floor, title):
        fig, ax = plt.subplots(figsize=(8.5, 4.2))
        run = 0
        for i, (name, v, kind) in enumerate(steps):
            if kind == 'total':
                lo, hi, c, run = floor, v, NAVY, v
            elif kind == 'down':
                lo, hi, c, run = run - v, run, RED, run - v
            else:
                lo, hi, c, run = (run, run + v, TEAL, run + v) if v >= 0 else (run + v, run, RED, run + v)
            ax.bar(i, (hi - lo) / 1e5, bottom=lo / 1e5, color=c, width=0.7)
            lab = indian(v) if kind == 'total' else ('+' if kind == 'up' and v >= 0 else '−') + indian(abs(v))
            ax.text(i, hi / 1e5 + (max(s[1] for s in steps) - floor) / 1e5 * 0.015, lab, ha='center', va='bottom', fontsize=6.5)
        ax.set_xticks(range(len(steps)))
        ax.set_xticklabels([s[0] for s in steps], rotation=30, ha='right', fontsize=7)
        ax.set_ylim(floor / 1e5, max(s[1] for s in steps) / 1e5 * 1.04)
        ax.set_ylabel('Lakh electors', fontsize=8)
        style_axes(ax, title)
        return fig

    def hbars(self, rows, title, xlabel, hi=lambda r: False, fmt=d1, h=None):
        """rows: (name, value). Largest at the top."""
        fig, ax = plt.subplots(figsize=(7.5, h or max(3, 0.19 * len(rows) + 1)))
        y = list(range(len(rows)))[::-1]
        ax.barh(y, [r[1] for r in rows], color=[RED if hi(r) else NAVY for r in rows], height=0.62)
        for yy, r in zip(y, rows):
            ax.text(r[1] + max(x[1] for x in rows) * 0.01, yy, fmt(r[1]), va='center', fontsize=6.5)
        ax.set_yticks(y)
        ax.set_yticklabels([r[0] for r in rows], fontsize=7)
        ax.set_xlabel(xlabel, fontsize=8)
        ax.grid(axis='x', color='#E1E5E8', linewidth=0.6)
        ax.set_axisbelow(True)
        ax.spines[['top', 'right']].set_visible(False)
        ax.set_title(title, fontsize=10, loc='left', fontweight='bold')
        return fig

    def heat(self, names, cols, rows, title):
        fig, ax = plt.subplots(figsize=(7.5, max(3, 0.2 * len(names) + 1.2)))
        ax.imshow(rows, cmap='Blues', aspect='auto', vmin=0, vmax=100)
        for i, r in enumerate(rows):
            for j, v in enumerate(r):
                ax.text(j, i, '%.0f' % v, ha='center', va='center', fontsize=6.5, color='white' if v > 55 else '#1C2833')
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=7)
        ax.set_xticks(range(len(cols)))
        ax.set_xticklabels(cols, fontsize=7.5)
        ax.xaxis.tick_top()
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(title, fontsize=10, loc='left', fontweight='bold', pad=22)
        return fig

    def dumbbell(self, rows, title, a_name, b_name, ref=50):
        """rows: (name, a, b)."""
        fig, ax = plt.subplots(figsize=(7.5, max(3, 0.19 * len(rows) + 1.2)))
        y = list(range(len(rows)))[::-1]
        for yy, (n, a, b) in zip(y, rows):
            ax.plot([a, b], [yy, yy], color='#D5D8DC', lw=1.5, zorder=1)
        ax.scatter([r[1] for r in rows], y, color=GREY, s=16, zorder=2, label=a_name)
        ax.scatter([r[2] for r in rows], y, color=RED, s=16, zorder=3, label=b_name)
        ax.axvline(ref, color='#1C2833', lw=0.7, ls='--')
        ax.set_yticks(y)
        ax.set_yticklabels([r[0] for r in rows], fontsize=7)
        ax.legend(fontsize=7, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.04), ncol=2)
        ax.grid(axis='x', color='#E1E5E8', linewidth=0.6)
        ax.spines[['top', 'right']].set_visible(False)
        ax.set_title(title, fontsize=10, loc='left', fontweight='bold')
        return fig

    def slope(self, rows, title, a_name, b_name, ylabel):
        """rows: (name, a, b, highlight, label)."""
        fig, ax = plt.subplots(figsize=(6.5, 5.5))
        for n, a, b, h, lab in sorted(rows, key=lambda r: r[3]):
            ax.plot([0, 1], [a, b], color=RED if h else '#AEB6BF', lw=1.8 if h else 0.8, marker='o', ms=3 if h else 2, zorder=3 if h else 1)
        # labels on the right, nudged apart so none overlaps
        labs = sorted([(b, n, h) for n, a, b, h, lab in rows if h or lab])
        span = max(max(r[1], r[2]) for r in rows) - min(min(r[1], r[2]) for r in rows)
        gap, pos = span * 0.035, []
        for b, n, h in labs:
            y_ = max(b, pos[-1] + gap) if pos else b
            pos.append(y_)
            ax.text(1.03, y_, n, fontsize=6.5, va='center', color=RED if h else '#4D5B69')
        ax.set_xticks([0, 1])
        ax.set_xticklabels([a_name, b_name], fontsize=8)
        ax.set_xlim(-0.1, 1.45)
        ax.set_ylabel(ylabel, fontsize=8)
        style_axes(ax, title)
        return fig

    def multiples(self, panels, steps, title):
        """panels: (name, [values], highlight). Index with the first step at 100."""
        n = len(panels)
        cols = 6 if n > 20 else 5
        rows_ = math.ceil(n / cols)
        lo = min(min(p[1]) for p in panels)
        hi = max(max(p[1]) for p in panels)
        fig, axs = plt.subplots(rows_, cols, figsize=(8, 1.15 * rows_ + 0.6), sharey=True)
        for i, ax in enumerate(axs.flat):
            if i >= n:
                ax.axis('off')
                continue
            name, v, h = panels[i]
            ax.plot(range(len(v)), v, color=RED if h else NAVY, lw=1.6, marker='o', ms=2)
            ax.axhline(100, color='#1C2833', lw=0.5, ls='--')
            ax.set_ylim(lo - 2, hi + 2)
            ax.set_xticks([])
            ax.tick_params(labelsize=6)
            ax.spines[['top', 'right']].set_visible(False)
            ax.set_title(name, fontsize=6.5, loc='left', color=RED if h else '#1C2833')
        fig.suptitle(title, fontsize=10, fontweight='bold', x=0.02, ha='left')
        fig.text(0.02, 0.005, 'Each line runs %s.' % ', '.join(steps[:-1]) + ' and ' + steps[-1], fontsize=7, color='#4D5B69')
        fig.tight_layout(rect=(0, 0.02, 1, 0.97))
        return fig

    def strip(self, groups, title, xlabel):
        """groups: (label, [(value, highlight)])."""
        fig, ax = plt.subplots(figsize=(7.5, 0.8 * len(groups) + 1.2))
        for gi, (lab, pts) in enumerate(groups):
            y0 = len(groups) - 1 - gi
            for k, (v, h) in enumerate(pts):
                j = ((k * 7919) % 101) / 101 - 0.5
                ax.scatter(v, y0 + j * 0.5, s=12, color=RED if h else NAVY, alpha=0.8, lw=0)
        ax.set_yticks(range(len(groups)))
        ax.set_yticklabels([g[0] for g in groups][::-1], fontsize=7.5)
        ax.set_xlabel(xlabel, fontsize=8)
        ax.grid(axis='x', color='#E1E5E8', linewidth=0.6)
        ax.spines[['top', 'right']].set_visible(False)
        ax.set_title(title, fontsize=10, loc='left', fontweight='bold')
        return fig

    def margin_scatter(self, groups, title, xlabel):
        """groups: (label, colour, [(x, margin)])."""
        fig, ax = plt.subplots(figsize=(7.5, 5))
        mx = 0
        for lab, col, pts in groups:
            ax.scatter([p[0] / 1e3 for p in pts], [p[1] / 1e3 for p in pts], s=12, color=col, alpha=0.85, label=lab, lw=0)
            mx = max([mx] + [max(p) for p in pts])
        xs = [p[0] / 1e3 for g in groups for p in g[2]]
        ys = [p[1] / 1e3 for g in groups for p in g[2]]
        top = min(max(xs), max(ys)) * 1.05
        ax.plot([0, top], [0, top], ls='--', lw=0.8, color='#555', label='Margin equals the count')
        ax.set_xlim(min(0, min(xs)) - max(xs) * 0.02, max(xs) * 1.05)
        ax.set_ylim(0, max(ys) * 1.05)
        ax.set_xlabel(xlabel + ', thousand', fontsize=8)
        ax.set_ylabel('2026 winning margin, thousand votes', fontsize=8)
        ax.legend(fontsize=7, frameon=False)
        style_axes(ax, title)
        return fig


def winners_table(R, rows, rate_key, rate_label, over_label):
    R.table(['Party that won', 'Seats', rate_label, 'Against own district', over_label],
            [[w['party'], str(w['seats']), d1(w[rate_key]), sg(w['vs_district']), str(w['over_margin'])] for w in rows],
            widths=[3.6, 1.6, 3.2, 3.2, 3.6], right={1, 2, 3, 4}, size=8.5)


def limits_section(R, can, cannot):
    R.h2('What these tables show and what they cannot')
    R.p(can)
    R.bullets(cannot)


# ============================================================ TAMIL NADU
def tamilnadu(R):
    S, D, A = J('tamilnadu', 'summary.json'), J('tamilnadu', 'districts.json'), J('tamilnadu', 'constituencies.json')
    F, C = Figs(R), S['chennai']
    W = {w['party']: w for w in S['winners']}
    low = D[-1]
    byDead = max(D, key=lambda d: d['dead_share'])
    CH = sorted([a for a in A if a['district'] == 'Chennai'], key=lambda a: -a['per_100'])

    R.cover('Special Intensive Revision 2025-26', 'Tamil Nadu: %s names left off the draft roll' % lakh(S['removed']),
            'Where the names were removed, on what recorded reason, what the final roll put back, and how the removals compare with the 2026 result',
            [('names left off the draft roll of 19 December 2025', indian(S['removed'])),
             ('of every 100 electors on the roll before the revision', d1(S['per_100'])),
             ('constituencies where more names were left off than the 2026 winning margin', '%d of %d' % (S['over_margin'], S['acs'])),
             ('removed per 100 electors in Chennai', d1(C['per_100']))])
    R.h1('Contents')
    R.toc()

    R.h1('In short')
    R.numbered([
        'The revision left %s names off Tamil Nadu\'s draft roll, the list published on 19 December 2025 for electors to check and contest. That is %s of every 100 electors on the roll before the revision began.' % (lakh(S['removed']), d1(S['per_100'])),
        'In %d of the %d assembly constituencies, the seats of the state legislature, more names were left off the draft roll than the 2026 winning margin, the votes by which the winner beat the runner-up. In those seats the removals were large enough to decide the result. If the names marked dead are left out and the rest are counted at each seat\'s own turnout, the removed voters still outnumber the margin in %d seats.' % (S['over_margin'], S['acs'], S['could_change']),
        '%s were entered as shifted or absent, %s as dead and %s as enrolled in more than one place. %s' % (pct(S['shares']['shifted_absent']), pct(S['shares']['dead']), pct(S['shares']['multiple']), REASON),
        'Chennai lost %s of every 100 electors, more than twice the state\'s rate. Its %d constituencies hold %s of the state\'s roll and %s of the names removed.' % (d1(C['per_100']), C['acs'], pct(S['chennai_share_of_roll']), pct(S['chennai_share_of_removed'])),
        'The final roll of 23 February 2026 was %s larger than the draft. That rise includes new voters, so it comes to at most %s of the names removed. The roll is still %s smaller than before the revision.' % (lakh(S['added_net']), pct(S['made_up_pct']), lakh(S['net_fall'])),
    ])
    R.p('The Chief Electoral Officer, who keeps the state\'s rolls for the Election Commission, has published no split of the removals by sex or age. So the tables cannot show whether women, the old or the young were removed more often. They show where names were removed, and they cannot show why.', italic=True)

    R.h1('The roll')
    R.stats([(lakh(S['removed']), 'left off the draft roll'), (d1(S['per_100']), 'per 100 electors'),
             (pct(S['shares']['shifted_absent']), 'shifted or absent'), (lakh(S['net_fall']), 'still off at the final roll')])

    R.h2('Constituency by constituency')
    byAc = {a['ac']: a for a in A}
    F.add(F.map(J('geo', 'tamilnadu.json'), lambda ac: byAc[ac]['per_100'] if ac in byAc else None, 'Names left off the draft roll per 100 electors',
                inset=[a['ac'] for a in CH], inset_name='Chennai, enlarged'),
          'Each constituency shaded by the names left off the draft roll for every 100 electors on the roll before the revision, in five bins with equal numbers of seats. Boundaries from DataMeet\'s assembly constituency map (CC BY 2.5 India), simplified.', width=15)
    R.p('Removals were heaviest in %s, then in %s. By constituency they run from %s per 100 electors in %s to %s in %s.' % (S['top_districts'][0], andj(S['top_districts'][1:]), d1(S['rate_min_v']), S['rate_min'], d1(S['rate_max_v']), S['rate_max']))

    R.h2('The roll, step by step')
    F.add(F.waterfall([('Roll before the revision', S['before'], 'total'), ('Dead', S['dead'], 'down'), ('Shifted or absent', S['shifted_absent'], 'down'),
                       ('Enrolled in more than one place', S['multiple'], 'down'), ('Draft roll', S['draft'], 'total'),
                       ('Net change after the draft', S['added_net'], 'up'), ('Final roll', S['final'], 'total')],
                      math.floor(S['draft'] * 0.8 / 1e5) * 1e5, 'Tamil Nadu, from the roll before the revision to the final roll'),
          'The bars start above zero so that the changes can be seen. The figure on each bar is the count.')
    R.p('The roll before the revision held %s names. %s were left off the draft roll of 19 December 2025, which held %s. Electors could then file claims, on Form 6, to add a name, and objections, on Form 7, to remove one. Together these raised the roll by a net %s to %s on the final roll of 23 February 2026, the roll that stands after the revision.'
        % (crore(S['before']), indian(S['removed']), crore(S['draft']), indian(S['added_net']), crore(S['final'])))

    R.h2('Per 100 electors, by district')
    F.add(F.hbars([(d['district'], d['per_100']) for d in D], 'Names left off the draft roll per 100 electors, by district', 'Removed per 100 electors',
                  hi=lambda r: r[0] == 'Chennai'), 'Names left off the draft roll of 19 December 2025, for every 100 electors on the roll before the revision. Chennai in red.', width=14)
    R.p('Chennai lost %s of every 100 electors, against %s for the state. The next four are %s. %s lost the fewest, %s.'
        % (d1(D[0]['per_100']), d1(S['per_100']), andj(['%s (%s)' % (d['district'], d1(d['per_100'])) for d in D[1:5]]), low['district'], d1(low['per_100'])))

    R.h2('The reasons, district by district')
    F.add(F.heat([d['district'] for d in D], ['Dead', 'Shifted or absent', 'In more than one place'],
                 [[100 * d[k] / d['removed'] for k in ('dead', 'shifted_absent', 'multiple')] for d in D], 'Share of each district\'s removals by reason, %'),
          'Districts in the same order as the figure above, from the highest removal rate to the lowest.', width=13)
    R.p('Across the state, %s of the names were entered as shifted or absent and %s as dead. In Chennai the share entered as shifted or absent is %s. '
        'Across the %d constituencies, the removal rate and the share entered as shifted or absent rise together. Their rank correlation, a measure that runs from -1 to 1 and comes near 1 when two things rise in step, is %.2f. So where many names were removed, most were marked as people who had moved or could not be found. '
        'Where fewer names were removed, more of them were entered as dead, up to %s in %s. %s'
        % (pct(S['shares']['shifted_absent']), pct(S['shares']['dead']), pct(C['shifted_share']), S['acs'], S['rho_rate_shifted'], pct(byDead['dead_share']), byDead['district'], REASON))

    R.h2('Chennai')
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    y = list(range(len(CH)))[::-1]
    left = [0] * len(CH)
    for k, lab, col in (('dead', 'Dead', GREY), ('shifted_absent', 'Shifted or absent', NAVY), ('multiple', 'Enrolled in more than one place', AMBER)):
        v = [100 * a[k] / a['before'] for a in CH]
        ax.barh(y, v, left=left, color=col, label=lab, height=0.65)
        left = [p + q for p, q in zip(left, v)]
    ax.set_yticks(y)
    ax.set_yticklabels([a['name'] for a in CH], fontsize=7.5)
    ax.set_xlabel('Removed per 100 electors', fontsize=8)
    ax.legend(fontsize=7, frameon=False, loc='lower right')
    style_axes(ax, 'Chennai\'s constituencies, removed per 100 electors by reason')
    F.add(fig, 'The sixteen constituencies of Chennai district, by names removed per 100 electors on the roll before the revision.', width=14)
    R.p('Every one of Chennai\'s %d constituencies lost more than %d of every 100 electors. %s lost %s, the most of any seat in the state. Chennai holds %s of the state\'s roll and %s of the names removed, %s names in all. '
        '%s of Chennai\'s removals were entered as shifted or absent and %s as dead. At the final roll Chennai\'s roll was still %s per 100 smaller than before the revision.'
        % (len(CH), math.floor(CH[-1]['per_100']), CH[0]['name'], d1(CH[0]['per_100']), pct(S['chennai_share_of_roll']), pct(S['chennai_share_of_removed']), indian(C['removed']),
           pct(C['shifted_share']), pct(C['dead_share']), d1(C['net_per_100'])))

    R.h2('Women')
    WD = {}
    for a in A:
        w = WD.setdefault(a['district'], [0, 0, 0, 0])
        w[0] += a['draft_women']; w[1] += a['final_women']; w[2] += a['draft']; w[3] += a['final']
    WR = sorted([(k, 100 * w[0] / w[2], 100 * (w[1] - w[0]) / (w[3] - w[2])) for k, w in WD.items()], key=lambda r: -(r[2] - r[1]))
    tw = [sum(w[i] for w in WD.values()) for i in range(4)]
    kw = sum(r[2] > r[1] for r in WR)
    R.p('The Chief Electoral Officer has published no split of the names left off by sex, and no roll by sex from before the revision, so women\'s share of the removals cannot be counted. What can be counted is the change after the draft.')
    F.add(F.dumbbell(WR, 'Women\'s share of the draft roll and of the net rise to the final roll, %', 'Share of the draft roll', 'Share of the net rise to the final roll'),
          'For each district, the grey dot is women\'s share of the draft roll and the red dot their share of the net rise from the draft to the final roll. The dashed line is half.', width=14)
    R.p('Women were %s of the draft roll and %s of the net rise to the final roll. Their share of the rise was higher than their share of the draft in %s of the %d districts. '
        'The rise counts new voters as well as names put back, so it does not say how many women\'s names were restored. Women were %s of the final roll.'
        % (pct(100 * tw[0] / tw[2]), pct(100 * (tw[1] - tw[0]) / (tw[3] - tw[2])), 'all' if kw == len(WR) else str(kw), len(WR), pct(S['women_final_pct'])))

    R.h2('After the draft')
    F.add(F.slope([(d['district'], d['per_100'], d['net_per_100'], d['district'] == 'Chennai', 0 < i < 4) for i, d in enumerate(D)],
                  'Removed at the draft and the fall that remains at the final roll', 'At the draft', 'At the final roll', 'Per 100 electors on the roll before the revision'),
          'Each line is a district. The flatter the line, the less was made up. Chennai in red.', width=12)
    R.p('The final roll is %s larger than the draft, and still %s smaller than the roll before the revision, a fall of %s of every 100 electors. The rise from the draft is at most %s of the names removed, and it includes new voters. '
        'Chennai\'s roll is %s per 100 smaller than before.' % (lakh(S['added_net']), lakh(S['net_fall']), d1(S['net_per_100']), pct(S['made_up_pct']), d1(C['net_per_100'])))

    R.h2('Every district')
    R.table(['District', 'Seats', 'Roll before', 'Removed', 'Per 100', 'Dead', 'Shifted or absent', 'More than one place', 'Final roll', 'Net fall per 100'],
            [[d['district'], str(d['acs']), indian(d['before']), indian(d['removed']), d1(d['per_100']), indian(d['dead']), indian(d['shifted_absent']), indian(d['multiple']), indian(d['final']), d1(d['net_per_100'])] for d in D],
            widths=[3.0, 1.0, 2.0, 1.8, 1.2, 1.6, 1.9, 1.6, 2.0, 1.4], size=7)

    # ---- the election
    R.h1('The 2026 election')
    R.h2('Names removed against the winning margin')
    G = [('TVK', AMBER), ('DMK', RED), ('AIADMK', NAVY)]
    groups = [(p, c, [(a['removed'], a['margin']) for a in A if a['winner'] == p]) for p, c in G] + [('Other parties', GREY, [(a['removed'], a['margin']) for a in A if a['winner'] not in ('TVK', 'DMK', 'AIADMK')])]
    F.add(F.margin_scatter(groups, 'Names left off the draft roll against the 2026 winning margin', 'Names left off the draft roll'),
          'Each dot is a constituency, coloured by the party that won it. Dots below the dashed line are seats where more names were left off than the winner won by.', width=14)
    R.p('In %d of the %d constituencies, more names were left off the draft roll than the 2026 winning margin. In those seats the removals were large enough to decide the result. Whether they did depends on how those people would have voted, and the lists cannot show that. '
        'The removal rate and the margin as a share of votes rise together a little (rank correlation %.2f). The seats that lost the most names were therefore not the closest contests.' % (S['over_margin'], S['acs'], S['rho_rate_margin']))

    R.h2('How many seats, on each count')
    R.stats([('%d of %d' % (S['over_margin'], S['acs']), 'every name left off the draft'), ('%d of %d' % (S['net_over_margin'], S['acs']), 'the net fall at the final roll'),
             ('%d of %d' % (S['could_change'], S['acs']), 'the living removed, at the seat\'s turnout')])
    R.p('Three counts set the removals against the margin, from the widest to the narrowest. The first counts every name left off the draft. The second counts the fall that remains on the final roll. '
        'The third leaves out the names marked dead and counts the rest at the seat\'s own 2026 turnout. Even on the narrowest count the removed voters outnumber the margin in %d of the %d seats. '
        'In the other %d, the runner-up could not have won even if every living person removed had voted, at the seat\'s turnout, for the runner-up.' % (S['could_change'], S['acs'], S['acs'] - S['could_change']))

    R.h2('Removals by the party that won')
    big = ['TVK', 'DMK', 'AIADMK']
    F.add(F.strip([('%s (%d seats)' % (p, W[p]['seats']), [(a['per_100'], a['district'] == 'Chennai') for a in A if a['winner'] == p]) for p in big]
                  + [('Other parties', [(a['per_100'], a['district'] == 'Chennai') for a in A if a['winner'] not in big])],
                  'Removed per 100 electors in every seat, by the party that won it', 'Removed per 100 electors'),
          'Each dot is a constituency. Chennai\'s sixteen seats are in red.', width=14)
    winners_table(R, S['winners'], 'per_100', 'Removed per 100', 'Removed over margin')
    R.p('Seats won by TVK lost %s of every 100 electors, against %s in DMK seats and %s in AIADMK seats. Most of that gap comes from where the seats are. TVK won most of the city seats, and the city seats lost the most names. '
        'To allow for that, each seat\'s rate can be set against the rate of its own district. On that measure each party\'s seats come out at %s for TVK, %s for the DMK and %s for the AIADMK, where a minus means fewer removals than the district as a whole. '
        'TVK won %d seats, the DMK %d and the AIADMK %d, and %d of the %d seats changed hands from 2021.'
        % (d1(W['TVK']['per_100']), d1(W['DMK']['per_100']), d1(W['AIADMK']['per_100']), sg(W['TVK']['vs_district']), sg(W['DMK']['vs_district']), sg(W['AIADMK']['vs_district']),
           S['seats_2026']['TVK'], S['seats_2026']['DMK'], S['seats_2026']['AIADMK'], S['changed_hands'], S['acs']))
    limits_section(R, 'The tables show how many names were left off the draft in every constituency, on what recorded reason, what the final roll put back, and how those numbers compare with the 2026 margins.',
                   ['Whether women, the old or the young were removed more often. The Chief Electoral Officer has not published the removals by sex or age.',
                    'Whether each removal was right. %s' % REASON,
                    'How anyone removed would have voted, or why the removals fell where they did. No list of removals can show intent.'])

    R.h1('What the Election Commission should do')
    R.p('%s names came off Tamil Nadu\'s draft roll, %s of them on an entry that the elector had moved or could not be found. The Election Commission should do five things.' % (lakh(S['removed']), lakh(S['shifted_absent'])))
    R.numbered([
        'Publish the names removed by sex and age for every constituency, with the roll before the revision by sex, so that it can be seen who was removed.',
        'Publish the basis for the %s entries marked shifted or absent, including the visits made and the notice given.' % lakh(S['shifted_absent']),
        'Publish how many of those added for the final roll had been left off the draft, so that names restored can be told apart from new voters.',
        'Explain why Chennai lost %s of every 100 electors, more than twice the state\'s rate.' % d1(C['per_100']),
        'Publish the roll the election was held on, constituency by constituency, so that turnout can be measured against it.',
    ])

    R.h1('Method and sources')
    R.p('The names left off the draft roll of 19 December 2025 are the Chief Electoral Officer\'s table for each of the %d assembly constituencies, under three reasons, deceased, shifted or absent, and enrolled at more than one place. '
        'The constituency rows add up to the district totals and to the state total of %s. No constituency table of the roll the revision started from has been published, so the draft roll plus the names left off it is that roll, %s in all, and every figure per 100 is out of it. '
        'That sum equals the state total announced with the draft.' % (S['acs'], indian(S['removed']), indian(S['before'])))
    R.p('The final roll of 23 February 2026, by constituency and by sex, is also the Chief Electoral Officer\'s table. The rise from the draft to the final roll is the names added on claims less those removed on objections, so it counts new voters as well as names put back, and it is the most that can have been restored.')
    R.p('The 2026 winner, runner-up and margin for every seat are from the Election Commission\'s constituency result pages, checked against its state-wise pages. Turnout is the votes polled over the final roll, because the result pages carry no electors. '
        'The 2021 result is from the Election Commission\'s statistical report, through a published compilation of it whose seat totals equal the declared result.')
    R.p('Three counts are set against the margin. A seat is counted on the first when the names left off the draft exceed the 2026 margin, and on the second when the fall from the roll before the revision to the final roll exceeds it. '
        'The third leaves out the names marked dead and multiplies the rest by the seat\'s turnout. It still assumes every one of those voters would have chosen the runner-up, which no one can know. '
        'Each seat\'s removal rate is also set against the rate of its own district, and those differences are averaged for each party\'s seats, because Chennai and the districts around it removed far more names than the rest of the state and the parties did not win evenly across districts.')
    R.p('The map uses DataMeet\'s assembly constituency map, licensed CC BY 2.5 India. Only counts are published, never a name, EPIC number or address.')

    R.h1('Every constituency')
    R.table(['No.', 'Constituency', 'District', 'Roll before', 'Removed', 'Per 100', 'Dead', 'Net fall per 100', 'Won 2026', 'Margin', 'Over margin'],
            [[str(a['ac']), a['name'], a['district'], indian(a['before']), indian(a['removed']), d1(a['per_100']), indian(a['dead']), d1(a['net_per_100']), a['winner'], indian(a['margin']), 'Yes' if a['over_margin'] else 'No'] for a in A],
            widths=[0.8, 2.6, 2.3, 1.7, 1.5, 1.1, 1.4, 1.3, 1.4, 1.4, 1.2], right={0, 3, 4, 5, 6, 7, 9}, size=6.5)


# ============================================================ KARNATAKA
def karnataka(R):
    S, D = J('karnataka', 'summary.json'), J('karnataka', 'districts.json')
    F, B, RS = Figs(R), S['bengaluru'], S['rest']
    BL = [d for d in D if d['bengaluru']]
    nxt = [d for d in D if not d['bengaluru']]
    low = D[-1]
    RK = [('absent', 'Absent'), ('shifted', 'Shifted'), ('dead', 'Dead'), ('duplicate', 'Already enrolled'), ('other', 'Other')]

    R.cover('Special Intensive Revision 2026', 'Karnataka: %s names left off the draft roll' % crore(S['removed']),
            'Where the names were removed, district by district, on what recorded reason, and what the roll looked like while notices were still being heard',
            [('names left off the draft roll of 24 August 2026', indian(S['removed'])),
             ('of every 100 electors on the roll of 16 June 2026', d1(S['per_100'])),
             ('of the names removed were in Bengaluru\'s four districts', pct(B['share_of_removed'])),
             ('of the names removed had come back by 9 October', pct(S['made_up_pct']))])
    R.h1('Contents')
    R.toc()

    R.h1('In short')
    R.numbered([
        'The revision left %s names off Karnataka\'s draft roll, the list published on 24 August 2026 for electors to check and contest. That is %s of every 100 electors on the roll of 16 June, before the revision began.' % (crore(S['removed']), d1(S['per_100'])),
        'Bengaluru\'s four districts lost %s of every 100 electors. They hold %s of the state\'s roll and %s of the names removed.' % (d1(B['per_100']), pct(B['share_of_roll']), pct(B['share_of_removed'])),
        '%s were entered as shifted, %s as absent, %s as dead and %s as already enrolled elsewhere. %s' % (pct(S['shares']['shifted']), pct(S['shares']['absent']), pct(S['shares']['dead']), pct(S['shares']['duplicate']), REASON),
        'By 9 October the roll had risen by %s since the draft, %s of the names removed. In Bengaluru it rose by %s. The rise counts new voters as well as names put back.' % (indian(S['added_sep']), pct(S['made_up_pct']), indian(B['added_sep'])),
    ])
    R.p('The Chief Electoral Officer, who keeps the state\'s rolls for the Election Commission, published the revision by its 34 election districts only. So no figure here is by assembly constituency, and the removals cannot be set against the winning margins of the 2023 election. '
        'The names removed are not split by sex. The final roll is due on 27 October 2026.', italic=True)

    R.h1('The roll')
    R.stats([(crore(S['removed']), 'left off the draft roll'), (d1(S['per_100']), 'per 100 electors'),
             (d1(B['per_100']), 'per 100 in Bengaluru'), (pct(S['made_up_pct']), 'back by 9 October')])

    R.h2('District by district')
    byN = {d['district']: d for d in D}
    F.add(F.map(J('geo', 'karnataka.json'), lambda n: byN[n]['per_100'] if n in byN else None, 'Names left off the draft roll per 100 electors, by district',
                inset=[d['district'] for d in BL if d['district'].startswith('B.B.M.P')], inset_name='Bengaluru city, enlarged', key='name', legend_loc='upper left'),
          'Each of the Chief Electoral Officer\'s 34 election districts shaded by the names left off the draft per 100 electors on the roll of 16 June 2026, in five bins. District shapes are built from DataMeet\'s assembly constituency map (CC BY 2.5 India), each constituency placed in its election district as the Election Commission lists it.', width=15)
    R.p('The revision was published by district only. The four Bengaluru districts stand apart from everywhere else, and outside them the rate runs from %s per 100 in %s to %s in %s.'
        % (d1(low['per_100']), low['district'], d1(nxt[0]['per_100']), nxt[0]['district']))

    R.h2('The roll, step by step')
    F.add(F.waterfall([('Roll of 16 June', S['before'], 'total'), ('Shifted', S['reasons']['shifted'], 'down'), ('Dead', S['reasons']['dead'], 'down'),
                       ('Absent', S['reasons']['absent'], 'down'), ('Already enrolled', S['reasons']['duplicate'], 'down'), ('Other', S['reasons']['other'], 'down'),
                       ('Draft roll', S['draft'], 'total'), ('Net change after the draft', S['added_sep'], 'up'), ('Roll of 9 October', S['sep'], 'total')],
                      math.floor(S['draft'] * 0.8 / 1e6) * 1e6, 'Karnataka, from 16 June to 9 October 2026'),
          'The bars start above zero so that the changes can be seen. The figure on each bar is the count. The final roll is due on 27 October 2026.')
    R.p('The roll of 16 June 2026 held %s names. %s were left off the draft roll of 24 August, which held %s. Electors could then file claims, on Form 6, to add a name, and objections, on Form 7, to remove one. By 9 October those had closed, notices were still being heard, and the roll stood at %s.'
        % (crore(S['before']), indian(S['removed']), crore(S['draft']), crore(S['sep'])))

    R.h2('Per 100 electors, by district')
    F.add(F.hbars([(d['district'], d['per_100']) for d in D], 'Names left off the draft roll per 100 electors, by district', 'Removed per 100 electors',
                  hi=lambda r: byN[r[0]]['bengaluru']), 'Names left off the draft roll of 24 August 2026, for every 100 electors on the roll of 16 June 2026. Bengaluru\'s four districts in red.', width=14)
    R.p('Bengaluru\'s four districts lost between %s and %s of every 100 electors, against %s for the state. The next highest is %s at %s. %s lost the fewest, %s.'
        % (d1(min(d['per_100'] for d in BL)), d1(D[0]['per_100']), d1(S['per_100']), nxt[0]['district'], d1(nxt[0]['per_100']), low['district'], d1(low['per_100'])))

    R.h2('The reasons, district by district')
    F.add(F.heat([d['district'] for d in D], [k[1] for k in RK], [[d['shares'][k[0]] for k in RK] for d in D], 'Share of each district\'s removals by reason, %'),
          'Districts in the same order as the figure above, from the highest removal rate to the lowest.', width=13)
    R.p('Across the state, %s of the names were entered as shifted and %s as absent, %s as dead and %s as already enrolled elsewhere. The more names a district removed, the larger the share marked shifted or absent. Their rank correlation, a measure that runs from -1 to 1 and comes near 1 when two things rise in step, is %.2f. '
        'Where fewer were removed, more were entered as dead, up to %s in %s. %s'
        % (pct(S['shares']['shifted']), pct(S['shares']['absent']), pct(S['shares']['dead']), pct(S['shares']['duplicate']), S['rho_rate_shifted'], pct(S['dead_max']['share']), S['dead_max']['district'], REASON))

    R.h2('Bengaluru')
    R.stats([(pct(B['share_of_roll']), 'of the roll before the revision'), (pct(B['share_of_removed']), 'of the names removed'),
             (d1(B['per_100']), 'removed per 100, against %s elsewhere' % d1(RS['per_100']))])
    fig, ax = plt.subplots(figsize=(7, 2.4))
    for i, (lab, sa, dd) in enumerate([('Bengaluru', B['shifted_absent_share'], B['dead_share']), ('Rest of the state', RS['shifted_absent_share'], RS['dead_share'])]):
        ax.barh(1 - i, sa, color=NAVY, height=0.55, label='Shifted or absent' if i == 0 else None)
        ax.barh(1 - i, dd, left=sa, color=GREY, height=0.55, label='Dead' if i == 0 else None)
        ax.barh(1 - i, 100 - sa - dd, left=sa + dd, color=AMBER, height=0.55, label='Already enrolled or other' if i == 0 else None)
        ax.text(sa / 2, 1 - i, pct(sa), color='white', ha='center', va='center', fontsize=7.5)
    ax.set_yticks([1, 0])
    ax.set_yticklabels(['Bengaluru', 'Rest of the state'], fontsize=8)
    ax.set_xlim(0, 100)
    ax.set_xlabel('% of names removed', fontsize=8)
    ax.legend(fontsize=7, frameon=False, ncol=3, loc='upper center', bbox_to_anchor=(0.5, -0.3))
    style_axes(ax, 'Reasons entered, Bengaluru and the rest of the state')
    F.add(fig, 'Bangalore Urban and the North, Central and South districts of the city corporation, B.B.M.P., against the other thirty districts.', width=13)
    R.p('Bengaluru holds %s of Karnataka\'s roll and %s of the names removed, %s names in all. %s of them were entered as shifted or absent and %s as dead. In the rest of the state the figures are %s and %s. Bangalore Rural is outside these four.'
        % (pct(B['share_of_roll']), pct(B['share_of_removed']), lakh(B['removed']), pct(B['shifted_absent_share']), pct(B['dead_share']), pct(RS['shifted_absent_share']), pct(RS['dead_share'])))

    R.h2('Women')
    R.p('The roll of 16 June is published as a total only and the names left off are not split by sex, so women\'s share of the removals cannot be counted from the Chief Electoral Officer\'s tables. '
        'Women were %s of the draft roll and %s of the roll of 9 October. The roll before the revision gives no count by sex, so these two figures cannot show whether women were left off more often than men.'
        % (pct(S['women_draft_pct']), pct(S['women_sep_pct'])))

    R.h2('After the draft')
    F.add(F.multiples([(d['district'], [100, 100 * d['draft'] / d['before'], 100 * d['sep'] / d['before']], d['bengaluru']) for d in D],
                      ['16 June', 'the draft', '9 October'], 'Each district\'s roll, 16 June 2026 = 100'),
          'Each small chart follows one district\'s roll from 16 June to the draft and to 9 October, with 16 June set at 100. The dashed line is the June level. Bengaluru\'s four districts in red.', width=16)
    R.p('By 9 October the roll had risen by %s since the draft, %s of the %s names removed. In Bengaluru it rose by %s, against %s names removed. Elsewhere the rise came to %s of the names removed. '
        'The final roll may change this, and the rise includes new voters, so it is the most that could have been restored.'
        % (indian(S['added_sep']), pct(S['made_up_pct']), crore(S['removed']), indian(B['added_sep']), lakh(B['removed']), pct(RS['made_up_pct'])))

    R.h2('Every district')
    R.table(['District', 'Roll before', 'Removed', 'Per 100', 'Shifted', 'Absent', 'Dead', 'Already enrolled', 'Other', 'Roll 9 Oct'],
            [[d['district'], indian(d['before']), indian(d['removed']), d1(d['per_100']), indian(d['shifted']), indian(d['absent']), indian(d['dead']), indian(d['duplicate']), indian(d['other']), indian(d['sep'])] for d in D],
            widths=[3.2, 2.0, 1.8, 1.2, 1.7, 1.6, 1.6, 1.6, 1.4, 2.0], size=7)
    limits_section(R, 'The tables show how many names were left off the draft in each of the 34 election districts, on what recorded reason, and how the roll stood on 9 October.',
                   ['Which constituencies lost the most names, or how the removals compare with the margins of the 2023 election. Nothing has been published by assembly constituency.',
                    'Whether women, the old or the young were removed more often.',
                    'Whether each removal was right. %s' % REASON])

    R.h1('What the Election Commission should do')
    R.p('%s names came off Karnataka\'s draft roll, %s of them in Bengaluru. The Election Commission should do five things before the final roll.' % (crore(S['removed']), lakh(B['removed'])))
    R.numbered([
        'Publish the names removed by assembly constituency and polling station, with the reason, so that the removals can be set against the places they came from.',
        'Publish the names removed by sex and age, with the roll of 16 June by sex.',
        'Publish the basis for the %s entries marked shifted or absent, including the visits made and the notice given.' % lakh(S['reasons']['shifted'] + S['reasons']['absent']),
        'Explain why Bengaluru lost %s of every 100 electors, against %s in the rest of the state.' % (d1(B['per_100']), d1(RS['per_100'])),
        'Publish with the final roll how many of those added had been left off the draft, so that names restored can be told apart from new voters.',
    ])

    R.h1('Method and sources')
    R.p('The Chief Electoral Officer, Karnataka, published the draft roll on 24 August 2026 with a table of the names left off it, by election district and under five reasons, absent, permanently shifted, dead, already enrolled and other. '
        'The %d district rows add up to the state row, %s names out of %s, and in every district the names removed and the forms digitised add up to the roll of 16 June 2026.' % (S['districts'], indian(S['removed']), indian(S['before'])))
    R.p('The Chief Electoral Officer published every table of the revision by its 34 election districts and for the state, and none by assembly constituency. Bengaluru appears as four of those districts, Bangalore Urban and the North, Central and South districts of the city corporation, B.B.M.P.')
    R.p('The final roll is due on 27 October 2026. Until then the latest figures are the roll of 9 October 2026, by district and sex. The rise from the draft to that roll is the names added less those removed since, so it counts new voters as well as names put back.')
    R.p('The map joins the constituency boundaries of DataMeet\'s assembly constituency map, licensed CC BY 2.5 India, by the district each constituency belongs to in the Election Commission\'s own list. Only counts are published, never a name, EPIC number or address.')


# ============================================================ WEST BENGAL
def westbengal(R):
    S, D, A = J('westbengal', 'summary.json'), J('westbengal', 'districts.json'), J('westbengal', 'constituencies.json')
    F, P, AD = Figs(R), S['pn05'], S['adj']
    W = {w['party']: w for w in S['winners']}
    kol = lambda name: name.startswith('Kolkata')
    low = D[-1]

    R.cover('Special Intensive Revision 2025-26', 'West Bengal: %s names left off the draft roll and %s held back' % (lakh(P['removed']), lakh(P['adjudication'])),
            'The names left off by reason, the names held back for adjudication, how much smaller each roll was at the 2026 election than in 2024, and how that compares with the result',
            [('names left off the draft roll of 16 December 2025', indian(P['removed'])),
             ('more held back from the final roll for adjudication', indian(P['adjudication'])),
             ('constituencies where the roll fell by more than the 2026 winning margin', '%d of %d' % (S['over_margin'], S['acs'])),
             ('of the names left off the draft were women', pct(P['women_removed_pct']))])
    R.h1('Contents')
    R.toc()

    R.h1('In short')
    R.numbered([
        'The revision left %s names off West Bengal\'s draft roll, the list published on 16 December 2025 for electors to check and contest. That is %s of every 100 electors. Another %s were held back from the final roll for adjudication, which means their eligibility was left for judicial officers to decide.' % (lakh(P['removed']), d1(P['removed_per_100']), lakh(P['adjudication'])),
        'In %d of the %d assembly constituencies, the seats of the state legislature, the roll the 2026 election was held on was smaller than the 2024 roll by more than the winning margin, the votes by which the winner beat the runner-up. So the fall was large enough to decide those seats. Counted at each seat\'s own turnout, it still exceeds the margin in %d.' % (S['over_margin'], S['acs'], S['could_change']),
        'Women were %s of the names left off the draft roll, against %s of the roll before it.' % (pct(P['women_removed_pct']), pct(P['women_before_pct'])),
        'Of the %s names held back, %s were found not eligible, as the Election Commission reported. %s of those appealed, and by press reports %s were restored in time to vote.' % (lakh(AD['under_adjudication']), lakh(AD['found_not_eligible']), lakh(AD['appeals_by_excluded']), indian(AD['restored_before_poll'])),
        'The roll the 2026 election was held on was %s smaller than the 2024 roll, %s of every 100 electors. Kolkata North\'s fell by %s per 100.' % (lakh(S['fall']), d1(S['per_100']), d1(D[0]['per_100'])),
        '%s of the names left off the draft were entered as dead, %s as shifted and %s as absent. %s' % (pct(P['shares']['dead']), pct(P['shares']['shifted']), pct(P['shares']['absent']), REASON),
    ])
    R.p('The Chief Electoral Officer, who keeps the state\'s rolls for the Election Commission, publishes no count of the names removed by district or constituency. So those figures measure the fall in the roll, how much smaller each roll was than in 2024. That fall takes in eighteen months of ordinary changes as well as the revision, and it is a different count from the names struck off.', italic=True)

    R.h1('The roll')
    R.stats([(lakh(P['removed']), 'left off the draft roll'), (lakh(P['adjudication']), 'held back for adjudication'),
             (lakh(S['fall']), 'fall in the roll, 2024 to 2026'), (pct(P['women_removed_pct']), 'of those left off were women')])

    R.h2('Constituency by constituency')
    byAc = {a['ac']: a for a in A}
    F.add(F.map(J('geo', 'westbengal.json'), lambda ac: byAc[ac]['per_100'] if ac in byAc else None, 'Fall in the roll per 100 electors, 2024 to the 2026 election',
                inset=[a['ac'] for a in A if kol(a['district'])], inset_name='Kolkata, enlarged', legend_loc='upper right'),
          'Each constituency shaded by how much smaller its roll was at the 2026 nominations than at the 2024 Lok Sabha nominations, for every 100 electors on the 2024 roll, in five bins with equal numbers of seats. Boundaries from DataMeet\'s assembly constituency map (CC BY 2.5 India), simplified.', width=15)
    R.p('Across the %d constituencies the fall runs from %s per 100 in %s to %s in %s.' % (S['acs'], d1(S['rate_min_v']), S['rate_min'], d1(S['rate_max_v']), S['rate_max']))

    R.h2('The roll, step by step')
    F.add(F.waterfall([('Roll of 27 October 2025', P['before'], 'total'), ('Dead', P['dead'], 'down'), ('Shifted', P['shifted'], 'down'), ('Absent', P['absent'], 'down'),
                       ('Already enrolled and other', P['duplicate'] + P['other'], 'down'), ('Draft roll', P['draft'], 'total'), ('Added on claims', P['added'], 'up'),
                       ('Removed on objections', P['form7'], 'down'), ('Held back for adjudication', P['adjudication'], 'down'), ('Final roll', P['final'], 'total'),
                       ('Net change after the final roll', S['after_final'], 'up'), ('Roll at the 2026 nominations', S['election'], 'total')],
                      math.floor(P['final'] * 0.85 / 1e6) * 1e6, 'West Bengal, from October 2025 to the 2026 nominations'),
          'As the Chief Electoral Officer reported it in press note PN-05-2026, with the roll at the 2026 nominations. The bars start above zero so that the changes can be seen.', width=15.5)
    R.p('%s names were left off the draft roll, %s of every 100 electors, and another %s were held back from the final roll for adjudication. %s were added on claims, filed on Form 6 to add a name, and %s removed on objections, filed on Form 7 to remove one. '
        'The final roll of 28 February 2026 held %s. By the 2026 nominations the roll had regained %s, and it was still %s smaller than in October 2025. %s'
        % (indian(P['removed']), d1(P['removed_per_100']), indian(P['adjudication']), indian(P['added']), indian(P['form7']), crore(P['final']), lakh(S['after_final']), lakh(S['fall_from_oct2025']), REASON))

    R.h2('The names held back for adjudication')
    R.p('The %s names marked under adjudication on the final roll were decided by judicial officers appointed on the Supreme Court\'s direction, and their orders could be appealed to tribunals. '
        'The split and the appeals below are the Election Commission\'s figures as they were reported, for the state as a whole.' % lakh(AD['under_adjudication']))
    fig, ax = plt.subplots(figsize=(7.5, 2.6))
    parts = [('Found eligible', AD['found_eligible'], TEAL), ('Not eligible, appealed', AD['appeals_by_excluded'], AMBER),
             ('Not eligible, no appeal', AD['not_eligible_no_appeal'], RED), ('Not accounted for', AD['not_accounted'], GREY)]
    left = 0
    for lab, v, col in parts:
        ax.barh(0, v / 1e5, left=left, color=col, height=0.5, label='%s, %s' % (lab, lakh(v)))
        left += v / 1e5
    ax.set_yticks([])
    ax.set_xlim(0, left)
    ax.set_xlabel('Lakh names held back', fontsize=8)
    ax.legend(fontsize=7, frameon=False, ncol=2, loc='upper center', bbox_to_anchor=(0.5, -0.45))
    style_axes(ax, 'What happened to the names held back, as reported')
    F.add(fig, 'The Election Commission\'s figures as reported. They are not published by district.', width=14)
    R.stats([(lakh(AD['appeals_by_excluded']), 'appeals by those found not eligible'), (lakh(AD['appeals_against_inclusion']), 'appeals against names kept'),
             (indian(AD['restored_before_poll']), 'restored in time to vote, by press reports'), (pct(AD['pending_pct']), 'of appeals undecided on 16 September')])
    R.p('As reported, of the %s names held back, %s were found eligible and %s were found not eligible, %s of the cases. %s of those found not eligible appealed, and by press reports alone %s were restored in time to vote. '
        'Another %s appeals asked the tribunals to remove names the judicial officers had kept. On 16 September %s of all %s appeals were still undecided. %s cases are not accounted for in the reported figures.'
        % (lakh(AD['under_adjudication']), lakh(AD['found_eligible']), lakh(AD['found_not_eligible']), pct(AD['not_eligible_pct']), lakh(AD['appeals_by_excluded']), indian(AD['restored_before_poll']),
           lakh(AD['appeals_against_inclusion']), pct(AD['pending_pct']), lakh(AD['appeals_total']), indian(AD['not_accounted'])))

    R.h2('Per 100 electors, by district')
    R.p('The Chief Electoral Officer has published no count of the names removed by district or constituency. What is published for every constituency is the roll at the 2024 Lok Sabha nominations and the roll at the 2026 Assembly nominations. '
        'What follows is the fall between the two, for every 100 electors on the 2024 roll. It takes in eighteen months of ordinary additions and deletions as well as the revision. '
        'The 2024 roll was %s smaller than the roll of October 2025 the revision started from, so this fall understates the fall from that roll.' % lakh(S['growth_2024_to_oct2025']))
    F.add(F.hbars([(d['district'], d['per_100']) for d in D], 'Fall in the roll per 100 electors, 2024 to the 2026 election, by district', 'Fall per 100 electors on the 2024 roll',
                  hi=lambda r: kol(r[0])), 'Kolkata\'s two districts in red.', width=14)
    R.p('The roll the 2026 election was held on was %s smaller than the 2024 roll, %s of every 100 electors. Kolkata North fell by %s per 100 and Kolkata South by %s. %s fell the least, %s.'
        % (lakh(S['fall']), d1(S['per_100']), d1(D[0]['per_100']), d1(D[1]['per_100']), low['district'], d1(low['per_100'])))

    R.h2('The reasons')
    fig, ax = plt.subplots(figsize=(7, 2.8))
    RK = [('dead', 'Dead'), ('shifted', 'Shifted'), ('absent', 'Absent'), ('duplicate', 'Already enrolled'), ('other', 'Other')]
    ys = list(range(len(RK)))[::-1]
    ax.barh(ys, [P[k] / 1e5 for k, _ in RK], color=[GREY, NAVY, RED, AMBER, PURPLE], height=0.6)
    for y, (k, _) in zip(ys, RK):
        ax.text(P[k] / 1e5 + 0.3, y, '%s (%s)' % (lakh(P[k]), pct(P['shares'][k])), va='center', fontsize=7)
    ax.set_yticks(ys)
    ax.set_yticklabels([n for _, n in RK], fontsize=8)
    ax.set_xlabel('Lakh names left off the draft', fontsize=8)
    ax.set_xlim(0, max(P[k] for k, _ in RK) / 1e5 * 1.35)
    style_axes(ax, 'Names left off the draft roll, by the reason entered')
    F.add(fig, 'The state as a whole. The reasons are not published by district or constituency.', width=12)
    R.p('%s of the names left off the draft were entered as dead, %s as shifted and %s as absent. The reasons are published for the state only, so none of the district or constituency figures can be split by reason. %s'
        % (pct(P['shares']['dead']), pct(P['shares']['shifted']), pct(P['shares']['absent']), REASON))

    R.h2('Women')
    DW = sorted(D, key=lambda d: -(d['women_fall_pct'] - d['women_2024_pct']))
    F.add(F.dumbbell([(d['district'], d['women_2024_pct'], d['women_fall_pct']) for d in DW], 'Women\'s share of the 2024 roll and of the fall in the roll, %',
                     'Share of the 2024 roll', 'Share of the fall in the roll'),
          'Where the red dot is to the right, more women left the roll than their share of it. The dashed line is half.', width=14)
    R.p('Women were %s of the names left off the draft roll, against %s of the roll before it. Between 2024 and the election, women were %s of the fall in the roll and %s of the 2024 roll. '
        'They were more than their share in %d of the %d districts. In Kolkata North and Kolkata South men were the larger part of the fall.'
        % (pct(P['women_removed_pct']), pct(P['women_before_pct']), pct(S['women_fall_pct']), pct(S['women_2024_pct']), S['districts_women_over'], S['districts']))

    R.h2('After the draft')
    DD = sorted(D, key=lambda d: -(d['per_100'] - d['draft_per_100']))
    top4 = [d['district'] for d in DD[:4]]
    F.add(F.slope([(d['district'], d['draft_per_100'], d['per_100'], d['district'] in top4, kol(d['district'])) for d in D],
                  'Fall in the roll at the draft and at the election roll', 'At the draft', 'At the election', 'Per 100 electors on the 2024 roll'),
          'Each line is a district. The steeper the climb, the more of the fall came after the draft. The four districts where it climbed most in red.', width=12)
    R.p('Most of the fall in %s, %s and %s came after the draft. %s\'s roll was %s per 100 smaller at the draft and %s per 100 smaller at the election. In Kolkata almost all of the fall was already in the draft. '
        'The %s names held back for adjudication are counted for the state only, so this gap is the nearest the published tables come to showing where they fell. It is not a count of them.'
        % (DD[0]['district'], DD[1]['district'], DD[2]['district'], DD[0]['district'], d1(DD[0]['draft_per_100']), d1(DD[0]['per_100']), lakh(P['adjudication'])))

    R.h2('Every district')
    R.table(['District', 'Seats', 'Roll 2024', 'Draft roll', 'Roll 2026', 'Fall per 100 at draft', 'Fall per 100 at 2026', 'Women, % of fall', 'BJP seats', 'AITC seats'],
            [[d['district'], str(d['acs']), indian(d['roll_2024']), indian(d['draft']), indian(d['election']), d1(d['draft_per_100']), d1(d['per_100']), d1(d['women_fall_pct']), str(d['seats_bjp']), str(d['seats_aitc'])] for d in D],
            widths=[3.2, 1.0, 2.0, 2.0, 2.0, 1.6, 1.6, 1.5, 1.1, 1.1], size=7)

    R.h1('The 2026 election')
    R.h2('The fall in the roll against the winning margin')
    G = [('BJP', '#E67E22'), ('AITC', TEAL)]
    groups = [(p, c, [(a['fall'], a['margin']) for a in A if a['winner'] == p]) for p, c in G] + [('Other parties', GREY, [(a['fall'], a['margin']) for a in A if a['winner'] not in ('BJP', 'AITC')])]
    F.add(F.margin_scatter(groups, 'Fall in the roll against the 2026 winning margin', 'Fall in the roll, 2024 to 2026'),
          'Each dot is a constituency, coloured by the party that won it. Dots below the dashed line are seats where the roll fell by more than the winner won by.', width=14)
    R.p('In %d of the %d constituencies, the roll fell by more than the 2026 winning margin, large enough to decide the seat. The fall and the margin as a share of votes are close to unrelated. Their rank correlation, a measure that runs from -1 to 1 and is near 0 when two things do not move together, is %.2f. So the seats whose rolls shrank most were not the closest contests.'
        % (S['over_margin'], S['acs'], S['rho_rate_margin']))

    R.h2('How many seats, on each count')
    R.stats([('%d of %d' % (S['draft_over_margin'], S['acs']), 'fall to the draft roll'), ('%d of %d' % (S['over_margin'], S['acs']), 'fall to the election roll'),
             ('%d of %d' % (S['could_change'], S['acs']), 'fall to the election roll, at turnout')])
    R.p('The first count stops at the draft roll of December 2025. The second runs to the roll the election was held on, after the names held back for adjudication. The third counts the second at the seat\'s own 2026 turnout. '
        'Counted at turnout, the fall still exceeds the margin in %d of the %d seats. In the other %d, the runner-up could not have won even if every elector missing from the roll had voted, at the seat\'s turnout, for the runner-up. '
        'None of the three separates the names entered as dead, because the reasons are published for the state only. The fall counts the dead and ordinary changes to the roll too, and nobody can know how anyone missing from it would have voted.'
        % (S['could_change'], S['acs'], S['acs'] - S['could_change']))

    R.h2('The fall by the party that won')
    F.add(F.strip([('BJP (%d seats)' % W['BJP']['seats'], [(a['per_100'], kol(a['district'])) for a in A if a['winner'] == 'BJP']),
                   ('AITC (%d seats)' % W['AITC']['seats'], [(a['per_100'], kol(a['district'])) for a in A if a['winner'] == 'AITC']),
                   ('Other parties', [(a['per_100'], kol(a['district'])) for a in A if a['winner'] not in ('BJP', 'AITC')])],
                  'Fall in the roll per 100 electors in every seat, by the party that won it', 'Fall per 100 electors on the 2024 roll'),
          'Each dot is a constituency. Kolkata\'s seats are in red.', width=14)
    winners_table(R, S['winners'], 'per_100', 'Fall per 100', 'Fall over margin')
    R.p('The BJP won %d seats and the AITC %d. The roll fell by %s per 100 in the seats the BJP won and by %s in those the AITC won. Set against the fall in their own districts, the two come out at %s and %s, so the difference comes from where the seats are. '
        'The fall exceeded the margin in %d of the BJP\'s seats and %d of the AITC\'s.'
        % (W['BJP']['seats'], W['AITC']['seats'], d1(W['BJP']['per_100']), d1(W['AITC']['per_100']), sg(W['BJP']['vs_district']), sg(W['AITC']['vs_district']), W['BJP']['over_margin'], W['AITC']['over_margin']))
    limits_section(R, 'The tables show the names left off the draft and the names held back for the state as a whole, and how much smaller every constituency\'s roll was at the 2026 election than in 2024.',
                   ['How many names were removed in each district or constituency, or on what recorded reason.',
                    'Where the names held back for adjudication were, or how many of them in each place were found eligible.',
                    'Whether each removal was right. %s' % REASON,
                    'How anyone missing from the roll would have voted. No list of removals can show intent.'])

    R.h1('What the Election Commission should do')
    R.p('%s names came off West Bengal\'s draft roll and %s more were held back from the final roll. The Election Commission should do five things.' % (lakh(P['removed']), lakh(P['adjudication'])))
    R.numbered([
        'Publish the names removed by constituency and polling station, with the reason and the sex of each, so that the removals can be counted where they happened.',
        'Publish the outcome of adjudication by district and constituency, as its own table and in full.',
        'Decide the %s appeals still pending, and publish how many names each decision restored or removed.' % lakh(AD['appeals_pending']),
        'Account for the %s cases missing from the reported outcome of adjudication.' % indian(AD['not_accounted']),
        'Publish how many of those added after the draft had been left off it, so that names restored can be told apart from new voters.',
    ])

    R.h1('Method and sources')
    R.p('The Chief Electoral Officer\'s press note PN-05-2026 gives the roll of 27 October 2025, the %s names left off the draft by reason, the claims and objections, the %s names held back for adjudication, and the final roll of 28 February 2026. '
        'Every one of those figures is for the state as a whole, and they add up step by step. The women and men on the roll before the revision, set against the draft roll by sex, give the share of women among the names left off.'
        % (indian(P['removed']), indian(P['adjudication'])))
    R.p('No table of the names removed by district or constituency has been published. What is published for all %d constituencies, by sex, is three rolls, the roll at the 2024 Lok Sabha nominations, the draft roll of 16 December 2025, and the roll at the 2026 Assembly nominations. '
        'So the constituency figures measure the fall in the roll from 2024. That fall includes the revision, the names held back for adjudication and those not restored, and also eighteen months of ordinary additions and deletions before the revision began. '
        'The roll of October 2025 was %s larger than the 2024 roll, so the fall from 2024 is smaller than the fall from the roll the revision started from.' % (S['acs'], lakh(S['growth_2024_to_oct2025'])))
    R.p('The outcome of adjudication and the appeals are the Election Commission\'s figures as the press reported them, including its affidavit of 16 September, and they are given here as reported. The district of each constituency is the Chief Electoral Officer\'s, and district figures are the sums of their constituencies.')
    R.p('The 2026 winner, runner-up and margin are from the Election Commission\'s constituency result pages, checked against its state-wise pages, with Falta\'s from its re-poll. Turnout is votes over the roll at the nominations. '
        'Each seat\'s fall per 100 is also set against the fall of its own district, and those differences are averaged for each party\'s seats. The map uses DataMeet\'s assembly constituency map, licensed CC BY 2.5 India. Only counts are published, never a name, EPIC number or address.')

    R.h1('Every constituency')
    R.table(['No.', 'Constituency', 'District', 'Roll 2024', 'Draft roll', 'Roll 2026', 'Fall', 'Per 100', 'Won 2026', 'Margin', 'Over margin'],
            [[str(a['ac']), a['name'], a['district'], indian(a['roll_2024']), indian(a['draft']), indian(a['election']), indian(a['fall']), d1(a['per_100']), a['winner'], indian(a['margin']), 'Yes' if a['over_margin'] else 'No'] for a in A],
            widths=[0.8, 2.6, 2.3, 1.6, 1.6, 1.6, 1.4, 1.1, 1.3, 1.4, 1.2], right={0, 3, 4, 5, 6, 7, 9}, size=6.5)


# ============================================================ KERALA
def kerala(R):
    S, D, A = J('kerala', 'summary.json'), J('kerala', 'districts.json'), J('kerala', 'constituencies.json')
    F = Figs(R)
    W = {w['party']: w for w in S['winners']}
    tvm = lambda n: n == 'Thiruvananthapuram'
    low = D[-1]
    grew = [d['district'] for d in D if d['per_100'] < 0]

    R.cover('Special Intensive Revision 2025-26', 'Kerala: the draft roll was %s smaller than in January 2025' % lakh(S['fall_draft']),
            'How much smaller each district and constituency\'s roll was at the draft, who was missing, how much came back before the 2026 election, and how that compares with the result',
            [('fewer electors on the draft roll than in January 2025', indian(S['fall_draft'])),
             ('of every 100 electors on the January 2025 roll', d1(S['draft_per_100'])),
             ('of that fall were women, against %s of the roll' % pct(S['women_2025_pct']), pct(S['women_fall_pct'])),
             ('constituencies where the fall at the draft exceeded the 2026 margin', '%d of %d' % (S['draft_over_margin'], S['acs']))])
    R.h1('Contents')
    R.toc()

    R.h1('In short')
    R.numbered([
        'Kerala\'s draft roll, the list published on 23 December 2025 for electors to check and contest, was %s smaller than its roll of January 2025. That is %s of every 100 electors.' % (lakh(S['fall_draft']), d1(S['draft_per_100'])),
        'In %d of the %d assembly constituencies, the seats of the state legislature, the roll fell by more at the draft than the 2026 winning margin, the votes by which the winner beat the runner-up. By the election the roll had grown back by %s since the draft, new voters included, and was still smaller than in January 2025 by more than the margin in %d seats, large enough to decide them.' % (S['draft_over_margin'], S['acs'], lakh(S['added_final'] + S['added_election']), S['over_margin']),
        'Women were %s of that fall, against %s of the roll, and more than their share in all %d districts.' % (pct(S['women_fall_pct']), pct(S['women_2025_pct']), S['districts']),
        '%s fell most, by %s per 100, and %s least, by %s.' % (D[0]['district'], d1(D[0]['draft_per_100']), low['district'], d1(low['draft_per_100'])),
        'By the 2026 election the roll had risen %s from the draft, which counts new voters as well as names put back, and it was %s smaller than in January 2025.' % (lakh(S['election'] - S['draft']), lakh(S['fall'])),
    ])
    R.p('No count of the names removed is published by constituency. So these figures measure the fall in the roll, how much smaller each roll was than in January 2025. That fall takes in ordinary changes as well as the revision, and it is a different count from the names struck off.', italic=True)

    R.h1('The roll')
    R.stats([(lakh(S['fall_draft']), 'smaller at the draft'), (d1(S['draft_per_100']), 'per 100 electors'),
             (pct(S['women_fall_pct']), 'of the fall were women'), (lakh(S['fall']), 'smaller at the election')])

    R.h2('Constituency by constituency')
    byAc = {a['ac']: a for a in A}
    F.add(F.map(J('geo', 'kerala.json'), lambda ac: byAc[ac]['draft_per_100'] if ac in byAc else None, 'Fall in the roll per 100 electors, January 2025 to the draft', legend_loc='upper right'),
          'Each constituency shaded by how much smaller its roll was at the draft than in January 2025, for every 100 electors, in five bins with equal numbers of seats. Boundaries from DataMeet\'s assembly constituency map (CC BY 2.5 India), simplified.', width=12)
    R.p('Across the %d constituencies the fall at the draft runs from %s per 100 in %s to %s in %s.' % (S['acs'], d1(S['rate_min_v']), S['rate_min'], d1(S['rate_max_v']), S['rate_max']))

    R.h2('The roll, step by step')
    F.add(F.waterfall([('Roll of January 2025', S['roll_2025'], 'total'), ('Fall to the draft', S['fall_draft'], 'down'), ('Draft roll', S['draft'], 'total'),
                       ('Net change to the final roll', S['added_final'], 'up'), ('Final roll', S['final'], 'total'), ('Net change to March 2026', S['added_election'], 'up'),
                       ('Roll of 23 March 2026', S['election'], 'total')], math.floor(S['draft'] * 0.85 / 1e6) * 1e6, 'Kerala, from January 2025 to March 2026'),
          'From the final roll of the 2025 summary revision to the roll the election was held on. The bars start above zero so that the changes can be seen.')
    R.p('The draft roll of 23 December 2025 was %s smaller than the roll of 6 January 2025, %s of every 100 electors. The final roll of 21 February 2026 and the additions before the election brought back %s, so the roll of 23 March 2026, on which the election was held, was %s smaller than in January 2025. '
        'The rise after the draft counts new voters as well as names put back.' % (lakh(S['fall_draft']), d1(S['draft_per_100']), lakh(S['election'] - S['draft']), lakh(S['fall'])))

    R.h2('Per 100 electors, by district')
    R.p('The Chief Electoral Officer, who keeps the state\'s rolls for the Election Commission, has published no count of the names left off the draft, by district or constituency. Every roll is published by constituency, so what follows is each district\'s fall from the roll of January 2025 to the draft. '
        'It takes in the ordinary changes of 2025 as well as the revision, though for the state the fall, %s, is within half a lakh of the %s names reported left off with the draft.' % (lakh(S['fall_draft']), lakh(S['press_removed'])))
    F.add(F.strip([(d['district'], [(max(a['draft_per_100'], 0), tvm(d['district'])) for a in A if a['district'] == d['district']]) for d in D],
                  'Fall in the roll at the draft per 100 electors, every constituency by district', 'Fall per 100 electors on the January 2025 roll'),
          'Each dot is a constituency. Districts from the largest fall to the smallest. Thiruvananthapuram in red.', width=14)
    R.p('%s\'s roll was %s per 100 smaller at the draft, against %s for the state. %s and %s come next. %s fell the least, %s.'
        % (D[0]['district'], d1(D[0]['draft_per_100']), d1(S['draft_per_100']), D[1]['district'], D[2]['district'], low['district'], d1(low['draft_per_100'])))

    R.h2('The reasons')
    R.p('No reasons have been published. The Chief Electoral Officer has given no split of the names left off by reason, by constituency or for the state, so none of the figures here can say how many were entered as dead, shifted or absent.')

    R.h2('Women')
    fig, ax = plt.subplots(figsize=(6.5, 5))
    xs = [a['women_2025_pct'] for a in A]
    ys = [a['women_fall_pct'] for a in A if a['fall_draft'] > 0]
    pts = [a for a in A if a['fall_draft'] > 0]
    ax.scatter([a['women_2025_pct'] for a in pts], [a['women_fall_pct'] for a in pts], s=12, color=[RED if tvm(a['district']) else NAVY for a in pts], alpha=0.85, lw=0)
    lo, hi = min(xs + ys) - 1, max(xs + ys) + 1
    ax.plot([lo, hi], [lo, hi], ls='--', lw=0.8, color='#555')
    ax.set_xlabel('Women, % of the January 2025 roll', fontsize=8)
    ax.set_ylabel('Women, % of the fall at the draft', fontsize=8)
    style_axes(ax, 'Women\'s share of the roll and of the fall at the draft')
    F.add(fig, 'Each dot is a constituency. Dots above the dashed line are seats where more women left the roll than their share of it. Thiruvananthapuram district in red.', width=11)
    R.p('Women were %s of the fall to the draft, against %s of the roll before it. They were more than their share in all %d districts and in %d of the %d constituencies. Of the rise after the draft, women were %s.'
        % (pct(S['women_fall_pct']), pct(S['women_2025_pct']), S['districts'], S['acs_women_over'], S['acs'], pct(S['women_added_pct'])))

    R.h2('After the draft')
    F.add(F.multiples([(d['district'], [100, 100 * d['draft'] / d['roll_2025'], 100 * d['final'] / d['roll_2025'], 100 * d['election'] / d['roll_2025']], tvm(d['district'])) for d in D],
                      ['January 2025', 'the draft', 'the final roll', 'March 2026'], 'Each district\'s roll, January 2025 = 100'),
          'Each small chart follows one district\'s roll through the four published rolls. The dashed line is the January level. Thiruvananthapuram in red.', width=15)
    R.p('In %s and %s the roll was still about %s per 100 smaller at the election than in January 2025. In %d districts it had grown past its January size by the election, %s. '
        'The rise after the draft counts new voters, including those who turned eighteen and those registered abroad, as well as names put back, so it cannot show how many of those left off were restored.'
        % (D[0]['district'], D[1]['district'], '%.0f' % ((D[0]['per_100'] + D[1]['per_100']) / 2), len(grew), andj(grew)))

    R.h2('Every district')
    R.table(['District', 'Seats', 'Roll Jan 2025', 'Draft roll', 'Final roll', 'Roll Mar 2026', 'Fall per 100 at draft', 'Fall per 100 at election', 'Women, % of fall'],
            [[d['district'], str(d['acs']), indian(d['roll_2025']), indian(d['draft']), indian(d['final']), indian(d['election']), d1(d['draft_per_100']), d1(d['per_100']), d1(d['women_fall_pct'])] for d in D],
            widths=[3.2, 1.0, 2.1, 2.0, 2.0, 2.0, 1.7, 1.7, 1.5], size=7)

    R.h1('The 2026 election')
    R.h2('The fall at the draft against the winning margin')
    G = [('INC', NAVY), ('CPI(M)', RED), ('IUML', TEAL)]
    groups = [(p, c, [(a['fall_draft'], a['margin']) for a in A if a['winner'] == p]) for p, c in G] + [('Other parties', GREY, [(a['fall_draft'], a['margin']) for a in A if a['winner'] not in ('INC', 'CPI(M)', 'IUML')])]
    F.add(F.margin_scatter(groups, 'Fall in the roll at the draft against the 2026 winning margin', 'Fall in the roll, January 2025 to the draft'),
          'Each dot is a constituency, coloured by the party that won it. Dots below the dashed line are seats where the roll fell by more than the winner won by.', width=14)
    R.p('In %d of the %d constituencies, the roll fell by more at the draft than the 2026 winning margin. The fall and the margin as a share of votes are close to unrelated. Their rank correlation, a measure that runs from -1 to 1 and is near 0 when two things do not move together, is %.2f.'
        % (S['draft_over_margin'], S['acs'], S['rho_rate_margin']))

    R.h2('How many seats, on each count')
    R.stats([('%d of %d' % (S['draft_over_margin'], S['acs']), 'fall to the draft roll'), ('%d of %d' % (S['over_margin'], S['acs']), 'fall to the election roll'),
             ('%d of %d' % (S['could_change'], S['acs']), 'fall to the election roll, at turnout')])
    R.p('The first count stops at the draft roll. The second runs to the roll the election was held on, after the names added on claims and before the poll. The third counts the second at the seat\'s own 2026 turnout. '
        'By the election the roll had grown back by %s since the draft, new voters included, and was still smaller than in January 2025 by more than the margin in %d seats, large enough to decide them. Counted at each seat\'s own turnout, that is %d seats. '
        'Nobody can know how anyone missing from the roll would have voted.' % (lakh(S['added_final'] + S['added_election']), S['over_margin'], S['could_change']))

    R.h2('The fall by the party that won')
    winners_table(R, S['winners'], 'draft_per_100', 'Fall per 100 at draft', 'Draft fall over margin')
    R.p('The INC won %d seats, the CPI(M) %d and the IUML %d. The roll fell at the draft by %s per 100 in the INC\'s seats, %s in the CPI(M)\'s and %s in the IUML\'s. '
        'Set against the fall in their own districts they come out at %s, %s and %s, so most of the difference comes from where the seats are.'
        % (W['INC']['seats'], W['CPI(M)']['seats'], W['IUML']['seats'], d1(W['INC']['draft_per_100']), d1(W['CPI(M)']['draft_per_100']), d1(W['IUML']['draft_per_100']),
           sg(W['INC']['vs_district']), sg(W['CPI(M)']['vs_district']), sg(W['IUML']['vs_district'])))
    limits_section(R, 'The tables show how much smaller every constituency\'s roll was at the draft and at the election than in January 2025, by sex, and how that compares with the 2026 margins.',
                   ['How many names were removed in each district or constituency, or on what recorded reason.',
                    'How many of those left off were put back.',
                    'Whether each removal was right, or how anyone missing from the roll would have voted. No list of removals can show intent.'])

    R.h1('What the Election Commission should do')
    R.p('Kerala\'s draft roll was %s smaller than its roll of January 2025, and no table of the names left off has been published. The Election Commission should do four things.' % lakh(S['fall_draft']))
    R.numbered([
        'Publish the names left off the draft by constituency and polling station, with the reason and the sex of each.',
        'Explain why women were %s of the fall at the draft, against %s of the roll.' % (pct(S['women_fall_pct']), pct(S['women_2025_pct'])),
        'Publish how many of those added for the final roll had been left off the draft, so that names restored can be told apart from new voters and electors registered abroad.',
        'Explain why %s lost %s of every 100 electors at the draft, %.1f times the rate of %s.' % (D[0]['district'], d1(D[0]['draft_per_100']), D[0]['draft_per_100'] / low['draft_per_100'], low['district']),
    ])

    R.h1('Method and sources')
    R.p('The Chief Electoral Officer, Kerala, publishes every roll by assembly constituency and sex. These figures use four of them, the final roll of the 2025 summary revision (6 January 2025), the draft roll of the Special Intensive Revision (23 December 2025), its final roll (21 February 2026) and the roll of 23 March 2026, on which the election was held. Each adds up to its own district and state totals.')
    R.p('No table of the names left off the draft has been published, by constituency or for the state. The figures measure how much smaller each roll was at the draft than in January 2025. That fall, %s in all, takes in the ordinary changes of 2025 as well as the revision. '
        'The count of names left off reported with the draft was %s. The draft plus that count comes to %s, which matches the roll frozen for the revision in October 2025 as the press reported it, a little more than the January roll. So for the state the fall and the removals are close. For a single constituency they may differ more.'
        % (indian(S['fall_draft']), indian(S['press_removed']), indian(S['frozen'])))
    R.p('The rise from the draft to the final roll and to the roll of March 2026 is the names added less those removed. It counts new voters, including those who turned eighteen and those registered abroad, as well as names put back.')
    R.p('The 2026 winner, runner-up and margin are from the Election Commission\'s constituency result pages, checked against its state-wise pages. Turnout is votes over the roll of 23 March 2026. Party comparisons are by party, because the fronts of the independents are not in the data. '
        'Each seat\'s fall per 100 is also set against the fall of its own district, and those differences are averaged for each party\'s seats. The map uses DataMeet\'s assembly constituency map, licensed CC BY 2.5 India. Only counts are published, never a name, EPIC number or address.')

    R.h1('Every constituency')
    R.table(['No.', 'Constituency', 'District', 'Roll Jan 2025', 'Draft roll', 'Roll Mar 2026', 'Fall at draft', 'Per 100', 'Won 2026', 'Margin', 'Draft fall over margin'],
            [[str(a['ac']), a['name'], a['district'], indian(a['roll_2025']), indian(a['draft']), indian(a['election']), indian(a['fall_draft']), d1(a['draft_per_100']), a['winner'], indian(a['margin']), 'Yes' if a['draft_over_margin'] else 'No'] for a in A],
            widths=[0.8, 2.6, 2.3, 1.6, 1.6, 1.6, 1.4, 1.1, 1.3, 1.4, 1.4], right={0, 3, 4, 5, 6, 7, 9}, size=6.5)


STATES = {
    'tamilnadu': (tamilnadu, RGBColor(0x8E, 0x44, 0x2B)),
    'karnataka': (karnataka, RGBColor(0x1E, 0x6B, 0x52)),
    'westbengal': (westbengal, RGBColor(0x1F, 0x4E, 0x79)),
    'kerala': (kerala, RGBColor(0x0E, 0x5E, 0x6F)),
}

if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] not in STATES:
        sys.exit('usage: state_report.py {%s} OUT.docx' % ','.join(STATES))
    build, accent = STATES[sys.argv[1]]
    R = Report(accent)
    build(R)
    out = sys.argv[2]
    R.save(out)
    R.save_html(out[:-5] + '.html')
    print('ok')
