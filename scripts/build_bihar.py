#!/usr/bin/env python3
"""Build every Bihar figure the site shows, from the booth-level sources.

    python3 scripts/build_bihar.py          # writes data/bihar/*.json and booths/
    python3 scripts/build_bihar.py --check  # fails if the committed output is stale

Inputs (data/bihar/raw/):
  booths_deletions_ls2024.csv.gz   one row per booth x 2024 Lok Sabha party
                                   (top three parties per booth, from Form 20),
                                   carrying the booth's SIR deletions and the
                                   2020 Assembly winner of its constituency
  booth_gender_religion.csv.gz     SIR deletions per booth x sex, split by
                                   name-estimated religion
  sir_deletions_by_ac_gender_phase.xlsx  CEO Bihar SIR deletions by
                                   constituency, phase and sex
  wikipedia_*.csv                  constituency-to-seat map, 2024 seat results
                                   and alliances, 2025 Assembly results

Two errors in the earlier dashboard are corrected here, and both are why this
script exists rather than a spreadsheet:

1. The booth file has about three rows per booth (one per party) and the
   gender-religion file two (one per sex). Joining them and summing gave every
   booth's deletions six times over: 39.2 million, reported as "2020". There is
   no 2020 deletion series. Every figure below takes one row per booth first.

2. The party labels in the Form 20 extract are wrong in nine seats. Vote
   shares match the official results to a tenth of a point; the names do not
   (LJP(RV) appears as "BSP", HAM(S) as "JD(S)" and so on). LABEL_FIXES
   corrects them, and verify_labels() fails the build unless every seat's
   first and second party then match the declared winner and runner-up.
"""

import gzip
import json
import math
import os
import re
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'bihar', 'raw')
OUT = os.path.join(ROOT, 'data', 'bihar')

# ------------------------------------------------------------------ parties
# Spelling variants, applied everywhere.
SPELLING = {'CPI(ML)(L)': 'CPI(ML)L', 'CPIM-L': 'CPI(ML)L', 'CPI(ML)': 'CPI(ML)L',
            'CPM': 'CPI(M)', 'LJPRV': 'LJP(RV)', 'JDU': 'JD(U)', 'HAM': 'HAM(S)'}

# Label errors, per Lok Sabha seat, with the evidence for each. "verified"
# means the relabelled party's share matches the official winner or runner-up
# share within half a point; "probable" means it matches the third-placed
# candidate, which the published table does not carry, so it rests on the
# share and on who contested.
LABEL_FIXES = {
    'Hajipur':    {'BSP': ('LJP(RV)', 'verified', '53.3% against the winner\'s 53.29%')},
    'Samastipur': {'BSP': ('LJP(RV)', 'verified', '53.0% against 52.97%')},
    'Khagaria':   {'BSP': ('LJP(RV)', 'verified', '50.8% against 50.73%')},
    'Vaishali':   {'BSP': ('LJP(RV)', 'verified', '48.2% against 48.38%')},
    'Jamui':      {'BSP': ('LJP(RV)', 'verified', 'BSP 33.8% and LJPRV 18.8% together 52.6% against 51.98%: one party under two labels')},
    'Gaya':       {'JD(S)': ('HAM(S)', 'verified', '51.4% against 51.36%; JD(S) does not contest in Bihar')},
    'Jahanabad':  {'IND': ('JD(U)', 'verified', 'runner-up 32.5% against JD(U)\'s 32.47%')},
    'Karakat':    {'JVM': ('IND', 'verified', 'runner-up 26.4% against Pawan Singh (independent) 26.63%'),
                   'IND': ('RLM', 'probable', 'third at 24.9%; Upendra Kushwaha (RLM) was the NDA candidate')},
    'Kishanganj': {'CPI': ('AIMIM', 'probable', 'third at 26.9%; CPI fielded no candidate, AIMIM\'s Akhtarul Iman came third')},
}

INDIA = {'RJD', 'INC', 'CPI(ML)L', 'CPI', 'CPI(M)', 'VIP', 'IIP'}


def alliance(party, year):
    """NDA / INDIA / Other. VIP was with the NDA in 2020 and INDIA from 2024;
    LJP fought 2020 alone."""
    if party is None or pd.isna(party):
        return None
    p = SPELLING.get(party, party)
    if year == 2020:
        if p in ('BJP', 'JD(U)', 'VIP', 'HAM(S)'):
            return 'NDA'
        if p in ('RJD', 'INC', 'CPI(ML)L', 'CPI', 'CPI(M)'):
            return 'INDIA'
        return 'Other'
    if p in ('BJP', 'JD(U)', 'LJP(RV)', 'HAM(S)', 'RLM'):
        return 'NDA'
    if p in INDIA:
        return 'INDIA'
    return 'Other'


def norm(s):
    return re.sub(r'\(.*?\)|\[.*?\]|[^a-z]', '', str(s).lower())


# ------------------------------------------------------------------- loaders
def load_booth_rows():
    b = pd.read_csv(os.path.join(RAW, 'booths_deletions_ls2024.csv.gz'))
    b.columns = ['key', 'ac', 'booth', 'deleted', 'ac_name', 'win2020',
                 'margin2020', 'margin2020_pct', 'party', 'votes', 'share']
    return b


