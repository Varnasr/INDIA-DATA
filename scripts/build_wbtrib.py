"""West Bengal's SIR appellate tribunals: every dated figure about the appeals
before them, with who gave it and where it was read.

Reads data/westbengal/raw/tribunals.csv (one row a figure) and
data/westbengal/raw/tribunal_orders.csv (the orders and events that shaped
the tribunals) and writes data/westbengal/tribunals.json, which the page
westbengal/tribunals/ reads.

    python3 scripts/build_wbtrib.py           # write
    python3 scripts/build_wbtrib.py --check   # fail if a row is unsound or the output is stale

Every row is a figure as its source wrote it (as_written), with the date the
figure is for (as_of), the date it was said in court or filed (said), or,
where the source gives no date of its own, the date of the report (reported).
The basis says who the figure comes from:

    official  an official document: the Commission's affidavit or annexure,
              or the Chief Electoral Officer's RTI reply
    court     the Supreme Court's own order
    counsel   a submission by named counsel in court
    analysis  an independent group's count of the tribunals' appeal portal
    press     the newspaper's own statement, with no source given
    unnamed   a source the newspaper does not name

Every row must name its source and address, and an item already on the site
(a disputes item, an RTI item, or a row of adjudication_state.csv) whose own
record cites that address. A row whose source says its count covers only part of the whole
carries approx 'part' and is read as a floor. Figures for the same measure
and the same date, or from the same document where one is undated, are flagged where they cannot both be true, and
so is a count of appeals filed or decided that is lower than an earlier one.
Nothing is corrected and nothing is dropped: the page shows each figure with
its flag.
"""
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'westbengal', 'raw')
OUT = os.path.join(ROOT, 'data', 'westbengal', 'tribunals.json')
CHECK = '--check' in sys.argv

MEASURES = {
    'filed': 'appeals', 'decided': 'appeals', 'pending': 'appeals',
    'on_roll': 'appeals', 'off_roll': 'appeals', 'share_on_roll': 'appeals',
    'tribunals': None, 'resigned': None, 'per_day': None,
}
APPEALS = {'all', 'by_deleted', 'against_inclusion'}
BASIS = {'official', 'court', 'counsel', 'analysis', 'press', 'unnamed'}
KINDS = {'as_of', 'said', 'reported'}
APPROX = {'', 'over', 'at least', 'nearly', 'about', 'a little over', 'range', 'part'}
# counts that can only grow: a later one below an earlier one is flagged
CUMULATIVE = {'filed', 'decided', 'resigned'}
# the number of tribunals is compared across reports a week apart or less
WINDOW = {'tribunals': 7}


def fail(msg):
    print('FAIL: ' + msg)
    sys.exit(1)


