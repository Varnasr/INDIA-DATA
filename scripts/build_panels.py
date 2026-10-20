"""Panels on the reading page (india/reading/): what commentators say, set
beside the site's own figures.

data/india/raw/panels_research/ holds three files.
  claims.json    each person's pieces and quotations, verbatim, with the
                 first reading's notes on what each rests on
  verified.json  a second, independent reading of every quotation, with
                 corrections
  plain.json     the site's own wording around each quotation (what it
                 rests on, the site's figures, where they stop), each
                 person's role, strongest points and overreach

Only quotations the second reading confirmed or corrected are kept, its
corrections are applied, and a quotation plain.json drops (with a reason)
stays off the page. The build fails on any of the site's own text that
breaks the writing rules, and on any figure plain.json says it quotes that
the published file no longer carries. Writes data/india/panels.json.

    python3 scripts/build_panels.py [--check]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'data' / 'india' / 'raw' / 'panels_research'
OUT = ROOT / 'data' / 'india' / 'panels.json'
# a quotation of these kinds stands alone, with no figures beside it
BARE = {'concession', 'framing'}


def rules(text, where):
    """The site's writing rules, for the site's own words (never a quotation)."""
    if '—' in text or '–' in text:
        sys.exit('FAIL - a dash in %s' % where)
    if ';' in text:
        sys.exit('FAIL - a semicolon in %s' % where)
    if re.search(r'[a-z]: ', text):
        sys.exit('FAIL - a sentence hinged on a colon in %s' % where)
    if re.search(r', not (a|an|the)\b', text):
        sys.exit('FAIL - an "X, not Y" turn in %s' % where)


def held(val, txt):
    """A figure the file stores to more places than the panel quotes still
    counts when it rounds to the quoted value (27.9776 is 27.98)."""
    if not re.fullmatch(r'-?[0-9]+\.[0-9]+', val):
        return False
    k = len(val.split('.')[1])
    for m in re.finditer(r'(?<![0-9.])-?[0-9]+\.[0-9]{%d,}(?![0-9])' % (k + 1), txt):
        if abs(round(float(m.group()) + 1e-9, k) - float(val)) < 1e-9:
            return True
    return False


def build():
    C = json.loads((RAW / 'claims.json').read_text(encoding='utf-8'))
    V = json.loads((RAW / 'verified.json').read_text(encoding='utf-8'))
    P = json.loads((RAW / 'plain.json').read_text(encoding='utf-8'))
    ver = {(v['person'], v['claim_index']): v for v in V}
    ent = {e['id']: e for e in C['entries']}
    if set(P['order']) != set(ent):
        sys.exit('FAIL - plain.json order does not match the people in claims.json')
    people, dropped = [], []
    for pid in P['order']:
        e, pl = ent[pid], P['people'][pid]
        for f in ('role', 'intro'):
            rules(pl[f], '%s %s' % (pid, f))
        for f in ('strongest', 'further'):
            for i, t in enumerate(pl[f]):
                rules(t, '%s %s %d' % (pid, f, i))
        pieces = {p['id']: p for p in e['pieces']}
        claims, used = [], []
        for i, c in enumerate(e['claims']):
            v = ver.get((e['name'], i))
            why = pl.get('drop', {}).get(str(i))
            if why:
                dropped.append({'person': pl['name'], 'quote': c['quote'], 'why': why})
                continue
            if not v or v['status'] not in ('confirmed', 'corrected'):
                dropped.append({'person': pl['name'], 'quote': c['quote'], 'why': 'not confirmed by the second reading'})
                continue
            c = dict(c, **{k: x for k, x in (v.get('fix') or {}).items() if k in ('quote', 'piece', 'relies_on', 'check', 'site_counts')})
            w = pl['claims'].get(str(i), {})
            bare = c['kind'] in BARE
            if not bare and not (w.get('rests') and w.get('site') and w.get('stops')) and not (c['kind'] == 'projection or survey' and w.get('rests')):
                sys.exit('FAIL - %s claim %d has no wording for what it rests on, the site and where it stops' % (pid, i))
            for f in ('rests', 'site', 'stops'):
                if w.get(f):
                    rules(w[f], '%s claim %d %s' % (pid, i, f))
            for fn, val in w.get('uses', []):
                txt = (ROOT / fn).read_text(encoding='utf-8')
                if not re.search(r'(?<![0-9.])' + re.escape(val) + r'(?![0-9])', txt) and not held(val, txt):
                    sys.exit('FAIL - %s claim %d quotes %s, which %s no longer carries' % (pid, i, val, fn))
            pc = pieces[c['piece']]
            used.append(pc['id'])
            claims.append({
                'quote': c['quote'], 'lang': 'hi' if re.search('[ऀ-ॿ]', c['quote']) else 'en',
                'translation': c.get('translation') or '', 'when': c.get('timestamp') or '',
                'kind': w.get('kind') or P['kinds'][c['kind']], 'piece': pc['id'],
                'outlet': w.get('outlet') or '',
                'rests': w.get('rests', ''), 'site': w.get('site', ''), 'stops': w.get('stops', ''),
            })
        ps = []
        for pc in e['pieces']:
            if pc['id'] not in used:
                continue
            if not pc.get('url'):
                sys.exit('FAIL - %s piece %s has no address' % (pid, pc['id']))
            ps.append({'id': pc['id'], 'title': pc['title'], 'title_en': pc.get('title_en') or '', 'outlet': pc['outlet'],
                       'date': pc['date'], 'url': pc['url'], 'length': pc.get('length') or ''})
        people.append({'id': pid, 'name': pl['name'], 'role': pl['role'], 'intro': pl['intro'],
                       'note': pl.get('dropped_note', ''), 'pieces': ps, 'claims': claims,
                       'strongest': pl['strongest'], 'further': pl['further']})
    # newest first: a panel's date is that of the latest piece it quotes, and
    # panels of the same date keep the order of plain.json
    people.sort(key=lambda p: max(x['date'] for x in p['pieces']), reverse=True)
    n = sum(len(p['claims']) for p in people)
    return {'checked': C['generated'], 'counts': {'people': len(people), 'quotes': n}, 'people': people, 'dropped': dropped}


def main():
    D = build()
    text = json.dumps(D, indent=1, ensure_ascii=False) + '\n'
    if '--check' in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding='utf-8') != text:
            sys.exit('FAIL - data/india/panels.json is stale: run scripts/build_panels.py')
        print('OK: %d people, %d quotations current' % (D['counts']['people'], D['counts']['quotes']))
        return
    OUT.write_text(text, encoding='utf-8')
    print('wrote %d people, %d quotations, dropped %d' % (D['counts']['people'], D['counts']['quotes'], len(D['dropped'])))


if __name__ == '__main__':
    main()