def load_map():
    m = pd.read_csv(os.path.join(RAW, 'wikipedia_ac_pc_map.csv'))
    m = m.rename(columns={'No.': 'ac', 'Name': 'name', 'Reservation': 'reserved',
                          'District': 'district', 'Lok Sabha constituency': 'pc'})
    m = m.rename(columns={c: 'electorate_2025' for c in m.columns if c.startswith('Electorate')})
    # Wikipedia files Minapur (90) under Muzaffarpur. It is a Vaishali segment:
    # Muzaffarpur then has six segments and Vaishali six, as delimited in 2008,
    # and both seats' booth totals match the declared results.
    m.loc[m.ac == 90, 'pc'] = 'Vaishali'
    m['reserved'] = m.reserved.fillna('GEN')
    return m


def fix_labels(rows, amap):
    rows = rows.merge(amap[['ac', 'pc']], on='ac', how='left')
    fixed = []
    for pc, party in zip(rows.pc, rows.party):
        if pd.isna(party):
            fixed.append(None)
            continue
        rule = LABEL_FIXES.get(pc, {}).get(party)
        p = rule[0] if rule else party
        fixed.append(SPELLING.get(p, p))
    rows['party_fixed'] = fixed
    return rows


def party_votes(rows):
    """One row per booth x party. Identical source rows are duplicates and are
    dropped; two different source labels that name the same party (Jamui's
    "BSP" and "LJPRV") are one party's votes split, and are added."""
    d = rows.dropna(subset=['party_fixed']).drop_duplicates(['key', 'party'])
    return d.groupby(['key', 'ac', 'pc', 'party_fixed'], as_index=False)[['votes', 'share']].sum()


def verify_labels(rows):
    """Every seat's top two parties, summed from booths, must be the declared
    winner and runner-up, at shares within a point of the published ones."""
    w = pd.read_csv(os.path.join(RAW, 'wikipedia_ls2024_pc_results.csv'))
    w['n'] = w.Constituency_Name.map(norm)
    d = party_votes(rows)
    d = d[d.share > 0].copy()
    d['booth_total'] = d.votes / (d.share / 100)
    btot = d.groupby('key').booth_total.median()
    report, bad = [], []
    for pc, g in d.groupby('pc'):
        tot = btot[g.key.unique()].sum()
        s = g.groupby('party_fixed').votes.sum().sort_values(ascending=False)
        r = w[w.n == norm(pc)].iloc[0]
        want = [SPELLING.get(r['Winner_Party.1'], r['Winner_Party.1']),
                SPELLING.get(r['Runner Up_Party.1'], r['Runner Up_Party.1'])]
        got = list(s.index[:2])
        shares = [round(100 * v / tot, 2) for v in s.values[:2]]
        pub = [float(r['Winner_%']), float(r['Runner Up_%'])]
        ok = got == want and all(abs(a - b) < 1.0 for a, b in zip(shares, pub))
        report.append({'pc': pc, 'first': got[0], 'first_share': shares[0], 'published_first_share': pub[0],
                       'second': got[1], 'second_share': shares[1], 'published_second_share': pub[1], 'match': ok})
        if not ok:
            bad.append((pc, got, want, shares, pub))
    return report, bad


