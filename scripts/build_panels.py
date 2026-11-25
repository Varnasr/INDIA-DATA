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

The national figures in data/india/states.json move with every draft and
final roll, so the site's own text never writes them out. It names them in
braces and the build fills them in from states.json:

  {final.removed}              a count, in Indian digit grouping: 8,87,25,044
  {final.per_100:2}            a figure to two places: 12.42
  {total.removed:crore2}       in crore, to two places: 13.39
  {n.no_final:Word}            a count of states in words: Seven (or seven)
  {states.West Bengal.withheld}  a figure from one state's row

A key is a path into the national blocks of states.json (adults, total,
after_draft, final), one state's row (states.<name>.<field>), or one of the
figures in derived() below. The build fails on a key that does not exist.
It also fails on the site's own text where a national figure is still
written out. That means a count of a thousand or more equal to one in WATCH,
and any count of states, rate or share written in the words that name a
national set ("24 states with a final roll", "13.8 per cent of the names
left off", "14.08 per 100 on the rolls before"), whatever its value. Other
short figures are left alone, because as the national figures move they meet
unrelated ones by chance. A figure that is the person's own, or names
another set, goes in the person's 'literal' list in plain.json, with the
phrase it sits in and the reason. A count of states in words fails below
two, since the sentence around it then needs rewriting.

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


WORDS = ('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen '
         'sixteen seventeen eighteen nineteen twenty').split()
KEY = re.compile(r'\{([A-Za-z0-9_. ]+?)(?::(word|Word|crore2|lakh2|[0-9]))?\}')
NATIONAL = ('adults', 'total', 'after_draft', 'final')


def ind(n):
    """Indian digit grouping, as the site prints counts: 4,55,00,011."""
    s = str(abs(int(n)))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        s = ','.join(([head] if head else []) + parts + [tail])
    return ('-' if n < 0 else '') + s


def derived(S):
    """National figures the panels quote that states.json does not store
    under a name of its own, worked out from its rows as build_india.py
    works out the stored ones."""
    draft = [r for r in S['states'] if r.get('removed') is not None]
    final = [r for r in draft if r.get('electors_final') is not None]
    return {
        # states with a draft and no final roll yet
        'n.no_final': len(draft) - len(final),
        # the rolls before the revision, in the states with a draft and in those with a final roll
        'total.before': sum(r['electors_before'] for r in draft),
        'final.before': sum(r['electors_before'] for r in final),
    }


def figures(S):
    """Every national figure a placeholder may name, by its key."""
    F = {}

    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, path + [k])
        elif isinstance(o, (int, float)) and not isinstance(o, bool):
            F['.'.join(path)] = o
    for b in NATIONAL:
        walk(S[b], [b])
    F.update(derived(S))
    return F


def lookup(key, S, F):
    if key in F:
        return F[key]
    m = re.fullmatch(r'states\.(.+)\.([a-z_0-9]+)', key)
    if m:
        row = next((r for r in S['states'] if r['state'] == m.group(1)), None)
        if row is not None and isinstance(row.get(m.group(2)), (int, float)):
            return row[m.group(2)]
    return None


def fill(text, S, F, where):
    """The text with each {key} replaced by its figure from states.json."""
    def one(m):
        key, fmt = m.group(1), m.group(2)
        v = lookup(key, S, F)
        if v is None:
            sys.exit('FAIL - %s names {%s}, which data/india/states.json does not carry' % (where, key))
        if fmt in ('word', 'Word'):
            if v != int(v) or not 2 <= v < len(WORDS):
                sys.exit('FAIL - %s counts {%s} in words and it is now %s: rewrite the sentence' % (where, key, v))
            w = WORDS[int(v)]
            return w.capitalize() if fmt == 'Word' else w
        if fmt in ('crore2', 'lakh2'):
            return '%.2f' % round(v / (1e7 if fmt == 'crore2' else 1e5) + 1e-9, 2)
        if fmt:
            return '%.*f' % (int(fmt), round(v + 1e-9, int(fmt)))
        if v != int(v):
            sys.exit('FAIL - %s prints {%s} as a count, and it is %s: give it a number of places' % (where, key, v))
        return ind(v)
    return KEY.sub(one, text)


# the national counts a panel sentence quotes: one written out in full is
# that count gone stale, or about to. The list is fixed here, and never read
# off plain.json, so that writing a figure out cannot also take it off the list.
WATCH = ('adults.states', 'adults.roll_total', 'adults.draft_total', 'adults.adults_total',
         'total.states', 'total.removed', 'total.dead', 'total.shifted_absent_other', 'total.duplicate', 'total.before',
         'after_draft.states', 'after_draft.removed',
         'final.states', 'final.removed', 'final.before', 'final.net_after_draft', 'n.no_final')
