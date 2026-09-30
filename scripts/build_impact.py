"""What the removals could have done to each seat's result.

Bihar held its 2025 Assembly election on the final roll, after the revision,
so the question there is concrete: had the names still off the roll been able
to vote, could any seat have gone the other way? Three estimates, each with its
assumption stated, and one figure that needs no assumption about how anyone
votes.

  booth    Each removed elector votes like their own polling booth did in the
           2024 Lok Sabha election (the three leading parties' shares, the rest
           counted as Other), at the seat's 2025 turnout.
  religion Each removed elector votes like their religious group did in the
           Axis My India exit poll of 11 November 2025, as reported by NDTV on
           12 November 2025: Muslims 6% NDA, 79% Mahagathbandhan. The
           non-Muslim split is derived from the same poll's overall 43% and 41%
           and the caste survey's 17.70% Muslim share. Unclassified names are
           split in the booth's classified proportions.
  sex      As above, by sex: women 45% NDA, 40% Mahagathbandhan; men 41% and
           42%.
  break-even  The share of the removed who would have voted, split between the
           two leading candidates only, that the runner-up needed to win the
           seat.

Who is counted. The base is each seat's net fall between the roll before the
revision and the final roll: the names removed at the draft and after it, less
the names added before the final roll. Additions include new electors, so this
understates the removed who stayed off (a lower bound); the upper bound drops
the additions. Names entered as dead are taken out of both, at the seat's own
dead share (phase 1 reasons and the final roll's 'expired'). Phase 2 has no
reasons, so its dead share is taken to be phase 1's.

Seats where the winner or the runner-up is outside the two alliances get the
break-even figure only: both sources count every other party as one 'Other'.

Hyderabad's last election, in 2023, came before the revision, so there is no
result the removals could have changed. Each seat gets the break-even figure
against its 2023 margin, at 2023 turnout on the roll before the revision, and
the religion of the removed against the roll.
"""
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import build_bihar as B  # noqa: E402

RAW = os.path.join(ROOT, 'data', 'bihar', 'raw')
CHECK = '--check' in sys.argv

# Axis My India exit poll, Bihar 2025, as reported by NDTV, 12 November 2025.
POLL = {'overall': {'NDA': 43, 'INDIA': 41}, 'muslim': {'NDA': 6, 'INDIA': 79},
        'women': {'NDA': 45, 'INDIA': 40}, 'men': {'NDA': 41, 'INDIA': 42}}
MUSLIM_SHARE = 0.177   # Bihar caste-based survey, 2 October 2023
POLL_SOURCE = 'Axis My India exit poll, Bihar Assembly election 2025, as reported by NDTV on 12 November 2025'


def non_muslim():
    m = MUSLIM_SHARE
    return {k: (POLL['overall'][k] - m * POLL['muslim'][k]) / (1 - m) for k in ('NDA', 'INDIA')}


def with_other(d):
    d = {k: v / 100 for k, v in d.items()}
    d['Other'] = 1 - d['NDA'] - d['INDIA']
    return d


