#!/usr/bin/env python3
"""Bihar: two tests of the reasons entered on the phase 1 lists.

    python3 scripts/build_bihar_tests.py          # writes data/bihar/tests.json
    python3 scripts/build_bihar_tests.py --check  # fails if it is stale

Deaths. The names entered as dead are set against the adult deaths Bihar
has in a year, from the Sample Registration System: the 2024 death rates by
age and sex (SRS Statistical Report 2024, Table 8) weighted by the 2024
population by age (Table 1) and the mid-year population (Civil Registration
System 2024, Statement 2). Ages 20 and over stand for the roll, because the
rates come in five-year groups and 15-19 straddles the voting age. Women's
share of adults is their share of the roll before the revision, from
data/bihar/summary.json.

Marriage. The excess of young women over young men among those entered as
shifted is set against the women who moved on marriage, from the 2011
census migration table D-3: in scale for the state, and district by
district against the share of women who had moved on marriage in the ten
years before the census. D-3 counts women where they arrived, not where
they left, so the district comparison is with marriage movement in general.

Sources are in data/bihar/raw/srs_bihar.csv, crs_bihar.csv and
census2011_marriage_migration.csv, each row with its table and page.
"""
import collections
import csv
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from build_india import spearman  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = lambda f: os.path.join(ROOT, 'data', 'bihar', 'raw', f)
OUT = os.path.join(ROOT, 'data', 'bihar', 'tests.json')
ADULT = ['20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80-84', '85+']
YOUNG = ('18-24', '25-29')
NAMES = {'East Champaran': 'Purba Champaran', 'West Champaran': 'Pashchim Champaran', 'Kaimur': 'Kaimur (Bhabua)'}


def deaths(rs):
    WOMEN = json.load(open(os.path.join(ROOT, 'data', 'bihar', 'summary.json'), encoding='utf-8'))['totals']['female_share_roll'] / 100
    srs = list(csv.DictReader(open(RAW('srs_bihar.csv'), encoding='utf-8')))
    crs = list(csv.DictReader(open(RAW('crs_bihar.csv'), encoding='utf-8')))
    A = {(x['sex'], x['age_group']): float(x['value']) for x in srs if x['table'] == 'ASDR' and x['year'] == '2024' and x['residence'] == 'Total'}
    P = {(x['sex'], x['age_group']): float(x['value']) for x in srs if x['table'] == 'POP_AGE_DIST_PCT' and x['year'] == '2024' and x['residence'] == 'Total'}
    pop = 1000 * int(next(x['value'] for x in crs if x['table'] == 'MIDYEAR_POPULATION_000' and x['year'] == '2024'))
    rate = sum(P[('Persons', a)] / 100 * A[('Persons', a)] for a in ADULT) / 1000
    dF = sum(P[('Female', a)] / 100 * A[('Female', a)] for a in ADULT) / 1000 * WOMEN
    dM = sum(P[('Male', a)] / 100 * A[('Male', a)] for a in ADULT) / 1000 * (1 - WOMEN)
    adult = round(rate * pop)
    dead = rs['totals']['dead']
    dead_f, dead_m = rs['by_sex']['dead']['F'], rs['by_sex']['dead']['M']
    reg = {x['year']: int(x['value']) for x in crs if x['table'] == 'REGISTERED_DEATHS_STATE'}
    lor = {x['year']: float(x['value']) for x in crs if x['table'] == 'LEVEL_OF_REGISTRATION_DEATHS' and 'revised' not in x.get('note', '').lower()}
    age = {(x['age_group'], x['sex']): int(x['value']) for x in crs if x['table'] == 'REGISTERED_DEATHS_BY_AGE' and x['year'] == '2024' and x['residence'] == 'Total'}
    over25 = [k for k, s in age if s == 'Persons' and k not in ('Less than 1 Year', '1 Year - 4 Year', '5 Year - 14 Year', '15 Year - 24 Year', 'Age Not Stated')]
    assert sum(v for (k, s), v in age.items() if s == 'Persons') == reg['2024'], 'registered deaths by age add to the total'
    d = rs['by_age']['dead']
    assert rs['bands'][6:] == ['70-79', '80+']
    return {
        'year': 2024, 'population': pop, 'adult_deaths_per_1000': round(1000 * rate, 2), 'adult_deaths': adult,
        'dead_removed': dead, 'years_of_deaths': round(dead / adult, 1),
        'women_share_expected': round(100 * dF / (dF + dM), 1), 'women_share_dead': round(100 * dead_f / (dead_f + dead_m), 1),
        'women_expected': round(dead * dF / (dF + dM)), 'women_dead': dead_f,
        'registered_2020_2024': sum(reg[str(y)] for y in range(2020, 2025)), 'registered_2024': reg['2024'],
        'registered_share_2024': lor['2024'],
        'registered_women_share': round(100 * sum(age[(k, 'Female')] for k in over25) / sum(age[(k, 'Persons')] for k in over25), 1),
        'over70_share_dead': round(100 * (d[6] + d[7]) / sum(d[1:]), 1),
        'over70_share_registered': round(100 * age[('70 Year & above', 'Persons')] / sum(age[(k, 'Persons')] for k in over25), 1),
    }


