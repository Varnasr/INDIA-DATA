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

    dl = load('delhi', 'summary.json')
    over = [s for s in states if s['gap'] > 0]
    summary = dict(states=len(states), over=len(over), over_1=sum(1 for s in states if s['gap'] >= 1),
                   top=states[0]['state'], top_gap=states[0]['gap'], delhi_w=dl['women_left_per_100'], delhi_m=dl['men_left_per_100'],
                   district_over=sum(d['over'] for d in districts), district_n=sum(d['districts'] for d in districts),
                   uk_acs_over=uk['acs_women_over'], kl_acs_over=kl['acs_women_over'])
    return dict(summary=summary, states=states, districts=districts, after=after, after_added_only=after_added_only, bihar=bihar, third=third)


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
