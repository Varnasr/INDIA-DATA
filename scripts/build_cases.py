"""Case studies: the places whose figures stand out, and what the records and
the reporting say about each.

Reads data/india/raw/cases_research: one research file per case (<file>.json,
each item a claim, a verbatim quote, outlet, date, address and kind), an
independent second reading of every item (verified_<file>.json) and the site's
own words for each item (plain.json). Writes data/india/cases.json.

    python3 scripts/build_cases.py           # write
    python3 scripts/build_cases.py --check   # fail if the output is stale

An item is shown only if the second reading confirmed or corrected it, it is
not dropped in plain.json, and plain.json gives it a sentence. The sentence is
the site's own and is held to the writing rules; the quote and the address
stay the source's. Every rejected or dropped item is listed with its reason, so
nothing leaves the page silently. The figures for each place are not stored
here: the page reads them from the state's own files when it loads.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'india', 'raw', 'cases_research')
OUT = os.path.join(ROOT, 'data', 'india', 'cases.json')
CHECK = '--check' in sys.argv
GROUPS = ('records', 'reported', 'said')


def rules(text, where):
    if '—' in text or '–' in text:
        sys.exit('FAIL - a dash in %s' % where)
    if ';' in text:
        sys.exit('FAIL - a semicolon in %s' % where)
    if re.search(r'[a-z]: ', text):
        sys.exit('FAIL - a sentence hinged on a colon in %s' % where)
    if re.search(r', not (a|an|the)\b|\bnot only\b', text):
        sys.exit('FAIL - an "X, not Y" turn in %s' % where)


def load(name):
    with open(os.path.join(RAW, name), encoding='utf-8') as fh:
        return json.load(fh)


def build():
    P = load('plain.json')
    cases = []
    for c in P['cases']:
        R = load(c['file'] + '.json')
        V = {v['id']: v for v in load('verified_' + c['file'] + '.json')}
        rules(c['intro'], c['id'] + ' intro')
        items, left = {g: [] for g in GROUPS}, []
        for it in R['items']:
            v = V.get(it['id'])
            assert v, 'no second reading of ' + it['id']
            fix = v.get('fix') or {}
            if v['status'] not in ('confirmed', 'corrected'):
                left.append({'id': it['id'], 'why': v['why']})
                assert it['id'] not in c['items'], it['id'] + ' was not confirmed and must not be shown'
                continue
            if it['id'] in c['drop']:
                left.append({'id': it['id'], 'why': c['drop'][it['id']]})
                continue
            assert it['id'] in c['items'], 'no sentence for ' + it['id'] + ' in plain.json'
            group, text = c['items'][it['id']]
            assert group in GROUPS, it['id']
            rules(text, it['id'])
            date = fix.get('date', it['date'])
            items[group].append({'id': it['id'], 'text': text, 'outlet': fix.get('outlet', it['outlet']),
                                 'date': date if re.fullmatch(r'\d{4}-\d{2}-\d{2}', date or '') else '',
                                 'url': fix.get('url', it['url'])})
        extra = set(c['items']) - {x['id'] for g in items.values() for x in g}
        assert not extra, 'sentences for items that are not shown: %s' % sorted(extra)
        for g in GROUPS:
            items[g].sort(key=lambda x: x['date'] or '9999')
        for t in c['not_found']:
            rules(t, c['id'] + ' not found')
        cases.append({'id': c['id'], 'title': c['title'], 'intro': c['intro'], 'items': items,
                      'not_found': c['not_found'], 'left_out': [x['id'] for x in left]})
    text = json.dumps({'cases': cases}, ensure_ascii=False, indent=1) + '\n'
    old = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else None
    return text, old != text


if __name__ == '__main__':
    text, stale = build()
    if CHECK:
        if stale:
            sys.exit('STALE, run python3 scripts/build_cases.py')
        print('OK: data/india/cases.json matches its research')
    else:
        open(OUT, 'w', encoding='utf-8').write(text)
        d = json.loads(text)
        for c in d['cases']:
            print(c['id'], {g: len(v) for g, v in c['items'].items()}, 'left out', len(c['left_out']))
