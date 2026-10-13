"""Maharashtra: the names left off the SIR draft roll of 31 August 2026, by
district, with the draft roll by district and sex.

Reads data/maharashtra/raw (see SOURCES.md there) and writes
data/maharashtra/summary.json, districts.json and districts.csv.

    python3 scripts/build_maharashtra.py           # write
    python3 scripts/build_maharashtra.py --check   # fail if the output is stale

The Chief Electoral Officer's press note of 31 August 2026 gives, for each of
the 36 districts, the draft roll by sex (Annexure-1) and the enumeration forms
not collected (Annexure-2), which are the names left off. The roll before the
revision is given for the state only, so a district's roll before is taken as
its draft plus its names left off, and the build fails unless those add up to
the state's 9,78,54,049.

Three more of the CEO's own tables give every one of the 288 assembly
constituencies: the statement enclosed with the press note of 16 September
2026 (roll before and names left off, ac_roll.csv), and the tables of 1
September 2026 (the names left off by reason, ac_reasons.csv, and the draft by
sex, ac_draft_sex.csv), with the reasons and the notices by district beside
them. Every constituency table is held to its own sums and to the district
annexures, and the constituencies are set against the 2024 Assembly result.
Nothing anywhere splits the names left off by sex.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the CEO's press note of 31 August 2026, which the All India row cites for its totals
NOTE_URL = 'https://ceoelection.maharashtra.gov.in/Downloads/PDF/Notification/Press%20Note%20English_31.08.2026%20Draft%20Roll.pdf'
RAW = os.path.join(ROOT, 'data', 'maharashtra', 'raw')
OUT = os.path.join(ROOT, 'data', 'maharashtra')
CHECK = '--check' in sys.argv

# the CEO's tables of 1 September 2026 (reasons by AC and district, draft by AC and sex)
REASONS_URL = 'https://ceoelection.maharashtra.gov.in/Downloads/PDF/Notification/Pressnotemarathi01.09.2026.pdf'
# the statement enclosed with the press note of 16 September 2026 (roll before by AC)
AC_URL = 'https://ceoelection.maharashtra.gov.in/Downloads/PDF/Notification/16.9.2026%20IE%20Report%20Response.pdf'
REASONS = ('dead', 'shifted', 'absent', 'duplicate', 'other')
# the tables misspell one name; the Commission's list of 2024 spells it Vikramgad
NAME_FIX = {129: 'Vikramgad (ST)'}
# The five districts that hold Mumbai and Pune and the suburbs round them
CITY = ('Mumbai City', 'Mumbai Suburban', 'Thane', 'Palghar', 'Pune')
# The note keeps three old district names; the state has since renamed them
NOW = {'Aurangabad': 'Chhatrapati Sambhajinagar', 'Ahmednagar': 'Ahilyanagar', 'Osmanabad': 'Dharashiv'}


def spearman(x, y):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r, i = [0.0] * len(v), 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    c = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    return c / (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5


def read(name):
    with open(os.path.join(RAW, name), encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def build():
    st = {r['measure']: r['value'] for r in read('state.csv')}
    S = {k: int(st[k]) for k in ('before', 'draft', 'draft_men', 'draft_women', 'draft_third_gender', 'left_off')}
    assert S['draft_men'] + S['draft_women'] + S['draft_third_gender'] == S['draft'], 'the draft by sex adds up'
    assert S['draft'] + S['left_off'] == S['before'], 'draft plus left off equals the roll before'

    dr, un = read('district_draft.csv'), read('district_uncollectable.csv')
    assert len(dr) == len(un) == 36, '36 districts in both annexures'
    assert [int(r['sr']) for r in dr] == list(range(1, 37)) == [int(r['sr']) for r in un], 'serials 1 to 36'
    assert [r['district'] for r in dr] == [r['district'] for r in un], 'the same districts in the same order'
    for c in list(CITY) + list(NOW):
        assert c in [r['district'] for r in dr], c

    D = []
    for a, b in zip(dr, un):
        men, women, third, draft = (int(a[k]) for k in ('men', 'women', 'third_gender', 'total'))
        assert men + women + third == draft, a['district']
        left = int(b['uncollectable'])
        before = draft + left
        D.append({'sr': int(a['sr']), 'district': a['district'], 'now': NOW.get(a['district'], ''), 'city': a['district'] in CITY,
                  'before': before, 'draft': draft, 'left_off': left,
                  'per_100': round(100 * left / before, 4),
                  'men': men, 'women': women, 'third': third,
                  'women_draft_pct': round(100 * women / draft, 4)})

    T = lambda L, k: sum(r[k] for r in L)
    assert T(D, 'draft') == S['draft'], 'districts add up to the state draft'
    assert T(D, 'men') == S['draft_men'] and T(D, 'women') == S['draft_women'] and T(D, 'third') == S['draft_third_gender'], 'districts add up to the state draft by sex'
    assert T(D, 'left_off') == S['left_off'], 'districts add up to the names left off'
    assert T(D, 'before') == S['before'], 'districts add up to the roll before'
    assert abs(100 * S['draft'] / S['before'] - float(st['draft_pct_of_before'])) < 0.005
    assert abs(100 * S['left_off'] / S['before'] - float(st['left_off_pct_of_before'])) < 0.005

    # the reasons and the notices, by district
    rs, nt = read('district_reasons.csv'), read('district_notices.csv')
    assert [r['district'] for r in rs] == [r['district'] for r in nt] == [r['district'] for r in dr], 'the same 36 districts'
    byd = {r['district']: r for r in D}
    for r, q in zip(rs, nt):
        d = byd[r['district']]
        v = {k: int(r[k]) for k in REASONS}
        assert sum(v.values()) == int(r['left_off']) == d['left_off'], r['district']
        d.update(v)
        d['discrepancy'], d['no_mapping'] = int(q['discrepancy']), int(q['no_mapping'])
        assert d['discrepancy'] + d['no_mapping'] == int(q['total_notices']), q['district']
        d['notices'] = int(q['total_notices'])
        d['notices_per_100'] = round(100 * d['notices'] / d['draft'], 4)
        d['shifted_absent_pct'] = round(100 * (v['shifted'] + v['absent']) / d['left_off'], 4)
    R = {k: T(D, k) for k in REASONS}
    assert sum(R.values()) == S['left_off']
    assert T(D, 'notices') == 12224007 and T(D, 'discrepancy') == 6248281 and T(D, 'no_mapping') == 5975726, 'the notices of 4 September 2026'

    # every constituency
    nd = {int(r['ac']): r for r in read('ac_district.csv')}
    roll = {int(r['ac']): r for r in read('ac_roll.csv')}
    why = {int(r['ac']): r for r in read('ac_reasons.csv')}
    sex = {int(r['ac']): r for r in read('ac_draft_sex.csv')}
    with open(os.path.join(ROOT, 'data', 'india', 'raw', 'assembly', 'maharashtra_2024.csv'), encoding='utf-8') as fh:
        res = {int(r['ac']): r for r in csv.DictReader(fh)}
    for t in (nd, roll, why, sex, res):
        assert sorted(t) == list(range(1, 289)), 'every table has ACs 1 to 288 once'
    A = []
    for n in range(1, 289):
        a, b, c, x = roll[n], why[n], sex[n], res[n]
        assert a['district'] == b['district'] == c['district'] == nd[n]['district'], n
        before, left, draft = int(a['roll_before']), int(a['left_off']), int(a['draft'])
        assert before - left == draft == int(c['draft']), n
        assert abs(100 * left / before - float(a['left_off_pct_printed'])) < 0.006, n
        v = {k: int(b[k]) for k in REASONS}
        assert sum(v.values()) == int(b['left_off']) == left, n
        men, women, third = int(c['men']), int(c['women']), int(c['third_gender'])
        assert men + women + third == draft, n
        margin, votes, el = int(x['margin']), int(x['total_votes']), int(x['electors'])
        assert int(x['winner_votes']) - int(x['runner_up_votes']) == margin > 0, n
        turnout = votes / el
        r = {'ac': n, 'name': NAME_FIX.get(n, a['ac_name']), 'district': a['district'], 'city': a['district'] in CITY,
             'before': before, 'left_off': left, 'draft': draft, 'per_100': round(100 * left / before, 4)}
        r.update(v)
        r['shifted_absent_pct'] = round(100 * (v['shifted'] + v['absent']) / left, 4)
        r['dead_pct'] = round(100 * v['dead'] / left, 4)
        r.update({'draft_men': men, 'draft_women': women, 'women_draft_pct': round(100 * women / draft, 4),
                  'winner_party': x['winner_party'], 'runner_up_party': x['runner_up_party'], 'margin': margin,
                  'electors_2024': el, 'turnout_2024': round(100 * turnout, 4),
                  'over_margin': left > margin, 'at_turnout': round(left * turnout), 'turnout_over_margin': left * turnout > margin})
        A.append(r)
    for k in ('before', 'left_off', 'draft') + REASONS:
        for d in D:
            got = sum(r[k] for r in A if r['district'] == d['district'])
            assert got == d[k], (d['district'], k, got, d[k])
    for d in D:
        for k, ck in (('men', 'draft_men'), ('women', 'draft_women')):
            assert sum(r[ck] for r in A if r['district'] == d['district']) == d[k], (d['district'], k)
    for r in A:
        r['vs_district'] = round(r['per_100'] - byd[r['district']]['per_100'], 4)
    for t in read('ac_top38.csv'):
        r = A[int(t['ac']) - 1]
        assert r['left_off'] == int(t['uncollected']) and r['before'] == int(t['total_electors']), ('top38 agrees', t['ac'])
    by_w = {}
    for r in A:
        by_w.setdefault(r['winner_party'], []).append(r)
    winners = [{'party': p, 'seats': len(L), 'per_100': round(100 * sum(r['left_off'] for r in L) / sum(r['before'] for r in L), 4),
                'vs_district': round(sum(r['vs_district'] for r in L) / len(L), 4), 'over_margin': sum(r['over_margin'] for r in L)}
               for p, L in sorted(by_w.items(), key=lambda kv: (-len(kv[1]), kv[0]))]
    Ar = sorted(A, key=lambda r: -r['per_100'])

    # the All India row now carries the CEO's exact reasons
    with open(os.path.join(ROOT, 'data', 'india', 'states.json'), encoding='utf-8') as fh:
        ind = [x for x in json.load(fh)['states'] if x['state'] == 'Maharashtra'][0]
    assert ind['electors_before'] == S['before'] and ind['removed'] == S['left_off'], 'All India row equals the press note'
    assert ind['dead'] == R['dead'] and ind['duplicate'] == R['duplicate'] and ind['shifted_absent_other'] == R['shifted'] + R['absent'] + R['other'] \
        and ind['figures'] == 'exact', 'the All India row carries the CEO\'s exact reasons'

    # the dates as last moved: the Commission's latest schedule for the state
    with open(os.path.join(ROOT, 'data', 'india', 'process.json'), encoding='utf-8') as fh:
        sch = [x for x in json.load(fh)['schedules'] if x['state'] == 'Maharashtra'][0]['steps']
    last = [x for x in sch if x.get('final')][-1]

    D.sort(key=lambda r: -r['per_100'])
    city, rest = [r for r in D if r['city']], [r for r in D if not r['city']]
    grp = lambda L: {
        'before': T(L, 'before'), 'left_off': T(L, 'left_off'), 'draft': T(L, 'draft'),
        'per_100': round(100 * T(L, 'left_off') / T(L, 'before'), 4),
        'share_of_roll': round(100 * T(L, 'before') / S['before'], 4),
        'share_of_left_off': round(100 * T(L, 'left_off') / S['left_off'], 4),
        'women_draft_pct': round(100 * T(L, 'women') / T(L, 'draft'), 4)}
    wsort = sorted(D, key=lambda r: r['women_draft_pct'])
    summary = {
        'before': S['before'], 'draft': S['draft'], 'left_off': S['left_off'],
        'per_100': round(100 * S['left_off'] / S['before'], 4),
        'draft_men': S['draft_men'], 'draft_women': S['draft_women'], 'draft_third': S['draft_third_gender'],
        'women_draft_pct': round(100 * S['draft_women'] / S['draft'], 4),
        'districts': len(D), 'acs': int(st['acs']),
        'top': [{'district': r['district'], 'per_100': r['per_100'], 'left_off': r['left_off']} for r in D[:5]],
        'low': [{'district': r['district'], 'per_100': r['per_100']} for r in D[-3:]],
        'most_names': max(D, key=lambda r: r['left_off'])['district'],
        'over_30': sum(r['per_100'] >= 30 for r in D),
        'under_15': sum(r['per_100'] < 15 for r in D),
        'above_state': sum(r['per_100'] > 100 * S['left_off'] / S['before'] for r in D),
        'city_names': list(CITY), 'city': grp(city), 'rest': grp(rest),
        'women_low': {'district': wsort[0]['district'], 'pct': wsort[0]['women_draft_pct']},
        'women_high': {'district': wsort[-1]['district'], 'pct': wsort[-1]['women_draft_pct']},
        'reasons': R, 'reason_shares': {k: round(100 * v / S['left_off'], 4) for k, v in R.items()},
        'reasons_url': REASONS_URL, 'ac_url': AC_URL,
        'notices': T(D, 'notices'), 'discrepancy': T(D, 'discrepancy'), 'no_mapping': T(D, 'no_mapping'),
        'notices_per_100': round(100 * T(D, 'notices') / S['draft'], 4),
        'acs_n': len(A), 'ac_max': Ar[0]['name'], 'ac_max_v': Ar[0]['per_100'], 'ac_min': Ar[-1]['name'], 'ac_min_v': Ar[-1]['per_100'],
        'top_acs': [{'ac': r['ac'], 'name': r['name'], 'district': r['district'], 'per_100': r['per_100']} for r in Ar[:10]],
        'acs_over_30': sum(r['per_100'] >= 30 for r in A), 'acs_under_10': sum(r['per_100'] < 10 for r in A),
        'over_margin': sum(r['over_margin'] for r in A), 'turnout_over_margin': sum(r['turnout_over_margin'] for r in A),
        'winners': winners,
        'rho_notices_left': round(spearman([d['notices_per_100'] for d in D], [d['per_100'] for d in D]), 3),
        'draft_date': st['draft_published'], 'claims_to_note': st['claims_objections_to'], 'final_due_note': st['final_roll_due'],
        'claims_to': last['claims'][1], 'notices_to': last['notice'][1], 'final_due': last['final'], 'final_due_source': last['label'],
    }
    # The CEO's own list of 38 constituencies with a high share of forms not
    # collected. It is a selection the CEO made, and its title says how: it
    # leaves out the seats a newspaper had called Muslim-heavy. It is shown as
    # printed, never mapped, ranked against other seats or added to anything.
    top = read('ac_top38.csv')
    summary['top38'] = {
        'title': 'Top 38 ACs with High Percentage of Uncollectable EF Electors (excluding Muslim-heavy ACs as claimed by Indian Express report)',
        'url': 'https://ceoelection.maharashtra.gov.in/Downloads/PDF/Notification/Top%20ACs%20with%20high%20percentage%20of%20%20Uncollectable%20EF%20excluding%20%20Muslim%20heavy%20seats.pdf',
        'file_date': '2026-09-30',
        'acs': len(top),
        'rows': [{'ac': int(r['ac']), 'name': r['ac_name'], 'district': r['district'], 'electors': int(r['total_electors']),
                  'uncollected': int(r['uncollected']), 'pct': float(r['uncollected_pct_printed'])} for r in top],
    }
    assert summary['claims_to'] >= summary['claims_to_note'] and summary['final_due'] >= summary['final_due_note']

    out = {'summary.json': json.dumps(summary, ensure_ascii=False, indent=1) + '\n',
           'districts.json': json.dumps(D, ensure_ascii=False, separators=(',', ':')) + '\n',
           'constituencies.json': json.dumps(A, ensure_ascii=False, separators=(',', ':')) + '\n'}
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    cols = ['ac', 'name', 'district', 'before', 'draft', 'left_off', 'per_100'] + list(REASONS) + ['draft_men', 'draft_women', 'women_draft_pct',
            'winner_party', 'runner_up_party', 'margin', 'turnout_2024', 'over_margin', 'turnout_over_margin', 'vs_district']
    w.writerow(['ac', 'constituency', 'district', 'roll_before', 'draft_roll_31_aug_2026', 'left_off', 'left_off_per_100', 'dead', 'shifted',
                'absent', 'enrolled_elsewhere', 'other', 'draft_men', 'draft_women', 'women_pct_of_draft', 'winner_2024', 'runner_up_2024',
                'margin_2024', 'turnout_2024', 'left_off_over_margin', 'left_off_at_turnout_over_margin', 'per_100_less_district'])
    for r in A:
        w.writerow([r[k] for k in cols])
    out['constituencies.csv'] = buf.getvalue()
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['district', 'roll_before', 'draft_roll_31_aug_2026', 'left_off', 'left_off_per_100',
                'draft_men', 'draft_women', 'draft_third_gender', 'women_pct_of_draft', 'dead', 'shifted', 'absent', 'enrolled_elsewhere', 'other',
                'notices_discrepancy', 'notices_no_mapping', 'notices', 'notices_per_100_draft'])
    for r in D:
        w.writerow([r[k] for k in ('district', 'before', 'draft', 'left_off', 'per_100', 'men', 'women', 'third', 'women_draft_pct') + REASONS
                    + ('discrepancy', 'no_mapping', 'notices', 'notices_per_100')])
    out['districts.csv'] = buf.getvalue()
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['ac', 'constituency', 'district', 'total_electors', 'forms_not_collected', 'not_collected_pct'])
    for r in summary['top38']['rows']:
        w.writerow([r['ac'], r['name'], r['district'], r['electors'], r['uncollected'], r['pct']])
    out['top38.csv'] = buf.getvalue()

    stale = []
    for name, text in out.items():
        path = os.path.join(OUT, name)
        old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
        if old != text:
            stale.append(name)
            if not CHECK:
                open(path, 'w', encoding='utf-8').write(text)
    return summary, stale


if __name__ == '__main__':
    s, stale = build()
    if CHECK:
        if stale:
            sys.exit('STALE, run python3 scripts/build_maharashtra.py: ' + ', '.join(stale))
        print('OK: data/maharashtra matches its raw tables')
    else:
        print('%d left off of %d (%.2f per 100); the five city districts %.2f per 100, %.1f%% of the names left off'
              % (s['left_off'], s['before'], s['per_100'], s['city']['per_100'], s['city']['share_of_left_off']))
