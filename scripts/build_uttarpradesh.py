"""Uttar Pradesh: the names left off the SIR draft roll, by district and
reason, and the state's roll from before the revision to the final roll.

Reads data/uttarpradesh/raw (see SOURCES.md there) and writes
data/uttarpradesh/summary.json, districts.json, districts.csv, and
analysis.json and seats.csv: the names left off set against the 2022 Assembly
margins, the district circumstances, the reasons, the notices after the draft,
the split by sex and by urban and rural area that the CEO gave the press, and
the schedule.

    python3 scripts/build_uttarpradesh.py           # write
    python3 scripts/build_uttarpradesh.py --check   # fail if the output is stale

The district table is the Chief Electoral Officer's handout of 6 January 2026,
known only from a photograph published by India TV and transcribed by eye.
Every row is held by two identities (roll before less draft = total, and the
five reasons add up to the total), and every column adds up to the handout's
printed State row, so a misread digit fails the build. No table by assembly
constituency could be reached, so there is no constituency page.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'uttarpradesh', 'raw')
OUT = os.path.join(ROOT, 'data', 'uttarpradesh')
CHECK = '--check' in sys.argv
R = ('dead', 'untraceable_absent', 'shifted', 'multiple', 'others')
# the handout's printed State row
STATE = {'roll_before': 154430092, 'draft': 125556025, 'dead': 4623796, 'untraceable_absent': 7952190,
         'shifted': 12977472, 'multiple': 2547207, 'others': 773402, 'total': 28874067}


def build():
    rows = list(csv.DictReader(open(os.path.join(RAW, 'asd_district.csv'), encoding='utf-8')))
    assert [int(r['sno']) for r in rows] == list(range(1, 76)), '75 districts, numbered 1 to 75'
    D = []
    for r in rows:
        v = {k: int(r[k]) for k in ('roll_before', 'draft', 'total') + R}
        assert v['roll_before'] - v['draft'] == v['total'] == sum(v[k] for k in R), r['district']
        d = {'district': r['district'].strip(), **v, 'per_100': round(100 * v['total'] / v['roll_before'], 4)}
        for k in R:
            d[k + '_pct'] = round(100 * v[k] / v['total'], 4)
        D.append(d)
    for k, t in STATE.items():
        assert sum(d[k] for d in D) == t, 'column %s does not add up to the State row' % k
    S = {(r['item'], r['date']): r for r in csv.DictReader(open(os.path.join(RAW, 'sir_state_summary.csv'), encoding='utf-8'))}
    get = lambda item: [r for (i, _), r in S.items() if i == item][0]
    dr, fn, nr = get('draft'), get('final'), get('net_rise_draft_to_final')
    assert int(dr['total']) == STATE['draft'] and int(dr['men']) + int(dr['women']) + int(dr['third']) == STATE['draft']
    assert int(fn['total']) - int(dr['total']) == int(nr['total']), 'final less draft equals the net rise'
    ra = get('removed_after_draft')
    f6, f7 = get('form6_2026-01-06_to_2026-03-06'), get('form7_2026-01-06_to_2026-03-06')
    T = STATE['total']
    D.sort(key=lambda d: -d['per_100'])
    summary = {
        'roll_before': STATE['roll_before'], 'draft': STATE['draft'], 'left_off': T, 'per_100': round(100 * T / STATE['roll_before'], 4),
        'reasons': {k: STATE[k] for k in R}, 'shares': {k: round(100 * STATE[k] / T, 4) for k in R},
        'final': int(fn['total']), 'final_date': '2026-04-10', 'net_rise': int(nr['total']), 'made_up_pct': round(100 * int(nr['total']) / T, 4),
        'removed_after': int(ra['total']), 'removed_after_kind': ra['kind'],
        'draft_women_pct': round(100 * int(dr['women']) / STATE['draft'], 4), 'final_women_pct': round(100 * int(fn['women']) / int(fn['total']), 4),
        'rise_women_pct': round(100 * int(nr['women']) / int(nr['total']), 4),
        'form6': int(f6['total']), 'form6_women_pct': round(100 * int(f6['women']) / int(f6['total']), 4),
        'form7': int(f7['total']), 'form7_women_pct': round(100 * int(f7['women']) / int(f7['total']), 4), 'forms_kind': f6['kind'],
        'districts': len(D), 'top': [{'district': d['district'], 'per_100': d['per_100'], 'total': d['total']} for d in D[:5]],
        'low': [{'district': d['district'], 'per_100': d['per_100']} for d in D[-3:]],
        'most_names': max(D, key=lambda d: d['total'])['district'],
        'over_20': sum(d['per_100'] >= 20 for d in D),
    }
    A = analysis(D, summary)
    out = {'analysis.json': json.dumps(A, ensure_ascii=False, indent=1) + '\n', 'summary.json': json.dumps(summary, ensure_ascii=False, indent=1) + '\n',
           'districts.json': json.dumps(D, ensure_ascii=False, separators=(',', ':')) + '\n'}
    buf = io.StringIO(); w = csv.writer(buf, lineterminator='\n')
    cols = ['district', 'roll_before', 'draft', 'total', 'per_100'] + list(R) + [k + '_pct' for k in R]
    w.writerow(['district', 'roll_27_oct_2025', 'draft_roll_6_jan_2026', 'left_off', 'left_off_per_100'] + list(R) + [k + '_pct_of_left_off' for k in R])
    for d in D:
        w.writerow([d[c] for c in cols])
    out['districts.csv'] = buf.getvalue()
    buf = io.StringIO(); w = csv.writer(buf, lineterminator='\n')
    w.writerow(['ac', 'ac_name', 'district', 'electors_2022', 'winner_party_2022', 'alliance_2022', 'margin_2022', 'district_left_off_per_100', 'left_off_spread_by_electors', 'spread_over_margin'])
    for r in A['margins']['seats']:
        w.writerow([r['ac'], r['name'], r['district'], r['electors'], r['party'], r['alliance'], r['margin'], r['per_100'], r['est'], int(r['over'])])
    out['seats.csv'] = buf.getvalue()
    stale = []
    for name, text in out.items():
        path = os.path.join(OUT, name)
        old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
        if old != text:
            stale.append(name)
            if not CHECK:
                open(path, 'w', encoding='utf-8').write(text)
    return summary, stale


# 2022 alliances, as they contested: the NDA (BJP, Apna Dal (Soneylal),
# NISHAD) and the SP's alliance (SP, RLD, SBSP). Codes as the Commission's
# statistical report prints them.
NDA, SPA = {'BJP', 'ADAL', 'NINSHAD'}, {'SP', 'RLD', 'SBSP'}
IND = os.path.join(ROOT, 'data', 'india')


def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def rho(x, y):
    rx, ry = rank(x), rank(y); n = len(x); mx, my = sum(rx) / n, sum(ry) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    return round(sxy / (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5, 4)


def analysis(D, S):
    byd = {d['district']: d for d in D}
    # ---- the 2022 Assembly margins. Each district's names left off are spread
    # over its constituencies by their 2022 electors: it estimates how many
    # seats, never which.
    acd = {int(r['AC_NO']): r['name'] for r in csv.DictReader(open(os.path.join(RAW, 'ac_district.csv'), encoding='utf-8'))}
    res = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'india', 'raw', 'assembly', 'uttarpradesh_2022.csv'), encoding='utf-8')))
    assert len(res) == 403 == len(acd) and set(acd.values()) == set(byd), 'every constituency in a known district'
    tot = {}
    for r in res:
        tot[acd[int(r['ac'])]] = tot.get(acd[int(r['ac'])], 0) + int(r['electors'])
    seats = []
    for r in res:
        dn = acd[int(r['ac'])]; d = byd[dn]; e = int(r['electors']); m = int(r['margin'])
        est = round(d['total'] * e / tot[dn]); p = r['winner_party']
        seats.append({'ac': int(r['ac']), 'name': r['ac_name'], 'district': dn, 'electors': e, 'party': p,
                      'alliance': 'NDA' if p in NDA else 'SP alliance' if p in SPA else 'Other', 'margin': m,
                      'per_100': d['per_100'], 'est': est, 'over': est > m})
    assert abs(sum(s['est'] for s in seats) - S['left_off']) < 403, 'the spread adds back to the state'
    al = {}
    for a in ('NDA', 'SP alliance', 'Other'):
        g = [s for s in seats if s['alliance'] == a]
        e = sum(s['electors'] for s in g)
        al[a] = {'seats': len(g), 'over': sum(s['over'] for s in g), 'per_100': round(sum(s['per_100'] * s['electors'] for s in g) / e, 4) if g else None}
    close = sorted(seats, key=lambda s: s['margin'])[:40]
    el22 = sum(int(r['electors']) for r in res)
    margins = {'seats': seats, 'over': sum(s['over'] for s in seats), 'n': len(seats), 'alliances': al,
               'under_5000': sum(s['margin'] < 5000 for s in seats), 'under_5000_over': sum(s['over'] for s in seats if s['margin'] < 5000),
               'median_margin': sorted(s['margin'] for s in seats)[201], 'median_est': sorted(s['est'] for s in seats)[201],
               'smallest_ratio': round(min(s['est'] / s['margin'] for s in seats), 3),
               'close40_over': sum(s['over'] for s in close), 'electors_2022': el22}
    # the state spread with no district split, as the All India margins page has it
    margins['state_even_over'] = sum(round(S['left_off'] * s['electors'] / el22) > s['margin'] for s in seats)
    # ---- the rolls behind the revision: 2022 Assembly, 2024 Lok Sabha and the
    # projected population aged 18 and over on 1 March 2026
    ad = [r for r in csv.DictReader(open(os.path.join(IND, 'raw', 'adults_ls2024.csv'), encoding='utf-8')) if r['state'] == 'Uttar Pradesh'][0]
    rolls = {'assembly_2022': el22, 'ls_2024': int(ad['electors_2024']), 'adults_2026': int(ad['adults_2026']),
             'before_per_100_adults': round(100 * S['roll_before'] / int(ad['adults_2026']), 2),
             'draft_per_100_adults': round(100 * S['draft'] / int(ad['adults_2026']), 2),
             'final_per_100_adults': round(100 * S['final'] / int(ad['adults_2026']), 2)}
    # ---- district circumstances: read from the factors and urban pages' own
    # files, so this page cannot disagree with them
    F = json.load(open(os.path.join(IND, 'factors.json'), encoding='utf-8'))
    fu = [x for x in F['states'] if x['state'] == 'Uttar Pradesh'][0]
    lab = {f['key']: f['label'] for f in F['factors']}
    U = [x for x in json.load(open(os.path.join(IND, 'urban.json'), encoding='utf-8'))['states'] if x['state'] == 'Uttar Pradesh'][0]
    uchance = round(1.96 / (U['units'] - 1) ** 0.5, 4)
    factors = {'chance': fu['chance'], 'n': 75, 'rows': [{'key': k, 'label': lab[k], 'rho': v['rho'], 'clear': v['clear'], 'n': v['n']} for k, v in fu['survey'].items()],
               'urban': {'rho': U['rho'], 'units': U['units'], 'chance': uchance, 'clear': abs(U['rho']) > uchance, 'bands': U['bands']}}
    # ---- the reasons against the rate, district by district
    reasons = {k: rho([d[k + '_pct'] for d in D], [d['per_100'] for d in D]) for k in R}
    # ---- the CEO's figures as the press carried them (press_ceo.csv)
    P = {r['item']: r for r in csv.DictReader(open(os.path.join(RAW, 'press_ceo.csv'), encoding='utf-8'))}
    v = lambda k: int(P[k]['value'])
    # men and women, rounded to the lakh: the roll before by sex is the draft
    # by sex (exact, the CEO's own) plus the rounded names left off
    dr = {r['item']: r for r in csv.DictReader(open(os.path.join(RAW, 'sir_state_summary.csv'), encoding='utf-8'))}['draft']
    wb_, mb_ = int(dr['women']) + v('left_off_women'), int(dr['men']) + v('left_off_men')
    assert abs(v('left_off_women') + v('left_off_men') - S['left_off']) < 100000, 'the rounded split adds to the total'
    sex = {'women': v('left_off_women'), 'men': v('left_off_men'), 'women_share': round(100 * v('left_off_women') / (v('left_off_women') + v('left_off_men')), 2),
           'women_share_before': round(100 * wb_ / (wb_ + mb_), 2), 'women_per_100': round(100 * v('left_off_women') / wb_, 2), 'men_per_100': round(100 * v('left_off_men') / mb_, 2),
           'ratio_before': v('sex_ratio_roll_2025'), 'ratio_draft': v('sex_ratio_draft'), 'ratio_final': round(1000 * 60909525 / 73071061),
           'father_scrutinised': v('women_father_address_scrutinised'), 'father_left_off': v('women_father_address_left_off'), 'father_kept': v('women_father_address_kept'),
           'father_beyond_multiple': v('women_father_address_left_off') - S['reasons']['multiple'], 'source': P['left_off_women']['source']}
    assert sex['ratio_final'] == 834
    ur, uu = v('roll_before_rural') - v('draft_rural'), v('roll_before_urban') - v('draft_urban')
    # each figure is rounded to the lakh, so the two parts may miss the exact total by a lakh
    assert abs(v('roll_before_rural') + v('roll_before_urban') - S['roll_before']) <= 100000 and abs(v('draft_rural') + v('draft_urban') - S['draft']) <= 100000
    urban = {'urban_before': v('roll_before_urban'), 'urban_draft': v('draft_urban'), 'urban_left': uu, 'urban_per_100': round(100 * uu / v('roll_before_urban'), 2),
             'rural_before': v('roll_before_rural'), 'rural_draft': v('draft_rural'), 'rural_left': ur, 'rural_per_100': round(100 * ur / v('roll_before_rural'), 2),
             'urban_share_roll': round(100 * v('roll_before_urban') / (v('roll_before_urban') + v('roll_before_rural')), 1),
             'urban_share_left': round(100 * uu / (uu + ur), 1), 'printed_rural_left': 12700000, 'source': P['roll_before_urban']['source']}
    # ---- after the draft
    st = {(r['item']): r for r in csv.DictReader(open(os.path.join(RAW, 'sir_state_summary.csv'), encoding='utf-8'))}
    g = lambda k: int(st[k]['total'])
    ra = {'total': g('removed_after_draft'), 'no_response': g('removed_after_draft_no_response_to_notice'), 'multiple': g('removed_after_draft_multiple'),
          'dead': g('removed_after_draft_dead'), 'underage_or_noncitizen': g('removed_after_draft_underage_or_noncitizen')}
    ra['shifted'] = ra['total'] - ra['no_response'] - ra['multiple'] - ra['dead'] - ra['underage_or_noncitizen']
    assert ra['shifted'] == 328960, 'printed as 3.28 lakh'
    notices = {'all': v('notices_all'), 'no_mapping': v('notices_no_mapping'), 'discrepancy': v('notices_discrepancy'),
               'per_100_draft': round(100 * v('notices_all') / S['draft'], 2), 'eros': v('hearing_eros'), 'aeros': v('hearing_aeros'),
               'per_aero': round(v('notices_all') / v('hearing_aeros')), 'hearing_days': 66,
               'per_aero_day': round(v('notices_all') / v('hearing_aeros') / 66), 'held_by_7_march': v('hearings_held_by_2026-03-07'),
               'removed_after': ra, 'removed_per_100_notices': round(100 * ra['total'] / v('notices_all'), 2),
               'no_response_per_100_notices': round(100 * ra['no_response'] / v('notices_all'), 2),
               'form6': S['form6'], 'form7': S['form7'], 'net_rise': S['net_rise'], 'source': P['notices_all']['source']}
    assert notices['no_mapping'] + notices['discrepancy'] == notices['all']
    # ---- the schedule, as each order set it and as it was carried out
    pr = json.load(open(os.path.join(IND, 'process.json'), encoding='utf-8'))
    sch = [x for x in pr['schedules'] if x['state'] == 'Uttar Pradesh'][0]['steps']
    done = {'label': 'As carried out', 'enum': ['2025-11-04', '2025-12-26'], 'draft': '2026-01-06', 'claims': ['2026-01-06', '2026-03-06'],
            'notice': ['2026-01-14', '2026-03-27'], 'final': '2026-04-10', 'src': 'https://www.instagram.com/p/DXEa2dkEuo7/'}
    return {'margins': margins, 'rolls': rolls, 'factors': factors, 'reason_rho': reasons, 'sex': sex, 'urban': urban, 'notices': notices,
            'schedule': sch + [done]}


if __name__ == '__main__':
    s, stale = build()
    if CHECK:
        if stale:
            sys.exit('STALE, run python3 scripts/build_uttarpradesh.py: ' + ', '.join(stale))
        print('OK: data/uttarpradesh matches its raw tables')
    else:
        print(json.dumps(s, indent=0)[:2500])
