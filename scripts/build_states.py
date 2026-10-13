"""Every state and union territory drawn by the shared state page.

Reads data/<slug>/raw/normal.json (the shape is in scripts/state_schema.md)
for each place in STATES, checks every identity, and writes
data/<slug>/summary.json and data/<slug>/tables.csv.

    python3 scripts/build_states.py           # write
    python3 scripts/build_states.py --check   # fail if anything is stale

The figures come from each state's own research folder, transcribed and
checked against its SOURCES.md. This script adds nothing to them but rates,
shares and the checks below, so a figure on the page is a figure in the file.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECK = '--check' in sys.argv

# place id in site/places.json, folder under data/
STATES = [
    ('cg', 'chhattisgarh'), ('mp', 'madhyapradesh'), ('ap', 'andhrapradesh'), ('od', 'odisha'),
    ('jh', 'jharkhand'), ('hr', 'haryana'), ('pb', 'punjab'), ('ga', 'goa'),
    ('mn', 'manipur'), ('ml', 'meghalaya'), ('mz', 'mizoram'), ('nl', 'nagaland'),
    ('sk', 'sikkim'), ('ar', 'arunachal'), ('tr', 'tripura'),
    ('py', 'puducherry'), ('ch', 'chandigarh'), ('ld', 'lakshadweep'), ('an', 'andaman'), ('dd', 'dnhdd'),
]

TOP = {'state', 'slug', 'ut', 'article', 'revision', 'dates', 'figures', 'reasons_complete', 'tables', 'sources', 'notes', 'cannot_show'}
FIG = {'roll_before', 'draft', 'removed', 'dead', 'shifted_absent_other', 'duplicate',
       'added_after', 'removed_after', 'net_after', 'final', 'notices'} | \
      {'%s_%s' % (s, w) for s in ('men', 'women', 'third') for w in ('before', 'draft', 'removed', 'final')}
FIGKEYS = {'v', 'src', 'press', 'rounded'}
KINDS = {
    'left_off': {'before': 'roll_before', 'draft': 'draft', 'removed': 'removed', 'dead': 'dead',
                 'shifted_absent_other': 'shifted_absent_other', 'duplicate': 'duplicate'},
    'after': {'draft': 'draft', 'added': 'added_after', 'removed': 'removed_after', 'final': 'final', 'net': 'net_after'},
    'draft': {'draft': 'draft', 'men': 'men_draft', 'women': 'women_draft', 'third': 'third_draft'},
    'final': {'final': 'final', 'draft': 'draft', 'men': 'men_final', 'women': 'women_final', 'third': 'third_final'},
    'fall': {},
}
LEVELS = {'district', 'region', 'ac', 'pc', 'island', 'tehsil', 'ward'}
TABKEYS = {'id', 'title', 'level', 'kind', 'src', 'partial', 'press', 'rows', 'note', 'removed_label'}


def fail(slug, msg):
    raise SystemExit('FAIL - %s: %s' % (slug, msg))


def build_one(pid, slug):
    p = os.path.join(ROOT, 'data', slug, 'raw', 'normal.json')
    if not os.path.exists(p):
        fail(slug, 'no raw/normal.json')
    d = json.load(open(p, encoding='utf-8'))
    extra = set(d) - TOP
    if extra:
        fail(slug, 'unknown fields %s' % sorted(extra))
    if d.get('article') not in (None, 'the'):
        fail(slug, 'article must be "the" or left out')
    if set(d.get('dates', {})) - {'roll_before', 'draft', 'final', 'notices'}:
        fail(slug, 'unknown dates %s' % sorted(set(d['dates']) - {'roll_before', 'draft', 'final', 'notices'}))
    if d.get('revision') not in ('sir', 'no_draft'):
        fail(slug, 'revision must be sir or no_draft')
    src = {s['id'] for s in d.get('sources', [])}
    for s in d.get('sources', []):
        if not s.get('title') or 'primary' not in s:
            fail(slug, 'source %s needs a title and primary' % s.get('id'))
    F = d.get('figures', {})
    for k, f in F.items():
        if k not in FIG:
            fail(slug, 'unknown figure %s' % k)
        if set(f) - FIGKEYS or not isinstance(f.get('v'), int) or f.get('src') not in src:
            fail(slug, 'figure %s needs an integer v and a known src' % k)
    v = {k: f['v'] for k, f in F.items()}

    def eq(a, b, what):
        if a != b:
            fail(slug, '%s: %s against %s' % (what, a, b))
    if all(k in v for k in ('roll_before', 'draft', 'removed')):
        eq(v['roll_before'] - v['draft'], v['removed'], 'roll before less draft is not the names left off')
    rs = [v[k] for k in ('dead', 'shifted_absent_other', 'duplicate') if k in v]
    if rs and 'removed' in v:
        if d.get('reasons_complete'):
            if len(rs) != 3:
                fail(slug, 'reasons_complete needs all three reasons')
            rounded = any(F[k].get('rounded') for k in ('dead', 'shifted_absent_other', 'duplicate'))
            if not rounded:
                eq(sum(rs), v['removed'], 'the three reasons do not add to the names left off')
        elif sum(rs) > v['removed'] * 1.005:
            fail(slug, 'the reasons add to more than the names left off')
    if all(k in v for k in ('added_after', 'removed_after', 'net_after')):
        eq(v['added_after'] - v['removed_after'], v['net_after'], 'added less removed after the draft is not the net')
    if all(k in v for k in ('draft', 'net_after', 'final')):
        eq(v['draft'] + v['net_after'], v['final'], 'draft plus the net is not the final roll')
    for w in ('before', 'draft', 'removed', 'final'):
        tot = {'before': 'roll_before', 'draft': 'draft', 'removed': 'removed', 'final': 'final'}[w]
        parts = ['men_' + w, 'women_' + w, 'third_' + w]
        if tot in v and all(x in v for x in parts):
            eq(sum(v[x] for x in parts), v[tot], 'men, women and third gender do not add to the %s' % w)

    tables = []
    for t in d.get('tables', []):
        if set(t) - TABKEYS or t.get('kind') not in KINDS or t.get('level') not in LEVELS or t.get('src') not in src or not t.get('rows'):
            fail(slug, 'table %s is not in the schema' % t.get('id'))
        rows = t['rows']
        for r in rows:
            for k, x in r.items():
                if k != 'name' and x is not None and not isinstance(x, int):
                    fail(slug, '%s, %s: %s is not an integer' % (t['id'], r.get('name'), k))
            if t['kind'] == 'after' and all(r.get(k) is not None for k in ('draft', 'added', 'removed', 'final')):
                eq(r['draft'] + r['added'] - r['removed'], r['final'], '%s, %s: draft plus added less removed' % (t['id'], r['name']))
            if t['kind'] == 'after' and r.get('net') is not None and r.get('added') is not None and r.get('removed') is not None:
                eq(r['added'] - r['removed'], r['net'], '%s, %s: added less removed is not the net' % (t['id'], r['name']))
            if t['kind'] == 'left_off':
                have = [k for k in ('before', 'draft', 'removed') if r.get(k) is not None]
                if len(have) == 2:
                    if 'before' not in have:
                        r['before'] = r['draft'] + r['removed']
                    elif 'draft' not in have:
                        r['draft'] = r['before'] - r['removed']
                    else:
                        r['removed'] = r['before'] - r['draft']
                elif len(have) == 3:
                    eq(r['before'] - r['draft'], r['removed'], '%s, %s: before less draft' % (t['id'], r['name']))
        if not t.get('partial'):
            for col, fk in KINDS[t['kind']].items():
                if fk in v and all(r.get(col) is not None for r in rows):
                    eq(sum(r[col] for r in rows), v[fk], 'table %s, column %s does not add to the state' % (t['id'], col))
        # rates the page draws
        for r in rows:
            if t['kind'] == 'left_off' and r.get('before') and r.get('removed') is not None:
                r['per_100'] = round(100 * r['removed'] / r['before'], 4)
            if t['kind'] == 'after' and r.get('draft'):
                if r.get('added') is not None:
                    r['added_1000'] = round(1000 * r['added'] / r['draft'], 1)
                if r.get('removed') is not None:
                    r['removed_1000'] = round(1000 * r['removed'] / r['draft'], 1)
            if t['kind'] == 'fall' and r.get('before'):
                end = r.get('final', r.get('draft'))
                if end is not None:
                    r['fall_100'] = round(100 * (r['before'] - end) / r['before'], 4)
            if t['kind'] in ('draft', 'final') and r.get('women') is not None and r.get('men') is not None:
                tot = r.get(t['kind']) or (r['men'] + r['women'] + (r.get('third') or 0))
                r['women_pct'] = round(100 * r['women'] / tot, 4)
        tables.append(t)

    rates = {}
    if 'removed' in v and 'roll_before' in v:
        rates['per_100'] = round(100 * v['removed'] / v['roll_before'], 4)
    if 'removed' in v and all(k in v for k in ('dead', 'shifted_absent_other', 'duplicate')):
        tot = v['dead'] + v['shifted_absent_other'] + v['duplicate']
        rates['shares'] = {k: round(100 * v[k] / tot, 1) for k in ('dead', 'shifted_absent_other', 'duplicate')}
    if 'net_after' in v and 'removed' in v:
        rates['made_up_pct'] = round(100 * v['net_after'] / v['removed'], 1)
    if 'final' in v and 'roll_before' in v:
        rates['final_vs_before'] = v['final'] - v['roll_before']
    for w, tot in (('before', 'roll_before'), ('draft', 'draft'), ('removed', 'removed'), ('final', 'final')):
        if 'women_' + w in v and tot in v:
            rates['women_%s_pct' % w] = round(100 * v['women_' + w] / v[tot], 4)
    if 'women_removed' in v and 'women_before' in v and 'men_removed' in v and 'men_before' in v:
        rates['women_per_100'] = round(100 * v['women_removed'] / v['women_before'], 1)
        rates['men_per_100'] = round(100 * v['men_removed'] / v['men_before'], 1)
    out = dict(d, id=pid, rates=rates, tables=tables)
    return out


def as_csv(d):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    cols = ['before', 'draft', 'removed', 'added', 'net', 'final', 'men', 'women', 'third', 'dead', 'shifted_absent_other', 'duplicate']
    w.writerow(['table', 'level', 'name', 'value'] + cols + ['source', 'press', 'partial'])
    sname = {s['id']: s['title'] for s in d['sources']}
    for k, f in d['figures'].items():
        w.writerow(['state', 'state', k, f['v']] + [''] * len(cols) + [sname[f['src']], 'yes' if f.get('press') else 'no', ''])
    for t in d['tables']:
        for r in t['rows']:
            w.writerow([t['id'], t['level'], r['name'], ''] + ['' if r.get(c) is None else r[c] for c in cols] +
                       [sname[t['src']], 'yes' if t.get('press') else 'no', 'yes' if t.get('partial') else 'no'])
    return buf.getvalue()


# States on the shared page whose constituency table is complete get a page
# per constituency and per district. The table names no district, so each
# carries raw/ac_district.csv from a published list, and the map is accepted
# only if every district's constituencies add up exactly to the state's own
# district table in every column the two share.
SEATS = {
    'meghalaya': dict(acs='constituencies', districts='districts', results='meghalaya_2023',
                      cols=('before', 'removed', 'dead', 'shifted_absent_other', 'duplicate', 'draft')),
    # the roll before and the final roll by constituency; the change takes in
    # the names left off and everything after the draft together
    'manipur': dict(acs='constituencies', districts='districts', results='manipur_2022',
                    cols=('before', 'final', 'men', 'women', 'third'), fall=('before', 'final')),
    # the draft to the final roll by constituency, names added and removed
    'odisha': dict(acs='acs_after', districts='districts_after', results='odisha_2024',
                   cols=('draft', 'added', 'removed', 'final'), extra=('districts_fall', 'before')),
}


def seat_files(slug):
    cfg = SEATS[slug]
    N = json.load(open(os.path.join(ROOT, 'data', slug, 'raw', 'normal.json'), encoding='utf-8'))
    T = {t['id']: t for t in N['tables']}
    dist = {int(r['ac']): r['district'] for r in csv.DictReader(open(os.path.join(ROOT, 'data', slug, 'raw', 'ac_district.csv'), encoding='utf-8'))}
    res = {int(r['ac']): r for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'india', 'raw', 'assembly', cfg['results'] + '.csv'), encoding='utf-8'))}
    seats = []
    for i, r in enumerate(T[cfg['acs']]['rows']):
        no, name = (int(r['name'].split()[0]), r['name'].split(' ', 1)[1]) if r['name'][0].isdigit() else (i + 1, r['name'])
        if no not in dist:
            fail(slug, 'constituency %d has no district in ac_district.csv' % no)
        x = dict(ac=no, name=name, district=dist[no])
        x.update({k: r[k] for k in cfg['cols']})
        if cfg.get('fall'):
            x['fall'] = r[cfg['fall'][0]] - r[cfg['fall'][1]]
        e = res.get(no)
        if e:
            x.update(winner=e['winner_party'], runner_up=e['runner_up_party'], margin=int(e['margin']),
                     turnout=round(100 * int(e['total_votes']) / int(e['electors']), 2) if e['total_votes'] and e['electors'] else None)
        seats.append(x)
    if sorted(s['ac'] for s in seats) != list(range(1, len(seats) + 1)):
        fail(slug, 'constituency numbers are not 1 to %d' % len(seats))
    out = []
    for r in T[cfg['districts']]['rows']:
        mine = [s for s in seats if s['district'] == r['name']]
        if not mine:
            fail(slug, 'district %s has no constituency in ac_district.csv' % r['name'])
        for k in cfg['cols']:
            if k in r and sum(s[k] for s in mine) != r[k]:
                fail(slug, '%s: its constituencies add to %d %s, the district table says %d' % (r['name'], sum(s[k] for s in mine), k, r[k]))
        y = dict(district=r['name'], acs=len(mine))
        y.update({k: sum(s[k] for s in mine) for k in cfg['cols'] + (('fall',) if cfg.get('fall') else ())})
        if cfg.get('extra'):
            # a district-only figure, joined by name: the roll before the revision
            hit = [e for e in T[cfg['extra'][0]]['rows'] if e['name'] == r['name']]
            if len(hit) != 1 or hit[0].get('draft', y['draft']) != y['draft']:
                fail(slug, '%s is not once in %s with the same draft' % (r['name'], cfg['extra'][0]))
            y[cfg['extra'][1]] = hit[0][cfg['extra'][1]]
        out.append(y)
    if sum(y['acs'] for y in out) != len(seats):
        fail(slug, 'some constituency sits in a district the district table does not list')
    return {os.path.join(ROOT, 'data', slug, 'constituencies.json'): json.dumps(seats, ensure_ascii=False, indent=1) + '\n',
            os.path.join(ROOT, 'data', slug, 'districts.json'): json.dumps(out, ensure_ascii=False, indent=1) + '\n'}


# States here with a complete district table and no constituency table get a
# page per district. The rows are the table's own, with a second table joined
# by district name where one adds the draft by sex.
DISTRICTS = {
    'andhrapradesh': dict(table='districts', cols=('before', 'draft', 'removed'), sex='districts_sex'),
    'chhattisgarh': dict(table='districts', cols=('draft', 'added', 'removed', 'net', 'final')),
    'mizoram': dict(table='districts', cols=('draft', 'final', 'men', 'women', 'third')),
}


def district_files(slug):
    cfg = DISTRICTS[slug]
    N = json.load(open(os.path.join(ROOT, 'data', slug, 'raw', 'normal.json'), encoding='utf-8'))
    T = {t['id']: t for t in N['tables']}
    if T[cfg['table']].get('partial'):
        fail(slug, 'the district table is partial, so it cannot have a page per district')
    out = []
    for r in T[cfg['table']]['rows']:
        y = dict(district=r['name'])
        y.update({k: r[k] for k in cfg['cols']})
        if cfg.get('sex'):
            s = [x for x in T[cfg['sex']]['rows'] if x['name'] == r['name']]
            if len(s) != 1 or s[0]['draft'] != r['draft']:
                fail(slug, '%s is not once in %s with the same draft' % (r['name'], cfg['sex']))
            y['draft_women_pct'] = round(100 * s[0]['women'] / s[0]['draft'], 4)
        out.append(y)
    return {os.path.join(ROOT, 'data', slug, 'districts.json'): json.dumps(out, ensure_ascii=False, indent=1) + '\n'}


def main():
    stale = []
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    for pid, slug in STATES:
        if only and slug not in only:
            continue
        if not os.path.exists(os.path.join(ROOT, 'data', slug, 'raw', 'normal.json')):
            if CHECK:
                continue
            print('skip %s: no normal.json yet' % slug)
            continue
        d = build_one(pid, slug)
        files = {os.path.join(ROOT, 'data', slug, 'summary.json'): json.dumps(d, ensure_ascii=False, indent=1) + '\n',
                 os.path.join(ROOT, 'data', slug, 'tables.csv'): as_csv(d)}
        if slug in SEATS:
            files.update(seat_files(slug))
        if slug in DISTRICTS:
            files.update(district_files(slug))
        for p, t in files.items():
            if not os.path.exists(p) or open(p, encoding='utf-8').read() != t:
                stale.append(p)
                if not CHECK:
                    open(p, 'w', encoding='utf-8').write(t)
        if not CHECK:
            print('%s: %s' % (slug, json.dumps(d['rates'])))
    if CHECK:
        if stale:
            raise SystemExit('FAIL - stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale))
        print('OK: state figures add up and are current')


if __name__ == '__main__':
    main()
