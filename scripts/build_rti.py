#!/usr/bin/env python3
"""RTI applications about the SIR, for india/rti/.

    python3 scripts/build_rti.py          # writes data/india/rti.json and .csv
    python3 scripts/build_rti.py --check  # fails if either is stale

No authority publishes how many applications under the Right to Information
Act have been filed about the revision, by state or district. The Central
Information Commission's returns give each public authority's yearly total
with no split by subject. So this is a list of the applications whose filing,
reply, refusal or appeal was published or reported, never a count of all of
them.

Reads data/india/raw/rti_research/rti.json (each application with what was
asked, what the authority answered, a verbatim quote, the outlet and its
address) and the second reading of it, verified.json. An item reaches the
page only if that reading confirmed or corrected it, and a correction
replaces the field it names. Anything else is listed under "What we could
not confirm". An applicant is an organisation or a role, never a person's
name. Nothing here says what the Commission or anyone else intended.
"""
import csv
import io
import json
import os
import sys
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RES = os.path.join(ROOT, 'data', 'india', 'raw', 'rti_research')
OUT = os.path.join(ROOT, 'data', 'india')

# what became of each application, in the order the page shows them
OUTCOMES = ['no record held', 'refused', 'transferred', 'partly supplied', 'supplied', 'appeal', 'no reply in time', 'pending']
KEEP = ('id', 'state', 'authority', 'filed', 'replied', 'applicant', 'asked', 'outcome', 'answer', 'quote', 'section',
        'kind', 'outlet', 'headline', 'url', 'published', 'doc_url', 'also')


def days(a, b):
    if not (a and b):
        return None
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def build():
    R = json.load(open(os.path.join(RES, 'rti.json'), encoding='utf-8'))
    p = os.path.join(RES, 'verified.json')
    V = json.load(open(p, encoding='utf-8')).get('items', {}) if os.path.exists(p) else {}
    items, unconfirmed, seen = [], [], set()
    for it in R['items']:
        if it['id'] in seen:
            raise SystemExit('FAIL - duplicate id ' + it['id'])
        seen.add(it['id'])
        v = V.get(it['id'], {})
        if v.get('status') not in ('confirmed', 'corrected'):
            unconfirmed.append({'outlet': it.get('outlet'), 'headline': it.get('headline'), 'date': it.get('published'),
                                'reason': v.get('note') or 'not yet checked against its source'})
            continue
        it = dict(it)
        it.update(v.get('fix') or {})
        it = {k: it.get(k, [] if k == 'also' else '') for k in KEEP}
        if it['outcome'] not in OUTCOMES:
            raise SystemExit('FAIL - %s has an outcome outside the list: %r' % (it['id'], it['outcome']))
        if not (it['url'] and it['published'] and it['asked'] and it['answer']):
            raise SystemExit('FAIL - %s lacks a source, date, question or answer' % it['id'])
        for k in ('asked', 'answer', 'applicant'):
            if '—' in it[k] or '–' in it[k]:
                raise SystemExit('FAIL - %s carries a dash the writing rules forbid' % it['id'])
        it['days'] = days(it['filed'], it['replied'])
        if it['days'] is not None and it['days'] < 0:
            raise SystemExit('FAIL - %s was answered before it was filed' % it['id'])
        items.append(it)
    order = {o: i for i, o in enumerate(OUTCOMES)}
    items.sort(key=lambda x: (order[x['outcome']], x['replied'] or x['published']))
    by_outcome = {o: sum(1 for i in items if i['outcome'] == o) for o in OUTCOMES}
    by_authority = {}
    for i in items:
        a = 'The Election Commission' if i['authority'].startswith('Election Commission') else (
            'A Chief Electoral Officer' if i['authority'].startswith('CEO') else 'Another authority')
        by_authority[a] = by_authority.get(a, 0) + 1
    dated = [i['days'] for i in items if i['days'] is not None]
    return {
        'items': [{k: v for k, v in i.items()} for i in items],
        'by_outcome': {o: c for o, c in by_outcome.items() if c},
        'by_authority': by_authority,
        'unconfirmed': sorted(unconfirmed, key=lambda u: u['date'] or ''),
        'counts': {'items': len(items), 'primary': sum(1 for i in items if i['kind'] == 'primary'),
                   'states': sorted({i['state'] for i in items if i['state'] != 'All India'}),
                   'dated': len(dated), 'days_max': max(dated) if dated else None, 'days_min': min(dated) if dated else None,
                   'first': min(i['published'] for i in items), 'last': max(i['published'] for i in items)},
    }


def as_csv(d):
    b = io.StringIO()
    w = csv.writer(b, lineterminator='\n')
    w.writerow(['state', 'authority', 'applicant', 'filed', 'replied', 'days', 'asked', 'outcome', 'answer', 'rti_section', 'kind', 'source', 'published', 'url'])
    for i in d['items']:
        w.writerow([i['state'], i['authority'], i['applicant'], i['filed'], i['replied'], '' if i['days'] is None else i['days'],
                    i['asked'], i['outcome'], i['answer'], i['section'], i['kind'], i['outlet'], i['published'], i['url']])
    return b.getvalue()


def main():
    d = build()
    files = {os.path.join(OUT, 'rti.json'): json.dumps(d, ensure_ascii=False, separators=(',', ':')) + '\n',
             os.path.join(OUT, 'rti.csv'): as_csv(d)}
    if '--check' in sys.argv:
        stale = [p for p, t in files.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != t]
        if stale:
            raise SystemExit('FAIL - stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale))
        print('rti current: %d items' % d['counts']['items'])
        return
    for p, t in files.items():
        open(p, 'w', encoding='utf-8').write(t)
    c = d['counts']
    print('%d applications (%d primary), %s to %s; %d not confirmed' % (c['items'], c['primary'], c['first'], c['last'], len(d['unconfirmed'])))


if __name__ == '__main__':
    main()
