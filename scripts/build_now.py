#!/usr/bin/env python3
"""The "What to do now" page of each state: which states have one, and the
small data file those pages read.

    python3 scripts/build_now.py           # write data/india/now.json
    python3 scripts/build_now.py --check   # fail if it is stale

A state's page (site/pages/<place>/now/, written by scripts/make_now_pages.py)
works out the stage of its revision in the browser, from process.json and
states.json, with the same code as the claims box on the state's overview
(SIR.owin in assets/sir.js), so it changes with the date and needs no
rebuild. What it also needs is gathered here into one file, so a phone
fetches one small file in place of the five large ones it comes from:

  * cite: every document a step on the page rests on, by a short key that
    assets/now.js names. Each key points into a file the site already
    publishes or holds (the help page's remedies, the forms and timeline of
    process.json, the disputes, states.json), and this script fails if one
    no longer resolves, so a step cannot lose its source quietly;
  * pages: for each state, its page and overview, its Chief Electoral
    Officer's official site and account where the repository cites them,
    how many organisations the help page lists for it, its court matters by
    court on the disputes page, its notice figures (notices.json) and, for
    Delhi, the Supreme Court hearing of 28 October 2026 and The Hindu's count
    of the names left off.

A new state is a row in PAGES, an entry in site/places.json, and a run of
make_now_pages.py, this script, build_site.py and the translations.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'india', 'now.json')
MONTHS = 'January February March April May June July August September October November December'.split()

# One row per state with a page. "place" is the state's id in places.json;
# "ceo" holds only official addresses the repository already cites (CLAUDE.md,
# "Final-roll day", and the sources in data/india/states.csv): Jharkhand has
# none. "bench" names the source in CITE, a disputes item, whose remarks the page states, and
# "split" asks for The Hindu's count from the state's note in states.json.
PAGES = [
    {'state': 'Delhi', 'place': 'dl', 'path': 'delhi/now/',
     'ceo': [['site', 'https://ceodelhi.gov.in/'], ['x', 'https://x.com/CeodelhiOffice']],
     'bench': 'c_bench', 'split': True},
    {'state': 'Maharashtra', 'place': 'mh', 'path': 'maharashtra/now/',
     'ceo': [['site', 'https://ceoelection.maharashtra.gov.in/']]},
    {'state': 'Jharkhand', 'place': 'jh', 'path': 'jharkhand/now/', 'ceo': []},
    {'state': 'Andhra Pradesh', 'place': 'ap', 'path': 'andhrapradesh/now/',
     'ceo': [['x', 'https://x.com/CEOAndhra']]},
    {'state': 'Telangana', 'place': 'hyd', 'path': 'hyderabad/telangana/now/',
     'ceo': [['x', 'https://x.com/CEO_Telangana']]},
    {'state': 'Haryana', 'place': 'hr', 'path': 'haryana/now/',
     'ceo': [['site', 'https://ceoharyana.gov.in/']]},
    {'state': 'Nagaland', 'place': 'nl', 'path': 'nagaland/now/',
     'ceo': [['site', 'https://ceo.nagaland.gov.in/']]},
]

# Every source a step cites. ('help', remedy id, [doc prefixes]) takes those
# documents from the help page's remedy (data/india/help.json, from
# raw/help_research/remedies.json); ('forms' or 'timeline', date, title) one
# entry of process.json; ('disputes', id) one item of the disputes page.
CITE = {
    'c_lists': ('timeline', '2025-12-10', 'Lists before the draft'),
    'c_listed_daily': ('forms', '2025-06-24', 'How objections were to be handled'),
    'c_form6_late': ('forms', '2025-06-24', 'Form 6 for those whose forms did not come back'),
    'c_decl_II': ('forms', '2025-10-27', 'A new declaration for Phase II'),
    'c_decl_III': ('forms', '2026-05-14', 'Phase III keeps the declaration'),
    'c_notices_III': ('timeline', '2026-05-14', 'The rest of the country'),
    'c_docs_home': ('timeline', '2026-09-26', 'Documents at the door, and a drive for those left off'),
    'c_h_form6_sir': ('help', 'form6', ['ECI SIR guidelines with Order No. 23/2025-ERS (Vol.II) of 24.06.2025, para 4(c)']),
    'c_h_get_form6': ('help', 'form6', ['Form 6, Application Form for New Voters (ECI)',
                                      'CEO Karnataka, Press Note on the SIR-2026 draft roll, 24.08.2026, para 6(b)']),
    'c_h_anytime': ('help', 'form6', ['ECI Press Note ECI/PN/120/2026, 26.09.2026',
                                    'ECI press release on Bihar final roll, PIB, 30.09.2025',
                                    'Representation of the People Act, 1950, section 23(3)']),
    'c_h_reapply': ('help', 'form6', ['ECI, Manual on Electoral Rolls, Document 10, Edition 2, March 2023',
                                    'Representation of the People Act, 1950, section 23(1)']),
    'c_h_drive': ('help', 'helpline_drive', ['ECI letter No. 23/2025/ERS(Vol-II), 01.10.2026, para 4(i)-(ii)']),
    'c_h_drive_form6': ('help', 'form6', ['ECI letter No. 23/2025/ERS(Vol-II), 01.10.2026']),
    'c_h_form7': ('help', 'form7', ['Form 7 (ECI)', 'ECI SIR Order No. 23/2025-ERS (Vol.II) of 24.06.2025, para 14',
                                  'ECI SIR guidelines, para 5']),
    'c_h_hearing': ('help', 'form7', ['Registration of Electors Rules, 1960, rule 19(1)(b)(ii)',
                                    'Registration of Electors Rules, 1960, rule 20(2)']),
    'c_h_appeal': ('help', 'appeal', ['Representation of the People Act, 1950, section 24',
                                    'CEO Goa, Press Note on the final roll of the SIR, 21.02.2026',
                                    'Registration of Electors Rules, 1960, rule 27(1)(a)-(b)']),
    'c_h_appeal_order': ('help', 'appeal', ['ECI SIR Order No. 23/2025-ERS (Vol.II) of 24.06.2025, para 14']),
    'c_h_helpline': ('help', 'helpline_drive', ['ECI press release, PIB, 29.10.2025']),
    'c_h_legal': ('help', 'legal_aid', ['NALSA, Legal Aid page (section 12', 'NALSA home page']),
    'c_bench': ('disputes', 'court-54'),
}


def J(*p):
    with open(os.path.join(ROOT, 'data', *p), encoding='utf-8') as fh:
        return json.load(fh)


def long_to_iso(s):
    d, m, y = s.split()
    return '%s-%02d-%02d' % (y, MONTHS.index(m) + 1, int(d))


def resolve(key, spec, H, P, D):
    """The documents one key cites: [{name, url, quote?}], and its date."""
    kind = spec[0]
    if kind == 'help':
        rem = next((r for r in H['remedies'] if r['id'] == spec[1]), None)
        if rem is None:
            raise SystemExit('FAIL - %s: the help page has no remedy %r' % (key, spec[1]))
        items, date = [], None
        for pre in spec[2]:
            # a whole name matches only itself; a prefix ends where a name goes on
            got = [s for s in rem['sources'] if s['doc'] == pre] or [s for s in rem['sources'] if s['doc'].startswith(pre)]
            if not got:
                raise SystemExit('FAIL - %s: the help page\'s remedy %r cites no document starting %r' % (key, spec[1], pre))
            for s in got:
                it = {'name': s['doc'], 'url': s['url'], 'date': s.get('date')}
                if s.get('quote'):
                    it['quote'] = s['quote']
                if s.get('status') == 'press':
                    it['press'] = True
                items.append(it)
                date = date or s.get('date')
        return {'items': items, 'date': date}
    if kind in ('forms', 'timeline'):
        e = [x for x in P[kind] if x['date'] == spec[1] and x['title'] == spec[2]]
        if len(e) != 1:
            raise SystemExit('FAIL - %s: process.json %s has %d entries of %s titled %r' % (key, kind, len(e), spec[1], spec[2]))
        return {'items': [{'name': s['name'], 'url': s['url']} for s in e[0]['src']], 'date': spec[1]}
    if kind == 'disputes':
        e = [it for sec in D['sections'] for it in sec['items'] if it['id'] == spec[1]]
        if len(e) != 1:
            raise SystemExit('FAIL - %s: the disputes page has %d items %r' % (key, len(e), spec[1]))
        it = e[0]
        items = [{'name': it['outlet'] + ', ' + it['headline'], 'url': it['url']}]
        if it.get('second_url'):
            items.append({'name': 'Bar and Bench' if 'barandbench' in it['second_url'] else it['second_url'], 'url': it['second_url']})
        return {'items': items, 'date': it['date'], 'disputes': 'india/disputes/#d-' + it['id']}
    raise SystemExit('FAIL - %s: unknown kind %r' % (key, kind))


def latest(series, cat):
    rows = [x for x in series if x['category'] == cat]
    if not rows:
        return None
    x = max(rows, key=lambda r: r['date'])
    return {'n': x['count'], 'date': x['date'], 'kind': x['kind'], 'url': x['source_url'], 'rounded': bool(x.get('rounded'))}


def split_of(note):
    """The Hindu's count of Delhi's names left off, from the state's note."""
    m = re.search(r"The Hindu's count of the Chief Electoral Officer's booth-wise lists of names left off, published on "
                  r"(\d{1,2} [A-Z][a-z]+ \d{4}), puts (\d+\.\d+) lakh of them as permanently shifted and (\d+\.\d+) lakh as untraceable or absent", note)
    if not m:
        raise SystemExit('FAIL - the Delhi note in states.json no longer gives The Hindu\'s count in the words this script reads')
    return {'date': long_to_iso(m.group(1)), 'shifted': m.group(2), 'absent': m.group(3)}