# ------------------------------------------------------------------- build
def build():
    amap = load_map()
    rows = fix_labels(load_booth_rows(), amap)
    report, bad = verify_labels(rows)
    if bad:
        for b in bad:
            print('LABEL MISMATCH', b)
        raise SystemExit('2024 labels do not reconcile with the declared results')

    # one row per booth
    booth = rows.drop_duplicates('key')[['key', 'ac', 'booth', 'deleted', 'win2020', 'margin2020', 'margin2020_pct']].copy()
    assert len(booth) == 77837 and int(booth.deleted.sum()) == 6559626, 'booth totals moved'

    # 2024 booth leader and margin
    v = party_votes(rows)
    v = v[v.party_fixed != 'NOTA']
    v = v.sort_values(['key', 'votes'], ascending=[True, False])
    first = v.drop_duplicates('key').set_index('key')
    second = v.drop(v.drop_duplicates('key').index).drop_duplicates('key').set_index('key')
    booth = booth.set_index('key')
    booth['lead24'] = first.party_fixed
    booth['lead24_share'] = first.share
    booth['lead24_margin'] = (first.share - second.share.reindex(first.index).fillna(0))
    booth['lead24_alliance'] = booth.lead24.map(lambda p: alliance(p, 2024))

    # sex and name-estimated religion per booth
    g = pd.read_csv(os.path.join(RAW, 'booth_gender_religion.csv.gz'))
    g.columns = ['ac', 'key', 'sex', 'hindu', 'muslim', 'unknown']
    g['n'] = g.hindu + g.muslim + g.unknown
    rel = g.groupby('key')[['hindu', 'muslim', 'unknown']].sum()
    sex = g.pivot_table(index='key', columns='sex', values='n', aggfunc='sum').fillna(0)
    for c in ['F', 'M', 'T']:
        booth[c.lower() if c != 'T' else 'third'] = sex.get(c, 0)
    booth = booth.join(rel)
    booth[['f', 'm', 'third', 'hindu', 'muslim', 'unknown']] = booth[['f', 'm', 'third', 'hindu', 'muslim', 'unknown']].fillna(0).astype(int)
    booth = booth.reset_index()

    # constituency level
    sir = pd.read_excel(os.path.join(RAW, 'sir_deletions_by_ac_gender_phase.xlsx'), header=None, skiprows=3)
    sir = sir.iloc[:, :11]
    sir.columns = ['ac', 'sir_name', 'p1_f', 'p1_m', 'p1', 'p2_f', 'p2_m', 'p2', 't_f', 't_m', 'total']
    sir = sir[pd.to_numeric(sir.ac, errors='coerce').notna()].astype({'ac': int})
    ae = pd.read_csv(os.path.join(RAW, 'wikipedia_ae2025_ac_results.csv'))
    ae = ae.rename(columns={'Constituency_No.': 'ac', 'Winner_Party.1': 'win2025', 'Margin_Votes': 'margin2025',
                            'Margin_%': 'margin2025_pct', 'Runner-up_Party.1': 'ru2025'})[['ac', 'win2025', 'ru2025', 'margin2025', 'margin2025_pct']]
    ae['win2025'] = ae.win2025.map(lambda p: SPELLING.get(p, p))
    # Votes come from a second table, not from the one above. Its margin
    # column is wrong in seven seats (two pairs of neighbours swapped, and
    # Daraunda, Raghopur and Bahadurpur mistyped) and its runner-up votes in
    # six more. ae2025_results.csv gives winner and runner-up votes, whose
    # difference is the margin in every seat, and the turnout; Daraunda's
    # 18,367 is also the figure India Today and Deccan Herald reported.
    # Parties still come from the table above.
    res = pd.read_csv(os.path.join(RAW, 'ae2025_results.csv'))
    assert len(res) == 243 and res.ac.is_unique and (res.winner_votes - res.runner_up_votes == res.margin).all()
    ae = ae.drop(columns=['margin2025', 'margin2025_pct']).merge(
        res[['ac', 'winner_votes', 'runner_up_votes', 'margin', 'turnout_pct']].rename(columns={
            'winner_votes': 'winner_votes2025', 'runner_up_votes': 'runner_up_votes2025', 'margin': 'margin2025', 'turnout_pct': 'turnout2025'}),
        on='ac', how='left')
    border = pd.read_csv(os.path.join(ROOT, 'data', 'ac_border_classification.csv'))[['ac_number', 'border_group', 'is_border_ac']].rename(columns={'ac_number': 'ac'})

    seg = v.groupby(['ac', 'party_fixed']).votes.sum().reset_index().sort_values('votes', ascending=False)
    seglead = seg.drop_duplicates('ac').set_index('ac').party_fixed

    a = booth.groupby('ac').agg(booths=('key', 'size'), deleted=('deleted', 'sum'),
                                booth_median=('deleted', 'median'), booth_p90=('deleted', lambda s: s.quantile(.9)),
                                booths_200=('deleted', lambda s: int((s >= 200).sum())),
                                hindu=('hindu', 'sum'), muslim=('muslim', 'sum'), unknown=('unknown', 'sum'),
                                win2020=('win2020', 'first'), margin2020=('margin2020', 'first'),
                                margin2020_pct=('margin2020_pct', 'first'))
    for al in ['NDA', 'INDIA', 'Other']:
        sub = booth[booth.lead24_alliance == al].groupby('ac')
        a['booths_' + al.lower()] = sub.size()
        a['del_' + al.lower()] = sub.deleted.sum()
    a = a.fillna(0).reset_index()
    a['seg2024'] = a.ac.map(seglead)
    a = a.merge(amap, on='ac').merge(sir, on='ac').merge(ae, on='ac', how='left').merge(border, on='ac', how='left')
    assert int(a.p1.sum()) == 6559409 and abs(int(a.p1.sum()) - int(a.deleted.sum())) < 500, 'SIR phase 1 and booth totals diverge'
    # 2020 margins from the Election Commission's Detailed Results
    # (data/bihar/raw/ae2020_results.csv). The booth file's margins differ in
    # eight seats, Gaighat by 15,361 (it gives 22,927 against 7,566), and its
    # percentages are rounded to whole points. The winners agree everywhere.
    e20 = pd.read_csv(os.path.join(RAW, 'ae2020_results.csv')).set_index('ac')
    assert len(e20) == 243
    a['margin2020'] = a.ac.map(e20.margin)
    a['margin2020_pct'] = a.ac.map(e20.margin / e20.votes_polled)
    a['win2020'] = a.win2020.map(lambda p: SPELLING.get(p, p))
    a['al2020'] = a.win2020.map(lambda p: alliance(p, 2020))
    a['al2024'] = a.seg2024.map(lambda p: alliance(p, 2024))
    a['al2025'] = a.win2025.map(lambda p: alliance(p, 2025))
    # Electors in 2025 from the Election Commission's Detailed Results (the
    # _electors rows of ae_party_votes_2020_2025.csv), the roll the election
    # was held on. The published seat list the map comes from agrees in 238
    # seats and has slips in five: Bahadurpur (85) by 9,000 and Bahadurganj
    # (52) by 1,100 are transcription errors.
    pv = pd.read_csv(os.path.join(RAW, 'ae_party_votes_2020_2025.csv'))
    e25 = pv[(pv.party == '_electors') & (pv.year == 2025)].set_index('ac').votes
    assert len(e25) == 243 and e25.index.is_unique, 'ECI electors for every seat'
    a['electorate_2025'] = a.ac.map(e25).astype(int)
    a['per_booth'] = a.deleted / a.booths
    a['per_100_electors'] = 100 * a.total / a.electorate_2025
    # Votes polled: turnout on the 2025 roll. Within about 1% of the winner's
    # votes divided by the winner's share, which the pages do not need.
    a['votes2025'] = (a.turnout2025 / 100 * a.electorate_2025).round()
    a['margin2025_pct'] = 100 * a.margin2025 / a.votes2025

    return booth, a, report


# ---------------------------------------------------------------- identity
# Caste and religion are estimated from names. Neither is recorded on the
# roll. Everything below reports a range rather than a point, and says what
# share of deletions the estimate could not classify at all.

