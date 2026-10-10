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
the state's 9,78,54,049. The note gives no count by reason, no split by sex of
the names left off and nothing by assembly constituency. The reasons on the
All India table are press figures in lakh; they are carried here with that
label and checked against the note's total, never mixed into it.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the CEO's press note of 31 August 2026, which the All India row cites for its totals
NOTE_URL = 'https://ceoelection.maharashtra.gov.in/Downloads/PDF/Notification/Press%20Note%20English_31.08.2026%20Draft%20Roll.pdf'
# the press report of the reasons in lakh, which the note does not give
PRESS_REASONS = 'https://indianexpress.com/article/cities/mumbai/maharashtra-draft-electoral-rolls-sir-2-crore-voters-excluded-claims-objections-portal-10857667/'
RAW = os.path.join(ROOT, 'data', 'maharashtra', 'raw')
OUT = os.path.join(ROOT, 'data', 'maharashtra')
CHECK = '--check' in sys.argv

# The five districts that hold Mumbai and Pune and the suburbs round them
CITY = ('Mumbai City', 'Mumbai Suburban', 'Thane', 'Palghar', 'Pune')
# The note keeps three old district names; the state has since renamed them
NOW = {'Aurangabad': 'Chhatrapati Sambhajinagar', 'Ahmednagar': 'Ahilyanagar', 'Osmanabad': 'Dharashiv'}


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

    # the All India row: the note's totals, and the press's reasons in lakh
    with open(os.path.join(ROOT, 'data', 'india', 'states.json'), encoding='utf-8') as fh:
        ind = [x for x in json.load(fh)['states'] if x['state'] == 'Maharashtra'][0]
    assert ind['electors_before'] == S['before'] and ind['removed'] == S['left_off'], 'All India row equals the press note'
    # the row cites the CEO's note for its totals; the reasons in it are the press's, in lakh
    assert ind['source'] == 'primary' and ind['source_url'] == NOTE_URL and ind['figures'] == 'rounded', 'the All India row cites the note, and its reasons are rounded press figures'
    press = {k: ind[k] for k in ('dead', 'shifted_absent_other', 'duplicate')}

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
        'press_reasons': press, 'press_reasons_sum': sum(press.values()),
        'press_shares': {k: round(100 * v / sum(press.values()), 4) for k, v in press.items()},
        'press_source': PRESS_REASONS,
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
           'districts.json': json.dumps(D, ensure_ascii=False, separators=(',', ':')) + '\n'}
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['district', 'roll_before', 'draft_roll_31_aug_2026', 'left_off', 'left_off_per_100',
                'draft_men', 'draft_women', 'draft_third_gender', 'women_pct_of_draft'])
    for r in D:
        w.writerow([r[k] for k in ('district', 'before', 'draft', 'left_off', 'per_100', 'men', 'women', 'third', 'women_draft_pct')])
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
