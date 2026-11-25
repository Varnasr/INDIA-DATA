"""Women and the revision: every count the site holds of who was removed, by
sex, gathered in one place for india/women/.

Writes data/india/women.json and data/india/women.csv.

    python3 scripts/build_women.py           # write
    python3 scripts/build_women.py --check   # fail if the output is stale

No new source. Everything is read from files other builds already write:
data/india/states.json (the curated split by sex, with a quality flag per
state), each state's summary, district and constituency files, and Bihar's
final roll and tests.

- Per 100 women and per 100 men. The roll before by sex is the state's roll
  before the revision times women's share of it, both from states.json.
- District by district, four states, each in its own measure and never set
  against each other: Bihar (the names removed in both phases), West Bengal and
  Kerala (the fall in the roll), Uttarakhand (the names removed after the
  draft). The gap is women's share of that count less their share of the roll
  it is taken from.
- After the draft: women's share of the names added and of the names removed
  after the draft, against their share of the draft, where a state published
  both by sex.
- Third-gender electors: on the roll before the revision and left off the
  draft, per 100, beside all electors left off per 100, for every state where
  both counts are published. Read from each state's raw/normal.json, Bihar's
  phase 1 lists and Format 4B, Delhi's raw/state.csv and, for West Bengal,
  data/india/raw/third_gender.csv. Each figure says whether it is official,
  came through the press, or is a difference worked out from two published
  counts.
- Age and sex: Uttar Pradesh's entries of the 2024 roll not found on the
  draft, by age band, for women and men, from data/uttarpradesh/analysis.json
  (s1d labs' digitised rolls, counted by scripts/count_s1d_up.py), beside
  Diagram Chasing's findings for Uttar Pradesh and Karnataka as the reading
  list records them (each figure is checked against that summary), and
  women's share of Bihar's phase 1 lists by age band and reason.
- Women per 1,000 men on the roll before the revision, on the draft, on the
  final roll and on the draft of the summary revision, for every state with
  the roll by sex at one stage or more. Each stage is a count of women and men,
  women's share alone, or a ratio as published, and says which. The page
  works the ratio out.
- Reports about women: the disputes items tagged Women that concern women on
  the roll or women working on the revision, each with a short note and a link
  to the item.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'india')
CHECK = '--check' in sys.argv


def load(*p):
    return json.load(open(os.path.join(ROOT, 'data', *p), encoding='utf-8'))


def r1(x):
    return round(x, 1)


def build():
    S = load('india', 'states.json')
    by = {s['state']: s for s in S['states']}
    states = []
    for g in S['gender']:
        before = by[g['state']]['electors_before']
        w_roll = before * g['women_share_roll'] / 100
        m_roll = before - w_roll
        w100 = 100 * g['women_removed'] / w_roll
        m100 = 100 * g['men_removed'] / m_roll
        states.append(dict(state=g['state'], quality=g['quality'], phase=g['phase'], source_url=g['source_url'], note=g['note'],
                           share_roll=g['women_share_roll'], share_removed=g['women_share_removed'], gap=r1(g['women_share_removed'] - g['women_share_roll']),
                           women_per_100=r1(w100), men_per_100=r1(m100), ratio=round(w100 / m100, 4)))
    states.sort(key=lambda s: -s['gap'])
    for s in states:
        if not (0 < s['women_per_100'] < 100 and 0 < s['men_per_100'] < 100):
            raise SystemExit('FAIL - %s: a rate outside 0 to 100' % s['state'])

    # district by district
    dist = []
    for r in load('bihar', 'identity.json')['districts']:
        dist.append(dict(state='Bihar', district=r['district'], share_roll=r['female_share_roll'], share=r['female_share_deleted']))
    for r in load('westbengal', 'districts.json'):
        dist.append(dict(state='West Bengal', district=r['district'], share_roll=r['women_2024_pct'], share=r['women_fall_pct']))
    for r in load('kerala', 'districts.json'):
        dist.append(dict(state='Kerala', district=r['district'], share_roll=r['women_2025_pct'], share=r['women_fall_pct']))
    for r in load('uttarakhand', 'districts.json'):
        dist.append(dict(state='Uttarakhand', district=r['district'], share_roll=r['women_draft_pct'], share=r['women_objections_pct']))
    for d in dist:
        d['gap'] = r1(d['share'] - d['share_roll'])
    MEASURE = {'Bihar': 'names left off or deleted in both phases', 'West Bengal': 'fall in the roll, 2024 roll to the 2026 election roll',
               'Kerala': 'fall in the roll, January 2025 roll to the draft', 'Uttarakhand': 'names deleted after the draft'}
    districts = []
    for st, m in MEASURE.items():
        rs = [d for d in dist if d['state'] == st]
        districts.append(dict(state=st, measure=m, districts=len(rs), over=sum(1 for d in rs if d['gap'] > 0),
                              min_gap=min(d['gap'] for d in rs), max_gap=max(d['gap'] for d in rs),
                              rows=sorted([dict(district=d['district'], share_roll=d['share_roll'], share=d['share'], gap=d['gap']) for d in rs], key=lambda d: -d['gap'])))

    # after the draft
    bf = load('bihar', 'final.json')['totals']
    uk = load('uttarakhand', 'summary.json')
    rj = load('rajasthan', 'summary.json')
    after = [dict(state='Bihar', draft=bf['women_share_draft'], added=bf['women_share_added'], removed=bf['women_share_removed_after']),
             dict(state='Uttarakhand', draft=uk['women_draft_pct'], added=uk['women_claims_pct'], removed=uk['women_objections_pct']),
             dict(state='Rajasthan', draft=rj['draft_women_pct'], added=rj['added_women_pct'], removed=rj['deleted_women_pct'])]
    kl = load('kerala', 'summary.json')
    up = load('uttarpradesh', 'summary.json')
    after_added_only = [dict(state='Kerala', added=kl['women_added_pct']), dict(state='Uttar Pradesh', added=up['rise_women_pct'], draft=up['draft_women_pct'])]

    # Bihar against outside records
    t = load('bihar', 'tests.json')
    bihar = dict(dead_share=t['deaths']['women_share_dead'], dead_expected=t['deaths']['women_share_expected'],
                 years_of_deaths=t['deaths']['years_of_deaths'], marriage_excess=t['marriage']['excess'],
                 marriage_years=t['marriage']['excess_years'], marriage_rho=t['marriage']['rho_share'],
                 removed_draft=bf['women_share_p1'], roll_before=bf['women_share_before'],
                 removed_after=bf['women_share_removed_after'], added=bf['women_share_added'], draft=bf['women_share_draft'])

    third = build_third(by)
    age = build_age()
    ratio = build_ratio(S, by)
    reports = build_reports()

    dl = load('delhi', 'summary.json')
    over = [s for s in states if s['gap'] > 0]
    summary = dict(states=len(states), over=len(over), over_1=sum(1 for s in states if s['gap'] >= 1),
                   top=states[0]['state'], top_gap=states[0]['gap'], delhi_w=dl['women_left_per_100'], delhi_m=dl['men_left_per_100'],
                   district_over=sum(d['over'] for d in districts), district_n=sum(d['districts'] for d in districts),
                   uk_acs_over=uk['acs_women_over'], kl_acs_over=kl['acs_women_over'])
    return dict(summary=summary, states=states, districts=districts, after=after, after_added_only=after_added_only, bihar=bihar, third=third,
                age=age, ratio=ratio, reports=reports)


# The states whose own notes say the names left off by sex are the roll before
# less the draft, so their third-gender count left off is a difference too.
LEFT_OFF_IS_DIFFERENCE = {'Goa', 'Manipur', 'Meghalaya'}


def build_third(by):
    rows = []
    for slug in sorted(os.listdir(os.path.join(ROOT, 'data'))):
        p = os.path.join(ROOT, 'data', slug, 'raw', 'normal.json')
        if not os.path.exists(p):
            continue
        N = json.load(open(p, encoding='utf-8'))
        F, SRC = N['figures'], {x['id']: x for x in N['sources']}
        if 'third_before' not in F or not ('third_removed' in F or 'third_draft' in F):
            continue
        kind = lambda f: 'press' if f.get('press') else 'official'
        b = F['third_before']
        if 'third_removed' in F and N['state'] not in LEFT_OFF_IS_DIFFERENCE:
            r, rk = F['third_removed']['v'], kind(F['third_removed'])
            how = 'Both counts are as published in %s.'
        else:
            d = F['third_draft']
            r = b['v'] - d['v']
            rk = 'derived' if not (b.get('press') or d.get('press')) else 'press'
            how = 'The figures are from %s, and the names left off are the roll before less the draft.'
            if 'third_removed' in F:
                assert F['third_removed']['v'] == r, N['state']
        rows.append(dict(state=N['state'], before=b['v'], left_off=r, before_kind=kind(b), left_off_kind=rk,
                         source_url=SRC[b['src']]['url'], note=how % SRC[b['src']]['title']))
    # Bihar: the draft from Format 4B, the names left off counted from the phase 1 lists
    rs = load('bihar', 'reasons.json')
    tl = sum(v['T'] for v in rs['by_sex'].values())
    fb = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'bihar', 'raw', 'final_roll_format4b.csv'), encoding='utf-8')))
    td = sum(int(x['draft_third_gender']) for x in fb)
    rows.append(dict(state='Bihar', before=td + tl, left_off=tl, before_kind='derived', left_off_kind='lists', source_url='',
                     note='The names left off are counted from the phase 1 lists. The roll before is the draft in Format 4B plus those names.'))
    # Delhi: the Chief Electoral Officer's figures as quoted in the press
    dc = {x['measure']: x for x in csv.DictReader(open(os.path.join(ROOT, 'data', 'delhi', 'raw', 'state.csv'), encoding='utf-8'))}
    db, dd = int(dc['roll_before_third_gender']['value']), int(dc['draft_third_gender']['value'])
    assert db - dd == int(dc['left_off_third_gender']['value'])
    rows.append(dict(state='Delhi', before=db, left_off=db - dd, before_kind='press', left_off_kind='derived', source_url='',
                     note="The roll before is the Chief Electoral Officer's figure as the press quoted it, and the draft is from the Chief Electoral Officer's table. The names left off are the difference."))
    # West Bengal: the press note and the AC-wise draft table
    for x in csv.DictReader(open(os.path.join(ROOT, 'data', 'india', 'raw', 'third_gender.csv'), encoding='utf-8')):
        if x['state'] == 'West Bengal':
            ac = sum(int(a['third']) for a in csv.DictReader(open(os.path.join(ROOT, 'data', 'westbengal', 'raw', 'draft_roll_ac.csv'), encoding='utf-8')))
            assert int(x['third_draft']) == ac, 'West Bengal draft third gender differs from draft_roll_ac.csv'
        b, d = int(x['third_before']), int(x['third_draft'])
        rows.append(dict(state=x['state'], before=b, left_off=b - d, before_kind='official', left_off_kind='derived',
                         source_url=x['source_url'], note=x['note']))
    names = [x['state'] for x in rows]
    assert len(names) == len(set(names)), 'a state twice in the third-gender table'
    for x in rows:
        if not 0 <= x['left_off'] <= x['before']:
            raise SystemExit('FAIL - %s: third-gender names left off outside 0 to the roll' % x['state'])
        x['per_100'] = round(100 * x['left_off'] / x['before'], 4)
        x['all_per_100'] = by[x['state']]['per_100']
        x['press'] = 'press' in (x['before_kind'], x['left_off_kind'])
    rows.sort(key=lambda x: x['state'])
    big = [x for x in rows if x['before'] >= 100]
    return dict(min_roll=100, states=len(rows), big=len(big), higher=sum(1 for x in big if x['per_100'] > x['all_per_100']),
                press=[x['state'] for x in rows if x['press']], rows=rows)


# ---- age and sex
# s1d labs' release as data/uttarpradesh/raw/SOURCES.md records it
S1D = {'url': 'https://labs.s1d.me/up-eci', 'version': 2, 'date': '2026-11-25', 'check_2026': 96.77, 'check_2024': 97.35}
# Diagram Chasing's figures by sex and age, as the reading list's summary of
# each piece gives them (data/india/raw/reads_research/round55.json and
# round43.json). Each is checked against that summary by the phrase beside it.
DC_UP = {'url': 'https://diagramchasing.fun/2026/sir/uttar-pradesh', 'date': '2026-11-24',
         'figures': {'added_18_24_gap_lakh': (5.9, '5.9 lakh more men than women aged 18 to 24 added on the final roll'),
                     'ratio_2024': (878, 'from 878 on the 2024 roll'), 'ratio_final': (836, 'to 836 on the final roll'),
                     'ratio_fall_under_25': (122, 'by 122 among electors under 25'),
                     'tg_pct': (38, '38 per cent of registered transgender electors'), 'all_pct': (23, 'against 23 per cent of men and women'),
                     'tg_seats': (316, 'in 316 of 386 constituencies'), 'seats': (386, 'in 316 of 386 constituencies'),
                     'q_women_pct': (62, 'women were 62 per cent of the electors stamped disqualified on the final roll')}}
DC_KA = {'url': 'https://diagramchasing.fun/2026/karnataka-sir', 'date': '2026-11-12',
         'figures': {'old_back': (206, '206 of 8.9 lakh aged 75 and over came back'), 'old_lakh': (8.9, '206 of 8.9 lakh aged 75 and over'),
                     'back_about': (14900, 'about 14,900 came back'), 'found_jan2025': (10548148, '1,05,48,148 electors left off the draft')}}


def _reads(url):
    R = load('india', 'reads.json')
    hit = [x for x in R['items'] if x.get('url') == url]
    assert len(hit) == 1, 'the reading list does not hold %s once' % url
    return hit[0]


def _dc(spec):
    r = _reads(spec['url'])
    assert r['date'] == spec['date'], spec['url']
    for k, (v, phrase) in spec['figures'].items():
        assert phrase in r['shows'], 'Diagram Chasing: "%s" is not in the reading list\'s summary' % phrase
    return dict(url=spec['url'], date=spec['date'], outlet=r['outlet'], authors=r['authors'], **{k: v for k, (v, _) in spec['figures'].items()})


def build_age():
    src = open(os.path.join(ROOT, 'data', 'uttarpradesh', 'raw', 'SOURCES.md'), encoding='utf-8').read()
    for phrase in ('version %d of %s' % (S1D['version'], '25 November'), str(S1D['check_2026']), str(S1D['check_2024']), S1D['url']):
        assert phrase in src.replace('\n', ' '), 's1d labs: "%s" is not in the Uttar Pradesh SOURCES.md' % phrase
    A = load('uttarpradesh', 'analysis.json')['age_sex']
    up = dict(bands=[dict(band=b['band'], women=b['women'], men=b['men'], ratio=b['ratio']) for b in A['bands']],
              women=A['women'], men=A['men'], u35_women=A['u35_women'], u35_men=A['u35_men'], u35_ratio=A['u35_ratio'],
              o55_women=A['o55_women'], o55_men=A['o55_men'], ratio_25_29=A['ratio_25_29'], third=A['third'], third_n=A['third_n'], s1d=S1D)
    dcu = _dc(DC_UP)
    # the counts here and Diagram Chasing's come from the same rolls: the two ratios it states must stay those analysis.json carries
    assert A['dc']['url'] == dcu['url'] and A['dc']['date'] == dcu['date']
    for k in ('u35_ratio', 'ratio_25_29', 'match_from', 'shifted_19_34_women', 'shifted_19_34_men'):
        dcu[k] = A['dc'][k]
    # Bihar: women's share of the phase 1 lists by age band, for every reason together and for each
    rs = load('bihar', 'reasons.json')
    K = ['dead', 'shifted', 'absent', 'already_enrolled']
    for k in K:
        assert sum(rs['by_age'][k]) == sum(rs['by_sex'][k].values()) and sum(rs['by_age_women'][k]) == rs['by_sex'][k]['F'], 'Bihar ages add to the reason ' + k
    nb = len(rs['bands'])
    bihar = dict(bands=rs['bands'], all=[sum(rs['by_age'][k][i] for k in K) for i in range(nb)],
                 all_women=[sum(rs['by_age_women'][k][i] for k in K) for i in range(nb)],
                 **{k: rs['by_age'][k] for k in K}, **{k + '_women': rs['by_age_women'][k] for k in K})
    return dict(up=up, dc_up=dcu, dc_ka=_dc(DC_KA), bihar=bihar)


# ---- women per 1,000 men at each stage
def _acsum(rel, w='women', m='men', where=None):
    rows = list(csv.DictReader(open(os.path.join(ROOT, 'data', rel), encoding='utf-8')))
    if where:
        rows = [r for r in rows if where(r)]
    assert rows, rel
    return dict(women=sum(int(r[w]) for r in rows), men=sum(int(r[m]) for r in rows))


def build_ratio(S, by):
    G = {g['state']: g for g in S['gender']}
    GQ = {'lists': 'counted from the lists', 'exact': 'official', 'rounded': 'official, rounded', 'unverified': 'a press analysis that names no source',
          'proxy': 'the January 2025 roll'}
    R = {}

    def put(st, stage, how, **v):
        R.setdefault(st, {})[stage] = dict(how=how, **v)

    for slug in sorted(os.listdir(os.path.join(ROOT, 'data'))):
        p = os.path.join(ROOT, 'data', slug, 'raw', 'normal.json')
        if not os.path.exists(p):
            continue
        N = json.load(open(p, encoding='utf-8'))
        F = N['figures']
        for stage in ('before', 'draft', 'final'):
            if 'women_' + stage in F and 'men_' + stage in F:
                w, m = F['women_' + stage], F['men_' + stage]
                put(N['state'], stage, 'press' if (w.get('press') or m.get('press')) else 'official', women=w['v'], men=m['v'])
    # Bihar: Format 4B for the draft and the final roll, and the roll before as the draft plus the phase 1 lists
    fb = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'bihar', 'raw', 'final_roll_format4b.csv'), encoding='utf-8')))
    rs = load('bihar', 'reasons.json')['by_sex']
    dw, dm = sum(int(x['draft_women']) for x in fb), sum(int(x['draft_men']) for x in fb)
    put('Bihar', 'before', 'the draft in Format 4B plus the names on the phase 1 lists', women=dw + sum(v['F'] for v in rs.values()), men=dm + sum(v['M'] for v in rs.values()))
    put('Bihar', 'draft', 'official', women=dw, men=dm)
    put('Bihar', 'final', 'official', women=sum(int(x['women_final']) for x in fb), men=sum(int(x['men_final']) for x in fb))
    # Uttar Pradesh: the press's ratio for the roll before, the Chief Electoral Officer's draft and final by sex
    up = load('uttarpradesh', 'analysis.json')['sex']
    put('Uttar Pradesh', 'before', 'the Chief Electoral Officer\'s ratio as the press reported it', ratio=up['ratio_before'])
    us = {r['item']: r for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'uttarpradesh', 'raw', 'sir_state_summary.csv'), encoding='utf-8'))}
    for stage in ('draft', 'final'):
        put('Uttar Pradesh', stage, 'official', women=int(us[stage]['women']), men=int(us[stage]['men']))
    assert round(1000 * int(us['draft']['women']) / int(us['draft']['men'])) == up['ratio_draft'], 'Uttar Pradesh draft ratio differs from the press'
    # state tables summed by constituency or district
    put('Tamil Nadu', 'draft', 'official', **_acsum('tamilnadu/raw/draft_roll_ac.csv'))
    put('Tamil Nadu', 'final', 'official', **_acsum('tamilnadu/raw/final_roll_ac.csv'))
    put('West Bengal', 'before', 'official', women=load('westbengal', 'summary.json')['pn05']['before_women'], men=load('westbengal', 'summary.json')['pn05']['before_men'])
    put('West Bengal', 'draft', 'official', **_acsum('westbengal/raw/draft_roll_ac.csv'))
    put('Kerala', 'before', 'the January 2025 roll', **_acsum('kerala/raw/roll_before_ac.csv'))
    put('Kerala', 'draft', 'official', **_acsum('kerala/raw/draft_roll_ac.csv'))
    put('Kerala', 'final', 'official', **_acsum('kerala/raw/final_roll_ac.csv'))
    put('Maharashtra', 'draft', 'official', **_acsum('maharashtra/raw/district_draft.csv'))
    put('Karnataka', 'draft', 'official, general electors', **_acsum('karnataka/raw/draft_roll_district.csv'))
    kf = load('karnataka', 'raw', 'final.json')
    put('Karnataka', 'final', 'press', women=kf['women'], men=kf['men'])
    put('Rajasthan', 'draft', 'official', **_acsum('rajasthan/raw/sir_state_summary.csv', where=lambda r: r['item'] == 'draft_roll' and r['scope'].startswith('199')))
    put('Rajasthan', 'final', 'official, general electors', **_acsum('rajasthan/raw/sir_state_summary.csv', where=lambda r: r['item'] == 'final_roll_general' and r['scope'].startswith('199')))
    ukst = lambda r: r['district'] == 'State'
    put('Uttarakhand', 'draft', 'official', **_acsum('uttarakhand/raw/district_printed.csv', 'draft_women', 'draft_men', where=ukst))
    put('Uttarakhand', 'final', 'official', **_acsum('uttarakhand/raw/district_printed.csv', 'final_women', 'final_men', where=ukst))
    dc = {x['measure']: int(x['value']) for x in csv.DictReader(open(os.path.join(ROOT, 'data', 'delhi', 'raw', 'state.csv'), encoding='utf-8'))}
    put('Delhi', 'before', 'press', women=dc['roll_before_women'], men=dc['roll_before_men'])
    put('Delhi', 'draft', 'official', women=dc['draft_women'], men=dc['draft_men'])
    asm = load('assam', 'summary.json')['state']
    put('Assam', 'final', 'the final roll of Assam\'s special revision, 10 February 2026, as the press reported it', women=asm['final_women'], men=asm['final_men'])
    # the roll before, as women's share only, for the states with no count of it above
    for st, g in G.items():
        if 'before' not in R.get(st, {}):
            put(st, 'before', GQ[g['quality']], women_pct=g['women_share_roll'])
    # the summary revision's draft
    for x in load('india', 'ssr_draft.json')['states']:
        d = x.get('draft')
        if d and d.get('women') is not None and d.get('men') is not None:
            how = 'press' if d.get('press') else ('official' if d['figures'] == 'exact' else d['figures'])
            put(x['state'], 'ssr', how, women=d['women'], men=d['men'], date=d['date'])
    # a count of women and men at the final roll must come near the total the state table holds
    for st, v in R.items():
        f, b = v.get('final'), by.get(st)
        if f and 'women' in f and b and b.get('electors_final') and st != 'Assam':
            gap = abs(f['women'] + f['men'] - b['electors_final']) / b['electors_final']
            assert gap < 0.005, '%s: women and men on the final roll are %.2f%% off its total' % (st, 100 * gap)
        for k, s in v.items():
            if isinstance(s, dict) and 'women' in s:
                assert 0 < s['women'] and 0 < s['men'], (st, k)
                assert 700 < 1000 * s['women'] / s['men'] < 1200, '%s %s: women per 1,000 men out of range' % (st, k)
    # a roll before that is an earlier roll, or a split that names no source, is shown and left out of the findings
    for v in R.values():
        for s in v.values():
            if isinstance(s, dict):
                s['firm'] = s['how'] not in ('the January 2025 roll', 'a press analysis that names no source')
    # Assam had a special revision and no intensive one, so its rows carry no roll before or draft of the intensive revision to miss
    R['Assam']['special'] = True
    rows = [dict(state=st, **v) for st, v in sorted(R.items())]
    stages = ('before', 'draft', 'final', 'ssr')
    none = sorted(st for st in by if st not in R)
    ssr_missing = []
    for x in load('india', 'ssr_draft.json')['states']:
        d = x.get('draft')
        if not (d and d.get('women') is not None):
            ssr_missing.append(dict(state=x['state'], due=x['due'], total_only=bool(d)))
    return dict(rows=rows, counts={k: sum(1 for r in rows if k in r) for k in stages}, none=none, ssr_missing=ssr_missing,
                all_three=[r['state'] for r in rows if all(k in r for k in stages[:3])])


# ---- reports about women: the disputes items tagged Women, each with a short
# note that carries no figure. The item itself carries the figures and the source.
REPORT_NOTES = {
    'process-28': 'women working as assistant booth level officers died in Tapi and Vadodara districts of Gujarat, and the husband of one said she had asked to be excused from the duty, which the Vadodara Collector disputed.',
    'process-13': 'the rules for logical discrepancies include a marital mapping mismatch, where a woman is linked to her father on the old roll and to her husband on the new one.',
    'soft-56': 'a member of the jury at the Telangana Voter Rights Forum\'s public hearings spoke of the difficulty married women have in linking themselves to their parents.',
    'up-35': 'Uttar Pradesh\'s Chief Electoral Officer ordered a special drive to find eligible women who are not on the roll and help them apply on Form 6 in the summary revision.',
    'up-43': 'Uttar Pradesh\'s Chief Electoral Officer set the summary revision\'s draft, for women and for men, against the projected adult population of each.',
    'form7-105': 'sex workers in Maharashtra said they could not link a parent\'s name to the 2002 roll, and the registration officer for Kasba Peth described the documents officials were accepting instead.',
    'up-52': 'the district administration of Gautam Buddh Nagar plans to involve ASHA and anganwadi workers, auxiliary nurse midwives and Sakhi groups to find eligible women and help them apply on Form 6 in the summary revision.',
}


# Tagged Women on the disputes page and kept off this one: the petition of the
# Network of Women in Media, India concerns the police's treatment of
# journalists at the October protests, and neither women electors nor women
# working on the revision.
NOT_ON_PAGE = {'court-83', 'court-91', 'court-93'}


def build_reports():
    T = load('india', 'raw', 'disputes_research', 'tags.json')['items']
    tagged = sorted(k for k, v in T.items() if 'Women' in v.get('issues', []))
    assert not set(REPORT_NOTES) & NOT_ON_PAGE
    assert set(tagged) == set(REPORT_NOTES) | NOT_ON_PAGE, 'disputes tagged Women and the notes differ: %s' % sorted(set(tagged) ^ (set(REPORT_NOTES) | NOT_ON_PAGE))
    D = load('india', 'disputes.json')
    found = {}

    def walk(o):
        if isinstance(o, dict):
            if o.get('id') in REPORT_NOTES:
                found[o['id']] = o
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(D)
    assert set(found) == set(REPORT_NOTES), 'an item tagged Women is not on the disputes page: %s' % sorted(set(REPORT_NOTES) - set(found))
    out = [dict(id=i, date=x['date'], state=x['state'], outlet=x['outlet'], headline=x['headline'], url=x['url'], kind=x['kind'], note=REPORT_NOTES[i])
           for i, x in found.items()]
    return sorted(out, key=lambda r: (r['date'], r['id']), reverse=True)

def as_csv(d):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['level', 'state', 'district', 'measure', 'women_share_of_roll', 'women_share_of_count', 'gap_points',
                'women_left_off_per_100_women', 'men_left_off_per_100_men', 'quality', 'source_url'])
    for s in d['states']:
        w.writerow(['state', s['state'], '', 'names left off the draft', s['share_roll'], s['share_removed'], s['gap'],
                    s['women_per_100'], s['men_per_100'], s['quality'], s['source_url']])
    for g in d['districts']:
        for r in g['rows']:
            w.writerow(['district', g['state'], r['district'], g['measure'], r['share_roll'], r['share'], r['gap'], '', '', '', ''])
    return buf.getvalue()


def main():
    d = build()
    files = {os.path.join(OUT, 'women.json'): json.dumps(d, ensure_ascii=False, indent=1) + '\n',
             os.path.join(OUT, 'women.csv'): as_csv(d)}
    stale = [p for p, t in files.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != t]
    if CHECK:
        if stale:
            raise SystemExit('FAIL - stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale))
        print('OK: women table up to date')
        return
    for p, t in files.items():
        open(p, 'w', encoding='utf-8').write(t)
    print(json.dumps(d['summary']))
    for s in d['states']:
        print(s['state'], s['quality'], s['share_roll'], s['share_removed'], s['gap'], s['women_per_100'], s['men_per_100'], s['ratio'])
    for g in d['districts']:
        print(g['state'], g['over'], 'of', g['districts'], g['min_gap'], g['max_gap'])


if __name__ == '__main__':
    main()
