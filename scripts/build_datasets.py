#!/usr/bin/env python3
"""Datasets and analyses of the revision made by others, for india/datasets/.

    python3 scripts/build_datasets.py          # writes data/india/datasets.json
    python3 scripts/build_datasets.py --check  # fails if it is stale

The entries are written by hand in data/india/raw/datasets_research/
datasets.json: who made each dataset or analysis, what it covers, how it was
made, how it can be had, the limits its makers state, and the site items that
use it. An entry may rest only on items the site already carries after their
second reading: the disputes items (data/india/disputes.json) and the reading
list (data/india/reads.json). It fails if

  * an item an entry names is not among them, or does not carry the phrase
    given for it;
  * a figure written in an entry's own sentences appears in none of the items
    it names (their text, quotation, reply, headline and research notes), so
    no figure can come from anywhere but a checked item;
  * a figure set beside an official one is not in its item as written, or the
    value given for it is not the value written (a figure in lakh or crore is
    read as rounded);
  * a figure counted from a data file does not equal the item's figure, or
    the official figure it is set beside is missing from its file;
  * an entry links a file (a table, an archive or a roll) where it should link
    a landing page.

The official figures are read by the page from their own files when it
loads, so a correction there reaches the comparison without a rebuild here.
"""
import csv
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IN = os.path.join(ROOT, 'data', 'india')
RAW = os.path.join(IN, 'raw', 'datasets_research', 'datasets.json')
OUT = os.path.join(IN, 'datasets.json')
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
# a link to a file of rows, never a landing page
ROWS = re.compile(r'\.(csv|tsv|parquet|tar|zip|gz|xlsx?|json|sqlite|db)(\?|$)|/eci-rolls/', re.I)
# the official figures the page reads, and the fields it may name
OFFICIAL_FILES = {'data/uttarpradesh/summary.json', 'data/india/states.json', 'data/westbengal/tribunals.json'}
STATE_FIELDS = {'removed', 'electors_before', 'electors_final', 'dead', 'draft'}
KINDS = {'dataset', 'analysis'}
ACCESS = {'public', 'request', 'aggregate', 'report'}
RELATIONS = {'same', 'rounded', 'part', 'floor'}


def load(path):
    with open(os.path.join(ROOT, path), encoding='utf-8') as fh:
        return json.load(fh)


def gid(g):
    """The id the reading page gives a group's heading."""
    return re.sub(r'-+$', '', re.sub(r'^-+|-+$', '', re.sub(r'[^a-z0-9]+', '-', g.lower()))[:60]) or 'group'


def long_date(d):
    y, m, day = d.split('-')
    return '%d %s %s' % (int(day), MONTHS[int(m) - 1], y)


def notes():
    """The research notes on each item, by item id or address."""
    out = {}
    for f in glob.glob(os.path.join(IN, 'raw', 'reads_research', '*verified.json')):
        for v in load(os.path.relpath(f, ROOT)):
            if isinstance(v, dict) and v.get('url'):
                out[v['url']] = out.get(v['url'], '') + ' ' + (v.get('note') or '')
    for f in glob.glob(os.path.join(IN, 'raw', 'disputes_research', 'verified_*.json')):
        D = load(os.path.relpath(f, ROOT))
        for k, v in (D.get('items') or {}).items():
            if isinstance(v, dict):
                out[k] = out.get(k, '') + ' ' + (v.get('note') or '')
    return out


def sources():
    out = {}
    for s in load('data/india/disputes.json')['sections']:
        for i in s['items']:
            out[i['id']] = {'id': i['id'], 'from': 'disputes', 'date': i['date'], 'state': i.get('state') or '',
                            'outlet': i['outlet'], 'headline': i['headline'], 'url': i['url'],
                            'text': ' '.join([i['claim'], i.get('quote') or '', i.get('response') or ''])}
    for i in load('data/india/reads.json')['items']:
        out[i['url']] = {'id': i['url'], 'from': 'reads', 'date': i['date'], 'state': '', 'outlet': i['outlet'],
                         'headline': i['title'], 'url': i['url'], 'text': i['shows'], 'group': gid(i['group']),
                         'subscription': bool(i.get('subscription'))}
    return out


def value(written):
    """The value of a figure as an item writes it, and whether it is rounded."""
    m = re.fullmatch(r'([\d.]+) (lakh|crore)', written)
    if m:
        return round(float(m.group(1)) * (1e5 if m.group(2) == 'lakh' else 1e7)), True
    assert re.fullmatch(r'\d{1,3}(,\d\d)*(,\d{3})?|\d+', written), 'cannot read the figure %r' % written
    return int(written.replace(',', '')), False


NUM = re.compile(r'\d[\d,]*(?:\.\d+)?')