# The 2022-23 Bihar caste-based survey, released 2 October 2023: population
# 130,725,310. Muslim castes are listed inside EBC (10.29 points), BC (2.09)
# and General (4.80); subtracting them gives the Hindu-caste baseline.
SURVEY = {'EBC': 36.01 - 10.29, 'BC': 27.12 - 2.09, 'SC': 19.65, 'ST': 1.68,
          'General': 15.52 - 4.80, 'Muslim': 17.70}
GROUPS = ['General', 'BC', 'EBC', 'SC', 'ST', 'Muslim']


def _variants(s):
    s = str(s).lower().replace('.', '').replace("'", '')
    out = {s}
    rules = [(r'rr', 'r'), (r'ii', 'i'), (r'uu', 'u'), (r'aa', 'a'), (r'm(?=[bcdfgjklpqrstvz])', 'n'),
             (r'v', 'w'), (r'a$', ''), (r'eya$', 'ey'), (r'ri$', 'ry'), (r'i$', 'y'), (r'mha$', 'ngh'),
             (r'sh', 's'), (r'kh', 'k'), (r'ya$', 'i'), (r'ama$', 'am'), (r'ada$', 'ad')]
    for _ in range(3):
        out |= {re.sub(a, b, x) for x in list(out) for a, b in rules}
    return out


def _mapping_class():
    """The project's own surname mapping, as given, keyed on a plain spelling.
    A surname the mapping files under more than one category is 'cross'."""
    m = pd.read_excel(os.path.join(RAW, 'caste_mapping.xlsx'))
    m['k'] = m.lastname.str.lower().str.strip().str.replace(r'[^a-z]', '', regex=True)

    def grp(r):
        c = str(r.CasteCategory).upper()
        if str(r.Religion).strip() == 'Islam' or c == 'MINORITY':
            return 'Muslim'
        return {'OBC': 'BC', 'GENERAL': 'General'}.get(c, c)
    m['g'] = m.apply(grp, axis=1)
    return m.groupby('k').g.agg(lambda x: x.iloc[0] if x.nunique() == 1 else 'cross')


def caste_estimates():
    strict = pd.read_csv(os.path.join(OUT, 'surname_classes.csv')).set_index('romanised').strict_class
    mapping = _mapping_class()
    titles = set(strict[strict == 'none'].index)
    res = {}
    for who, fn in [('guardian', 'deleted_guardian_surname_counts.csv.gz'), ('own', 'deleted_surname_counts.csv.gz')]:
        d = pd.read_csv(os.path.join(RAW, fn)).iloc[:, :2]
        d.columns = ['s', 'n']
        d = d.dropna()
        total = float(d.n.sum())
        est = {}
        # A: the project mapping, reached through the spelling bridge, titles removed
        def a_class(s):
            if s in titles:
                return 'none'
            hits = sorted({mapping[v] for v in _variants(s) if v in mapping.index})
            if not hits:
                return 'unmatched'
            return hits[0] if len(hits) == 1 else 'cross'
        d['A'] = d.s.map(a_class)
        d['B'] = d.s.map(lambda s: strict.get(s, 'unmatched'))
        for k in ['A', 'B']:
            t = d.groupby(k).n.sum()
            classified = float(sum(t.get(g, 0) for g in GROUPS))
            unresolved = total - classified
            est[k] = {
                'coverage_pct': round(100 * classified / total, 1),
                'cross_pct': round(100 * t.get('cross', 0) / total, 1),
                'no_information_pct': round(100 * t.get('none', 0) / total, 1),
                'unmatched_pct': round(100 * t.get('unmatched', 0) / total, 1),
                'groups': {g: {
                    'deleted': int(t.get(g, 0)),
                    'share_of_classified': round(100 * t.get(g, 0) / classified, 1),
                    # bounds over all deletions: none of the unresolved belong / all do
                    'share_low': round(100 * t.get(g, 0) / total, 1),
                    'share_high': round(100 * (t.get(g, 0) + unresolved) / total, 1),
                    'survey_share': round(SURVEY[g], 2),
                    'ratio_to_survey': round((100 * t.get(g, 0) / classified) / SURVEY[g], 2),
                } for g in GROUPS},
            }
        top = d.sort_values('n', ascending=False).head(25)
        est['top_surnames'] = [{'surname': r.s, 'deleted': int(r.n), 'strict': r.B, 'mapping': r.A} for r in top.itertuples()]
        res[who] = est
    return res


DISTRICT_NAMES = {'West Champaran': 'Pashchim Champaran', 'East Champaran': 'Purba Champaran',
                  'Kaimur': 'Kaimur (Bhabua)', 'Jehanabad': 'Jehanabad', 'Purnia': 'Purnia',
                  'Kishanganj': 'Kishanganj', 'Sheikhpura': 'Sheikhpura'}


def women_roll_share(a):
    """Women's share of the roll before the revision: the draft roll by sex
    from Format 4B plus the phase 1 removals by sex."""
    fr = pd.read_csv(os.path.join(RAW, 'final_roll_format4b.csv'))
    return round(100 * (fr.draft_women.sum() + a.p1_f.sum()) / (fr.electors_draft.sum() + a.p1.sum()), 2)