def bihar():
    amap = B.load_map()
    rows = B.fix_labels(B.load_booth_rows(), amap)
    v = B.party_votes(rows)
    v = v[v.party_fixed != 'NOTA'].copy()
    v['al'] = v.party_fixed.map(lambda p: B.alliance(p, 2024))
    sh = v.pivot_table(index='key', columns='al', values='share', aggfunc='sum').fillna(0) / 100
    for c in ('NDA', 'INDIA', 'Other'):
        if c not in sh:
            sh[c] = 0.0
    sh['Other'] = (1 - sh.NDA - sh.INDIA).clip(lower=0)

    booth = rows.drop_duplicates('key')[['key', 'ac', 'booth', 'deleted']].set_index('key')
    booth = booth.join(sh[['NDA', 'INDIA', 'Other']], how='left')

    r = pd.read_csv(os.path.join(RAW, 'reasons_by_booth.csv.gz'))
    dead = r[r.reason == 'dead'].groupby(['ac', 'jan_part'])['count'].sum()
    booth['dead'] = [int(dead.get((a, b), 0)) for a, b in zip(booth.ac, booth.booth)]
    booth['alive'] = (booth.deleted - booth.dead).clip(lower=0)

    g = pd.read_csv(os.path.join(RAW, 'booth_gender_religion.csv.gz'))
    g.columns = ['ac', 'key', 'sex', 'hindu', 'muslim', 'unknown']
    g['n'] = g.hindu + g.muslim + g.unknown
    rel = g.groupby('key')[['hindu', 'muslim', 'unknown']].sum()
    sex = g.pivot_table(index='key', columns='sex', values='n', aggfunc='sum').fillna(0)
    booth = booth.join(rel).join(sex[['F', 'M']])

    seats = {x['ac']: x for x in json.load(open(os.path.join(ROOT, 'data', 'bihar', 'constituencies.json')))}
    final = {x['ac']: x for x in json.load(open(os.path.join(ROOT, 'data', 'bihar', 'final.json')))['seats']}

    nm = with_other(non_muslim())
    mu = with_other(POLL['muslim'])
    wo, me = with_other(POLL['women']), with_other(POLL['men'])

    out = []
    for ac, b in booth.groupby('ac'):
        s, f = seats[ac], final[ac]
        W = s['al2025']
        R = B.alliance(s['ru2025'], 2024)
        # composition of the removed who could have voted, from the booths
        live = b.alive.fillna(0)
        has = b.NDA.notna()
        wts = live[has]
        comp = {k: float((b.loc[has, k] * wts).sum() / wts.sum()) for k in ('NDA', 'INDIA', 'Other')}
        cls = b.hindu + b.muslim
        mshare = float(b.muslim.sum() / cls.sum()) if cls.sum() else 0.0
        fshare = float(b.F.sum() / (b.F.sum() + b.M.sum()))
        rel_c = {k: mshare * mu[k] + (1 - mshare) * nm[k] for k in ('NDA', 'INDIA', 'Other')}
        sex_c = {k: fshare * wo[k] + (1 - fshare) * me[k] for k in ('NDA', 'INDIA', 'Other')}

        removed_all = s['total'] + f['removed_after']
        dead_all = s['r_dead'] * (s['total'] / s['p1']) + f['r_expired']
        alive_frac = 1 - dead_all / removed_all
        t = s['turnout2025'] / 100
        lower = max(f['net_fall'], 0) * alive_frac * t
        upper = removed_all * alive_frac * t
        margin = s['margin2025']

        modelled = {W, R} == {'NDA', 'INDIA'}

        def swing(c, V):
            # The booth file and the poll give one 'Other' share for every party
            # outside the two alliances, which cannot stand for a BSP, AIMIM or
            # independent candidate. Those seats get the break-even figure only.
            if not modelled:
                return None
            return V * (c[R] - c[W])

        rec = {'ac': ac, 'name': s['name'], 'district': s['district'], 'winner': s['win2025'], 'runner_up': s['ru2025'],
               'alliance_w': W, 'alliance_r': R, 'modelled': modelled, 'margin': margin, 'turnout': s['turnout2025'],
               'voters_lower': round(lower), 'voters_upper': round(upper),
               'comp_booth': {k: round(100 * v, 1) for k, v in comp.items()},
               'muslim_share_removed': round(100 * mshare, 1), 'women_share_removed': round(100 * fshare, 1)}
        for label, c in (('booth', comp), ('religion', rel_c), ('sex', sex_c)):
            for bound, V in (('lower', lower), ('upper', upper)):
                sw = swing(c, V)
                rec['%s_%s' % (label, bound)] = None if sw is None else round(sw)
        # break-even: of the removed who would have voted, split between the two
        # leading candidates only, what share did the runner-up need?
        rec['breakeven_lower'] = round(100 * (1 + margin / lower) / 2, 1) if lower > 0 else None
        rec['breakeven_upper'] = round(100 * (1 + margin / upper) / 2, 1) if upper > 0 else None
        out.append(rec)

    def flips(key):
        return sorted([x for x in out if x[key] is not None and x[key] > x['margin']], key=lambda x: x['margin'])

    two = [x for x in out if {x['alliance_w'], x['alliance_r']} == {'NDA', 'INDIA'}]
    summary = {}
    for label in ('booth', 'religion', 'sex'):
        for bound in ('lower', 'upper'):
            k = '%s_%s' % (label, bound)
            fl = flips(k)
            net = {'NDA': 0, 'INDIA': 0}
            for x in two:
                if x[k] is None:
                    continue
                # a positive swing helps the runner-up
                net[x['alliance_r']] += x[k]
                net[x['alliance_w']] -= x[k]
            summary[k] = {'flips': len(fl), 'seats': [{'ac': x['ac'], 'name': x['name'], 'winner': x['winner'],
                                                      'runner_up': x['runner_up'], 'margin': x['margin'],
                                                      'swing': x[k]} for x in fl],
                          'to_nda': sum(1 for x in fl if x['alliance_r'] == 'NDA'),
                          'to_india': sum(1 for x in fl if x['alliance_r'] == 'INDIA'),
                          'net_to_runner_up_nda_seats': round(sum(x[k] for x in two if x['alliance_w'] == 'NDA' and x[k] is not None)),
                          'net_to_runner_up_india_seats': round(sum(x[k] for x in two if x['alliance_w'] == 'INDIA' and x[k] is not None))}
    def bands_of(key):
        be = [x[key] for x in out if x[key] is not None]
        return {'under_55': sum(1 for v in be if v < 55), '55_to_65': sum(1 for v in be if 55 <= v < 65),
                '65_to_100': sum(1 for v in be if 65 <= v <= 100), 'over_100': sum(1 for v in be if v > 100)}
    bands = {'lower': bands_of('breakeven_lower'), 'upper': bands_of('breakeven_upper')}
    close = sorted([x for x in out if x['breakeven_lower'] is not None and x['breakeven_lower'] < 55], key=lambda x: x['breakeven_lower'])
    tot_c = {k: 0.0 for k in ('NDA', 'INDIA', 'Other')}
    wsum = 0
    for x in out:
        if not x['modelled']:
            continue
        for k in tot_c:
            tot_c[k] += x['comp_booth'][k] * x['voters_lower']
        wsum += x['voters_lower']
    return {
        'as_of': '2026-09-30',
        'poll_source': POLL_SOURCE,
        'poll': POLL, 'muslim_share_used': MUSLIM_SHARE,
        'non_muslim_derived': {k: round(v, 1) for k, v in non_muslim().items()},
        'seats_total': len(out),
        'seats_nda_vs_india': len(two),
        'voters_lower': round(sum(x['voters_lower'] for x in out)),
        'voters_upper': round(sum(x['voters_upper'] for x in out)),
        'comp_booth_all': {k: round(v / wsum, 1) for k, v in tot_c.items()},
        'summary': summary,
        'breakeven_bands': bands,
        'close': [{'ac': x['ac'], 'name': x['name'], 'winner': x['winner'], 'runner_up': x['runner_up'], 'margin': x['margin'],
                   'modelled': x['modelled'],
                   'voters_lower': x['voters_lower'], 'breakeven_lower': x['breakeven_lower'],
                   'booth_lower': x['booth_lower'], 'booth_upper': x['booth_upper']} for x in close],
        'seats': out,
    }


