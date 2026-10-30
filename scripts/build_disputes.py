#!/usr/bin/env python3
"""Protests and disputes over the SIR, for india/disputes/.

    python3 scripts/build_disputes.py          # writes data/india/disputes.json and .csv
    python3 scripts/build_disputes.py --check  # fails if either is stale

Reads the research in data/india/raw/disputes_research/ (up.json for Uttar Pradesh, courts.json,
protests.json, form7.json, software.json) and the second reading of each,
tags.json (court, parties and bodies, places and issues for every item, which
the page's filters use),
verified_<name>.json. An item reaches the page only if that reading confirmed it or
corrected it, and a correction replaces the original claim, quote, date or
address. Anything else is listed by outlet and headline under "What we could
not confirm". The press reports the process page already carries, which were
checked when they went on it, join the sections they belong to, so the two
pages cannot disagree.

listings.json holds the hearings and deadlines ahead that a source dates,
for the "Next in court" list at the top of the page and for the calendars
(scripts/build_feeds.py). A listing reaches the page only if its second
reading, verified_listings.json, confirmed or corrected it, and only if the
disputes entry it names is on the page. They are written into disputes.json
under "listings" and into court_listings.csv.

Nothing here says the revision was meant to exclude anyone. A party's claim
is its allegation, attributed by name, and the Commission's reply sits beside
it where one was reported.
"""
import csv
import io
import json
import os
import re
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
FILES = ['courts', 'protests', 'form7', 'software', 'up']
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
# the page's filters read these, from tags.json: the court, the parties and
# bodies that act, the constituencies or districts named, and the issues
TAGS = ('court', 'actors', 'places', 'issues')
ISSUES = {'Form 6', 'Form 7', 'Form 8', 'Pre-printed forms', 'Notices and hearings', 'Documents and declaration',
          'Software (ECINET/ERONET)', 'Names left off or deleted', 'Living electors marked dead', 'Duplicates and errors', 'BLO workload',
          'Deaths', 'Adjudication and appeals', 'Women', 'Migrants', 'Minorities', "Commission's independence",
          'Transparency of lists', 'Schedule and deadlines', 'Police and FIRs', 'Assembly resolution', 'Protest and march'}
# the court listings: what each carries onto the page, and the languages its
# court, matter and what is due are translated into
LKEEP = ('id', 'date', 'date_kind', 'computed_from', 'court', 'state', 'matter', 'due', 'disputes_id', 'source_name', 'source_url', 'quote', 't')
LANGS = ('hi', 'ur', 'te', 'ta', 'bn')
DATE_KINDS = ('exact', 'approximate', 'tentative')
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
            for k in ('claim', 'quote', 'date', 'url', 'outlet', 'kind', 'section', 'state', 'response', 'case', 'headline'):
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
    T = (load('tags') or {}).get('items', {})
    for it in items:
        t = T.get(it['id'])
        if t is None:
            raise SystemExit('FAIL - %s has no entry in tags.json' % it['id'])
        if not set(t.get('issues', [])) <= ISSUES or not t.get('issues'):
            raise SystemExit('FAIL - %s has an issue outside the list, or none' % it['id'])
        for k in TAGS:
            it[k] = t.get(k, '' if k == 'court' else [])
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
        'listings': listings({i['id'] for i in items}),
        'sections': [s for s in sections if s['items']],
        'by_state': dict(sorted(by_state.items(), key=lambda kv: -kv[1])),
        'by_month': dict(sorted(by_month.items())),
        'unconfirmed': sorted(unconfirmed, key=lambda u: u['date'] or ''),
        'counts': {'items': len(items), 'primary': sum(1 for i in items if i['kind'] == 'primary'),
                   'states': len(by_state), 'first': min(i['date'] for i in items), 'last': max(i['date'] for i in items)},
    }


