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
    MEASURE = {'Bihar': 'names removed in both phases', 'West Bengal': 'fall in the roll, 2024 roll to the 2026 election roll',
               'Kerala': 'fall in the roll, January 2025 roll to the draft', 'Uttarakhand': 'names removed after the draft'}
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

    dl = load('delhi', 'summary.json')
    over = [s for s in states if s['gap'] > 0]
    summary = dict(states=len(states), over=len(over), over_1=sum(1 for s in states if s['gap'] >= 1),
                   top=states[0]['state'], top_gap=states[0]['gap'], delhi_w=dl['women_left_per_100'], delhi_m=dl['men_left_per_100'],
                   district_over=sum(d['over'] for d in districts), district_n=sum(d['districts'] for d in districts),
                   uk_acs_over=uk['acs_women_over'], kl_acs_over=kl['acs_women_over'])
    return dict(summary=summary, states=states, districts=districts, after=after, after_added_only=after_added_only, bihar=bihar)


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