def religion_projection():
    """Each district's Muslim share carried from Census 2011 to 2025 at the
    2001-2011 growth rates of its Muslim and total populations. Jehanabad and
    Arwal were one district in 2001, so both take the joint unit's change."""
    c = pd.read_csv(os.path.join(RAW, 'census_religion_2001_2011.csv'))
    c = c[c.residence == 'Total']
    u = c.pivot_table(index='comparable_unit_2001_2011', columns='census_year',
                      values=['total_persons', 'muslim_persons'], aggfunc='sum')
    gm = np.log(u.muslim_persons[2011] / u.muslim_persons[2001]) / 10
    gt = np.log(u.total_persons[2011] / u.total_persons[2001]) / 10
    ratio = np.exp(14 * (gm - gt))
    c11 = c[(c.census_year == 2011) & (c.district != 'BIHAR (state)')]
    out = {norm(x.district): 100 * x.muslim_persons / x.total_persons * ratio[x.comparable_unit_2001_2011]
           for x in c11.itertuples()}
    st = u.loc['BIHAR (state)']
    state = 100 * st[('muslim_persons', 2011)] / st[('total_persons', 2011)] * ratio['BIHAR (state)']
    assert abs(state - 17.34) < 0.01, 'projected state share moved'
    return out, round(state, 2)


def district_identity(a):
    c = pd.read_csv(os.path.join(RAW, 'census2011_districts_all_india.csv'))
    c = c[c['State name'] == 'BIHAR'].copy()
    assert abs(100 * c.Muslims.sum() / c.Population.sum() - 16.87) < 0.01, 'census religion total moved'
    assert abs(100 * c.SC.sum() / c.Population.sum() - 15.91) < 0.01, 'census SC total moved'
    c['key'] = c['District name'].map(norm)
    a = a.copy()
    a['key'] = a.district.map(lambda d: norm(DISTRICT_NAMES.get(d, d)))
    missing = set(a.key) - set(c.key)
    assert not missing, 'districts not matched to the census: %s' % missing
    g = a.groupby(['district', 'key']).agg(acs=('ac', 'size'), total=('total', 'sum'), p1=('p1', 'sum'), p1_f=('p1_f', 'sum'),
                                           t_f=('t_f', 'sum'), t_m=('t_m', 'sum'), electorate=('electorate_2025', 'sum'),
                                           hindu=('hindu', 'sum'), muslim=('muslim', 'sum'), unknown=('unknown', 'sum')).reset_index()
    g = g.merge(c[['key', 'Population', 'Female', 'Muslims', 'SC']], on='key')
    # Women's share of the roll the names were removed from: the draft roll by
    # sex (Format 4B) plus the phase 1 removals by sex, seat by seat.
    fr = pd.read_csv(os.path.join(RAW, 'final_roll_format4b.csv'))[['ac_number', 'electors_draft', 'draft_women']]
    r = a[['ac', 'district', 'p1', 'p1_f']].merge(fr, left_on='ac', right_on='ac_number', validate='one_to_one')
    assert len(r) == 243, 'a draft roll for every seat'
    r = r.groupby('district').agg(roll=('electors_draft', 'sum'), roll_f=('draft_women', 'sum'), p1=('p1', 'sum'), p1_f=('p1_f', 'sum'))
    g = g.merge(r[['roll', 'roll_f']].rename(columns={'roll': 'draft', 'roll_f': 'draft_f'}), left_on='district', right_index=True)
    proj, _ = religion_projection()
    out = []
    for x in g.itertuples():
        cls = x.hindu + x.muslim + x.unknown
        out.append({
            'district': x.district, 'acs': int(x.acs), 'deleted': int(x.total), 'per_100': round(100 * x.total / x.electorate, 2),
            'female_share_deleted': round(100 * x.t_f / (x.t_f + x.t_m), 1),
            'female_share_roll': round(100 * (x.draft_f + x.p1_f) / (x.draft + x.p1), 1),
            'muslim_share_deleted_low': round(100 * x.muslim / cls, 1),
            'muslim_share_deleted_high': round(100 * (x.muslim + x.unknown) / cls, 1),
            'muslim_share_population_2011': round(100 * x.Muslims / x.Population, 1),
            'muslim_share_projected_2025': round(proj[x.key], 1),
            'sc_share_population_2011': round(100 * x.SC / x.Population, 1),
        })
    return sorted(out, key=lambda r: r['district'])