def hyderabad():
    """Break-even against the 2023 margin, and the religion of the removed
    against the roll. No vote model: there are no polling-station results
    here, and a runner-up such as Yakutpura's MBT draws on the same voters as
    the winner, so no split by religion can be assumed for it."""
    s = json.load(open(os.path.join(ROOT, 'data', 'hyderabad', 'summary.json')))
    out = []
    for a in s['acs']:
        e = a['e2023']
        valid, margin = e['valid'], e['margin']
        t = valid / a['electors']
        m = a['muslim_share_roll'] / 100
        dm = a['electors'] * m * a['muslim_rate'] / 100
        dh = a['electors'] * (a['hindu_share_roll'] / 100) * a['hindu_rate'] / 100
        rs = a.get('reasons') or {}
        alive = a['deleted'] - rs.get('Death', 0)
        V = alive * t
        out.append({'name': a['name'], 'winner': e['winner'], 'margin': margin, 'valid': valid,
                    'turnout_on_roll': round(100 * t, 1), 'deleted': a['deleted'], 'dead': rs.get('Death', 0),
                    'voters': round(V), 'muslim_share_roll': a['muslim_share_roll'],
                    'muslim_share_removed': round(100 * dm / (dm + dh), 1),
                    'breakeven': round(100 * (1 + margin / V) / 2, 1)})
    return {'as_of': '2026-09-30', 'seats': out}


def write(path, obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    if CHECK:
        old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
        if old != s:
            print('STALE', path)
            sys.exit(1)
        return
    open(path, 'w', encoding='utf-8').write(s)


if __name__ == '__main__':
    write(os.path.join(ROOT, 'data', 'bihar', 'impact.json'), bihar())
    write(os.path.join(ROOT, 'data', 'hyderabad', 'impact.json'), hyderabad())
    print('OK' if CHECK else 'wrote data/bihar/impact.json and data/hyderabad/impact.json')
