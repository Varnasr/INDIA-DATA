#!/usr/bin/env python3
"""The rules reported for the "logical discrepancy" flags, for india/flags/.

    python3 scripts/build_flags.py          # writes data/india/flags.json
    python3 scripts/build_flags.py --check  # fails if it is stale

The Election Commission has published no list of the rules its software used
to flag electors for "logical discrepancies". What is known comes from a
Chief Electoral Officer's press note, a Supreme Court order reading the record
before it, and reports. This builds the page's data from items the site
already carries after their second reading: the disputes items
(data/india/disputes.json), the reading list (data/india/reads.json), the RTI
replies (data/india/rti.json) and the Commission's timeline
(data/india/process.json). Where a reading-list summary does not carry a
rule's words, data/india/raw/flags_research/passages.json holds a passage
quoted word for word from that item's own page. It reads nothing else and
writes no sentence of its own: every source keeps the claim, quote and address
it has on the page it comes from.

A rule names the sources that state it, and for each source a phrase that
must appear in that source's own text, so a rule cannot be given a source
that does not say it. A threshold is written once, here, and the page draws
its labels and its check from it.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IN = os.path.join(ROOT, 'data', 'india')
OUT = os.path.join(IN, 'flags.json')
# Passages quoted word for word from reading-list items whose summary does not
# carry the words of a rule. A rule source with a third element names one.
PASSAGES = os.path.join(IN, 'raw', 'flags_research', 'passages.json')

# Each rule: an id the page labels, the test the self-check applies (field,
# operator, value) or None where the check asks nothing that could test it,
# and the sources, each with a phrase from its own text. A third element names
# a passage in PASSAGES, quoted from the source, that holds the phrase, and the
# page shows that passage under the rule.
RULES = [
    {'id': 'parent_young', 'test': ['pgap', 'lt', 15], 'src': [
        ['soft-15', 'less than 15 years or more than 50 years'],
        ['soft-67', 'less than 15 or more than 50 years apart'],
        ['soft-07', '15-to-45-year range'],
        ['up-49', 'a parent less than 15 years older than the elector'],
        ['https://diagramchasing.fun/2026/karnataka-sir', 'Parent Age Difference <15', 'conditions']]},
    {'id': 'parent_old45', 'test': ['pgap', 'gt', 45], 'src': [
        ['soft-07', '15-to-45-year range']]},
    {'id': 'parent_old50', 'test': ['pgap', 'gt', 50], 'src': [
        ['soft-15', 'less than 15 years or more than 50 years'],
        ['soft-13', 'more than 50 years'],
        ['soft-67', 'less than 15 or more than 50 years apart'],
        ['https://diagramchasing.fun/2026/karnataka-sir', 'Parent Age difference >50', 'conditions']]},
    {'id': 'grand_young', 'test': ['ggap', 'lt', 40], 'src': [
        ['soft-15', 'less than 40 years between an elector and grandparent'],
        ['soft-13', 'less than 40 years'],
        ['soft-07', 'less than 40 years older'],
        ['soft-67', 'less than 40 years apart'],
        ['https://diagramchasing.fun/2026/karnataka-sir', 'Grandparent Age difference <40', 'conditions']]},
    # "more than six" children: seven or more, the elector among them
    {'id': 'kids_more6', 'test': ['kids', 'gt', 6], 'src': [
        ['soft-15', 'more than six children being linked to the same parent'],
        ['soft-13', 'more than six progeny'],
        ['soft-07', 'More than six voters had linked themselves to a single ancestor'],
        ['soft-45', 'six other electors had also named the same man as their father'],
        ['form7-102', 'six other persons had given the name of his father'],
        ['https://www.hrw.org/news/2026/10/28/india-mass-voter-roll-exclusions-deeply-flawed', 'six or more siblings']]},
    # The Wire read "six or more" in the code, and Diagram Chasing quotes
    # "Progeny >= 6" from Karnataka's notices: six children, the elector among them
    {'id': 'kids_six', 'test': ['kids', 'ge', 6], 'src': [
        ['soft-67', 'six or more children'],
        ['https://diagramchasing.fun/2026/karnataka-sir', 'Progeny >= 6', 'conditions']]},
    {'id': 'sibling', 'test': ['sib', 'is', True], 'src': [
        ['soft-15', 'less than nine months between siblings'],
        ['process-13', 'sibling age gap of nine months or less'],
        ['https://diagramchasing.fun/2026/karnataka-sir', 'Progeny Age Gap <9 Month', 'conditions'],
        ['https://www.hrw.org/news/2026/10/28/india-mass-voter-roll-exclusions-deeply-flawed', 'siblings born less than nine months apart']]},
    {'id': 'name_own', 'test': ['own', 'is', 'no'], 'src': [
        ['soft-15', "mismatch between the elector's name and the name available in the SIR 2005 records"],
        ['soft-07', 'Differences in spelling between the names'],
        ['process-12', 'Xalxo and Khalkho'],
        ['https://diagramchasing.fun/2026/karnataka-sir', 'Self Name Mismatch', 'names']]},
    {'id': 'name_parent', 'test': ['par', 'is', 'no'], 'src': [
        ['soft-15', "mismatch between the elector's parent's name"],
        ['soft-13', 'mismatch of the father’s name'],
        ['soft-67', "a father's name that does not match"],
        ['https://diagramchasing.fun/2026/karnataka-sir', 'Parent Name Mismatch', 'names']]},
    {'id': 'marital', 'test': ['wed', 'is', True], 'src': [
        ['process-13', 'marital mapping mismatch']]},
    {'id': 'gender', 'test': None, 'src': [
        ['soft-07', 'The gender of the voter did not align with the name provided']]},
    # the other list: an elector who could not be linked to the old roll at all
    {'id': 'no_mapping', 'test': ['map', 'is', 'no'], 'src': [
        ['2026-05-14|The rest of the country', 'the no-mapping list'],
        ['soft-40', "categorised as ‘No Mapping’"],
        ['https://diagramchasing.fun/2026/karnataka-sir', 'Unmapped with Last SIR', 'unmapped']]},
]

# Sources that say the rules were never published or defined.
UNPUBLISHED = [
    ['rti-09', 'not available in the Commission'],
    ['rti-08', 'logical discrepancy'],
    ['process-13', 'never been clearly defined'],
    ['process-11', 'no criteria for deciding which flagged voters to summon had been made public'],
    ['court-37', 'has not published the criteria for logical discrepancies'],
    ['https://internetfreedom.in/analysis-and-explainer-on-the-software-of-the-sir-that-runs-without-transparency/', 'none has a published specification'],
]
# How the notices were produced, as officials and reports describe it.
MADE = [
    ['soft-12', 'not been digitised accurately'],
    ['process-12', 'generated in bulk'],
    ['soft-08', 'that button has disappeared'],
    ['process-16', 'controlled from Delhi'],
    ['soft-45', 'the only option on the screen was to schedule a hearing'],
    ['soft-53', 'decide logical-discrepancy cases themselves'],
    ['soft-67', 'rules used to flag electors are written into the West Bengal dashboard'],
]
# What a flag led to: the notice, the hearing and what came after.
AFTER = [
    ['2026-05-14|The rest of the country', 'notices would go to'],
    ['2026-09-26|Documents at the door, and a drive for those left off', 'A hearing would be held only in exceptional cases'],
    ['soft-40', 'does not mean the voter has been finally deleted'],
    ['soft-54', 'neither mapping nor logical discrepancies affect an elector'],
    ['form7-56', 'could not be reached at hearings and were marked ineligible'],
    ['form7-54', 'deleted on the ground of logical discrepancies'],
    ['https://diagramchasing.fun/2026/karnataka-sir', 'deleted after a notice that flagged children born less than nine months apart'],
    ['court-54', 'had not finally decided whether the logical discrepancy exercise is lawful'],
]
# The count of categories The Hindu gave for the third phase.
CATEGORIES = ['process-13', 'up to 11 categories', 11, 'up from four', 4]


def load(name):
    with open(os.path.join(IN, name + '.json'), encoding='utf-8') as fh:
        return json.load(fh)


def sources():
    out = {}
    D = load('disputes')
    for s in D['sections']:
        for i in s['items']:
            out[i['id']] = {'id': i['id'], 'from': 'disputes', 'date': i['date'], 'state': i.get('state') or 'All India',
                            'kind': i['kind'], 'outlet': i['outlet'], 'headline': i['headline'], 'url': i['url'],
                            'text': i['claim'], 'quote': i.get('quote') or '', 'response': i.get('response') or ''}
    for i in load('rti')['items']:
        out[i['id']] = {'id': i['id'], 'from': 'rti', 'date': i['published'], 'state': i['state'], 'kind': i['kind'],
                        'outlet': i['outlet'], 'headline': i['headline'], 'url': i['url'],
                        'text': i['asked'] + ' ' + i['answer'], 'quote': i.get('quote') or '', 'response': ''}
    for i in load('reads')['items']:
        out[i['url']] = {'id': i['url'], 'from': 'reads', 'date': i['date'], 'state': '', 'kind': 'press',
                         'outlet': i['outlet'], 'headline': i['title'], 'url': i['url'], 'text': i['shows'], 'quote': '',
                         'response': '', 'subscription': bool(i.get('subscription'))}
    for t in load('process')['timeline']:
        k = t['date'] + '|' + t['title']
        src = (t.get('src') or [{}])[0]
        out[k] = {'id': k, 'from': 'process', 'date': t['date'], 'state': 'All India', 'kind': 'primary',
                  'outlet': src.get('name', ''), 'headline': t['title'], 'url': src.get('url', ''), 'text': t['text'],
                  'quote': '', 'response': ''}
    return out


def build():
    S = sources()
    used = {}

    def take(key, needle):
        assert key in S, 'no item %s among the checked items' % key
        s = S[key]
        hay = ' '.join([s['text'], s['quote'], s['response'], s['headline']])
        assert needle in hay, '%s does not say %r' % (key, needle)
        used[key] = s
        return key

    P = json.load(open(PASSAGES, encoding='utf-8'))['sources']
    # a reading-list item carries no state, so the passages file names the
    # state whose notices it quotes
    for k, p in P.items():
        if p.get('state') and k in S and not S[k]['state']:
            S[k]['state'] = p['state']

    def passage(key, needle, name):
        assert key in S, 'no item %s among the checked items' % key
        q = P[key]['passages'][name]
        assert needle in q, 'passage %s of %s does not say %r' % (name, key, needle)
        used[key] = S[key]
        return q

    rules = []
    for r in RULES:
        src, quotes = [], {}
        for e in r['src']:
            if len(e) == 3:
                quotes[e[0]] = {'quote': passage(*e)}
                src.append(e[0])
            else:
                src.append(take(*e))
        rule = {'id': r['id'], 'test': r['test'], 'src': src}
        if quotes:
            rule['quotes'] = quotes
        rules.append(rule)
    unpub = [take(k, n) for k, n in UNPUBLISHED]
    made = [take(k, n) for k, n in MADE]
    after = [take(k, n) for k, n in AFTER]
    cid, cn, n, fn, f = CATEGORIES
    take(cid, cn)
    take(cid, fn)
    now = load('now')['pages']
    return {
        'rules': rules, 'unpublished': unpub, 'made': made, 'after': after,
        'categories': {'src': cid, 'phase3': n, 'first': f},
        'sources': {k: used[k] for k in sorted(used)},
        'now': sorted([[st, p['path']] for st, p in now.items()]),
        'counts': {'rules': len(rules), 'sources': len(used),
                   'primary': sum(1 for s in used.values() if s['kind'] == 'primary'),
                   'rule_sources': len({k for r in rules for k in r['src']}),
                   'first': min(s['date'] for s in used.values()), 'last': max(s['date'] for s in used.values())},
    }


def main():
    text = json.dumps(build(), ensure_ascii=False, separators=(',', ':')) + '\n'
    if '--check' in sys.argv:
        if not os.path.exists(OUT) or open(OUT, encoding='utf-8').read() != text:
            raise SystemExit('FAIL - stale: data/india/flags.json (run scripts/build_flags.py)')
        print('flags current')
        return
    open(OUT, 'w', encoding='utf-8').write(text)
    d = json.loads(text)
    print('%d rules from %d sources (%d official)' % (d['counts']['rules'], d['counts']['sources'], d['counts']['primary']))


if __name__ == '__main__':
    main()
