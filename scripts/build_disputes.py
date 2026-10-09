#!/usr/bin/env python3
"""Protests and disputes over the SIR, for india/disputes/.

    python3 scripts/build_disputes.py          # writes data/india/disputes.json and .csv
    python3 scripts/build_disputes.py --check  # fails if either is stale

Reads the research in data/india/raw/disputes_research/ (courts.json,
protests.json, form7.json, software.json) and the second reading of each,
verified_<name>.json. An item reaches the page only if that reading confirmed it or
corrected it, and a correction replaces the original claim, quote, date or
address. Anything else is listed by outlet and headline under "What we could
not confirm". The press reports the process page already carries, which were
checked when they went on it, join the sections they belong to, so the two
pages cannot disagree.

Nothing here says the revision was meant to exclude anyone. A party's claim
is its allegation, attributed by name, and the Commission's reply sits beside
it where one was reported.
"""
import csv
import io
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RES = os.path.join(ROOT, 'data', 'india', 'raw', 'disputes_research')
OUT = os.path.join(ROOT, 'data', 'india')

SECTIONS = [
    ('courts', 'In the courts'),
    ('resolutions', 'Resolutions in the Assemblies'),
    ('protests', 'Protests by parties and groups'),
    ('boycotts', 'Booth officers\' protests'),
    ('form7', 'Form 7 objections and pre-printed forms'),
    ('software', 'Changes to the software'),
    ('instructions', 'Instructions given without a written order'),
    ('errors', 'Wrong entries reported on the rolls'),
    ('deaths', 'Deaths reported during the revision'),
]
FILES = ['courts', 'protests', 'form7', 'software']
# The process page's checked press reports, by its topic, into this page's sections.
FROM_PROCESS = {
    'Bulk Form 7 objections': 'form7',
    'Form 6 changed online': 'software', 'Logical discrepancy notices': 'software',
    'The Commission\'s software': 'software', 'Form 6 after the revision': 'software',
    'Deletions and house visits': 'errors', 'Living electors marked dead': 'errors',
    'Errors and duplicates in the roll': 'errors',
    'Booth officers\' deaths and workload': 'deaths', 'Deaths families linked to hearings': 'deaths',
}
KEEP = ('id', 'section', 'state', 'place', 'date', 'kind', 'outlet', 'case', 'headline', 'url', 'claim', 'quote', 'response')
ALIAS = {'Hyderabad': 'Telangana', 'NCT of Delhi': 'Delhi', 'Orissa': 'Odisha'}


def load(name):
    p = os.path.join(RES, name + '.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def states_of(s):
    out = []
    for x in (s or 'India').replace(',', ';').split(';'):
        x = ALIAS.get(x.strip(), x.strip())
        if x and x not in out:
            out.append(x)
    return out


def build():
    # one second reading per research file: verified_<name>.json
    V = {}
    for f in FILES:
        d = load('verified_' + f) or {}
        V.update(d.get('items', d))
    items, unconfirmed, seen = [], [], set()
    for f in FILES:
        d = load(f)
        if not d:
            continue
        for it in d['items']:
            if it['id'] in seen:
                raise SystemExit('FAIL - duplicate id ' + it['id'])
            seen.add(it['id'])
            v = V.get(it['id'], {})
            st = v.get('status')
            if st not in ('confirmed', 'corrected'):
                unconfirmed.append({'outlet': it.get('outlet'), 'headline': it.get('headline'), 'date': it.get('date'),
                                    'reason': v.get('note') or 'not yet checked against its source'})
                continue
            it = dict(it)
            for k in ('claim', 'quote', 'date', 'url', 'outlet', 'kind', 'section', 'state', 'response'):
                if v.get(k):
                    it[k] = v[k]
            items.append({k: it.get(k, '') for k in KEEP})
    P = json.load(open(os.path.join(OUT, 'process.json'), encoding='utf-8'))
    for n, r in enumerate(P['reported']):
        sec = FROM_PROCESS.get(r.get('topic'))
        if not sec:
            continue
        items.append({'id': 'process-%02d' % n, 'section': sec, 'state': r['state'], 'place': '', 'date': r['date'],
                      'kind': 'press', 'outlet': r['outlet'], 'case': '', 'headline': r.get('headline', ''), 'url': r['url'],
                      'claim': r['text'], 'quote': '', 'response': r.get('response', '')})
    known = {s for s, _ in SECTIONS}
    for it in items:
        if it['section'] not in known:
            raise SystemExit('FAIL - %s has no section %r' % (it['id'], it['section']))
        if not (it['url'] and it['date'] and it['claim']):
            raise SystemExit('FAIL - %s lacks a source, date or claim' % it['id'])
        if '—' in it['claim'] or '–' in it['claim']:
            raise SystemExit('FAIL - %s carries a dash the writing rules forbid' % it['id'])
        it['states'] = states_of(it['state'])
    order = {s: i for i, (s, _) in enumerate(SECTIONS)}
    items.sort(key=lambda x: (order[x['section']], x['kind'] != 'primary', x['date']))
    by_state, by_month = {}, {}
    for it in items:
        for s in it['states']:
            if s != 'India':
                by_state[s] = by_state.get(s, 0) + 1
        m = it['date'][:7]
        by_month.setdefault(m, {}).setdefault(it['section'], 0)
        by_month[m][it['section']] += 1
    sections = [{'id': s, 'title': t, 'items': [i for i in items if i['section'] == s]} for s, t in SECTIONS]
    return {
        'sections': [s for s in sections if s['items']],
        'by_state': dict(sorted(by_state.items(), key=lambda kv: -kv[1])),
        'by_month': dict(sorted(by_month.items())),
        'unconfirmed': sorted(unconfirmed, key=lambda u: u['date'] or ''),
        'counts': {'items': len(items), 'primary': sum(1 for i in items if i['kind'] == 'primary'),
                   'states': len(by_state), 'first': min(i['date'] for i in items), 'last': max(i['date'] for i in items)},
    }


def as_csv(d):
    b = io.StringIO()
    w = csv.writer(b, lineterminator='\n')
    w.writerow(['section', 'date', 'state', 'kind', 'source', 'what_happened', 'commission_reply', 'url'])
    for s in d['sections']:
        for i in s['items']:
            w.writerow([s['title'], i['date'], i['state'], i['kind'], i['outlet'], i['claim'], i['response'], i['url']])
    return b.getvalue()


def main():
    d = build()
    files = {os.path.join(OUT, 'disputes.json'): json.dumps(d, ensure_ascii=False, separators=(',', ':')) + '\n',
             os.path.join(OUT, 'disputes.csv'): as_csv(d)}
    if '--check' in sys.argv:
        stale = [p for p, t in files.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != t]
        if stale:
            raise SystemExit('FAIL - stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale))
        print('disputes current: %d items' % d['counts']['items'])
        return
    for p, t in files.items():
        open(p, 'w', encoding='utf-8').write(t)
    c = d['counts']
    print('%d items (%d primary) across %d states, %s to %s; %d not confirmed' % (c['items'], c['primary'], c['states'], c['first'], c['last'], len(d['unconfirmed'])))


if __name__ == '__main__':
    main()
