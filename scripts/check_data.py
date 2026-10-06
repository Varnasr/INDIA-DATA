#!/usr/bin/env python3
"""Integrity checks for the SIR analyses. Run by CI.

    python3 scripts/check_data.py

Until September 2026 this file pinned five known defects in the Bihar data so
that they could not be forgotten. Those defects are now corrected, and the
checks below pin the corrections instead, so that none of them can come back
quietly. Each names the failure it guards against.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, 'data', 'bihar')
results = []


def check(name, fn):
    try:
        fn()
        results.append((True, name, ''))
    except AssertionError as e:
        results.append((False, name, str(e)))


def load(name):
    with open(os.path.join(B, name), encoding='utf-8') as fh:
        txt = fh.read()
    assert 'NaN' not in txt, '%s contains NaN, which is not JSON and breaks every page that reads it' % name
    return json.loads(txt)


S = load('summary.json')
A = load('constituencies.json')
T = S['totals']


def _fresh():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_bihar.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-600:]


def _tamilnadu_fresh():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_tamilnadu.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def _karnataka_fresh():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_karnataka.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def _westbengal_fresh():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_westbengal.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def _kerala_fresh():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_kerala.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def _hyderabad_fresh():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_hyderabad.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-600:]


def _hyderabad_totals():
    with open(os.path.join(ROOT, 'data', 'hyderabad', 'summary.json'), encoding='utf-8') as fh:
        H = json.load(fh)
    t = H['totals']
    assert len(H['acs']) == 5 and t['parts'] == 1158, 'expected five constituencies and 1,158 parts'
    assert t['electors'] == 1657207 and t['deleted'] == 662063, 'Hyderabad totals moved: %s' % t
    mal = [a for a in H['acs'] if a['name'] == 'Malakpet'][0]
    assert not mal['linked'] and mal['within_part']['unlinked_minus_linked'] is None, 'Malakpet has no 2002 linkage and must not be given a linked rate'


def _one_row_per_booth():
    # The six-fold join gave 39.2 million. One row per booth gives 6,559,626,
    # which the constituency-level SIR sheet confirms to within its own rounding.
    assert T['booths'] == 77837, T['booths']
    assert 6_500_000 < T['p1'] < 6_600_000, 'phase 1 total %s is not the SIR draft-roll figure' % T['p1']
    assert abs(sum(a['booths'] for a in A) - 77837) == 0


def _phases():
    assert T['p1'] + T['p2'] == T['total'] == 6910559, T
    assert T['female'] + T['male'] == T['total']


def _constituencies():
    assert len(A) == 243 and sorted(a['ac'] for a in A) == list(range(1, 244))
    # Two pairs of different seats share a name; a join on name merges them.
    names = [a['name'] for a in A]
    assert names.count('Kalyanpur') == 2 and names.count('Pipra') == 2, 'Kalyanpur and Pipra must stay two seats each'


def _labels_reconcile():
    bad = [r['pc'] for r in S['label_verification'] if not r['match']]
    assert len(S['label_verification']) == 40 and not bad, 'seats whose 2024 top two do not match the declared result: %s' % bad


def _alliances_cover_all():
    # The old alliance_2024_ls classified 131 of 243 seats.
    for y in ['al2020', 'al2024', 'al2025']:
        missing = [a['ac'] for a in A if a[y] not in ('NDA', 'INDIA', 'Other')]
        assert not missing, '%s unlabelled in %s' % (len(missing), y)
    assert sum(1 for a in A if a['al2025'] == 'NDA') == 202, '2025 NDA seats should be 202'


def _caste_not_uniform():
    # The old district caste file carried identical shares everywhere.
    I = load('identity.json')
    g = I['caste']['guardian']['A']['groups']
    assert abs(g['EBC']['share_of_classified'] - 60.9) > 5, 'EBC back at the Devi-inflated 60.9%'
    shares = {round(d['muslim_share_deleted_low'], 1) for d in I['districts']}
    assert len(shares) > 20, 'district religion shares are suspiciously uniform'


def _no_people():
    # Aggregates only: no file under data/bihar may carry an EPIC-like field.
    for dirpath, _, files in os.walk(B):
        for f in files:
            if f.endswith('.json'):
                with open(os.path.join(dirpath, f), encoding='utf-8') as fh:
                    head = fh.read(4000).lower()
                assert 'epic' not in head and 'elector_name' not in head, '%s looks like it carries individual records' % f


def _india():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_india.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]
    d = json.load(open(os.path.join(ROOT, 'data', 'india', 'states.json'), encoding='utf-8'))
    b = next(x for x in d['states'] if x['state'] == 'Bihar')
    rs = load('reasons.json')
    # Bihar's row is the lists' own count, not a rounded press figure.
    assert b['removed'] == rs['total'] and b['dead'] == rs['totals']['dead'] and b['duplicate'] == rs['totals']['already_enrolled'], 'Bihar row differs from the lists'
    assert b['shifted_absent_other'] == rs['totals']['shifted'] + rs['totals']['absent']


def _downloads():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_downloads.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _electors():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_electors.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _margins():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_margins.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _rajasthan():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_rajasthan.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _delhi():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_delhi.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _notices():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_notices.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _uttarpradesh():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_uttarpradesh.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _maharashtra():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_maharashtra.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _gujarat():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_gujarat.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'data', 'gujarat', 'raw', 'check_raw.py')], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _uttarakhand():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_uttarakhand.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'data', 'uttarakhand', 'raw', 'check_raw.py')], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _cities():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_cities.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]

def _border():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_border.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]

def _women():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_women.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]

def _urban():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_urban.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]

def _census_a01():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'census_a01.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]

def _reserved():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_reserved.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]

def _telangana():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_telangana.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _bihar_final():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_bihar_final.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _bihar_tests():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_bihar_tests.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _impact():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_impact.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _swing():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_swing.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _robust():
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_robust.py'), '--check'], capture_output=True, text=True)
    assert r.returncode == 0, (r.stdout + r.stderr).strip()[-300:]


def _short_and_faq():
    # Every page but the full reports opens with an "In short" box and carries
    # questions and answers: its own (#pageFaq) or, on an FAQ tab, all (#qas).
    import glob
    with open(os.path.join(ROOT, 'site', 'places.json'), encoding='utf-8') as fh:
        SECTIONS = {x[0].split('/')[0] for p in json.load(fh)['places'] for x in p['pages']}
    pages = ['index.html'] + sorted(glob.glob(os.path.join(ROOT, '*', '**', 'index.html'), recursive=True))
    for p in pages:
        rel = os.path.relpath(os.path.join(ROOT, p), ROOT)
        # the front page says what the site is; it carries no findings box
        if rel.split(os.sep)[0] not in SECTIONS:
            continue
        if os.sep + 'report' + os.sep in rel:
            continue
        html = open(os.path.join(ROOT, rel), encoding='utf-8').read()
        assert 'id="short"' in html, '%s has no In short box' % rel
        assert 'id="pageFaq"' in html or 'id="qas"' in html, '%s has no questions and answers' % rel
        assert 'SIR.showFaq(' in html or rel == os.path.join('india', 'index.html'), '%s never fills its box' % rel


def _pages_link_method():
    for p in ['bihar/index.html', 'bihar/results/index.html', 'bihar/people/index.html',
              'hyderabad/index.html', 'hyderabad/people/index.html', 'hyderabad/parts/index.html', 'hyderabad/hearings/index.html',
              'tamilnadu/index.html', 'tamilnadu/elections/index.html', 'karnataka/index.html',
              'westbengal/index.html', 'westbengal/elections/index.html',
              'kerala/index.html', 'kerala/elections/index.html', 'maharashtra/index.html',
              'gujarat/index.html', 'gujarat/elections/index.html', 'uttarakhand/index.html']:
        with open(os.path.join(ROOT, p), encoding='utf-8') as fh:
            assert 'method/' in fh.read(), '%s no longer links to the method page' % p


for name, fn in [
    ('generated data matches its sources', _fresh),
    ('Hyderabad data matches the explorer', _hyderabad_fresh),
    ('Tamil Nadu data matches its raw tables', _tamilnadu_fresh),
    ('Karnataka data matches its raw tables', _karnataka_fresh),
    ('West Bengal data matches its raw tables', _westbengal_fresh),
    ('Kerala data matches its raw tables', _kerala_fresh),
    ('Hyderabad totals, parts and Malakpet linkage', _hyderabad_totals),
    ('booth deletions counted once per booth', _one_row_per_booth),
    ('phases and sexes add to the total', _phases),
    ('243 constituencies, joined by number', _constituencies),
    ('2024 labels reconcile in all 40 seats', _labels_reconcile),
    ('every seat has an alliance in all three elections', _alliances_cover_all),
    ('caste and religion figures are measured, not repeated', _caste_not_uniform),
    ('no individual records in published data', _no_people),
    ('All India table current, and Bihar row equal to the lists', _india),
    ('downloadable tables current', _downloads),
    ('Lok Sabha electors current and within range', _electors),
    ('Rajasthan data matches its raw tables', _rajasthan),
    ('Uttar Pradesh data matches its raw tables', _uttarpradesh),
    ('Maharashtra data matches its raw tables', _maharashtra),
    ('Gujarat data matches its raw tables, and the raw tables add up', _gujarat),
    ('Uttarakhand data matches its raw tables, and the raw tables add up', _uttarakhand),
    ('the cities table is current and every city adds up from its state', _cities),
    ('the reserved-seat table is current and every state has its Delimitation Order seats', _reserved),
    ('the border table is current, every listed district is found and Bihar matches its own pages', _border),
    ('the women table is current and every rate lies between 0 and 100', _women),
    ('Census 2011 A-01 districts are current and add to the India totals', _census_a01),
    ('the rural and urban table is current and every district has a 2011 parent', _urban),
    ('Notices table matches its raw table', _notices),
    ('Delhi data matches its raw tables', _delhi),
    ('removals against winning margins current, 2024 margins match the published ones', _margins),
    ('Hyderabad against Telangana current, and two seats equal to the lists', _telangana),
    ('Bihar final roll current, and equal to the press note', _bihar_final),
    ('Bihar deaths and marriage tests current, and the census districts add up', _bihar_tests),
    ('Impact estimates for Bihar and Hyderabad current', _impact),
    ('2020 to 2025 swing current, 2025 votes match the declared result', _swing),
    ('robustness checks current', _robust),
    ('every page opens with In short and carries questions', _short_and_faq),
    ('findings pages link to the method page', _pages_link_method),
]:
    check(name, fn)

bad = [r for r in results if not r[0]]
for ok, name, msg in results:
    print(('  ok    ' if ok else '  FAIL  ') + name + ('' if ok else ': ' + msg))
print('FAIL: %d of %d' % (len(bad), len(results)) if bad else 'PASS: %d checks' % len(results))
sys.exit(1 if bad else 0)
