#!/usr/bin/env python3
"""Bulk Form 7 filings, state by state, for the process page's Form 7 section.

    python3 scripts/build_form7.py          # writes data/india/form7_bulk.json
    python3 scripts/build_form7.py --check  # fails if it is stale or a row breaks a rule

Each row is one reported bulk filing: Form 7 objections filed in numbers at one
place or by one filer, or generated in numbers in an officer's name. The rows
come from the `bulk` field on the entries in the disputes research
(data/india/raw/disputes_research/form7.json, up.json and software.json) and,
for two press reports the process page carries, from `bulk_process` in
form7.json, keyed by the report's address. Entries that share a `row` key are
one row. Everything else is read from the disputes page's own items as
build_disputes.py builds them, after their second reading, so a row can only
link to an item that page carries, and its claim is the checked one.

Rules the build holds:
- every count is a figure in the checked claim of the entry that carries it,
  written as the claim writes it (Indian grouping), and a row has one count
  at most;
- who filed is given by role or party, as the claim states it;
- a status is one of STATUS;
- every entry in a row is about the same state.

The context line is not written here. It is the process page's own sentence
on the order of 15 October 2026, and the first sentence of the disputes
item that reports the letter of 9 October, each with its source.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_disputes  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RES = os.path.join(ROOT, 'data', 'india', 'raw', 'disputes_research')
OUT = os.path.join(ROOT, 'data', 'india', 'form7_bulk.json')
FILES = ['form7', 'up', 'software']
STATUS = [
    ('rejected', 'Rejected or refused on verification'),
    ('withdrawn', 'Withdrawn or cancelled'),
    ('deleted', 'Names deleted'),
    ('inquiry', 'Official inquiry'),
    ('police', 'Police case or FIR'),
    ('court', 'Court order or direction'),
]
UNITS = {'forms', 'electors'}
QUAL = {'', 'about', 'more than', 'at least'}
# the disputes item that reports the Commission's letter of 9 October 2026
LETTER = 'form7-45'


def indian(n):
    s = str(n)
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ','.join(parts) + ',' + tail


def has_figure(text, n):
    return re.search(r'(?<![\d,])' + re.escape(indian(n)) + r'(?![\d,])', text) is not None


def build():
    D = build_disputes.build()
    items = {i['id']: i for s in D['sections'] for i in s['items']}
    by_url = {i['url']: i['id'] for i in items.values() if i['id'].startswith('process-')}
    marks = []  # (item id, bulk dict)
    for f in FILES:
        d = build_disputes.load(f) or {'items': []}
        for it in d['items']:
            for b in it.get('bulk', []):
                marks.append((it['id'], b))
        for p in d.get('bulk_process', []):
            if p['url'] not in by_url:
                raise SystemExit('FAIL - no process report at %s' % p['url'])
            for b in p['bulk']:
                marks.append((by_url[p['url']], b))
    rows, order = {}, []
    for iid, b in marks:
        it = items.get(iid)
        if it is None:
            raise SystemExit('FAIL - %s carries a bulk field but is not on the disputes page' % iid)
        k = b['row']
        if k not in rows:
            rows[k] = {'id': k, 'state': '', 'place': '', 'count': None, 'count_to': None, 'count_q': '', 'unit': '',
                       'count_from': '', 'filer': '', 'status': [], 'outcomes': [], 'entries': []}
            order.append(k)
        r = rows[k]
        st = build_disputes.states_of(it['state'])[0]
        if r['state'] and r['state'] != st:
            raise SystemExit('FAIL - row %s mixes %s and %s' % (k, r['state'], st))
        r['state'] = st
        for f in ('place', 'filer'):
            if b.get(f):
                if r[f]:
                    raise SystemExit('FAIL - row %s gives %s twice' % (k, f))
                r[f] = b[f]
        if b.get('count') is not None:
            if r['count'] is not None:
                raise SystemExit('FAIL - row %s has two counts' % k)
            if b.get('unit') not in UNITS or b.get('count_q', '') not in QUAL:
                raise SystemExit('FAIL - row %s has a count with no unit, or an unknown qualifier' % k)
            for n in [b['count']] + ([b['count_to']] if b.get('count_to') else []):
                if not isinstance(n, int) or not has_figure(it['claim'], n):
                    raise SystemExit('FAIL - row %s count %s is not a figure in the claim of %s' % (k, n, iid))
            r.update(count=b['count'], count_to=b.get('count_to'), count_q=b.get('count_q', ''), unit=b['unit'], count_from=iid)
        for s in b.get('status', []):
            if s not in dict(STATUS):
                raise SystemExit('FAIL - row %s has an unknown status %r' % (k, s))
            if s not in r['status']:
                r['status'].append(s)
        if b.get('outcome'):
            r['outcomes'].append({'text': b['outcome'], 'id': iid, 'date': it['date']})
        if iid not in [e['id'] for e in r['entries']]:
            r['entries'].append({'id': iid, 'outlet': it['outlet'], 'date': it['date']})
    out = []
    for k in order:
        r = rows[k]
        if not (r['place'] and r['filer']):
            raise SystemExit('FAIL - row %s lacks a place or who filed' % k)
        for t in [r['filer']] + [o['text'] for o in r['outcomes']]:
            if '—' in t or '–' in t or ';' in t:
                raise SystemExit('FAIL - row %s carries a dash or semicolon the writing rules forbid' % k)
        r['entries'].sort(key=lambda e: (e['date'], e['id']))
        r['outcomes'].sort(key=lambda o: (o['date'], o['id']))
        r['status'] = [s for s, _ in STATUS if s in r['status']]
        r['first'], r['last'] = r['entries'][0]['date'], r['entries'][-1]['date']
        out.append(r)
    out.sort(key=lambda r: (r['state'], r['first'], r['place']))

    # the context: the Commission's own limits, as the process page records them
    P = json.load(open(os.path.join(ROOT, 'data', 'india', 'process.json'), encoding='utf-8'))
    order15 = [t for t in P['timeline'] if t['date'] == '2026-10-15' and '2 per cent' in t['text']]
    if len(order15) != 1:
        raise SystemExit('FAIL - the order of 15 October 2026 on deletions over 2 per cent is not in process.json once')
    sent = [s for s in re.split(r'(?<=\.)\s+', order15[0]['text']) if '2 per cent' in s]
    if len(sent) != 1 or 'more than five' not in sent[0] or '9 October 2026' not in sent[0]:
        raise SystemExit('FAIL - the sentence on the 2 per cent rule and the letter of 9 October has changed in process.json')
    letter = items.get(LETTER)
    if not letter or '9 October' not in letter['claim']:
        raise SystemExit('FAIL - %s, the report of the letter of 9 October, is not on the disputes page' % LETTER)
    first = re.split(r'(?<=\.)\s+', letter['claim'])[0]
    return {
        'rows': out,
        'status': [list(s) for s in STATUS],
        'context': {
            'order': {'date': '2026-10-15', 'text': sent[0], 'title': order15[0]['title'], 'src': order15[0]['src'][0]},
            'letter': {'date': letter['date'], 'text': first, 'id': LETTER},
        },
        'counts': {'rows': len(out), 'states': len({r['state'] for r in out}), 'with_count': sum(1 for r in out if r['count'] is not None),
                   'police': sum(1 for r in out if 'police' in r['status']), 'court': sum(1 for r in out if 'court' in r['status']),
                   'entries': len({e['id'] for r in out for e in r['entries']})},
    }


def main():
    text = json.dumps(build(), ensure_ascii=False, separators=(',', ':')) + '\n'
    if '--check' in sys.argv:
        if not os.path.exists(OUT) or open(OUT, encoding='utf-8').read() != text:
            raise SystemExit('FAIL - stale: data/india/form7_bulk.json')
        print('form7_bulk current')
        return
    open(OUT, 'w', encoding='utf-8').write(text)
    c = json.loads(text)['counts']
    print('%d rows across %d states, %d with a count, from %d entries' % (c['rows'], c['states'], c['with_count'], c['entries']))


if __name__ == '__main__':
    main()