NUM = re.compile(r'(?<![0-9.,{])([0-9]{1,3}(?:,[0-9]{2})*,[0-9]{3}|[0-9]{4,})(?![0-9])')
COUNT = r'\b(?P<n>[0-9]+|%s)' % '|'.join(WORDS[1:])
SHARE = r'(?P<n>[0-9]+\.[0-9]+)'
# a count of states, a rate or a share written in the words that name one of
# the national sets, whatever its value: these are the sentences a final
# roll makes wrong
SETS = [re.compile(COUNT + r' states(?: and union territories)? (?:with an? (?:draft|final roll|projection)|with final rolls'
                   r'|with projected adults|with projections|whose final rolls|that (?:report|published)|it covers'
                   r'|(?:with a draft )?have no final roll)', re.I),
        re.compile(r'left off the drafts in (?P<n>[0-9]+) states'),
        re.compile(SHARE + r'(?:%| per cent) of (?:the names left off|them, which)'),
        re.compile(SHARE + r' per 100 (?:of the \S+ )?on the rolls before'),
        re.compile(r'names were left off of \S+ \(' + SHARE + r' per 100\)')]


def literals(text, F):
    """Figures written out in the site's own text that should be named in
    braces: a count of a thousand or more equal to one in WATCH, and any
    count, rate or share in the words that name a national set.
    (start, end, keys)."""
    out = []
    for m in NUM.finditer(text):
        v = int(m.group(1).replace(',', ''))
        keys = [k for k in WATCH if F.get(k) == v]
        if keys:
            out.append((m.start(), m.end(), keys))
    for rx in SETS:
        for m in rx.finditer(text):
            out.append((m.start('n'), m.end('n'), []))
    return out


def guard(text, F, keep, where):
    """Fail on a national figure written out instead of named."""
    spans = [(m.start(), m.end()) for p in keep for m in re.finditer(re.escape(p), text)]
    for a, b, keys in literals(text, F):
        if any(x <= a and b <= y for x, y in spans):
            continue
        what = ' or '.join('{%s}' % k for k in keys) if keys else 'a count, rate or share of one of the national sets'
        sys.exit('FAIL - %s writes out %s, which is %s in data/india/states.json: name it in braces, '
                 'or add the phrase to the person\'s literal list with the reason' % (where, text[a:b], what))


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
    S = json.loads((ROOT / 'data' / 'india' / 'states.json').read_text(encoding='utf-8'))
    F = figures(S)
    ver = {(v['person'], v['claim_index']): v for v in V}
    ent = {e['id']: e for e in C['entries']}
    if set(P['order']) != set(ent):
        sys.exit('FAIL - plain.json order does not match the people in claims.json')
    people, dropped = [], []
    for pid in P['order']:
        e, pl = ent[pid], P['people'][pid]
        keep = [p for p, why in pl.get('literal', [])]
        texts = [t for t in [pl['role'], pl['intro'], pl.get('dropped_note', '')] + pl['strongest'] + pl['further'] if t]
        texts += [w.get(f) or '' for w in pl['claims'].values() for f in ('rests', 'site', 'stops')]
        for p, why in pl.get('literal', []):
            if not why or not any(p in t for t in texts):
                sys.exit('FAIL - %s keeps "%s" literal, which its text no longer carries or which has no reason' % (pid, p))
            if not literals(p, F):
                sys.exit('FAIL - %s keeps "%s" literal, which no longer holds a national figure: take it off the list' % (pid, p))

        def site(t, where):
            # the site's own words: no national figure written out, each
            # named one filled in, then the writing rules
            guard(t, F, keep, where)
            t = fill(t, S, F, where)
            rules(t, where)
            return t
        pl = dict(pl, role=site(pl['role'], pid + ' role'), intro=site(pl['intro'], pid + ' intro'),
                  dropped_note=site(pl.get('dropped_note', ''), pid + ' dropped_note'),
                  strongest=[site(t, '%s strongest %d' % (pid, i)) for i, t in enumerate(pl['strongest'])],
                  further=[site(t, '%s further %d' % (pid, i)) for i, t in enumerate(pl['further'])])
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
            w = dict(w, **{f: site(w[f], '%s claim %d %s' % (pid, i, f)) for f in ('rests', 'site', 'stops') if w.get(f)})
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