def district_economy(a):
    """Census 2011 and the state's district GDP series, from the file the old
    dashboard already carried. Only its census and GDDP columns are used: its
    deletion columns were computed from the duplicated join."""
    d = pd.read_csv(os.path.join(ROOT, 'data', 'district_demography_summary.csv'))
    keep = ['district_name', 'census_2011_total_pop', 'census_2011_density_per_sqkm', 'census_2011_literacy_rate',
            'census_2011_female_literacy', 'census_2011_urban_pct', 'per_capita_gddp_2021_22_constant_inr',
            'gddp_prosperity_rank']
    d = d[keep].copy()
    d['key'] = d.district_name.map(norm)
    # urban share and density come from the Registrar General's own table A-01
    # (scripts/census_a01.py), not the compiled file, whose figures differ
    c = pd.read_csv(os.path.join(ROOT, 'data', 'india', 'raw', 'census2011_a01_districts.csv'))
    c = c[c.state == 'Bihar'].copy()
    c['key'] = c.district.map(norm)
    assert set(d.key) <= set(c.key), 'districts not in census A-01: %s' % sorted(set(d.key) - set(c.key))
    d = d.drop(columns=['census_2011_urban_pct', 'census_2011_density_per_sqkm']).merge(
        c[['key', 'urban_pct', 'density']].rename(columns={'urban_pct': 'census_2011_urban_pct', 'density': 'census_2011_density_per_sqkm'}), on='key', how='left')
    bd = pd.read_csv(os.path.join(ROOT, 'data', 'district_border_classification.csv'))
    alias = {'jahanabad': 'jehanabad', 'paschimchamparan': 'pashchimchamparan', 'purvichamparan': 'purbachamparan'}
    bd['key'] = bd.district_name.map(norm).map(lambda k: alias.get(k, k))
    d = d.merge(bd[['key', 'border_group']], on='key', how='left')
    assert d.border_group.notna().all(), 'a district has no border classification'
    a = a.copy()
    a['key'] = a.district.map(lambda x: norm(DISTRICT_NAMES.get(x, x)))
    g = a.groupby(['district', 'key']).agg(acs=('ac', 'size'), total=('total', 'sum'), electorate=('electorate_2025', 'sum'),
                                           booths=('booths', 'sum'), deleted=('deleted', 'sum')).reset_index()
    m = g.merge(d, on='key', how='left')
    missing = m[m.census_2011_total_pop.isna()].district.tolist()
    assert not missing, 'districts not matched to the demography file: %s' % missing
    n = pd.read_csv(os.path.join(RAW, 'nfhs5_districts.csv'))
    n = n[n.indicator.str.startswith('NFHS-5:')].copy()
    n['k'] = n.indicator.str.extract(r'NFHS-5: (\d+)\.')[0].map({'1': 'girls_schooled', '14': 'women_literate',
                                                                  '15': 'women_10yrs', '16': 'child_marriage', '3': 'sex_ratio'})
    n = n.assign(key=n.district.map(norm)).pivot(index='key', columns='k', values='value')
    m = m.merge(n, left_on='key', right_index=True, how='left')
    assert m.women_literate.notna().all(), 'a district has no NFHS-5 figures' 
    return [{'district': x.district, 'acs': int(x.acs), 'deleted': int(x.total),
             'per_100': round(100 * x.total / x.electorate, 2), 'per_booth': round(x.deleted / x.booths, 1),
             'electors_per_booth': round(x.electorate / x.booths, 0),
             'density': int(x.census_2011_density_per_sqkm), 'urban_pct': float(x.census_2011_urban_pct),
             'women_literate': float(x.women_literate), 'girls_schooled': float(x.girls_schooled),
             'child_marriage': float(x.child_marriage),
             'gddp_pc': int(x.per_capita_gddp_2021_22_constant_inr), 'gddp_rank': int(x.gddp_prosperity_rank),
             'border': x.border_group} for x in m.sort_values('district').itertuples()]


def within_seat(booth):
    """NDA-led against INDIA-led booths inside the same constituency.

    Comparing seats mixes politics with geography: Seemanchal loses more names
    and votes differently. Comparing booths within one seat holds the seat
    fixed. The pooled figure is the booth-level difference after removing each
    constituency's mean (a fixed-effects estimate), and the seat-by-seat list
    shows how often the direction holds."""
    b = booth.dropna(subset=['lead24_alliance']).copy()
    b = b[b.lead24_alliance.isin(['NDA', 'INDIA'])]
    b['dm'] = b.deleted - b.groupby('ac').deleted.transform('mean')
    pooled = b.groupby('lead24_alliance').dm.mean()
    seats = []
    for ac, g in b.groupby('ac'):
        n = g.lead24_alliance.value_counts()
        if n.get('NDA', 0) >= 20 and n.get('INDIA', 0) >= 20:
            m = g.groupby('lead24_alliance').deleted.mean()
            seats.append({'ac': int(ac), 'n_nda': int(n['NDA']), 'n_india': int(n['INDIA']),
                          'mean_nda': round(float(m['NDA']), 1), 'mean_india': round(float(m['INDIA']), 1),
                          'diff': round(float(m['NDA'] - m['INDIA']), 1), '_d': float(m['NDA'] - m['INDIA'])})
    # Count the direction on the unrounded difference: rounding first turns a
    # small real gap into 0.0 and drops the seat from both counts.
    diffs = [x.pop('_d') for x in seats]
    return {'pooled_nda_minus_india': round(float(pooled['NDA'] - pooled['INDIA']), 2),
            'booths': int(len(b)), 'seats_compared': len(seats),
            'seats_nda_higher': int(sum(d > 0 for d in diffs)), 'seats_india_higher': int(sum(d < 0 for d in diffs)),
            'median_seat_diff': round(float(pd.Series(diffs).median()), 1), 'seats': seats}


def intensity(booth):
    """Who led the booths that lost the most names.

    `bins` groups booths by how many names they lost, statewide. `within_seat`
    ranks booths inside their own constituency into fifths, so the lightest
    and heaviest fifth of every seat are compared with geography held fixed."""
    b = booth.copy()
    edges = [0, 50, 100, 150, 200, 250, 300, 400, 10**6]
    labels = ['1-49', '50-99', '100-149', '150-199', '200-249', '250-299', '300-399', '400+']
    b['bin'] = pd.cut(b.deleted, bins=edges, right=False, labels=labels)
    out = []
    for lab, g in b.groupby('bin', observed=False):
        led = g.lead24_alliance.value_counts()
        coded = int(led.get('NDA', 0) + led.get('INDIA', 0) + led.get('Other', 0))
        d = int(g.deleted.sum())
        out.append({'bin': lab, 'booths': int(len(g)), 'deleted': d, 'coded': coded,
                    'nda': int(led.get('NDA', 0)), 'india': int(led.get('INDIA', 0)), 'other': int(led.get('Other', 0)),
                    'nda_pct': r(100 * led.get('NDA', 0) / coded, 1), 'india_pct': r(100 * led.get('INDIA', 0) / coded, 1),
                    'other_pct': r(100 * led.get('Other', 0) / coded, 1),
                    'women_pct': r(100 * g.f.sum() / d, 1), 'muslim_pct': r(100 * g.muslim.sum() / d, 1),
                    'hindu_pct': r(100 * g.hindu.sum() / d, 1), 'unknown_pct': r(100 * g.unknown.sum() / d, 1)})
    c = b.dropna(subset=['lead24_alliance']).copy()
    c['q'] = c.groupby('ac').deleted.rank(method='first', pct=True).mul(5).apply(lambda v: min(int(math.ceil(v)), 5))
    ws = []
    for q, g in c.groupby('q'):
        led = g.lead24_alliance.value_counts()
        ws.append({'fifth': int(q), 'booths': int(len(g)), 'mean_deleted': r(g.deleted.mean(), 1),
                   'nda_pct': r(100 * led.get('NDA', 0) / len(g), 1), 'india_pct': r(100 * led.get('INDIA', 0) / len(g), 1)})
    return {'bins': out, 'within_seat_fifths': ws}


