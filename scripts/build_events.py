"""Events about the revision: hearings, marches, protests, press conferences
and official camps, for india/events/.

data/india/raw/events_research/ holds two files.
  events.json           the first reading: each event with its source, a
                        verbatim line from the source giving the date, and
                        the site's own one-line description
  events_verified.json  a second, independent reading of every event, with
                        corrections

Only events the second reading confirmed or corrected are kept, and its
corrections are applied. Whether an event is coming up or past is decided
by the page on the reader's own date, so the file never goes stale on that
count. Events organised by political parties are listed and carry
party: true, which the page marks. Government and Election Commission events
are left out; their dates are on the Rules page. The build fails on any of the site's own text
that breaks the writing rules. Writes data/india/events.json.

    python3 scripts/build_events.py [--check]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'data' / 'india' / 'raw' / 'events_research'
OUT = ROOT / 'data' / 'india' / 'events.json'
KINDS = {'hearing', 'march', 'protest', 'rally', 'press conference', 'convention', 'meeting', 'webinar'}


def rules(text, where):
    if '—' in text or '–' in text:
        sys.exit('FAIL - a dash in %s' % where)
    if ';' in text:
        sys.exit('FAIL - a semicolon in %s' % where)
    if re.search(r'[a-z]: ', text):
        sys.exit('FAIL - a sentence hinged on a colon in %s' % where)
    if re.search(r', not (a|an|the)\b', text) or 'rather than' in text:
        sys.exit('FAIL - an "X, not Y" turn in %s' % where)


def build():
    E = json.loads((RAW / 'events.json').read_text(encoding='utf-8'))
    V = {v['id']: v for v in json.loads((RAW / 'events_verified.json').read_text(encoding='utf-8'))['checked']}
    out, dropped = [], []
    for e in E['events']:
        v = V.get(e['id'])
        if not v or v['status'] not in ('confirmed', 'corrected'):
            dropped.append({'id': e['id'], 'title': e['title'], 'why': (v or {}).get('note', 'not read a second time')})
            continue
        e = dict(e, **(v.get('fix') or {}))
        if e['kind'] not in KINDS:
            sys.exit('FAIL - %s has an unknown kind %r' % (e['id'], e['kind']))
        if not re.fullmatch(r'\d{4}-\d\d-\d\d', e['start']) or (e.get('end') and not re.fullmatch(r'\d{4}-\d\d-\d\d', e['end'])):
            sys.exit('FAIL - %s has no date in YYYY-MM-DD' % e['id'])
        if not e.get('url') or not e.get('quote'):
            sys.exit('FAIL - %s has no source or no line from it' % e['id'])
        rules(e['what'], '%s what' % e['id'])
        out.append(dict({k: e.get(k, '') for k in ('id', 'title', 'organiser', 'start', 'end', 'time', 'place', 'kind', 'states', 'url', 'source_kind', 'quote', 'what')}, party=bool(e.get('party'))))
    out.sort(key=lambda e: (e['start'], e['id']))
    return {'checked': E['generated'], 'scope': E['scope'], 'counts': {'events': len(out)}, 'events': out, 'dropped': dropped}


def main():
    D = build()
    text = json.dumps(D, indent=1, ensure_ascii=False) + '\n'
    if '--check' in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding='utf-8') != text:
            sys.exit('FAIL - data/india/events.json is stale: run scripts/build_events.py')
        print('OK: %d events current' % len(D['events']))
        return
    OUT.write_text(text, encoding='utf-8')
    print('wrote %d events, dropped %d' % (len(D['events']), len(D['dropped'])))


if __name__ == '__main__':
    main()
