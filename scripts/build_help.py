#!/usr/bin/env python3
"""What an elector whose name was left off can do, for help/.

    python3 scripts/build_help.py          # writes data/india/help.json
    python3 scripts/build_help.py --check  # fails if it is stale

Reads data/india/raw/help_research/: remedies.json (the law, the Commission's
orders and the Supreme Court's orders, each step with the document it rests
on), orgs.json and orgs2.json (organisations that helped electors, each with
the source showing the help it gave), and verified.json, an independent second
reading of every remedy and every organisation. A remedy reaches the page only
if that reading confirmed or corrected it. An organisation reaches the page
only if the research marked it to publish and the reading did not reject it.
No political party, and nothing led by a sitting party office-holder, is
listed, and no private person is named.
"""
import json
import os
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
    VR, VO = V.get('remedies', {}), V.get('orgs', {})
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
    orgs, dropped = [], []
    for f in ('orgs', 'orgs2'):
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
            orgs.append({k: o.get(k, '') for k in ('id', 'name', 'state', 'what', 'how_to_reach', 'source_url', 'source_outlet', 'source_date', 'active_as_of', 'confidence', 'quote', 'second_url')})
    orgs.sort(key=lambda o: (o['state'] == 'India', o['state'], o['name']))
    states = sorted({o['state'] for o in orgs if o['state'] != 'India'})
    return {'remedies': rem, 'orgs': orgs, 'org_states': states,
            'counts': {'remedies': len(rem), 'orgs': len(orgs), 'states': len(states), 'dropped': len(dropped)}}


def main():
    text = json.dumps(build(), ensure_ascii=False, separators=(',', ':')) + '\n'
    if '--check' in sys.argv:
        if not os.path.exists(OUT) or open(OUT, encoding='utf-8').read() != text:
            raise SystemExit('FAIL - stale: data/india/help.json')
        print('help current')
        return
    open(OUT, 'w', encoding='utf-8').write(text)
    c = json.loads(text)['counts']
    print('%d remedies, %d organisations in %d states (%d left out)' % (c['remedies'], c['orgs'], c['states'], c['dropped']))


if __name__ == '__main__':
    main()