# ------------------------------------------------------------------- outputs
def r(x, n=2):
    return None if pd.isna(x) else round(float(x), n)


# ----------------------------------------------------------------- reasons
# The reason the officer entered against each phase 1 removal: dead, shifted,
# absent or already enrolled. Counted from the row-level list by
# scripts/aggregate_bihar_reasons.py, which keeps counts only. Phase 2
# removals (3,51,150) carry no reason in any file used here.
REASONS = ['dead', 'shifted', 'absent', 'already_enrolled']


def load_reasons():
    rb = pd.read_csv(os.path.join(RAW, 'reasons_by_booth.csv.gz'))
    ra = pd.read_csv(os.path.join(RAW, 'reasons_by_ac.csv.gz'))
    assert set(rb.reason) <= set(REASONS) and set(ra.reason) <= set(REASONS), 'unknown reason code'
    assert int(rb['count'].sum()) == 6559626 == int(ra['count'].sum()), 'reason totals moved'
    wide = rb.pivot_table(index=['ac', 'jan_part'], columns='reason', values='count', aggfunc='sum').reindex(columns=REASONS).fillna(0).astype(int)
    return wide.reset_index().rename(columns={'jan_part': 'booth'}), ra


def reasons_summary(ra, a):
    """Statewide, by sex, by age band and by district; phase 1 only."""
    tot = ra.groupby('reason')['count'].sum().reindex(REASONS)
    sx = ra.pivot_table(index='reason', columns='sex', values='count', aggfunc='sum').reindex(REASONS).fillna(0)
    ag = ra.pivot_table(index='age_band', columns='reason', values='count', aggfunc='sum').reindex(columns=REASONS).fillna(0)
    agf = ra[ra.sex == 'F'].pivot_table(index='age_band', columns='reason', values='count', aggfunc='sum').reindex(columns=REASONS).fillna(0)
    bands = ['18-24', '25-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
    ag, agf = ag.reindex(bands).fillna(0), agf.reindex(bands).fillna(0)
    d = a.groupby('district')[['r_' + k for k in REASONS]].sum()
    return {
        'phase': 1, 'total': int(tot.sum()),
        'totals': {k: int(tot[k]) for k in REASONS},
        'by_sex': {k: {sx_: int(sx.loc[k, sx_]) for sx_ in ['F', 'M', 'T'] if sx_ in sx.columns} for k in REASONS},
        'bands': bands,
        'by_age': {k: [int(v) for v in ag[k]] for k in REASONS},
        'by_age_women': {k: [int(v) for v in agf[k]] for k in REASONS},
        'districts': [{'district': dn, **{k: int(v['r_' + k]) for k in REASONS}} for dn, v in d.sort_index().iterrows()],
    }


def outputs(booth, a, report):
    rb, ra = load_reasons()
    booth = booth.merge(rb, on=['ac', 'booth'], how='left')
    assert booth[REASONS].notna().all().all(), 'a booth has no reason counts'
    assert (booth[REASONS].sum(axis=1) == booth.deleted).all(), 'reasons do not add up to a booth\'s removals'
    ac_r = booth.groupby('ac')[REASONS].sum().add_prefix('r_').reset_index()
    a = a.merge(ac_r, on='ac', how='left')
    acs = []
    for _, x in a.sort_values('ac').iterrows():
        acs.append({
            'ac': int(x.ac), 'name': x['name'], 'district': x.district, 'pc': x.pc, 'reserved': x.reserved,
            'border': x.border_group, 'is_border': bool(x.is_border_ac),
            'electorate_2025': int(x.electorate_2025), 'booths': int(x.booths),
            'p1': int(x.p1), 'p2': int(x.p2), 'total': int(x.total),
            'p1_f': int(x.p1_f), 'p1_m': int(x.p1_m), 't_f': int(x.t_f), 't_m': int(x.t_m),
            'per_booth': r(x.per_booth, 1), 'per_100': r(x.per_100_electors, 2),
            'booth_median': r(x.booth_median, 0), 'booth_p90': r(x.booth_p90, 0), 'booths_200': int(x.booths_200),
            'hindu': int(x.hindu), 'muslim': int(x.muslim), 'unknown': int(x.unknown),
            'win2020': x.win2020, 'al2020': x.al2020, 'margin2020': int(x.margin2020), 'margin2020_pct': r(100 * x.margin2020_pct, 1),
            'seg2024': x.seg2024, 'al2024': x.al2024,
            'booths_nda': int(x.booths_nda), 'booths_india': int(x.booths_india), 'booths_other': int(x.booths_other),
            'del_nda': int(x.del_nda), 'del_india': int(x.del_india), 'del_other': int(x.del_other),
            'win2025': x.win2025, 'ru2025': x.ru2025, 'al2025': x.al2025,
            'margin2025': None if pd.isna(x.margin2025) else int(x.margin2025), 'margin2025_pct': r(x.margin2025_pct, 2),
            'votes2025': int(x.votes2025), 'turnout2025': r(x.turnout2025, 1),
            'winner_votes2025': int(x.winner_votes2025), 'runner_up_votes2025': int(x.runner_up_votes2025),
            'r_dead': int(x.r_dead), 'r_shifted': int(x.r_shifted), 'r_absent': int(x.r_absent), 'r_enrolled': int(x.r_already_enrolled),
        })

    # booth files, one per constituency, loaded on demand
    bdir = os.path.join(OUT, 'booths')
    os.makedirs(bdir, exist_ok=True)
    for ac, g in booth.sort_values(['ac', 'booth']).groupby('ac'):
        recs = [[int(b.booth), int(b.deleted), b.lead24 if isinstance(b.lead24, str) else None,
                 r(b.lead24_margin, 1), int(b.f), int(b.m), int(b.hindu), int(b.muslim), int(b.unknown),
                 int(b.dead), int(b.shifted), int(b.absent), int(b.already_enrolled)]
                for b in g.itertuples()]
        write(os.path.join(bdir, 'ac_%03d.json' % ac),
              {'fields': ['booth', 'deleted', 'lead2024', 'lead_margin_pp', 'female', 'male', 'hindu', 'muslim', 'unknown', 'dead', 'shifted', 'absent', 'already_enrolled'], 'rows': recs})

    # state summary
    bins = [0, 50, 100, 150, 200, 250, 300, 400, 10**6]
    labels = ['0-49', '50-99', '100-149', '150-199', '200-249', '250-299', '300-399', '400+']
    hist = pd.cut(booth.deleted, bins=bins, right=False, labels=labels).value_counts().reindex(labels)
    lab = {}
    for year, col in [(2020, 'al2020'), (2024, 'al2024'), (2025, 'al2025')]:
        grp = a.groupby(col).agg(acs=('ac', 'size'), deleted=('total', 'sum'), electorate=('electorate_2025', 'sum'), booths=('booths', 'sum'))
        lab[str(year)] = {k: {'acs': int(v.acs), 'deleted': int(v.deleted), 'per_100': r(100 * v.deleted / v.electorate, 2),
                              'per_booth': r(v.deleted / v.booths, 1)} for k, v in grp.iterrows()}
    bl = booth.dropna(subset=['lead24_alliance']).groupby('lead24_alliance').deleted.agg(['size', 'sum', 'mean', 'median'])
    summary = {
        'totals': {'booths': int(len(booth)), 'acs': int(a.ac.nunique()), 'p1': int(a.p1.sum()), 'p2': int(a.p2.sum()),
                   'total': int(a.total.sum()), 'female': int(a.t_f.sum()), 'male': int(a.t_m.sum()),
                   'female_share_roll': women_roll_share(a),
                   'electorate_2025': int(a.electorate_2025.sum()),
                   'booths_with_2024_result': int(booth.lead24.notna().sum()),
                   'religion_classified': int((booth.hindu + booth.muslim + booth.unknown).sum()),
                   'hindu': int(booth.hindu.sum()), 'muslim': int(booth.muslim.sum()), 'unknown': int(booth.unknown.sum())},
        'booth_histogram': {k: int(v) for k, v in hist.items()},
        'by_alliance_label': lab,
        'by_booth_leader_2024': {k: {'booths': int(v['size']), 'deleted': int(v['sum']), 'mean': r(v['mean'], 1), 'median': r(v['median'], 1)}
                                 for k, v in bl.iterrows()},
        'within_seat_2024': within_seat(booth),
        'intensity': intensity(booth),
        'label_verification': report,
        'label_fixes': {pc: {src: {'party': t[0], 'status': t[1], 'evidence': t[2]} for src, t in fx.items()} for pc, fx in LABEL_FIXES.items()},
    }
    write(os.path.join(OUT, 'constituencies.json'), acs)
    write(os.path.join(OUT, 'districts.json'), district_economy(a))
    write(os.path.join(OUT, 'identity.json'), {'caste': caste_estimates(), 'districts': district_identity(a),
                                               'survey_baseline': SURVEY, 'muslim_projected_2025': religion_projection()[1]})
    write(os.path.join(OUT, 'summary.json'), summary)
    write(os.path.join(OUT, 'reasons.json'), reasons_summary(ra, a))


def write(path, obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(',', ':'), sort_keys=False)
    if CHECK:
        with open(path, encoding='utf-8') as fh:
            if fh.read() != s:
                STALE.append(os.path.relpath(path, ROOT))
        return
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(s)


CHECK = '--check' in sys.argv
STALE = []

if __name__ == '__main__':
    booth, a, report = build()
    outputs(booth, a, report)
    if CHECK:
        if STALE:
            print('STALE: %d generated file(s) differ from the sources: %s' % (len(STALE), STALE[:5]))
            sys.exit(1)
        print('OK: generated Bihar data matches its sources')
    else:
        print('wrote data/bihar: %d constituencies, %d booths, %d deletions' % (a.ac.nunique(), len(booth), booth.deleted.sum()))
