"""Assam's Special Revision of 2025-26, and the record around it: D-voters,
Foreigners Tribunals, detention centres and the 2019 NRC.

Reads data/assam/raw (sources and checks in SOURCES.md there) and writes
data/assam/summary.json and data/assam/assam.csv.

    python3 scripts/build_assam.py           # write
    python3 scripts/build_assam.py --check   # fail if the output is stale

- Assam had a Special Revision under section 21 of the Representation of the
  People Act 1950, ordered on 17 November 2025, and no Special Intensive
  Revision. Existing electors filled no enumeration form and showed no
  document, and the order makes no link to an earlier roll or to the NRC.
- The 10,56,291 names (dead, shifted, entered more than once) were reported as
  identified for deletion. No figure from the Chief Electoral Officer says they
  were off the draft, and the draft is larger than the roll of January 2025, so
  every page calls them flagged for deletion.
- Every state figure is the Chief Electoral Officer's, as quoted by the press:
  the CEO's own site could not be reached. The context figures are Lok Sabha
  answers of the Ministry of Home Affairs (primary) and, for 2026, the Assam
  Assembly's replies as reported by the press, each row flagged.
- The build fails unless every identity in SOURCES.md holds.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'assam', 'raw')
OUT = os.path.join(ROOT, 'data', 'assam')
CHECK = '--check' in sys.argv


def rows(name):
    return list(csv.DictReader(open(os.path.join(RAW, name + '.csv'), encoding='utf-8')))


def need(ok, msg):
    if not ok:
        raise SystemExit('FAIL - ' + msg)


def num(v):
    return float(v) if '.' in v else int(v)


def build():
    S = {r['item']: int(r['value']) for r in rows('state')}
    draft, draft_ex, dv = S['electors_draft_incl_d_voters_27122025'], S['electors_draft_excl_d_voters_27122025'], S['d_voters_on_draft_27122025']
    need(draft_ex + dv == draft, 'draft without D-voters plus D-voters is not the draft')
    flagged = S['flagged_for_deletion_dead'] + S['flagged_for_deletion_shifted'] + S['flagged_for_deletion_multiple_or_similar_entries']
    need(flagged == S['flagged_for_deletion_total'], 'the three reasons do not add to the printed 10,56,291')
    final = S['electors_final_10022026']
    need(S['electors_final_men'] + S['electors_final_women'] + S['electors_final_third_gender'] == final, 'final roll by sex does not add up')
    draft_f = S['electors_draft_as_stated_with_final_27122025']
    need(draft_f - final == S['net_fall_draft_to_final'], 'draft less final is not the stated fall')
    jan = S['electors_previous_final_roll_jan2025']
    state = dict(roll_jan2025=jan, draft=draft, draft_excl_d=draft_ex, d_voters_draft=dv, draft_as_stated_with_final=draft_f,
                 draft_gap=draft - draft_f, flagged=flagged, flagged_dead=S['flagged_for_deletion_dead'],
                 flagged_shifted=S['flagged_for_deletion_shifted'], flagged_multiple=S['flagged_for_deletion_multiple_or_similar_entries'],
                 net_fall=S['net_fall_draft_to_final'], final=final, final_men=S['electors_final_men'], final_women=S['electors_final_women'],
                 final_third=S['electors_final_third_gender'], women_final_pct=round(100 * S['electors_final_women'] / final, 4),
                 households=S['households_visited'], unenrolled_found=S['unenrolled_eligible_identified_18plus'],
                 prospective_found=S['prospective_electors_identified_17plus'], polling_stations=S['polling_stations_after_rationalisation_draft'],
                 blos=S['blos'], draft_vs_jan=draft - jan, final_vs_jan=final - jan,
                 flagged_per_100_draft=round(100 * flagged / draft, 4))

    # the context: D-voters over time, the tribunals, detention, the NRC
    dvot = [dict(as_of=r['as_of'], value=int(r['d_voters']), women=int(r['d_voters_women']) if r['d_voters_women'] else None,
                 source=r['source'], primary=r['primary'] == 'true') for r in rows('d_voters')]
    ft = {(r['as_of'], r['item']): dict(value=num(r['value']), source=r['source'], primary=r['primary'] == 'true') for r in rows('foreigners_tribunals')}
    ftv = {k[1] if k[1] != 'cases_disposed_by_FTs' else 'disposed_' + k[0]: v for k, v in ft.items()}
    disposed = [dict(year=int(y), value=int(ftv['disposed_' + y]['value'])) for y in ('2016', '2017', '2018', '2019', '2020')]
    need(sum(d['value'] for d in disposed) == 136064, 'tribunal disposals 2016-2020 do not add to the printed 1,36,064')
    a26 = {k: int(ftv[k]['value']) for k in ('d_voter_cases_referred_to_FTs_cumulative', 'd_voter_cases_disposed_cumulative',
                                               'd_voters_declared_foreigners_by_FTs', 'd_voters_declared_indian_by_FTs',
                                               'border_police_cases_referred_to_FTs_cumulative', 'border_police_cases_disposed',
                                               'border_police_cases_declared_foreigners', 'declared_foreigners_expelled_total')}
    a26['d_voter_disposals_not_described'] = a26['d_voter_cases_disposed_cumulative'] - a26['d_voters_declared_foreigners_by_FTs'] - a26['d_voters_declared_indian_by_FTs']
    a26['d_voter_cases_pending_implied'] = a26['d_voter_cases_referred_to_FTs_cumulative'] - a26['d_voter_cases_disposed_cumulative']
    need(a26['d_voter_disposals_not_described'] == 83760, 'the undescribed D-voter disposals moved from 83,760')
    tribunals = dict(
        to_oct2019=dict(referred=int(ftv['matters_referred_to_FTs_cumulative']['value']), indian=int(ftv['persons_declared_indian_by_FTs_cumulative']['value']),
                        foreigners=int(ftv['persons_declared_foreigners_by_FTs_cumulative']['value']), deported_after_declaration=int(ftv['persons_deported_after_FT_declaration_bangladesh']['value']) + int(ftv['persons_deported_after_FT_declaration_afghanistan']['value'])),
        women_declared_2019=int(ftv['women_declared_foreigners']['value']),
        deported_to_dec2019=int(ftv['foreigners_deported_to_country_of_origin']['value']),
        pending_d_voter_cases_2020=int(ftv['pending_d_voter_cases_in_FTs']['value']),
        declared_2015_to_jun2020=int(ftv['persons_declared_foreigners']['value']),
        pending_dec2020=int(ftv['cases_pending_in_FTs_all']['value']),
        tribunals_2021=int(ftv['FTs_constituted']['value']), disposed=disposed,
        assembly_2026=a26, assembly_2026_press=True,
        sent_to_bangladesh_2024_26=int(ftv['persons_sent_to_bangladesh']['value']),
        declared_sent_to_bangladesh_2024_26=int(ftv['declared_foreigners_sent_to_bangladesh']['value']))

    cen = [dict(centre=r['centre'], capacity=int(r['capacity_2020']), men=int(r['inmates_men_20191128']), women=int(r['inmates_women_20191128']),
                inmates=int(r['inmates_total_20191128'])) for r in rows('detention_centres')]
    for c in cen:
        need(c['men'] + c['women'] == c['inmates'], '%s: men and women do not add to the inmates' % c['centre'])
    D = {r['item']: int(r['value']) for r in rows('detention_state')}
    need(sum(c['capacity'] for c in cen) == D['capacity_total_2020'], 'centre capacities do not add to 3,331')
    need(sum(c['inmates'] for c in cen) == D['inmates_total_20191128'], 'inmates do not add to 970')
    need(sum(c['men'] for c in cen) == D['inmates_men_20191128'] and sum(c['women'] for c in cen) == D['inmates_women_20191128'], 'inmates by sex do not add up')
    detention = dict(centres=cen, capacity=D['capacity_total_2020'], inmates=D['inmates_total_20191128'], men=D['inmates_men_20191128'],
                     women=D['inmates_women_20191128'], matia_capacity=D['matia_goalpara_capacity_under_construction_2020'],
                     died=D['inmates_died_20190301_20200229'], over_3_years_declared=D['declared_foreigners_over_3_years_in_detention_2019'],
                     over_3_years_convicted=D['convicted_foreigners_over_3_years_in_detention_2019'], detained_2019=D['declared_foreigners_detained_in_2019'],
                     released_after_3_years=D['released_after_3_years_per_sc_10052019'])

    N = {r['item']: num(r['value']) for r in rows('nrc_2019')}
    need(N['persons_found_eligible_for_inclusion_final_nrc_31082019'] + N['persons_left_out_31082019'] == N['persons_applied'], 'NRC included plus left out is not the applicants')
    nrc = dict(included=N['persons_found_eligible_for_inclusion_final_nrc_31082019'], left_out=N['persons_left_out_31082019'], applied=N['persons_applied'],
               left_out_pct=round(100 * N['persons_left_out_31082019'] / N['persons_applied'], 4), cost_crore=N['approved_cost_rs_crore'])

    rules = [dict(aspect=r['aspect'], assam=r['assam_special_revision'], para=r['assam_para'], quote=r['assam_quote'], sir=r['sir_phase2']) for r in rows('rules')]
    schedule = [dict(step=int(r['step']), activity=r['activity'], start=r['from'] or None, end=r['to'] or None) for r in rows('schedule')]
    return dict(state=state, d_voters=dvot, tribunals=tribunals, detention=detention, nrc=nrc, rules=rules, schedule=schedule)


def as_csv(d):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['section', 'item', 'as_of', 'value', 'source', 'primary'])
    for name in ('state', 'd_voters', 'foreigners_tribunals', 'detention_state', 'nrc_2019'):
        for r in rows(name):
            if name == 'state':
                w.writerow(['revision', r['item'], '', r['value'], r['source'], 'press'])
            elif name == 'd_voters':
                w.writerow(['d_voters', 'd_voters', r['as_of'], r['d_voters'], r['source'], 'primary' if r['primary'] == 'true' else 'press'])
            else:
                w.writerow([name, r['item'], r.get('as_of', ''), r['value'], r['source'], 'primary' if r['primary'] == 'true' else 'press'])
    for c in d['detention']['centres']:
        for k in ('capacity', 'men', 'women', 'inmates'):
            w.writerow(['detention_centres', c['centre'] + ' ' + k, '2020-03' if k == 'capacity' else '2019-11-28', c[k],
                        'Lok Sabha USQ 3880, 17.03.2020' if k == 'capacity' else 'Lok Sabha USQ 2340, 03.12.2019', 'primary'])
    return buf.getvalue()


def main():
    d = build()
    files = {os.path.join(OUT, 'summary.json'): json.dumps(d, ensure_ascii=False, indent=1) + '\n',
             os.path.join(OUT, 'assam.csv'): as_csv(d)}
    stale = [p for p, t in files.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != t]
    if CHECK:
        if stale:
            raise SystemExit('FAIL - stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale))
        print('OK: Assam figures add up and are current')
        return
    for p, t in files.items():
        open(p, 'w', encoding='utf-8').write(t)
    print(json.dumps(d['state']))


if __name__ == '__main__':
    main()