def marriage(rs):
    acs = {a['ac']: a['district'] for a in json.load(open(os.path.join(ROOT, 'data', 'bihar', 'constituencies.json'), encoding='utf-8'))}
    g = collections.defaultdict(collections.Counter)
    for x in csv.DictReader(gzip.open(RAW('reasons_by_ac.csv.gz'), 'rt', encoding='utf-8')):
        g[acs[int(x['ac'])]][(x['reason'], x['sex'], x['age_band'])] += int(x['count'])
    rows = list(csv.DictReader(open(RAW('census2011_marriage_migration.csv'), encoding='utf-8')))
    st = next(x for x in rows if x['row_type'] == 'state')
    m = {x['area_name_census2011']: x for x in rows if x['row_type'] == 'district'}
    assert len(m) == 38 and set(NAMES.get(d, d) for d in g) == set(m), 'the 38 districts match'
    recent = 'female_marriage_migrants_dur_0_9yr_COMPUTED_SUM_of_lt1_1to4_5to9'
    for k in ('female_pop_2011_all_ages', 'female_marriage_migrants_all_durations', recent):
        assert sum(int(x[k]) for x in m.values()) == int(st[k]), k
    ds = []
    for d, c in g.items():
        M = m[NAMES.get(d, d)]
        fp = int(M['female_pop_2011_all_ages'])
        sf = sum(c[('shifted', 'F', a)] for a in YOUNG)
        sm = sum(c[('shifted', 'M', a)] for a in YOUNG)
        ds.append({'district': d, 'young_shifted_f': sf, 'young_shifted_m': sm, 'women_share': round(100 * sf / (sf + sm), 1),
                   'excess_per_1000_women': round(1000 * (sf - sm) / fp, 2), 'recent_marriage_pct': round(100 * int(M[recent]) / fp, 2)})
    sf, sm = sum(x['young_shifted_f'] for x in ds), sum(x['young_shifted_m'] for x in ds)
    assert sf == sum(rs['by_age_women']['shifted'][:2])
    recent_n = int(st[recent])
    out9 = sum(int(st[k]) for k in ('female_marriage_OUTmigrants_to_other_states_dur_lt1', 'female_marriage_OUTmigrants_to_other_states_dur_1_4', 'female_marriage_OUTmigrants_to_other_states_dur_5_9'))
    return {
        'young_shifted_f': sf, 'young_shifted_m': sm, 'excess': sf - sm, 'women_share': round(100 * sf / (sf + sm), 1),
        'recent_marriage': recent_n, 'recent_marriage_per_year': round(recent_n / 10), 'excess_years': round((sf - sm) / (recent_n / 10), 2),
        'out_of_state_recent': out9,
        'rho_share': spearman([(x['recent_marriage_pct'], x['women_share']) for x in ds]),
        'rho_excess': spearman([(x['recent_marriage_pct'], x['excess_per_1000_women']) for x in ds]),
        'top': [x['district'] for x in sorted(ds, key=lambda x: -x['women_share'])[:5]],
        'districts': sorted(ds, key=lambda x: x['district']),
    }


def build():
    rs = json.load(open(os.path.join(ROOT, 'data', 'bihar', 'reasons.json'), encoding='utf-8'))
    return {'deaths': deaths(rs), 'marriage': marriage(rs)}


def main():
    j = json.dumps(build(), ensure_ascii=False, indent=1) + '\n'
    if '--check' in sys.argv:
        if not os.path.exists(OUT) or open(OUT, encoding='utf-8').read() != j:
            sys.exit('stale: data/bihar/tests.json (run scripts/build_bihar_tests.py)')
        print('PASS: data/bihar/tests.json is current')
        return
    open(OUT, 'w', encoding='utf-8').write(j)
    d = json.loads(j)
    print(json.dumps({k: v for k, v in d['deaths'].items()}), json.dumps({k: v for k, v in d['marriage'].items() if k != 'districts'}))


if __name__ == '__main__':
    main()