def places():
    with open(os.path.join(ROOT, 'site', 'places.json'), encoding='utf-8') as fh:
        return {p['id']: p for p in json.load(fh)['places']}


def build():
    H, P, D, S, N = J('india', 'help.json'), J('india', 'process.json'), J('india', 'disputes.json'), J('india', 'states.json'), J('india', 'notices.json')
    PL = places()
    sched = {s['state']: s for s in P['schedules']}
    srow = {r['state']: r for r in S['states']}
    nrow = {r['state']: r for r in N['states']}
    cite = {k: resolve(k, v, H, P, D) for k, v in sorted(CITE.items())}
    pages = {}
    for row in PAGES:
        name = row['state']
        if name not in sched:
            raise SystemExit('FAIL - %s has a "What to do now" page and no schedule in process.json' % name)
        pl = PL.get(row['place'])
        if pl is None or not pl.get('pages'):
            raise SystemExit('FAIL - %s: no place %r with pages in places.json' % (name, row['place']))
        if row['path'] not in [x[0] for x in pl['pages']]:
            raise SystemExit('FAIL - %s: places.json does not list %s among %s\'s pages' % (name, row['path'], row['place']))
        for kind, url in row['ceo']:
            assert kind in ('site', 'x') and url.startswith('https://'), (name, url)
        orgs = sum(1 for o in H['orgs'] if o['state'] == name)
        courts = {}
        for sec in D['sections']:
            if sec['id'] != 'courts':
                continue
            for it in sec['items']:
                if name in it['states'] and it['court']:
                    courts[it['court']] = courts.get(it['court'], 0) + 1
        nr = nrow.get(name)
        notices = None
        if nr and nr.get('notices'):
            notices = {'n': nr['notices'], 'date': nr['date'], 'kind': nr['kind'], 'url': nr['source_url'], 'rounded': bool(nr.get('rounded')),
                       'no_mapping': nr.get('no_mapping'), 'discrepancy': nr.get('discrepancy'),
                       'lists_url': nr.get('lists_source') or (nr['source_url'] if nr.get('lists_same_source') else None),
                       'hearings': latest(nr.get('series', []), 'hearings_held'),
                       'deleted': latest(nr.get('series', []), 'deleted_after_notice')}
        page = {'path': row['path'], 'overview': pl['pages'][0][0], 'label': pl['label'], 'phase': sched[name]['phase'],
                'ceo': row['ceo'], 'orgs': orgs, 'courts': [[c, k] for c, k in sorted(courts.items(), key=lambda x: (-x[1], x[0]))],
                'notices': notices}
        if row.get('bench'):
            if row['bench'] not in CITE:
                raise SystemExit('FAIL - %s: its bench %r is not a source in CITE' % (name, row['bench']))
            page['bench'] = row['bench']
        if row.get('split'):
            r = srow[name]
            d = r['draft_date']
            page['split'] = dict(split_of(r['note']), url=r['source_url'],
                                 name='Chief Electoral Officer, %s, press note on the draft roll of %s.%s.%s' % (name, d[8:], d[5:7], d[:4]))
        pages[name] = page
    return {'cite': cite, 'pages': pages}


def text():
    return json.dumps(build(), ensure_ascii=False, indent=1, sort_keys=True) + '\n'


if __name__ == '__main__':
    new = text()
    old = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else None
    if '--check' in sys.argv:
        if old != new:
            sys.exit('STALE: data/india/now.json, run python3 scripts/build_now.py')
        print('OK: data/india/now.json is current')
    else:
        if old != new:
            open(OUT, 'w', encoding='utf-8').write(new)
        print('wrote data/india/now.json' if old != new else 'data/india/now.json unchanged')
