#!/usr/bin/env python3
"""The downloadable tables for Bihar, Hyderabad and All India, written from the published JSON.

    python3 scripts/build_downloads.py          # writes the CSVs
    python3 scripts/build_downloads.py --check  # fails if any is stale

Counts only; every column is an aggregate the pages already show.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
J = lambda *p: json.load(open(os.path.join(ROOT, 'data', *p), encoding='utf-8'))


def table(rows, cols):
    b = io.StringIO()
    w = csv.writer(b, lineterminator='\n')
    w.writerow([c for c, _ in cols])
    for r in rows:
        w.writerow(['' if f(r) is None else f(r) for _, f in cols])
    return b.getvalue()


def outputs():
    A = J('bihar', 'constituencies.json')
    ac = table(A, [(k, (lambda k: lambda r: r[k])(k)) for k in [
        'ac', 'name', 'district', 'pc', 'reserved', 'border', 'electorate_2025', 'booths', 'p1', 'p2', 'total', 'per_100',
        't_f', 't_m', 'r_dead', 'r_shifted', 'r_absent', 'r_enrolled', 'hindu', 'muslim', 'unknown',
        'win2020', 'al2020', 'margin2020', 'seg2024', 'al2024', 'win2025', 'al2025', 'margin2025', 'votes2025']])
    FS = {f['ac']: f for f in J('bihar', 'final.json')['seats']}
    ac = table(A, [(k, (lambda k: lambda r: r[k])(k)) for k in [
        'ac', 'name', 'district', 'pc', 'reserved', 'border', 'electorate_2025', 'booths', 'p1', 'p2', 'total', 'per_100',
        't_f', 't_m', 'r_dead', 'r_shifted', 'r_absent', 'r_enrolled', 'hindu', 'muslim', 'unknown',
        'win2020', 'al2020', 'margin2020', 'seg2024', 'al2024', 'win2025', 'al2025', 'margin2025', 'votes2025']] +
               [(n, (lambda k: lambda r: FS[r['ac']][k])(k)) for n, k in (('draft_roll', 'draft'), ('added_after_draft', 'added'), ('removed_after_draft', 'removed_after'),
                                                                     ('final_roll', 'final'), ('final_less_draft', 'net_after'), ('net_fall', 'net_fall'))])
    D = J('bihar', 'districts.json')
    RS = {d['district']: d for d in J('bihar', 'reasons.json')['districts']}
    ID = {d['district']: d for d in J('bihar', 'identity.json')['districts']}
    dist = table(D, [('district', lambda r: r['district']), ('constituencies', lambda r: r['acs']), ('removed', lambda r: r['deleted']),
                     ('per_100', lambda r: r['per_100']), ('border', lambda r: r['border'])] +
                 [(k, (lambda k: lambda r: RS[r['district']][k])(k)) for k in ('dead', 'shifted', 'absent', 'already_enrolled')] +
                 [('women_pct_removed', lambda r: ID[r['district']]['female_share_deleted']),
                  ('muslim_pct_removed_low', lambda r: ID[r['district']]['muslim_share_deleted_low']),
                  ('muslim_pct_removed_high', lambda r: ID[r['district']]['muslim_share_deleted_high'])])
    H = J('hyderabad', 'summary.json')
    reasons = H['reasons']
    hac = table(H['acs'], [('constituency', lambda r: r['name']), ('electors', lambda r: r['electors']), ('struck_off', lambda r: r['deleted']),
                           ('pct_struck_off', lambda r: r['rate']), ('summoned_to_hearing', lambda r: r['hearing']),
                           ('pct_summoned', lambda r: r['hearing_rate'])] +
                [(k.lower().replace('/', '_').replace(' ', '_'), (lambda k: lambda r: r['reasons'][k])(k)) for k in reasons] +
                [('women_pct_struck_off', lambda r: r['female_rate']), ('men_pct_struck_off', lambda r: r['male_rate']),
                 ('margin_2023', lambda r: r['e2023']['margin'])])
    P = J('hyderabad', 'parts.json')
    parts = table([dict(zip(P['fields'], r)) for r in P['rows']], [(k, (lambda k: lambda r: r[k])(k)) for k in P['fields']])
    # All India: the process timeline and schedules, women among the removed, the final rolls
    PR = J('india', 'process.json')
    src = lambda r: ' | '.join(x['url'] for x in r.get('src', []))
    tl = table(PR['timeline'], [('date', lambda r: r['date']), ('who', lambda r: {'eci': 'Election Commission', 'sc': 'Supreme Court', 'ceo': 'State election officer'}.get(r['who'], r['who'])),
                                ('phase', lambda r: r['phase']), ('title', lambda r: r['title']), ('what_changed', lambda r: r['text']),
                                ('documents', lambda r: ' | '.join(x['name'] for x in r.get('src', []))), ('document_links', src)])
    rng = lambda k, i: lambda r: (r.get(k) or [None, None])[i] if isinstance(r.get(k), list) else None
    steps = [dict(st, state=S['state'], phase_=S['phase']) for S in PR['schedules'] for st in S['steps']]
    sch = table(steps, [('state', lambda r: r['state']), ('phase', lambda r: r['phase_']), ('schedule', lambda r: r.get('label')),
                        ('as_published', lambda r: 'yes' if r.get('kind') == 'published' else 'no'),
                        ('enumeration_from', rng('enum', 0)), ('enumeration_to', rng('enum', 1)), ('draft_roll', lambda r: r.get('draft')),
                        ('claims_from', rng('claims', 0)), ('claims_to', rng('claims', 1)), ('notices_from', rng('notice', 0)), ('notices_to', rng('notice', 1)),
                        ('final_roll', lambda r: r.get('final')), ('document_link', lambda r: r.get('src'))])
    IN = J('india', 'states.json')
    gen = table(IN['gender'], [('state', lambda r: r['state']), ('phase', lambda r: r['phase']), ('women_removed', lambda r: r['women_removed']),
                               ('men_removed', lambda r: r['men_removed']), ('women_pct_of_removed', lambda r: r['women_share_removed']),
                               ('women_pct_of_roll', lambda r: r['women_share_roll']), ('gap_points', lambda r: r['gap']),
                               ('quality', lambda r: r['quality']), ('note', lambda r: r['note']), ('source', lambda r: r['source_url'])])
    FR = [r for r in IN['states'] if r.get('electors_final') or r.get('final_date')]
    fin = table(FR, [('state', lambda r: r['state']), ('phase', lambda r: r['phase']), ('roll_before', lambda r: r['electors_before']),
                     ('left_off_draft', lambda r: r['removed']), ('final_date', lambda r: r.get('final_date')),
                     ('added_after_draft', lambda r: r.get('added_after_draft')), ('removed_after_draft', lambda r: r.get('removed_after_draft')),
                     ('withheld', lambda r: r.get('withheld')), ('final_roll', lambda r: r.get('electors_final')),
                     ('final_less_draft', lambda r: r.get('net_after_draft')), ('net_fall', lambda r: r.get('net_fall')),
                     ('net_fall_per_100', lambda r: r.get('net_fall_per_100')), ('reconciles', lambda r: r.get('reconciles')),
                     ('source', lambda r: (r.get('final_source') or {}).get('url'))])
    return {
        os.path.join(ROOT, 'data', 'india', 'process_timeline.csv'): tl,
        os.path.join(ROOT, 'data', 'india', 'process_schedules.csv'): sch,
        os.path.join(ROOT, 'data', 'india', 'women_removed.csv'): gen,
        os.path.join(ROOT, 'data', 'india', 'final_rolls.csv'): fin,
        os.path.join(ROOT, 'data', 'bihar', 'constituencies.csv'): ac,
        os.path.join(ROOT, 'data', 'bihar', 'districts.csv'): dist,
        os.path.join(ROOT, 'data', 'hyderabad', 'constituencies.csv'): hac,
        os.path.join(ROOT, 'data', 'hyderabad', 'parts.csv'): parts,
    }


def main():
    out = outputs()
    if '--check' in sys.argv:
        stale = [p for p, s in out.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != s]
        if stale:
            sys.exit('stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale) + ' (run scripts/build_downloads.py)')
        print('PASS: downloads are current')
        return
    for p, s in out.items():
        open(p, 'w', encoding='utf-8').write(s)
        print('wrote', os.path.relpath(p, ROOT))


if __name__ == '__main__':
    main()
