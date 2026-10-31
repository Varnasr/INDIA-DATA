"""Karnataka: the names left off the draft roll of 24 August 2026, by
election district and reason, with the draft roll and the roll during claims
and objections (9 October 2026) by sex, and the final roll of 27 October 2026
for the state.

Reads data/karnataka/raw (see SOURCES.md there) and writes
data/karnataka/summary.json, districts.json and districts.csv.

    python3 scripts/build_karnataka.py           # write
    python3 scripts/build_karnataka.py --check   # fail if the output is stale

The CEO published the revision by its 34 election districts only, so there is
no constituency table. Bengaluru is four of the 34: Bangalore Urban and the
three B.B.M.P districts. The final roll was published on 27 October 2026,
and it was reported for the state only, as a total and by sex, with no
count of names added or deleted after the draft. So the district rows stop
at the roll of 9 October, published while notices were being heard. The
field is still called `sep`, after the roll of 25 September it first held.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'karnataka', 'raw')
OUT = os.path.join(ROOT, 'data', 'karnataka')
CHECK = '--check' in sys.argv

REASONS = ('absent', 'shifted', 'dead', 'duplicate', 'other')
# The CEO's state row, press note DPAR 163 of 24.08.2026
STATE = {'before': 55432314, 'absent': 1517042, 'shifted': 6545679, 'dead': 1639864,
         'duplicate': 709870, 'other': 383884, 'removed': 10796339, 'draft': 44635975}
SEP_TOTAL = 45161393   # the roll of 9 October 2026; 44,844,080 on 25 September
DRAFT_SERVICE = 44176  # service electors on the draft, Annexure-10 of the same note
# The final roll of 27 October 2026, for the state, from raw/final.json, which
# scripts/add_final.py writes (the shape is in scripts/final_roll.py). No CEO
# note was on ceo.karnataka.gov.in that day. The split by sex is ETV Bharat's,
# quoting the CEO's office, and its sum is taken as the final roll of general
# electors, the same footing as the draft. The Hindu's total of 4,55,00,011 is
# 44,322 larger, close to the 44,176 service electors listed with the draft, so
# it is taken to include them (`service` in the file). The Times of India of 28
# October gives 10.08 lakh added and 1.88 lakh deleted after the draft, which
# agree with this to the lakh.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import final_roll  # noqa: E402
_F = final_roll.read('karnataka')
FINAL = {'date': _F['date'], 'total': _F['electors'], 'total_with_service': _F['electors'] + _F['service'],
         'men': _F['men'], 'women': _F['women'], 'third': _F['third'], 'added': _F['added'], 'deleted': _F['deleted']}
BENGALURU = ('BANGALORE URBAN', 'B.B.M.P(NORTH)', 'B.B.M.P(CENTRAL)', 'B.B.M.P(SOUTH)')
NAMES = {'B.B.M.P(NORTH)': 'B.B.M.P (North)', 'B.B.M.P(CENTRAL)': 'B.B.M.P (Central)',
         'B.B.M.P(SOUTH)': 'B.B.M.P (South)'}


def rows(name):
    with open(os.path.join(RAW, name), encoding='utf-8') as fh:
        return {r['district']: r for r in csv.DictReader(fh)}


def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    return cov / (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5


def build():
    asd, draft, sep = rows('asd_district.csv'), rows('draft_roll_district.csv'), rows('roll_20261009_district.csv')
    assert len(asd) == 34 and set(asd) == set(draft) == set(sep), 'the same 34 districts in all three tables'
    dist = []
    for code, a in asd.items():
        d, s = draft[code], sep[code]
        g = {k: int(a[k]) for k in REASONS}
        before, removed = int(a['electors_before']), int(a['total'])
        assert sum(g.values()) == removed, code
        dw, dtot = int(d['women']), int(d['general_total'])
        assert dtot == int(a['digitised']) == before - removed, code
        sw, stot = int(s['women']), int(s['total'])
        assert int(s['men']) + sw + int(s['third']) == stot, code
        row = {'district': NAMES.get(code, code.title()), 'bengaluru': code in BENGALURU,
               'before': before, 'removed': removed}
        row.update(g)
        row.update({
            'per_100': round(100 * removed / before, 4),
            'shares': {k: round(100 * g[k] / removed, 4) for k in REASONS},
            'draft': dtot, 'draft_women_pct': round(100 * dw / dtot, 4),
            'sep': stot, 'sep_women_pct': round(100 * sw / stot, 4),
            'added_sep': stot - dtot,
            'net_per_100': round(100 * (before - stot) / before, 4),
        })
        dist.append(row)
    dist.sort(key=lambda r: -r['per_100'])

    T = lambda k: sum(r[k] for r in dist)
    for k in ('before', 'removed', 'draft') + REASONS:
        assert T(k) == STATE[k], k
    assert T('sep') == SEP_TOTAL
    # the reported rise from the draft to the reported total, 8.64 lakh, and the fall of general electors from 5,54,32,314
    assert round((FINAL['total_with_service'] - STATE['draft']) / 1e3) == 864 and STATE['before'] - FINAL['total'] == 9976625
    assert FINAL['total'] == FINAL['men'] + FINAL['women'] + FINAL['third']
    # The Times of India's 10.08 lakh added less 1.88 lakh deleted equals the rise to the lakh
    assert round((FINAL['total'] - STATE['draft']) / 1e5, 1) == round((FINAL['added'] - FINAL['deleted']) / 1e5, 1)
    # the three sexes as reported fall short of the reported total by 44,322, which the method page states
    assert FINAL['total_with_service'] - (FINAL['men'] + FINAL['women'] + FINAL['third']) == 44322
    # the identities every final roll is held to, and agreement with the All India table
    final_roll.block(_F, 'Karnataka', STATE['before'], STATE['draft'], STATE['removed'], '2026-08-24')

    blr = [r for r in dist if r['bengaluru']]
    rest = [r for r in dist if not r['bengaluru']]
    B = lambda L, k: sum(r[k] for r in L)
    before, removed, sep_t = T('before'), T('removed'), T('sep')
    summary = {
        'before': before, 'removed': removed, 'draft': T('draft'), 'sep': sep_t,
        'per_100': round(100 * removed / before, 4),
        'reasons': {k: T(k) for k in REASONS},
        'shares': {k: round(100 * T(k) / removed, 4) for k in REASONS},
        'added_sep': sep_t - T('draft'),
        'made_up_pct': round(100 * (sep_t - T('draft')) / removed, 4),
        'net_fall': before - sep_t,
        'net_per_100': round(100 * (before - sep_t) / before, 4),
        'women_draft_pct': round(100 * sum(int(r['women']) for r in draft.values()) / T('draft'), 4),
        'women_sep_pct': round(100 * sum(int(r['women']) for r in sep.values()) / sep_t, 4),
        'districts': len(dist),
        'draft_service': DRAFT_SERVICE,
        'final_date': FINAL['date'], 'final': FINAL['total'],
        'final_men': FINAL['men'], 'final_women': FINAL['women'], 'final_third': FINAL['third'],
        'final_by_sex': FINAL['men'] + FINAL['women'] + FINAL['third'], 'final_with_service': FINAL['total_with_service'],
        'added_after_draft_reported': FINAL['added'], 'deleted_after_draft_reported': FINAL['deleted'],
        'added_final': FINAL['total'] - T('draft'),
        'made_up_final_pct': round(100 * (FINAL['total'] - T('draft')) / removed, 4),
        'net_fall_final': before - FINAL['total'],
        'net_per_100_final': round(100 * (before - FINAL['total']) / before, 4),
        'women_final_pct': round(100 * FINAL['women'] / (FINAL['men'] + FINAL['women'] + FINAL['third']), 4),
        'top': [{'district': r['district'], 'per_100': r['per_100']} for r in dist[:5]],
        'low': [{'district': r['district'], 'per_100': r['per_100']} for r in dist[-3:]],
        'bengaluru': {
            'districts': len(blr), 'before': B(blr, 'before'), 'removed': B(blr, 'removed'),
            'per_100': round(100 * B(blr, 'removed') / B(blr, 'before'), 4),
            'share_of_roll': round(100 * B(blr, 'before') / before, 4),
            'share_of_removed': round(100 * B(blr, 'removed') / removed, 4),
            'shifted_absent_share': round(100 * (B(blr, 'shifted') + B(blr, 'absent')) / B(blr, 'removed'), 4),
            'dead_share': round(100 * B(blr, 'dead') / B(blr, 'removed'), 4),
            'net_per_100': round(100 * (B(blr, 'before') - B(blr, 'sep')) / B(blr, 'before'), 4),
            'added_sep': B(blr, 'sep') - B(blr, 'draft'),
            'made_up_pct': round(100 * (B(blr, 'sep') - B(blr, 'draft')) / B(blr, 'removed'), 4),
        },
        'rest': {
            'per_100': round(100 * B(rest, 'removed') / B(rest, 'before'), 4),
            'shifted_absent_share': round(100 * (B(rest, 'shifted') + B(rest, 'absent')) / B(rest, 'removed'), 4),
            'dead_share': round(100 * B(rest, 'dead') / B(rest, 'removed'), 4),
            'made_up_pct': round(100 * (B(rest, 'sep') - B(rest, 'draft')) / B(rest, 'removed'), 4),
        },
        'rho_rate_shifted': round(spearman([r['per_100'] for r in dist],
                                           [r['shares']['shifted'] + r['shares']['absent'] for r in dist]), 3),
    }
    by_dead = max(dist, key=lambda r: r['shares']['dead'])
    summary['dead_max'] = {'district': by_dead['district'], 'share': by_dead['shares']['dead']}

    out = {}
    out['summary.json'] = json.dumps(summary, ensure_ascii=False, indent=1) + '\n'
    out['districts.json'] = json.dumps(dist, ensure_ascii=False, separators=(',', ':')) + '\n'
    cols = ['district', 'before', 'removed', 'per_100'] + list(REASONS) + ['draft', 'sep', 'net_per_100']
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['district', 'roll_before', 'removed', 'removed_per_100', 'absent', 'shifted', 'dead',
                'already_enrolled', 'other', 'draft_roll', 'roll_9_oct_2026', 'net_fall_per_100'])
    for r in dist:
        w.writerow([r[c] for c in cols])
    out['districts.csv'] = buf.getvalue()

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
            sys.exit('STALE, run python3 scripts/build_karnataka.py: ' + ', '.join(stale))
        print('OK: data/karnataka matches its raw tables')
    else:
        print('%d removed of %d (%.2f per 100); Bengaluru %.2f per 100, %.1f%% of removals'
              % (s['removed'], s['before'], s['per_100'], s['bengaluru']['per_100'], s['bengaluru']['share_of_removed']))
