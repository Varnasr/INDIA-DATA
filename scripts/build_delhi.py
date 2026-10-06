"""Delhi: the names left off the SIR draft roll in each of the 70 assembly
constituencies, set against the 2025 assembly result.

Reads data/delhi/raw (see SOURCES.md there; check_raw.py there rebuilds the
raw CSVs from their sources) and writes data/delhi/summary.json,
constituencies.json, districts.json and the two CSVs.

    python3 scripts/build_delhi.py           # write
    python3 scripts/build_delhi.py --check   # fail if the output is stale

- The constituency figures are the Chief Electoral Officer's own table of the
  draft (draft roll by sex and uncollectable forms, by district and AC), read
  from the CEO's PDF; check_raw.py also holds it equal, row by row, to the data
  behind Business Standard's map of the same table. The roll before the
  revision is the draft plus the forms not collected, and the build fails
  unless all three add up to the CEO's state figures.
- The reasons and the split by sex are for the state only, from the CEO's
  press note of 31 August 2026. A split by AC exists only as a third party's
  count of the named lists (secondary_reasons_ac.csv), and it is not used.
- Districts are the 13 the CEO's table uses, the districts Delhi has now.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'delhi', 'raw')
OUT = os.path.join(ROOT, 'data', 'delhi')
CHECK = '--check' in sys.argv


def rd(name):
    return list(csv.DictReader(open(os.path.join(RAW, name), encoding='utf-8')))


def r1(x):
    return round(x, 1)


def main():
    st = {r['measure']: int(r['value']) for r in rd('state.csv')}
    A = rd('ac.csv')
    res = {int(r['ac']): r for r in rd('results_2025.csv')}
    assert len(A) == 70 and len(res) == 70
    rows = []
    for a in A:
        n = int(a['ac']); e = res[n]
        rb, dr, lo = int(a['roll_before']), int(a['draft']), int(a['left_off'])
        assert rb == dr + lo, n
        assert int(a['draft_men']) + int(a['draft_women']) + int(a['draft_tg']) == dr, n
        margin, votes, el = int(e['margin']), int(e['votes_total']), int(e['electors'])
        assert margin > 0 and int(e['winner_votes']) - int(e['runner_up_votes']) == margin, n
        rows.append({'ac': n, 'name': a['name_as_published'], 'district': a['district'],
                     'roll_before': rb, 'draft': dr, 'left_off': lo, 'per_100': r1(100 * lo / rb),
                     'electors_2025': el, 'winner': e['winner_party'], 'runner_up': e['runner_up_party'], 'margin': margin,
                     'turnout_2025': r1(100 * votes / el),
                     'over_margin': lo > margin,
                     # the names left off, at the seat's own 2025 turnout
                     'at_turnout_over_margin': lo * votes / el > margin})
    # every column adds up to the CEO's state figures
    assert sum(r['roll_before'] for r in rows) == st['roll_before']
    assert sum(r['draft'] for r in rows) == st['draft']
    assert sum(r['left_off'] for r in rows) == st['left_off'] == st['roll_before'] - st['draft']
    assert st['shifted_absent_other'] + st['dead'] + st['duplicate'] == st['left_off']
    assert st['draft_men'] + st['draft_women'] + st['draft_third_gender'] == st['draft']
    assert sum(1 for r in rows if r['winner'] == 'BJP') == 48 and sum(1 for r in rows if r['winner'] == 'AAP') == 22

    D = {}
    for r in rows:
        d = D.setdefault(r['district'], {'district': r['district'], 'acs': 0, 'roll_before': 0, 'draft': 0, 'left_off': 0})
        d['acs'] += 1
        for k in ('roll_before', 'draft', 'left_off'):
            d[k] += r[k]
    for d in D.values():
        d['per_100'] = r1(100 * d['left_off'] / d['roll_before'])
    dist = sorted(D.values(), key=lambda d: -d['per_100'])
    for r in rows:
        r['vs_district'] = r1(r['per_100'] - D[r['district']]['per_100'])
    rows.sort(key=lambda r: -r['per_100'])

    def party(p):
        S = [r for r in rows if r['winner'] == p]
        return {'party': p, 'seats': len(S), 'per_100': r1(100 * sum(r['left_off'] for r in S) / sum(r['roll_before'] for r in S)),
                'vs_district': round(sum(r['vs_district'] for r in S) / len(S), 2), 'over_margin': sum(r['over_margin'] for r in S)}

    women_before = st['roll_before_women']
    summ = {
        'roll_before': st['roll_before'], 'draft': st['draft'], 'left_off': st['left_off'],
        'per_100': r1(100 * st['left_off'] / st['roll_before']),
        'reasons': {'shifted_absent_other': st['shifted_absent_other'], 'dead': st['dead'], 'duplicate': st['duplicate']},
        'shares': {k: round(100 * st[k] / st['left_off'], 2) for k in ('shifted_absent_other', 'dead', 'duplicate')},
        'women_before_pct': round(100 * women_before / (st['roll_before_men'] + women_before + st['roll_before_third_gender']), 2),
        'women_draft_pct': round(100 * st['draft_women'] / st['draft'], 2),
        'women_left_off_pct': round(100 * st['left_off_women'] / (st['left_off_men'] + st['left_off_women'] + st['left_off_third_gender']), 2),
        'women_left_per_100': r1(100 * st['left_off_women'] / women_before),
        'men_left_per_100': r1(100 * st['left_off_men'] / st['roll_before_men']),
        'electors_2025': sum(r['electors_2025'] for r in rows),
        'acs': 70, 'over_margin': sum(r['over_margin'] for r in rows), 'at_turnout_over_margin': sum(r['at_turnout_over_margin'] for r in rows),
        'parties': [party('BJP'), party('AAP')],
        'acs_over_40': sum(r['per_100'] >= 40 for r in rows),
        'rate_max': rows[0]['name'], 'rate_max_v': rows[0]['per_100'], 'rate_min': rows[-1]['name'], 'rate_min_v': rows[-1]['per_100'],
        'notices_issued': st.get('notices_issued'),
    }
    co = {r['form']: int(r['applications']) for r in rd('claims_objections.csv') if r['area'] == 'Delhi' and r['period'] == 'up to 2026-09-29'}
    summ['form6_to_0929'] = co.get('Form 6'); summ['form7_to_0929'] = co.get('Form 7')

    files = {}
    files['summary.json'] = json.dumps(summ, ensure_ascii=False, indent=1) + '\n'
    files['constituencies.json'] = json.dumps(rows, ensure_ascii=False, indent=0) + '\n'
    files['districts.json'] = json.dumps(dist, ensure_ascii=False, indent=0) + '\n'
    for name, data, cols in (('constituencies.csv', sorted(rows, key=lambda r: r['ac']), ['ac', 'name', 'district', 'roll_before', 'draft', 'left_off', 'per_100', 'vs_district', 'winner', 'runner_up', 'margin', 'turnout_2025', 'over_margin', 'at_turnout_over_margin']),
                             ('districts.csv', dist, ['district', 'acs', 'roll_before', 'draft', 'left_off', 'per_100'])):
        b = io.StringIO(); w = csv.writer(b, lineterminator='\n'); w.writerow(cols)
        for r in data:
            w.writerow([r[c] for c in cols])
        files[name] = b.getvalue()
    if CHECK:
        stale = [k for k, t in files.items() if not os.path.exists(os.path.join(OUT, k)) or open(os.path.join(OUT, k), encoding='utf-8').read() != t]
        assert not stale, 'stale: ' + ', '.join(stale)
        print('OK: data/delhi matches its raw tables')
        return
    for k, t in files.items():
        open(os.path.join(OUT, k), 'w', encoding='utf-8').write(t)
    print('wrote data/delhi: %d left off, %.1f per 100; over the 2025 margin in %d of 70 (%d at turnout)' % (summ['left_off'], summ['per_100'], summ['over_margin'], summ['at_turnout_over_margin']))


if __name__ == '__main__':
    main()
