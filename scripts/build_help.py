#!/usr/bin/env python3
"""What an elector whose name was left off can do, for help/.

    python3 scripts/build_help.py          # writes data/india/help.json
    python3 scripts/build_help.py --check  # fails if it is stale

Reads data/india/raw/help_research/: remedies.json (the law, the Commission's
orders and the Supreme Court's orders, each step with the document it rests
on), orgs.json to orgs4.json (organisations that helped electors, each with
the source showing the help it gave), and verified.json, an independent second
reading of every remedy and every organisation. A remedy reaches the page only
if that reading confirmed or corrected it. An organisation reaches the page
only if the research marked it to publish and the reading did not reject it.
No political party, and nothing led by a sitting party office-holder, is
listed, and no private person is named.
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RES = os.path.join(ROOT, 'data', 'india', 'raw', 'help_research')
OUT = os.path.join(ROOT, 'data', 'india', 'help.json')
ORDER = ['form6', 'form7', 'appeal', 'helpline_drive', 'legal_aid', 'supreme_court', 'writ']


def load(name):
    p = os.path.join(RES, name + '.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def dash(t):
    return '—' in t or '–' in t


def build():
    V = load('verified') or {}
    VR, VO = V.get('remedies', {}), dict(V.get('orgs', {}))
    # the Uttar Pradesh search (orgs3.json) and the Delhi addition (orgs4.json)
    # were each read again on their own
    VO.update((load('verified_orgs3') or {}).get('orgs', {}))
    VO.update((load('verified_orgs4') or {}).get('orgs', {}))
    R = load('remedies')
    rem = []
    for it in sorted(R['items'], key=lambda x: ORDER.index(x['id'])):
        v = VR.get(it['id'], {})
        if v.get('status') not in ('confirmed', 'corrected'):
            raise SystemExit('FAIL - remedy %s has not been confirmed by the second reading' % it['id'])
        it = dict(it, **{k: v[k] for k in ('plain', 'steps', 'sources', 'title') if v.get(k)})
        for t in [it['plain']] + it.get('steps', []):
            if dash(t):
                raise SystemExit('FAIL - remedy %s carries a dash the writing rules forbid' % it['id'])
        src = [{k: s.get(k) for k in ('doc', 'url', 'date', 'status', 'quote')} for s in it['sources'] if s.get('url')]
        if not src:
            raise SystemExit('FAIL - remedy %s has no source' % it['id'])
        rem.append({'id': it['id'], 'title': it['title'], 'plain': it['plain'], 'steps': it.get('steps', []), 'sources': src})
    # public contacts (contacts.json): organisational lines only, each with the
    # page it is printed on. Two were read only from a search index and are
    # held back until their page is opened.
    C = (load('contacts') or {}).get('contacts', {})
    HOLD = {'dl-vam', 'wb-nakhoda-masjid'}
    orgs, dropped = [], []
    for f in ('orgs', 'orgs2', 'orgs3', 'orgs4'):
        d = load(f)
        if not d:
            continue
        for o in d['organisations']:
            v = VO.get(o['id'], {})
            if not o.get('publish', True) or v.get('status') == 'rejected':
                dropped.append(o['id'])
                continue
            if v.get('status') not in ('confirmed', 'corrected'):
                dropped.append(o['id'])
                continue
            o = dict(o, **{k: v[k] for k in ('what', 'quote', 'source_url', 'active_as_of', 'how_to_reach') if v.get(k)})
            if dash(o['what']) or not (o.get('source_url') and o.get('quote')):
                raise SystemExit('FAIL - organisation %s lacks a source or carries a dash' % o['id'])
            row = {k: o.get(k, '') for k in ('id', 'name', 'state', 'what', 'how_to_reach', 'source_url', 'source_outlet', 'source_date', 'active_as_of', 'confidence', 'quote', 'second_url')}
            c = C.get(o['id'])
            if c and c.get('level') in ('own', 'parent body') and o['id'] not in HOLD:
                if dash(c['how_to_reach']):
                    raise SystemExit('FAIL - contact for %s carries a dash' % o['id'])
                row.update(contact=c['how_to_reach'], contact_level=c['level'], contact_src=c['source_url'], contact_checked=c.get('checked_on', ''))
            orgs.append(row)
    orgs.sort(key=lambda o: (o['state'] == 'India', o['state'], o['name']))
    states = sorted({o['state'] for o in orgs if o['state'] != 'India'})
    # Hindi and Bengali: every sentence on the page, every step and every
    # organisation's description, keyed by the English. strings_en.json holds
    # the page's own sentences; the rest come from the data above, so a new
    # step or organisation cannot reach the page untranslated.
    want = set(json.load(open(os.path.join(RES, 'strings_en.json'), encoding='utf-8')))
    for r in rem:
        want |= {r['title'], r['plain']} | set(r['steps'])
    want |= {o['what'] for o in orgs} | set(states)
    tr = {}
    for lg in ('hi', 'bn'):
        d = load('i18n_' + lg) or {}
        miss = sorted(k for k in want if not d.get(k))
        if miss:
            raise SystemExit('FAIL - %d strings have no %s translation, first: %r' % (len(miss), lg, miss[0][:80]))
        for k in want:
            ph = lambda x: sorted(re.findall(r'\{\w+\}', x))
            if ph(k) != ph(d[k]) or any(n not in d[k] for n in re.findall(r'\b(?:1950|15100)\b', k)) or dash(d[k]):
                raise SystemExit('FAIL - the %s translation of %r changes a placeholder or number, or carries a dash' % (lg, k[:60]))
        tr[lg] = {k: d[k] for k in sorted(want)}
    return {'remedies': rem, 'orgs': orgs, 'org_states': states, 'tr': tr,
            'counts': {'remedies': len(rem), 'orgs': len(orgs), 'states': len(states), 'dropped': len(dropped)}}


COUNTS = os.path.join(ROOT, 'data', 'india', 'help_counts.json')


def main():
    H = build()
    text = json.dumps(H, ensure_ascii=False, separators=(',', ':')) + '\n'
    # the organisations per state, for pages that show the count and not the list
    by = {}
    for o in H['orgs']:
        by[o['state']] = by.get(o['state'], 0) + 1
    counts = json.dumps({'counts': H['counts'], 'orgs_by_state': dict(sorted(by.items()))}, ensure_ascii=False, separators=(',', ':')) + '\n'
    if '--check' in sys.argv:
        for p, t in ((OUT, text), (COUNTS, counts)):
            if not os.path.exists(p) or open(p, encoding='utf-8').read() != t:
                raise SystemExit('FAIL - stale: ' + os.path.relpath(p, ROOT))
        print('help current')
        return
    open(COUNTS, 'w', encoding='utf-8').write(counts)
    open(OUT, 'w', encoding='utf-8').write(text)
    c = json.loads(text)['counts']
    print('%d remedies, %d organisations in %d states (%d left out)' % (c['remedies'], c['orgs'], c['states'], c['dropped']))


if __name__ == '__main__':
    main()