def listings(ids):
    """The hearings and deadlines ahead, soonest first, each checked against
    its source and tied to an entry on the page."""
    import datetime
    d = load('listings')
    if not d:
        return []
    V = (load('verified_listings') or {}).get('items', {})
    out, seen = [], set()
    for it in d['items']:
        if it['id'] in seen:
            raise SystemExit('FAIL - duplicate listing ' + it['id'])
        seen.add(it['id'])
        v = V.get(it['id'], {})
        if v.get('status') not in ('confirmed', 'corrected'):
            continue
        it = dict(it)
        for k in ('date', 'date_kind', 'computed_from', 'court', 'state', 'matter', 'due', 'disputes_id', 'source_name', 'source_url', 'quote', 't'):
            if v.get(k):
                it[k] = v[k]
        try:
            datetime.date.fromisoformat(it['date'])
        except (KeyError, TypeError, ValueError):
            raise SystemExit('FAIL - listing %s has no date that parses' % it['id'])
        if it.get('date_kind') not in DATE_KINDS:
            raise SystemExit('FAIL - listing %s: date_kind must be one of %s' % (it['id'], ', '.join(DATE_KINDS)))
        if it['date_kind'] == 'approximate' and not it.get('computed_from'):
            raise SystemExit('FAIL - listing %s is approximate and does not say how the date was worked out' % it['id'])
        if it.get('disputes_id') not in ids:
            raise SystemExit('FAIL - listing %s names %r, which is not an entry on the disputes page' % (it['id'], it.get('disputes_id')))
        if not (it.get('court') and it.get('matter') and it.get('due') and it.get('source_name') and str(it.get('source_url', '')).startswith('http')):
            raise SystemExit('FAIL - listing %s lacks a court, matter, what is due or a source' % it['id'])
        for lang in LANGS:
            tr = (it.get('t') or {}).get(lang) or {}
            if not all(tr.get(k) for k in ('court', 'matter', 'due')):
                raise SystemExit('FAIL - listing %s has no %s translation of its court, matter and what is due' % (it['id'], lang))
        text = ' '.join([it['court'], it['matter'], it['due']] + [x for tr in it['t'].values() for x in tr.values()])
        if '—' in text or '–' in text:
            raise SystemExit('FAIL - listing %s carries a dash the writing rules forbid' % it['id'])
        if re.search('[০-৯०-९٠-٩۰-۹௦-௯౦-౯]', text):
            raise SystemExit('FAIL - listing %s writes a figure in Indic digits, which the site writes in Western digits' % it['id'])
        out.append({k: it.get(k, '') for k in LKEEP})
    return sorted(out, key=lambda x: (x['date'], x['id']))


def listings_csv(d):
    b = io.StringIO()
    w = csv.writer(b, lineterminator='\n')
    w.writerow(['date', 'date_kind', 'computed_from', 'court', 'state', 'matter', 'due', 'disputes_entry', 'source', 'url', 'quote'])
    for x in d['listings']:
        w.writerow([x['date'], x['date_kind'], x['computed_from'], x['court'], x['state'], x['matter'], x['due'],
                    'india/disputes/#d-' + x['disputes_id'], x['source_name'], x['source_url'], x['quote']])
    return b.getvalue()


def as_csv(d):
    b = io.StringIO()
    w = csv.writer(b, lineterminator='\n')
    w.writerow(['section', 'date', 'state', 'places', 'court', 'parties_and_bodies', 'issues', 'kind', 'source', 'what_happened', 'commission_reply', 'url'])
    for s in d['sections']:
        for i in s['items']:
            w.writerow([s['title'], i['date'], i['state'], '; '.join(i['places']), i['court'], '; '.join(i['actors']), '; '.join(i['issues']),
                        i['kind'], i['outlet'], i['claim'], i['response'], i['url']])
    return b.getvalue()


def by_state(d):
    # items naming each state, as a state page counts them
    items = [i for s in d['sections'] for i in s['items']]
    names = sorted({x.strip() for i in items for x in re.split(r',| and ', i.get('state') or '') if x.strip()})
    return {n: sum(1 for i in items if n in (i.get('state') or '')) for n in names}


def main():
    d = build()
    files = {os.path.join(OUT, 'disputes.json'): json.dumps(d, ensure_ascii=False, separators=(',', ':')) + '\n',
             os.path.join(OUT, 'disputes.csv'): as_csv(d),
             os.path.join(OUT, 'court_listings.csv'): listings_csv(d),
             # the counts alone, for pages that show the count and not the items
             os.path.join(OUT, 'disputes_counts.json'): json.dumps({'counts': d['counts'], 'by_state': by_state(d)}, ensure_ascii=False, separators=(',', ':')) + '\n'}
    if '--check' in sys.argv:
        stale = [p for p, t in files.items() if not os.path.exists(p) or open(p, encoding='utf-8').read() != t]
        if stale:
            raise SystemExit('FAIL - stale: ' + ', '.join(os.path.relpath(p, ROOT) for p in stale))
        print('disputes current: %d items' % d['counts']['items'])
        return
    for p, t in files.items():
        open(p, 'w', encoding='utf-8').write(t)
    c = d['counts']
    print('%d items (%d primary) across %d states, %s to %s; %d not confirmed; %d court listings' % (c['items'], c['primary'], c['states'], c['first'], c['last'], len(d['unconfirmed']), len(d['listings'])))


if __name__ == '__main__':
    main()