def build():
    S, N = sources(), notes()
    raw = load(os.path.relpath(RAW, ROOT))
    used = {}
    entries = []
    states = {s['state']: s for s in load('data/india/states.json')['states']}
    trib = load('data/westbengal/tribunals.json')['rows']
    ids = set()

    def hay(key):
        s = S[key]
        return ' '.join([s['text'], s['headline'], long_date(s['date']), N.get(key, ''), N.get(s['url'], '')])

    def take(key, needle):
        assert key in S, 'no item %s among the checked items' % key
        assert needle in hay(key), '%s does not say %r' % (key, needle)
        used[key] = S[key]
        return key

    for e in raw['entries']:
        assert e['id'] not in ids, 'two entries are called %s' % e['id']
        ids.add(e['id'])
        assert e['kind'] in KINDS and e['access'] in ACCESS, '%s: kind or access not known' % e['id']
        assert not ROWS.search(e['url']), '%s links a file of rows (%s): link its landing page' % (e['id'], e['url'])
        items = [take(k, n) for k, n in e['items']]
        cmp = []
        for c in e['compare']:
            assert c['relation'] in RELATIONS, '%s: relation %s not known' % (e['id'], c['relation'])
            take(c['item'], c['as_written'])
            v, rounded = value(c['as_written'])
            x = {'what': c['what'], 'as_written': c['as_written'], 'item': c['item'], 'relation': c['relation'], 'type': c['type']}
            if c['type'] == 'file' and 'theirs_csv' in c:
                f, col = c['theirs_csv']
                with open(os.path.join(ROOT, f), encoding='utf-8') as fh:
                    total = sum(int(r[col]) for r in csv.DictReader(fh))
                assert total == v, '%s: %s sums to %d, the item says %s' % (e['id'], f, total, c['as_written'])
                x['theirs'] = total
                x['theirs_file'] = f
            else:
                x['theirs'] = c['theirs']
                assert c['theirs'] == v, '%s: %r is %d, the entry says %d' % (e['id'], c['as_written'], v, c['theirs'])
            assert rounded == (c['relation'] == 'rounded'), '%s: %r should be read as %s' % (e['id'], c['as_written'], 'rounded' if rounded else 'exact')
            if c['type'] == 'file':
                f, key = c['official']
                assert f in OFFICIAL_FILES and isinstance(load(f).get(key), int), '%s: %s carries no %s' % (e['id'], f, key)
                x['official'] = {'file': f, 'key': key}
            elif c['type'] == 'states':
                s = states.get(c['state'])
                assert s and c['field'] in STATE_FIELDS, '%s: no %s for %s' % (e['id'], c['field'], c['state'])
                need = ['electors_before', 'removed'] if c['field'] == 'draft' else [c['field']]
                assert all(isinstance(s.get(k), int) for k in need), '%s: states.json has no %s for %s' % (e['id'], c['field'], c['state'])
                x['official'] = {'file': 'data/india/states.json', 'state': c['state'], 'field': c['field']}
            elif c['type'] == 'tribunals':
                m = c['match']
                rows = [r for r in trib if all(r.get(k) == v2 for k, v2 in m.items())]
                assert len(rows) == 1, '%s: %d tribunal rows match %s' % (e['id'], len(rows), m)
                x['official'] = {'file': 'data/westbengal/tribunals.json', 'match': m, 'who': rows[0]['who'], 'url': rows[0]['url']}
            elif c['type'] == 'pair':
                take(c['official_item'], c['official_written'])
                ov, _ = value(c['official_written'])
                assert ov == c['official'], '%s: %r is not %d' % (e['id'], c['official_written'], c['official'])
                x['official'] = {'value': ov, 'item': c['official_item'], 'who': c['official_who']}
            else:
                raise AssertionError('%s: comparison type %s not known' % (e['id'], c['type']))
            cmp.append(x)
        # every figure in the entry's own sentences is in an item it names
        keys = list(dict.fromkeys(items + [c['item'] for c in e['compare']] +
                                  [c['official_item'] for c in e['compare'] if c.get('official_item')]))
        text = ' '.join(hay(k) for k in keys)
        for f in ('name', 'covers', 'how', 'access_text', 'limits', 'recorded'):
            for num in NUM.findall(e.get(f) or ''):
                num = num.rstrip(',.')
                assert num in text, '%s: the figure %s in its %s is in none of its items' % (e['id'], num, f)
        for p, _ in e['pages']:
            assert os.path.exists(os.path.join(ROOT, 'site', 'pages', p.split('#')[0], 'index.html')), '%s: no page %s' % (e['id'], p)
        entries.append({k: e[k] for k in ('id', 'maker', 'kind', 'states', 'name', 'url', 'first', 'covers', 'how', 'access',
                                           'access_text', 'limits', 'recorded', 'pages')} | {'via': e.get('via') or '', 'items': items, 'compare': cmp})
    srcs = {}
    for k in sorted(used):
        s = used[k]
        srcs[k] = {x: s[x] for x in ('id', 'from', 'date', 'state', 'outlet', 'headline', 'url') if x in s}
        if s['from'] == 'reads':
            srcs[k]['group'] = s['group']
            srcs[k]['subscription'] = s['subscription']
    states_n = sorted({st for e in entries for st in e['states']})
    return {
        'entries': entries, 'sources': srcs,
        'counts': {'entries': len(entries), 'datasets': sum(1 for e in entries if e['kind'] == 'dataset'),
                   'makers': len({e['maker'] for e in entries}), 'states': len(states_n),
                   'comparisons': sum(len(e['compare']) for e in entries), 'items': len(used),
                   'first': min(s['date'] for s in used.values()), 'last': max(s['date'] for s in used.values())},
    }


def main():
    text = json.dumps(build(), ensure_ascii=False, separators=(',', ':')) + '\n'
    if '--check' in sys.argv:
        if not os.path.exists(OUT) or open(OUT, encoding='utf-8').read() != text:
            raise SystemExit('FAIL - stale: data/india/datasets.json (run scripts/build_datasets.py)')
        print('datasets current')
        return
    open(OUT, 'w', encoding='utf-8').write(text)
    d = json.loads(text)['counts']
    print('%d entries from %d makers, %d comparisons, %d items' % (d['entries'], d['makers'], d['comparisons'], d['items']))


if __name__ == '__main__':
    main()