def read(name):
    with open(os.path.join(RAW, name), encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def items():
    """Every item on the site by id, with the text of its own record."""
    out = {}
    dr = os.path.join(ROOT, 'data', 'india', 'raw', 'disputes_research')
    for name in ('courts.json', 'software.json', 'form7.json', 'protests.json'):
        with open(os.path.join(dr, name), encoding='utf-8') as fh:
            for it in json.load(fh)['items']:
                out[it['id']] = json.dumps(it, ensure_ascii=False)
    with open(os.path.join(ROOT, 'data', 'india', 'raw', 'rti_research', 'rti.json'), encoding='utf-8') as fh:
        d = json.load(fh)
        for it in (d['items'] if isinstance(d, dict) else d):
            out[it['id']] = json.dumps(it, ensure_ascii=False)
    # published: only an item the site shows counts
    with open(os.path.join(ROOT, 'data', 'india', 'disputes.json'), encoding='utf-8') as fh:
        shown = {x['id'] for s in json.load(fh)['sections'] for x in s['items']}
    with open(os.path.join(ROOT, 'data', 'india', 'rti.json'), encoding='utf-8') as fh:
        shown |= {x['id'] for x in json.load(fh)['items']}
    out = {k: v for k, v in out.items() if k in shown}
    for r in read('adjudication_state.csv'):
        out['wb-adj:' + r['measure']] = json.dumps(r, ensure_ascii=False)
    return out


def bare(url):
    return re.sub(r'^https?://(www\.)?', '', url).rstrip('/')


def span(r):
    v, a = r['value'], r['approx']
    if a == 'range':
        return (v, r['value_hi'])
    # 'part' is a count its source says covers only part of the whole (the
    # Civic Research Group's portal count), so it sets a floor
    if a in ('over', 'at least', 'part'):
        return (v, float('inf'))
    if a == 'nearly':  # 'nearly 38 lakh' is said of 38.31 lakh
        return (0.9 * v, 1.01 * v)
    if a == 'about':
        return (0.95 * v, 1.05 * v)
    if a == 'a little over':
        return (v, 1.1 * v)
    return (v, v)


def apart(a, b):
    sa, sb = span(a), span(b)
    return sa[1] < sb[0] or sb[1] < sa[0]


def days(d):
    y, m, dd = map(int, d.split('-'))
    import datetime
    return datetime.date(y, m, dd).toordinal()


def build():
    known = items()
    rows = []
    for i, r in enumerate(read('tribunals.csv')):
        where = 'tribunals.csv row %d' % (i + 2)
        if not re.match(r'^2026-\d\d-\d\d$', r['date']):
            fail('%s: date %r' % (where, r['date']))
        if r['date_kind'] not in KINDS:
            fail('%s: date_kind %r' % (where, r['date_kind']))
        if r['measure'] not in MEASURES:
            fail('%s: measure %r' % (where, r['measure']))
        if (MEASURES[r['measure']] == 'appeals') != (r['appeals'] in APPEALS):
            fail('%s: %r appeals for %s' % (where, r['appeals'], r['measure']))
        if r['basis'] not in BASIS:
            fail('%s: basis %r' % (where, r['basis']))
        if r['approx'] not in APPROX or (r['approx'] == 'range') != bool(r['value_hi']):
            fail('%s: approx %r with value_hi %r' % (where, r['approx'], r['value_hi']))
        for k in ('as_written', 'who', 'source', 'url', 'item'):
            if not r[k].strip():
                fail('%s: no %s' % (where, k))
        if not r['url'].startswith('https://'):
            fail('%s: %s is not an https address' % (where, r['url']))
        if r['item'] not in known:
            fail('%s: item %s is not on the site' % (where, r['item']))
        if bare(r['url']) not in known[r['item']] and r['url'] not in known[r['item']]:
            fail('%s: item %s does not cite %s' % (where, r['item'], r['url']))
        if r['paywall'] and 'Subscription.' not in r['note']:
            fail('%s: a subscription story must say so in its note' % where)
        # the figure must be in the words quoted, as the source prints it
        digits = re.sub(r'\D', '', r['as_written'])
        if not digits and not re.search(r'\b(one|two|three|four|fourth|nineteen)\b', r['as_written'], re.I):
            fail('%s: as_written carries no figure' % where)
        v = int(r['value'])
        row = {
            'date': r['date'], 'date_kind': r['date_kind'], 'measure': r['measure'], 'appeals': r['appeals'] or None,
            'value': v, 'value_hi': int(r['value_hi']) if r['value_hi'] else None, 'approx': r['approx'] or None,
            'as_written': r['as_written'], 'basis': r['basis'], 'who': r['who'], 'doc_key': r['doc_key'] or None,
            'source': r['source'], 'url': r['url'], 'item': r['item'], 'paywall': bool(r['paywall']), 'note': r['note'],
        }
        rows.append(row)
    rows.sort(key=lambda x: (x['date'], x['measure'], x['appeals'] or '', x['source']))
    for i, x in enumerate(rows):
        x['id'] = 't%02d' % (i + 1)

    # decided, both outcomes added, where a source gives the two parts and no
    # total of its own: marked derived, and drawn as such
    derived = []
    groups = {}
    for x in rows:
        groups.setdefault((x['date'], x['source'], x['appeals'] or ''), {})[x['measure']] = x
    for (d, s, a), g in sorted(groups.items()):
        if a == 'all' and 'on_roll' in g and 'off_roll' in g and 'decided' not in g:
            p, q = g['on_roll'], g['off_roll']
            derived.append({'date': d, 'date_kind': p['date_kind'], 'measure': 'decided', 'appeals': 'all', 'value': p['value'] + q['value'],
                            'basis': p['basis'], 'who': p['who'], 'doc_key': p['doc_key'], 'source': s, 'url': p['url'], 'item': p['item'],
                            'from': [p['id'], q['id']]})
    by_src = {}
    for x in rows:
        if x['measure'] == 'decided' and x['appeals'] in ('by_deleted', 'against_inclusion'):
            by_src.setdefault((x['date'], x['source']), {})[x['appeals']] = x
    for (d, s), g in sorted(by_src.items()):
        if len(g) == 2 and not any(y['measure'] == 'decided' and y['appeals'] == 'all' and y['date'] == d and y['source'] == s for y in rows):
            p, q = g['by_deleted'], g['against_inclusion']
            derived.append({'date': d, 'date_kind': p['date_kind'], 'measure': 'decided', 'appeals': 'all', 'value': p['value'] + q['value'],
                            'basis': p['basis'], 'who': p['who'], 'doc_key': None, 'source': s, 'url': p['url'], 'item': p['item'],
                            'from': [p['id'], q['id']]})
    for i, x in enumerate(derived):
        x['id'] = 'd%02d' % (i + 1)

    # flags: two figures that cannot both be true
    flags = []

    def add(kind, a, b, why):
        key = (kind, a['id'], b['id'])
        if any((f['kind'], f['rows'][0], f['rows'][1]) == key for f in flags):
            return
        flags.append({'kind': kind, 'rows': [a['id'], b['id']], 'measure': a['measure'], 'appeals': a['appeals'], 'why': why})
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            if a['measure'] != b['measure'] or a['appeals'] != b['appeals'] or not apart(a, b):
                continue
            if a['date'] == b['date'] and a['source'] != b['source']:
                add('differ', a, b, 'date')
            # two dated figures from one document can both be true when the
            # later is the larger, so only an undated one is compared
            elif a['doc_key'] and a['doc_key'] == b['doc_key'] and 'reported' in (a['date_kind'], b['date_kind']):
                add('differ', a, b, 'document')
            elif a['measure'] in WINDOW and abs(days(a['date']) - days(b['date'])) <= WINDOW[a['measure']]:
                add('differ', a, b, 'week')
            elif a['measure'] in CUMULATIVE and a['date'] < b['date'] and span(b)[1] < span(a)[0]:
                add('falls', a, b, 'later')
    for f in flags:
        for rid in f['rows']:
            next(x for x in rows if x['id'] == rid).setdefault('flags', []).append(flags.index(f))

    orders = []
    for i, r in enumerate(read('tribunal_orders.csv')):
        where = 'tribunal_orders.csv row %d' % (i + 2)
        if r['basis'] not in BASIS or not r['url'].startswith('https://') or r['item'] not in known:
            fail('%s: basis, address or item' % where)
        if bare(r['url']) not in known[r['item']] and r['url'] not in known[r['item']]:
            fail('%s: item %s does not cite %s' % (where, r['item'], r['url']))
        orders.append({k: r[k] for k in ('date', 'key', 'basis', 'source', 'url', 'item', 'note')})
    keys = [o['key'] for o in orders]
    if len(set(keys)) != len(keys):
        fail('tribunal_orders.csv: a key is used twice')

    latest = {}
    for x in rows:
        if x['basis'] == 'official' and x['measure'] in ('filed', 'decided', 'pending') and x['appeals'] == 'all' and x['date_kind'] != 'reported':
            if x['measure'] not in latest or x['date'] > latest[x['measure']]['date']:
                latest[x['measure']] = x
    return {'rows': rows, 'derived': derived, 'flags': flags, 'orders': orders,
            'latest_official': {k: v['id'] for k, v in sorted(latest.items())},
            'counts': {'rows': len(rows), 'sources': len({x['source'] for x in rows}), 'flags': len(flags)}}


def main():
    data = build()
    text = json.dumps(data, ensure_ascii=False, indent=1) + '\n'
    if CHECK:
        try:
            cur = open(OUT, encoding='utf-8').read()
        except FileNotFoundError:
            cur = ''
        if cur != text:
            fail('data/westbengal/tribunals.json is stale; run scripts/build_wbtrib.py')
        print('OK: %d figures from %d sources, %d flagged pairs' % (data['counts']['rows'], data['counts']['sources'], data['counts']['flags']))
        return
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write(text)
    print('wrote %s: %d figures, %d flagged pairs' % (os.path.relpath(OUT, ROOT), data['counts']['rows'], data['counts']['flags']))
    for f in data['flags']:
        a, b = [next(x for x in data['rows'] if x['id'] == i) for i in f['rows']]
        print('  %s (%s) %s/%s: %s %s %s %s  vs  %s %s %s %s' % (f['kind'], f['why'], f['measure'], f['appeals'], a['date'], a['source'], a['as_written'], '', b['date'], b['source'], b['as_written'], ''))


if __name__ == '__main__':
    main()
